#!/usr/bin/env bash
set -euo pipefail

# ICHIN OS Kernel Build Script
# Produces a bootable ISO from the bare-metal x86_64 kernel
# Usage: ./build.sh [release|debug]

PROFILE="${1:-release}"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=== ICHIN OS Kernel Build ==="
echo "Profile: $PROFILE"

# Step 1: Build kernel in Docker
echo "[1/3] Building kernel (Docker cross-compile)..."
docker build -t ichin-kernel-builder -f Dockerfile.build .
docker run --rm -v "$DIR:/build" ichin-kernel-builder \
    bash -c "cd /build && cargo build --target target.json -Z build-std=core,alloc --$PROFILE"

KERNEL_BIN="target/x86_64-unknown-none/$PROFILE/ichin-kernel"
if [ ! -f "$KERNEL_BIN" ]; then
    echo "ERROR: Kernel binary not found at $KERNEL_BIN"
    exit 1
fi

# Step 2: Prepare ISO root
echo "[2/3] Preparing ISO structure..."
rm -rf iso_root
mkdir -p iso_root/boot/limine

cp "$KERNEL_BIN" iso_root/boot/ichin-kernel
cp limine.conf iso_root/
cp -r /limine/* iso_root/boot/limine/ 2>/dev/null || \
    cp -r limine/* iso_root/boot/limine/ 2>/dev/null || true

# Step 3: Generate ISO
ISO_NAME="ichin-os-$(date +%Y%m%d).iso"
echo "[3/3] Generating ISO: $ISO_NAME"

xorriso -as mkisofs \
    -b boot/limine/limine-bios-cd.bin \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    --efi-boot boot/limine/limine-uefi-cd.bin \
    -efi-boot-part --efi-boot-image --protective-msdos-label \
    iso_root -o "$ISO_NAME"

# Install Limine BIOS stage
if [ -f /limine/limine ]; then
    /limine/limine bios-install "$ISO_NAME"
elif [ -f limine/limine ]; then
    ./limine/limine bios-install "$ISO_NAME"
fi

rm -rf iso_root
echo "=== Build complete: $ISO_NAME ==="
echo "Run with: qemu-system-x86_64 -cdrom $ISO_NAME -serial stdio -m 512M"
