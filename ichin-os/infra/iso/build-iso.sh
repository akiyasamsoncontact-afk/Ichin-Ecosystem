#!/usr/bin/env bash
set -euo pipefail

# ICHIN OS — Full ISO Build Script
# Usage: ./build-iso.sh [--docker]
#   --docker: Build inside Docker container (recommended for cross-platform)
#   (no flag): Build natively (requires Linux with build tools)

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

BUILD_MODE="${1:-native}"
ISO_NAME="ichin-os-$(date +%Y%m%d).iso"
BUILD_DIR="build"

echo "=== ICHIN OS ISO Builder ==="
echo "Mode: $BUILD_MODE"
echo "ISO:  $ISO_NAME"

if [ "$BUILD_MODE" = "--docker" ]; then
    echo ""
    echo "[1/5] Building Docker builder image..."
    docker build -t ichin-iso-builder -f Dockerfile.iso .

    echo "[2/5] Building kernel & services in Docker..."
    docker run --rm -v "$DIR/..:/ichin" -w /ichin ichin-iso-builder \
        bash /ichin/infra/iso/build-iso.sh native

    echo "[3/5] Copying artifacts..."
    cp "$BUILD_DIR/$ISO_NAME" "$ISO_NAME" 2>/dev/null || true

    echo ""
    echo "=== ISO built: $ISO_NAME ==="
    echo "Run: qemu-system-x86_64 -cdrom $ISO_NAME -m 2G"
    exit 0
fi

# === Native build ===

# Check dependencies
MISSING=""
for cmd in wget make gcc python3 pip3 cpio gzip grub-mkrescue xorriso; do
    command -v "$cmd" &>/dev/null || MISSING="$MISSING $cmd"
done
if [ -n "$MISSING" ]; then
    echo "ERROR: Missing dependencies:$MISSING"
    echo "Install them: sudo apt install build-essential grub-pc-bin grub-common xorriso cpio python3-pip wget"
    exit 1
fi

echo ""
echo "[1/5] Building Linux kernel..."
make -f Makefile kernel KERNEL_DIR="$BUILD_DIR/kernel"

echo ""
echo "[2/5] Building ICHIN bare-metal kernel (if possible)..."
make -f Makefile ichin-kernel BUILD_DIR="$BUILD_DIR" KERNEL_SRC="../../kernel" 2>/dev/null || \
    echo "  (bare-metal kernel build skipped — not critical for ISO)"

echo ""
echo "[3/5] Preparing initramfs with ICHIN services..."
make -f Makefile initramfs BUILD_DIR="$BUILD_DIR" INITRAMFS_DIR="$BUILD_DIR/initramfs" \
    KERNEL_DIR="$BUILD_DIR/kernel" SERVICES_DIR="../../services" KERNEL_SRC="../../kernel"

echo ""
echo "[4/5] Installing Python dependencies..."
make -f Makefile services BUILD_DIR="$BUILD_DIR" SERVICES_DIR="../../services"

echo ""
echo "[5/5] Assembling bootable ISO..."
make -f Makefile iso BUILD_DIR="$BUILD_DIR" ISO_DIR="$BUILD_DIR/iso" \
    ISO_NAME="$ISO_NAME" KERNEL_DIR="$BUILD_DIR/kernel" SERVICES_DIR="../../services" \
    APPS_DIR="../../apps"

echo ""
echo "=== Build complete ==="
echo "ISO: $ISO_NAME ($(du -h "$ISO_NAME" | cut -f1))"
echo ""
echo "Quick test:"
echo "  qemu-system-x86_64 -cdrom $ISO_NAME -m 2G -serial stdio"
echo ""
echo "Write to USB:"
echo "  dd if=$ISO_NAME of=/dev/sdX bs=4M status=progress"
