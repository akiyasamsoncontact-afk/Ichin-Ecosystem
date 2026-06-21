# ICHIN OS — Full ISO Build System
# Builds a bootable Linux-based ICHIN OS ISO with all ecosystem services
#
# Requirements: Linux, Docker, make, wget, sudo
# Build:        sudo make iso
# Run:          make run

SHELL := /bin/bash
BUILD_DIR := build
ISO_DIR := $(BUILD_DIR)/iso
INITRAMFS_DIR := $(BUILD_DIR)/initramfs
KERNEL_DIR := $(BUILD_DIR)/kernel
SERVICES_DIR := ../services
APPS_DIR := ../apps
KERNEL_SRC := ../kernel
ISO_NAME := ichin-os-$(shell date +%Y%m%d).iso

EXTERNAL_DIR := $(BUILD_DIR)/external
OPENJARVIS_URL := https://github.com/open-jarvis/OpenJarvis.git
RUFLO_URL := https://github.com/ruvnet/ruflo.git
DEXTER_URL := https://github.com/virattt/dexter.git
SKILLS_URL := https://github.com/mattpocock/skills.git
JCODE_URL := https://github.com/1jehuang/jcode.git
CLAWROUTER_URL := https://github.com/BlockRunAI/ClawRouter.git
AGENTIC_INBOX_URL := https://github.com/cloudflare/agentic-inbox.git
OBSIDIAN_MIND_URL := https://github.com/breferrari/obsidian-mind.git
OBSIDIAN_SKILLS_URL := https://github.com/kepano/obsidian-skills.git
OBSIDIAN_SECOND_BRAIN_URL := https://github.com/eugeniughelbur/obsidian-second-brain.git

.PHONY: all clean iso kernel initramfs services external openjarvis ruflo dexter skills jcode clawrouter agentic-inbox obsidian-mind obsidian-skills obsidian-second-brain run

all: iso

# === Step 1: Download Linux kernel ===
kernel:
	@mkdir -p $(KERNEL_DIR)
	@if [ ! -f $(KERNEL_DIR)/bzImage ]; then \
		echo "Downloading Linux kernel 6.6..."; \
		wget -q -O $(KERNEL_DIR)/linux.tar.xz \
			https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.54.tar.xz; \
		cd $(KERNEL_DIR) && tar xf linux.tar.xz && cd linux-6.6.54; \
		make defconfig && make -j$$(nproc) bzImage; \
		cp arch/x86_64/boot/bzImage $(KERNEL_DIR)/bzImage; \
	fi

# === Step 2: Build ICHIN Rust services (kernel, app-runtime, security-core) ===
ichin-kernel:
	@echo "Building ICHIN bare-metal kernel..."
	@cd $(KERNEL_SRC) && cargo build --target target.json -Z build-std=core,alloc --release 2>/dev/null || \
		echo "WARNING: Bare-metal kernel build failed (requires nightly+Rust). Using fallback."
	@mkdir -p $(BUILD_DIR)/modules
	@if [ -f $(KERNEL_SRC)/target/x86_64-unknown-none/release/ichin-kernel ]; then \
		cp $(KERNEL_SRC)/target/x86_64-unknown-none/release/ichin-kernel $(BUILD_DIR)/modules/ichin-kernel; \
	fi

# === Step 3: Build initramfs with ICHIN services ===
initramfs: kernel
	@echo "Building initramfs with ICHIN services..."
	@rm -rf $(INITRAMFS_DIR)
	@mkdir -p $(INITRAMFS_DIR)/{bin,dev,etc,home,lib,lib64,mnt,proc,root,run,sbin,sys,tmp,usr/bin,usr/lib,var/log}
	
	# Busybox for init system
	@if [ ! -f $(BUILD_DIR)/busybox ]; then \
		wget -q -O $(BUILD_DIR)/busybox https://busybox.net/downloads/binaries/1.36.1-x86_64-linux-musl/busybox; \
		chmod +x $(BUILD_DIR)/busybox; \
	fi
	@cp $(BUILD_DIR)/busybox $(INITRAMFS_DIR)/bin/busybox
	@for applet in sh init mount umount sleep cat echo ls mkdir cp mv rm chmod chown dmesg grep ps kill modprobe mdev; do \
		ln -sf /bin/busybox $(INITRAMFS_DIR)/bin/$$applet; \
	done

	# Python runtime for services
	@if [ ! -d $(BUILD_DIR)/python ]; then \
		mkdir -p $(BUILD_DIR)/python; \
		wget -q -O - https://github.com/niess/python-build-standalone/releases/download/20241002/cpython-3.12.7-x86_64-unknown-linux-gnu-install_only.tar.gz | \
			tar xz -C $(BUILD_DIR)/python; \
	fi
	@cp -r $(BUILD_DIR)/python/* $(INITRAMFS_DIR)/

	# ICHIN Python services
	@for svc in orchestrator agents memory-engine ai-studio; do \
		mkdir -p $(INITRAMFS_DIR)/ichin/services/$$svc; \
		cp -r $(SERVICES_DIR)/$$svc/* $(INITRAMFS_DIR)/ichin/services/$$svc/ 2>/dev/null || true; \
	done

	# ICHIN Rust services (copy binaries if built)
	@for svc in app-runtime security-core system-daemon; do \
		if [ -f $(SERVICES_DIR)/$$svc/target/release/ichin-$$svc ]; then \
			cp $(SERVICES_DIR)/$$svc/target/release/ichin-$$svc $(INITRAMFS_DIR)/ichin/bin/; \
		fi; \
	done

	# ICHIN kernel module
	@mkdir -p $(INITRAMFS_DIR)/ichin/kernel
	@if [ -f $(BUILD_DIR)/modules/ichin-kernel ]; then \
		cp $(BUILD_DIR)/modules/ichin-kernel $(INITRAMFS_DIR)/ichin/kernel/; \
	fi

	# Ecosystem (app store, developer portal)
	@mkdir -p $(INITRAMFS_DIR)/ichin/ecosystem
	@cp -r ../ecosystem/ichin-app-store $(INITRAMFS_DIR)/ichin/ecosystem/ 2>/dev/null || true
	@cp -r ../ecosystem/developer-portal $(INITRAMFS_DIR)/ichin/ecosystem/ 2>/dev/null || true

	# External AI repos
	@mkdir -p $(INITRAMFS_DIR)/ichin/external
	@for repo in OpenJarvis ruflo dexter skills jcode ClawRouter agentic-inbox obsidian-mind obsidian-skills obsidian-second-brain; do \
		if [ -d $(EXTERNAL_DIR)/$$repo ]; then \
			cp -r $(EXTERNAL_DIR)/$$repo $(INITRAMFS_DIR)/ichin/external/; \
			echo "  Included $$repo"; \
		fi; \
	done

	# Init script
	@cp init.sh $(INITRAMFS_DIR)/init
	@chmod +x $(INITRAMFS_DIR)/init

	# Create initramfs archive
	@cd $(INITRAMFS_DIR) && find . | cpio -H newc -o | gzip -9 > ../initramfs.cpio.gz
	@echo "Initramfs: $(BUILD_DIR)/initramfs.cpio.gz"

# === Step 4: Build Python services as pip-installable ===
services:
	@echo "Pre-building Python service dependencies..."
	@for svc in orchestrator agents memory-engine ai-studio; do \
		if [ -f $(SERVICES_DIR)/$$svc/requirements.txt ]; then \
			pip install -r $(SERVICES_DIR)/$$svc/requirements.txt --target=$(BUILD_DIR)/pylibs 2>/dev/null || true; \
		fi; \
	done

# === Step 4b: Clone external AI repos ===
external: openjarvis ruflo dexter skills jcode clawrouter agentic-inbox obsidian-mind obsidian-skills obsidian-second-brain

openjarvis:
	@echo "Cloning OpenJarvis (Stanford local-first personal AI)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/OpenJarvis ]; then \
		git clone --depth 1 $(OPENJARVIS_URL) $(EXTERNAL_DIR)/OpenJarvis && \
		rm -rf $(EXTERNAL_DIR)/OpenJarvis/.git; \
	else \
		echo "  OpenJarvis already cloned"; \
	fi

ruflo:
	@echo "Cloning Ruflo (multi-agent meta-harness)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/ruflo ]; then \
		git clone --depth 1 $(RUFLO_URL) $(EXTERNAL_DIR)/ruflo && \
		rm -rf $(EXTERNAL_DIR)/ruflo/.git; \
	else \
		echo "  Ruflo already cloned"; \
	fi

dexter:
	@echo "Cloning Dexter (autonomous financial research agent)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/dexter ]; then \
		git clone --depth 1 $(DEXTER_URL) $(EXTERNAL_DIR)/dexter && \
		rm -rf $(EXTERNAL_DIR)/dexter/.git; \
	else \
		echo "  Dexter already cloned"; \
	fi

skills:
	@echo "Cloning mattpocock/skills (engineering skills for coding agents)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/skills ]; then \
		git clone --depth 1 $(SKILLS_URL) $(EXTERNAL_DIR)/skills && \
		rm -rf $(EXTERNAL_DIR)/skills/.git; \
	else \
		echo "  skills already cloned"; \
	fi

jcode:
	@echo "Cloning jcode (coding agent harness)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/jcode ]; then \
		git clone --depth 1 $(JCODE_URL) $(EXTERNAL_DIR)/jcode && \
		rm -rf $(EXTERNAL_DIR)/jcode/.git; \
	else \
		echo "  jcode already cloned"; \
	fi

clawrouter:
	@echo "Cloning ClawRouter (agent-native LLM router)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/ClawRouter ]; then \
		git clone --depth 1 $(CLAWROUTER_URL) $(EXTERNAL_DIR)/ClawRouter && \
		rm -rf $(EXTERNAL_DIR)/ClawRouter/.git; \
	else \
		echo "  ClawRouter already cloned"; \
	fi

agentic-inbox:
	@echo "Cloning agentic-inbox (Cloudflare AI email agent)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/agentic-inbox ]; then \
		git clone --depth 1 $(AGENTIC_INBOX_URL) $(EXTERNAL_DIR)/agentic-inbox && \
		rm -rf $(EXTERNAL_DIR)/agentic-inbox/.git; \
	else \
		echo "  agentic-inbox already cloned"; \
	fi

obsidian-mind:
	@echo "Cloning obsidian-mind (persistent memory vault for AI agents)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/obsidian-mind ]; then \
		git clone --depth 1 $(OBSIDIAN_MIND_URL) $(EXTERNAL_DIR)/obsidian-mind && \
		rm -rf $(EXTERNAL_DIR)/obsidian-mind/.git; \
	else \
		echo "  obsidian-mind already cloned"; \
	fi

obsidian-skills:
	@echo "Cloning obsidian-skills (agent skills for Obsidian)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/obsidian-skills ]; then \
		git clone --depth 1 $(OBSIDIAN_SKILLS_URL) $(EXTERNAL_DIR)/obsidian-skills && \
		rm -rf $(EXTERNAL_DIR)/obsidian-skills/.git; \
	else \
		echo "  obsidian-skills already cloned"; \
	fi

obsidian-second-brain:
	@echo "Cloning obsidian-second-brain (cross-CLI second brain)..."
	@mkdir -p $(EXTERNAL_DIR)
	@if [ ! -d $(EXTERNAL_DIR)/obsidian-second-brain ]; then \
		git clone --depth 1 $(OBSIDIAN_SECOND_BRAIN_URL) $(EXTERNAL_DIR)/obsidian-second-brain && \
		rm -rf $(EXTERNAL_DIR)/obsidian-second-brain/.git; \
	else \
		echo "  obsidian-second-brain already cloned"; \
	fi

# === Step 5: Assemble ISO ===
iso: clean initramfs services external
	@echo "Assembling ISO..."
	@mkdir -p $(ISO_DIR)/boot/grub
	@mkdir -p $(ISO_DIR)/ichin

	# Kernel
	@cp $(KERNEL_DIR)/bzImage $(ISO_DIR)/boot/vmlinuz

	# Initramfs
	@cp $(BUILD_DIR)/initramfs.cpio.gz $(ISO_DIR)/boot/initrd.img

	# GRUB config
	@cp grub.cfg $(ISO_DIR)/boot/grub/

	# ICHIN service code (for runtime)
	@cp -r $(SERVICES_DIR) $(ISO_DIR)/ichin/services 2>/dev/null || true
	@cp -r $(APPS_DIR) $(ISO_DIR)/ichin/apps 2>/dev/null || true
	@cp -r ../packages $(ISO_DIR)/ichin/packages 2>/dev/null || true
	@cp -r ../ecosystem $(ISO_DIR)/ichin/ecosystem 2>/dev/null || true
	@cp -r ../infra $(ISO_DIR)/ichin/infra 2>/dev/null || true
	@cp ../README.md $(ISO_DIR)/ichin/ 2>/dev/null || true

	# Build ISO with grub-mkrescue
	@grub-mkrescue -o $(ISO_NAME) $(ISO_DIR) 2>/dev/null || \
		xorriso -as mkisofs -b boot/grub/eltorito.img -no-emul-boot \
			-boot-load-size 4 -boot-info-table --eltorito-boot boot/grub/eltorito.img \
			--protective-msdos-label $(ISO_DIR) -o $(ISO_NAME)

	@echo "=== ISO created: $(ISO_NAME) ==="
	@echo "Size: $$(du -h $(ISO_NAME) | cut -f1)"

# === Run in QEMU ===
run: iso
	@qemu-system-x86_64 -cdrom $(ISO_NAME) -m 2G -smp 2 \
		-serial stdio -device virtio-net,netdev=net0 \
		-netdev user,id=net0,hostfwd=tcp::8011-:8011,hostfwd=tcp::8012-:8012,\
			hostfwd=tcp::8013-:8013,hostfwd=tcp::8081-:8081,\
			hostfwd=tcp::8080-:8080,hostfwd=tcp::8090-:8090,\
			hostfwd=tcp::8091-:8091,hostfwd=tcp::8092-:8092,\
			hostfwd=tcp::8093-:8093,hostfwd=tcp::8402-:8402,\
			hostfwd=tcp::8094-:8094

# === Clean ===
clean:
	@rm -rf $(BUILD_DIR) $(ISO_NAME) *.iso
	@echo "Cleaned."
