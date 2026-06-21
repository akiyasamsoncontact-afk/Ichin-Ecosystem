# ICHIN OS Kernel Build & ISO Generator
# Uses Docker for cross-compilation (Rust nightly + x86_64-unknown-none)

.PHONY: all build iso clean docker-build

TOOLCHAIN ?= nightly-2024-07-01
PROFILE ?= release
KERNEL_BIN = target/x86_64-unknown-none/$(PROFILE)/ichin-kernel
ISO_NAME = ichin-os-$(shell date +%Y%m%d).iso

all: iso

# Build kernel via Docker (handles cross-compilation for bare-metal)
docker-build:
	docker build -t ichin-kernel-builder -f Dockerfile.build .
	docker run --rm -v $(PWD):/build ichin-kernel-builder \
		bash -c "cd /build && cargo build --target target.json -Z build-std=core,alloc --$(PROFILE)"

# Build kernel directly (requires Rust nightly + x86_64 target)
build:
	cargo build --target target.json -Z build-std=core,alloc --$(PROFILE)

# Create bootable ISO
iso: docker-build
	@mkdir -p iso_root/boot
	@cp $(KERNEL_BIN) iso_root/boot/ichin-kernel
	@cp limine.conf iso_root
	@cp -r limine iso_root/boot/
	@xorriso -as mkisofs -b boot/limine/limine-bios-cd.bin \
		-no-emul-boot -boot-load-size 4 -boot-info-table \
		--efi-boot boot/limine/limine-uefi-cd.bin \
		-efi-boot-part --efi-boot-image --protective-msdos-label \
		iso_root -o $(ISO_NAME)
	@./limine/limine bios-install $(ISO_NAME)
	@rm -rf iso_root
	@echo "=== ISO created: $(ISO_NAME) ==="

# Run in QEMU
run: iso
	qemu-system-x86_64 -cdrom $(ISO_NAME) -serial stdio -m 512M -cpu host

# Clean build artifacts
clean:
	cargo clean
	rm -rf iso_root *.iso

# Setup: download Limine bootloader
setup:
	@mkdir -p limine
	@wget -q https://github.com/limine-bootloader/limine/releases/download/v8.3.0/limine-8.3.0.zip -O /tmp/limine.zip
	@unzip -q /tmp/limine.zip -d limine/
	@echo "Limine bootloader v8.3.0 downloaded"
