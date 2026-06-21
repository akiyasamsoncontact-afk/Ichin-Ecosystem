# Boot Process

## Boot Flow

```
Power On
  │
  ▼
UEFI Firmware
  │ Secure Boot verification
  ▼
Shim (signed first-stage)
  │ Verify GRUB signature
  ▼
GRUB 2 (signed second-stage)
  │ Load kernel + initramfs
  ▼
Linux Kernel
  │
  ├── Hardware init (CPU, memory, devices)
  ├── TPM measurement
  ├── initramfs → mount rootfs
  └── Switch root → /sbin/init
  │
  ▼
systemd (PID 1)
  │
  ├── Mount all filesystems
  ├── Start udev (device manager)
  ├── Load kernel modules
  ├── Start system.slice services
  │   ├── Network (NetworkManager/systemd-networkd)
  │   ├── Bluetooth
  │   ├── Audio (PipeWire)
  │   ├── GPU drivers
  │   ├── ichind (Ichin Daemon)
  │   └── Security core
  │
  ├── Start AI infrastructure
  │   ├── Redis (event bus)
  │   ├── PostgreSQL (persistence)
  │   └── Qdrant (vector store)
  │
  ├── Start Ichin services
  │   ├── Orchestrator
  │   ├── Agents
  │   ├── Memory Engine
  │   ├── AI Router
  │   ├── Voice Engine
  │   ├── Browser Engine
  │   ├── AI Metasearch
  │   ├── Mail AI
  │   ├── Knowledge Graph
  │   ├── AI Studio
  │   ├── App Runtime
  │   └── Security Core
  │
  ├── Start display manager (greeter)
  │   └── Desktop Environment (Ichin Shell)
  │       ├── Compositor (Wayland)
  │       ├── Desktop UI (React/TypeScript)
  │       ├── AI Orb service
  │       └── Workspace manager
  │
  └── User session starts
      ├── Restore workspace state
      ├── Start user agents
      └── Ready
```

## Optimization Strategies

1. **Parallel service startup** — All independent services start concurrently
2. **Lazy loading** — AI models loaded on demand, not at boot
3. **Pre-linked binaries** — Reduce dynamic linking overhead
4. **Read-ahead caching** — Predict and cache boot-critical files
5. **Minimal initramfs** — Only essential drivers
6. **Kernel same-page merging** — Deduplicate memory pages
7. **Fast userspace** — systemd with parallelized socket activation

## Boot Targets

| Target | Description | Time |
|--------|-------------|------|
| `basic.target` | Kernel + filesystems + udev | ~2s |
| `ichin-system.target` | All system services running | ~4s |
| `ichin-ai.target` | AI infrastructure ready | ~6s |
| `graphical.target` | Desktop environment visible | ~8s |
| `ichin-session.target` | Full user session ready | ~10s |

## Recovery Modes

- **Safe mode**: Boot with minimal services, no AI
- **Recovery shell**: Drop to root shell for repair
- **Snapshot rollback**: Boot from previous Btrfs snapshot
- **Factory reset**: Revert to pristine system state
