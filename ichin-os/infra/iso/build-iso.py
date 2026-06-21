#!/usr/bin/env python3
"""
ICHIN OS ISO Builder — Build a bootable ICHIN OS ISO from source.
Works on Linux (recommended) and Windows (limited).

Usage:
    python build-iso.py              # Build ISO natively
    python build-iso.py --docker     # Build ISO via Docker
    python build-iso.py --qemu       # Build + run in QEMU
"""

import os
import sys
import shutil
import subprocess
import argparse
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
ICHIN_ROOT = os.path.normpath(os.path.join(ROOT, ".."))
BUILD_DIR = os.path.join(ROOT, "build")
ISO_DIR = os.path.join(BUILD_DIR, "iso")
INITRAMFS_DIR = os.path.join(BUILD_DIR, "initramfs")
ISO_NAME = f"ichin-os-{datetime.now().strftime('%Y%m%d')}.iso"

SERVICES = {
    "orchestrator": {"port": 8011, "src": "orchestrator/main.py", "lang": "python"},
    "agents": {"port": 8012, "src": "agents/main.py", "lang": "python"},
    "memory-engine": {"port": 8013, "src": "memory-engine/main.py", "lang": "python"},
    "ui-system": {"port": 8014, "src": "ai-studio/ui_system.py", "lang": "python"},
    "ai-studio": {"port": 8016, "src": "ai-studio/main.py", "lang": "python"},
    "account": {"port": 8081, "src": "account/server/target/release/ichin-account-server", "lang": "rust"},
    "mail": {"port": 8080, "src": "mail/target/release/ichin-mail-server", "lang": "rust"},
    "search-engine": {"port": 3001, "src": "search-engine/server/target/release/ichin-search", "lang": "rust"},
}

EXTERNAL_REPOS = {
    "OpenJarvis": {
        "url": "https://github.com/open-jarvis/OpenJarvis.git",
        "branch": "main",
        "dir": "OpenJarvis",
        "install": "pip",
        "port": 8090,
    },
    "ruflo": {
        "url": "https://github.com/ruvnet/ruflo.git",
        "branch": "main",
        "dir": "ruflo",
        "install": "npm",
        "port": 8091,
    },
    "dexter": {
        "url": "https://github.com/virattt/dexter.git",
        "branch": "main",
        "dir": "dexter",
        "install": "bun",
        "port": 8092,
    },
    "mattpocock-skills": {
        "url": "https://github.com/mattpocock/skills.git",
        "branch": "main",
        "dir": "skills",
        "install": "none",
        "port": None,
    },
    "jcode": {
        "url": "https://github.com/1jehuang/jcode.git",
        "branch": "master",
        "dir": "jcode",
        "install": "cargo",
        "port": 8093,
    },
    "ClawRouter": {
        "url": "https://github.com/BlockRunAI/ClawRouter.git",
        "branch": "main",
        "dir": "ClawRouter",
        "install": "npm",
        "port": 8402,
    },
    "agentic-inbox": {
        "url": "https://github.com/cloudflare/agentic-inbox.git",
        "branch": "main",
        "dir": "agentic-inbox",
        "install": "npm",
        "port": 8094,
    },
    "obsidian-mind": {
        "url": "https://github.com/breferrari/obsidian-mind.git",
        "branch": "main",
        "dir": "obsidian-mind",
        "install": "npm",
        "port": None,
    },
    "obsidian-skills": {
        "url": "https://github.com/kepano/obsidian-skills.git",
        "branch": "main",
        "dir": "obsidian-skills",
        "install": "none",
        "port": None,
    },
    "obsidian-second-brain": {
        "url": "https://github.com/eugeniughelbur/obsidian-second-brain.git",
        "branch": "main",
        "dir": "obsidian-second-brain",
        "install": "bash",
        "port": None,
    },
}


def log(msg):
    print(f"  [{msg}]")


def run(cmd, cwd=None):
    print(f"  $ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=cwd or ROOT)


def build_initramfs():
    """Create the initramfs with ICHIN services."""
    log("Building initramfs...")
    if os.path.exists(INITRAMFS_DIR):
        shutil.rmtree(INITRAMFS_DIR)

    dirs = ["bin", "dev", "etc", "home", "lib", "lib64", "mnt", "proc",
            "root", "run", "sbin", "sys", "tmp", "usr/bin", "usr/lib", "var/log"]
    for d in dirs:
        os.makedirs(os.path.join(INITRAMFS_DIR, d), exist_ok=True)

    # Copy busybox
    busybox_path = os.path.join(BUILD_DIR, "busybox")
    if not os.path.exists(busybox_path):
        url = "https://busybox.net/downloads/binaries/1.36.1-x86_64-linux-musl/busybox"
        log(f"Downloading busybox from {url}")
        run(f"wget -q -O {busybox_path} {url}")
        os.chmod(busybox_path, 0o755)

    shutil.copy(busybox_path, os.path.join(INITRAMFS_DIR, "bin", "busybox"))
    for applet in ["sh", "init", "mount", "umount", "sleep", "cat", "echo", "ls",
                   "mkdir", "cp", "mv", "rm", "chmod", "chown", "dmesg", "grep",
                   "ps", "kill", "modprobe", "mdev", "ip", "ln"]:
        os.symlink("/bin/busybox", os.path.join(INITRAMFS_DIR, "bin", applet))

    # Copy ICHIN services
    services_dir = os.path.join(ICHIN_ROOT, "services")
    ichin_dir = os.path.join(INITRAMFS_DIR, "ichin")
    os.makedirs(os.path.join(ichin_dir, "services"), exist_ok=True)
    os.makedirs(os.path.join(ichin_dir, "bin"), exist_ok=True)
    os.makedirs(os.path.join(ichin_dir, "kernel"), exist_ok=True)

    for svc_name in os.listdir(services_dir):
        svc_path = os.path.join(services_dir, svc_name)
        if os.path.isdir(svc_path):
            dst = os.path.join(ichin_dir, "services", svc_name)
            log(f"  Copying service: {svc_name}")
            shutil.copytree(svc_path, dst, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "node_modules", "target", ".git"))

    # Copy init script
    init_src = os.path.join(ROOT, "init.sh")
    if os.path.exists(init_src):
        shutil.copy(init_src, os.path.join(INITRAMFS_DIR, "init"))
        os.chmod(os.path.join(INITRAMFS_DIR, "init"), 0o755)

    # Copy kernel module if exists
    kernel_bin = os.path.join(ICHIN_ROOT, "kernel",
                              "target/x86_64-unknown-none/release/ichin-kernel")
    if os.path.exists(kernel_bin):
        shutil.copy(kernel_bin, os.path.join(ichin_dir, "kernel", "ichin-kernel"))
        log("  Included bare-metal kernel module")

    # Clone and copy external AI repos (OpenJarvis, Ruflo)
    clone_external_repos()
    external_dst = os.path.join(ichin_dir, "external")
    os.makedirs(external_dst, exist_ok=True)
    for name, repo in EXTERNAL_REPOS.items():
        src = os.path.join(BUILD_DIR, "external", repo["dir"])
        dst = os.path.join(external_dst, repo["dir"])
        if os.path.exists(src):
            log(f"  Including external: {name}")
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "node_modules", ".git", ".github"))
        else:
            log(f"  SKIPPED {name} (not cloned)")

    # Package initramfs
    log("Packaging initramfs...")
    os.chdir(INITRAMFS_DIR)
    run("find . | cpio -H newc -o | gzip -9 > ../initramfs.cpio.gz")
    os.chdir(ROOT)
    log(f"Initramfs: {os.path.join(BUILD_DIR, 'initramfs.cpio.gz')}")


def clone_external_repos():
    """Clone OpenJarvis and Ruflo for inclusion in the ISO."""
    external_dir = os.path.join(BUILD_DIR, "external")
    os.makedirs(external_dir, exist_ok=True)
    for name, repo in EXTERNAL_REPOS.items():
        dest = os.path.join(external_dir, repo["dir"])
        if not os.path.exists(dest):
            log(f"Cloning {name} from {repo['url']}...")
            run(f"git clone --depth 1 -b {repo['branch']} {repo['url']} {dest}")
            # Remove .git to save space
            shutil.rmtree(os.path.join(dest, ".git"), ignore_errors=True)
        else:
            log(f"{name} already cloned at {dest}")


def download_kernel():
    """Download a pre-built Linux kernel."""
    kernel_dir = os.path.join(BUILD_DIR, "kernel")
    os.makedirs(kernel_dir, exist_ok=True)
    kernel_path = os.path.join(kernel_dir, "bzImage")

    if not os.path.exists(kernel_path):
        log("Downloading Linux kernel (pre-built)...")
        url = ("https://github.com/ichin-os/kernel-releases/releases/download/"
               "v6.6.54/bzImage")
        result = run(f"wget -q -O {kernel_path} {url}")
        if result.returncode != 0:
            # Fallback: build from source
            log("Download failed, building kernel from source...")
            run(f"""
                cd {kernel_dir}
                wget -q https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.54.tar.xz
                tar xf linux-6.6.54.tar.xz
                cd linux-6.6.54
                make defconfig
                make -j$(nproc) bzImage
                cp arch/x86_64/boot/bzImage ../bzImage
            """)
    return kernel_path


def assemble_iso():
    """Assemble the final bootable ISO."""
    log("Assembling ISO...")
    if os.path.exists(ISO_DIR):
        shutil.rmtree(ISO_DIR)

    os.makedirs(os.path.join(ISO_DIR, "boot", "grub"))
    os.makedirs(os.path.join(ISO_DIR, "ichin"))

    # Copy kernel
    kernel_path = os.path.join(BUILD_DIR, "kernel", "bzImage")
    if os.path.exists(kernel_path):
        shutil.copy(kernel_path, os.path.join(ISO_DIR, "boot", "vmlinuz"))

    # Copy initramfs
    initrd_path = os.path.join(BUILD_DIR, "initramfs.cpio.gz")
    if os.path.exists(initrd_path):
        shutil.copy(initrd_path, os.path.join(ISO_DIR, "boot", "initrd.img"))

    # Copy GRUB config
    grub_cfg = os.path.join(ROOT, "grub.cfg")
    if os.path.exists(grub_cfg):
        shutil.copy(grub_cfg, os.path.join(ISO_DIR, "boot", "grub", "grub.cfg"))

    # Copy all source code for live runtime
    for item in ["services", "apps", "packages", "ecosystem", "infra", "kernel",
                 "README.md", "AUDIT.md", ".env.example"]:
        src = os.path.join(ICHIN_ROOT, item)
        dst = os.path.join(ISO_DIR, "ichin", item)
        if os.path.exists(src):
            try:
                if os.path.isdir(src):
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                        "__pycache__", "*.pyc", "node_modules", "target",
                        ".git", ".github"))
                else:
                    shutil.copy(src, dst)
            except Exception as e:
                log(f"  Warning: could not copy {item}: {e}")

    # Build ISO
    iso_path = os.path.join(BUILD_DIR, ISO_NAME)
    log(f"Creating ISO: {iso_path}")

    # Try grub-mkrescue first, fall back to xorriso
    result = run(f"grub-mkrescue -o {iso_path} {ISO_DIR} 2>/dev/null")
    if result.returncode != 0:
        run(f"""
            xorriso -as mkisofs \\
                -b boot/grub/eltorito.img -no-emul-boot \\
                -boot-load-size 4 -boot-info-table \\
                --eltorito-boot boot/grub/eltorito.img \\
                --protective-msdos-label \\
                {ISO_DIR} -o {iso_path}
        """)

    # Copy ISO to root
    shutil.copy(iso_path, os.path.join(ROOT, ISO_NAME))
    size = os.path.getsize(iso_path)
    log(f"=== ISO created: {ISO_NAME} ({size / 1024 / 1024:.1f} MB) ===")
    return iso_path


def build_with_docker():
    """Build ISO using Docker."""
    log("Building with Docker...")
    result = run(f"docker build -t ichin-iso-builder -f {ROOT}/Dockerfile.iso {ICHIN_ROOT}")
    if result.returncode != 0:
        log("Docker build failed")
        return False

    result = run(f"docker run --rm -v {ROOT}:/output ichin-iso-builder "
                 f"bash -c 'cp /*.iso /output/ 2>/dev/null || true'")
    return result.returncode == 0


def run_qemu(iso_path):
    """Boot ISO in QEMU."""
    log("Launching QEMU...")
    run(f"""
        qemu-system-x86_64 -cdrom {iso_path} -m 2G -smp 2 \\
        -serial stdio \\
        -device virtio-net,netdev=net0 \\
        -netdev user,id=net0,hostfwd=tcp::8011-:8011,hostfwd=tcp::8012-:8012,\\
                hostfwd=tcp::8013-:8013,hostfwd=tcp::8014-:8014,\\
                hostfwd=tcp::8016-:8016,hostfwd=tcp::8081-:8081,\\
                hostfwd=tcp::8080-:8080,hostfwd=tcp::8090-:8090,\\
                hostfwd=tcp::8091-:8091,hostfwd=tcp::8092-:8092,\\
                hostfwd=tcp::8093-:8093,hostfwd=tcp::8402-:8402,\\
                hostfwd=tcp::8094-:8094
    """)


def main():
    parser = argparse.ArgumentParser(description="ICHIN OS ISO Builder")
    parser.add_argument("--docker", action="store_true", help="Build via Docker")
    parser.add_argument("--qemu", action="store_true", help="Build + run in QEMU")
    parser.add_argument("--skip-kernel", action="store_true", help="Skip kernel download")
    args = parser.parse_args()

    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(ISO_DIR, exist_ok=True)

    if args.docker:
        if not build_with_docker():
            log("Docker build failed, falling back to native build")
        else:
            return

    if not args.skip_kernel:
        download_kernel()
    build_initramfs()
    iso_path = assemble_iso()

    if args.qemu:
        run_qemu(iso_path)

    log("Done!")


if __name__ == "__main__":
    main()
