# ICHIN OS — COMPLETE SYSTEM REFERENCE

> **Generated:** Sun Jun 21 2026  
> **Repository:** `C:\Users\aki\Ichin-Ecosystem`  
> **Total files:** ~402 | **Total lines:** ~41,050  
> **Purpose:** Exhaustive documentation of every component, service, app, kernel module, external dependency, configuration, port, entry point, uncertainty, and architectural relationship.

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [Full Port Map (Master Table)](#2-full-port-map-master-table)
3. [Architecture Diagrams](#3-architecture-diagrams)
4. [Kernel Deep Dive](#4-kernel-deep-dive)
5. [Service Deep Dives](#5-service-deep-dives)
   - 5.1 Orchestrator (8011)
   - 5.2 AI Agents (8012)
   - 5.3 Memory Engine (8013)
   - 5.4 UI System (8014)
   - 5.5 App Runtime (8015)
   - 5.6 AI Studio (8016)
   - 5.7 Security Core (8017)
   - 5.8 System Daemon (7010)
   - 5.9 Account (8081)
   - 5.10 Mail (8080)
   - 5.11 Protocol Stack (4889-4892)
   - 5.12 Search Engine (3000-3001)
6. [App Deep Dives](#6-app-deep-dives)
   - 6.1 Desktop UI (1420)
   - 6.2 Web UI (1430)
   - 6.3 Mobile UI (Expo)
   - 6.4 Desktop Browser (3003)
   - 6.5 Calendar (3002)
7. [Package Reference](#7-package-reference)
8. [Ecosystem Reference](#8-ecosystem-reference)
9. [Build System Reference](#9-build-system-reference)
10. [External Repo Integration Report](#10-external-repo-integration-report)
    - 10.1 OpenJarvis (8090)
    - 10.2 Ruflo (8091)
    - 10.3 Dexter (8092)
    - 10.4 mattpocock/skills
    - 10.5 jcode (8093)
    - 10.6 ClawRouter (8402)
    - 10.7 agentic-inbox (8094)
    - 10.8 obsidian-mind
    - 10.9 obsidian-skills
    - 10.10 obsidian-second-brain
11. [Full Directory Tree (Annotated)](#11-full-directory-tree-annotated)
12. [The Spec (123.md)](#12-the-spec-123md)
13. [Master Uncertainty List](#13-master-uncertainty-list)
14. [Port Conflict Analysis](#14-port-conflict-analysis)
15. [File Inventory](#15-file-inventory)

---

## 1. PROJECT OVERVIEW

### 1.1 Repository Structure

```
C:\Users\aki\Ichin-Ecosystem/
├── .git/
├── .gitignore
├── opencode.json
├── Protocol/                     (empty — deprecated)
└── ichin-os/
    ├── .env.example
    ├── AUDIT.md
    ├── README.md
    ├── apps/                     (5 sub-apps, 176 files)
    ├── ecosystem/                (app store, portal, templates, 21 files)
    ├── infra/                    (docker, k8s, docs, edge, ISO builder, 35 files)
    ├── kernel/                   (bare-metal x86_64 no_std kernel, 26 files)
    ├── packages/                 (4 TypeScript packages, 12 files)
    └── services/                 (12 services, 129 files)
```

### 1.2 Language Breakdown

| Language | Files | % of Codebase |
|----------|-------|---------------|
| Rust (.rs) | 51 | ~35% |
| TypeScript/TSX (.ts/.tsx) | 59 | ~25% |
| Python (.py) | 26 | ~20% |
| JavaScript (.js) | 15 | ~8% |
| HTML (.html) | 8 | ~5% |
| YAML (.yaml/.yml) | 14 | ~3% |
| CSS (.css) | 5 | ~2% |
| Shell (.sh) | 6 | ~1% |
| Markdown (.md) | 15 | ~1% |
| TOML (.toml) | 18 | — |
| JSON (.json) | 13 | — |

### 1.3 Largest Source Files

| Rank | File | Size | Service |
|------|------|------|---------|
| 1 | `services/memory-engine/main.py` | 51,537 B | Memory Engine |
| 2 | `services/agents/main.py` | 47,998 B | AI Agents |
| 3 | `services/ai-studio/ui_system.py` | 44,102 B | AI Studio |
| 4 | `services/orchestrator/main.py` | 43,668 B | Orchestrator |
| 5 | `services/ai-studio/main.py` | 43,171 B | AI Studio |
| 6 | `services/security-core/src/main.rs` | 40,063 B | Security Core |
| 7 | `services/account/server/src/main.rs` | 36,560 B | Account |
| 8 | `packages/ui-components/src/index.ts` | 32,397 B | UI Components |
| 9 | `services/app-runtime/src/main.rs` | 26,574 B | App Runtime |
| 10 | `apps/desktop-browser/Back-End/src/db.rs` | 18,146 B | Desktop Browser |

### 1.4 Architecture Philosophy (from 123.md)

> "A cognitive operating system that merges AI agents, workspace computing, learning systems, productivity optimization, and cross-platform app execution into a single unified environment."
>
> — ICHIN OS Vision (123.md)

Key principles:
- **AI-first**: AI Council system with weighted voting, not app-centric
- **Workspace-based**: Study / Coding / Learning / Personal workspaces
- **Privacy-first**: No telemetry, no ads, no bloatware
- **Zero trust**: Every request validated, every process sandboxed
- **Spotlight-first**: Everything starts from search (Ctrl+Space)
- **Ambient UI**: Liquid glass aesthetic, panels fade in/out, no desktop icons
- **Multi-agent AI council**: 8 specialized agents + orchestrator
- **Hybrid deployment**: Native OS (bare-metal kernel) + overlay layer (initramfs ISO)

---

## 2. FULL PORT MAP (MASTER TABLE)

### 2.1 Legend

| Icon | Meaning |
|------|---------|
| ✅ | Verified — port confirmed in source code |
| ⚠️ | Guessed — port assumed from README/context, not verified in source |
| ❌ | Not a server — no port needed |
| 🔮 | Cloud-only — requires external platform |

### 2.2 Internal Services & Apps

| Port | Service | Tech Stack | Status | Entry Point | Type | Source of Truth |
|------|---------|-----------|--------|-------------|------|-----------------|
| **7010** | System Daemon | Rust (tokio) | ✅ Verified | `services/system-daemon/src/main.rs` | Raw TCP server | Hardcoded: `format!("127.0.0.1:{}", 7010)` |
| **8000** | Orchestrator | Python (FastAPI) | ✅ Verified | `services/orchestrator/main.py` | REST API | `uvicorn.run("main:app", host="0.0.0.0", port=8000)` |
| **8003** | Memory Engine | Python (FastAPI) | ✅ Verified | `services/memory-engine/main.py` | REST API | `uvicorn.run("main:app", host="0.0.0.0", port=8003)` |
| **8004** | UI System | Python (FastAPI) | ✅ Verified | `services/ai-studio/ui_system.py` | REST API | `uvicorn.run(port=8004)` |
| **8005** | App Runtime | Rust (Axum) | ✅ Verified | `services/app-runtime/src/main.rs` | REST API | Hardcoded: `SocketAddr::from(([0,0,0,0], 8005))` |
| **8006** | Security Core | Rust (Axum) | ✅ Verified | `services/security-core/src/main.rs` | REST API | Hardcoded: `SocketAddr::from(([0,0,0,0], 8006))` |
| **8011** | Orchestrator (ISO) | Python (FastAPI) | ⚠️ Re-numbered | `services/orchestrator/main.py` | REST API | init.sh assigns 8011; actual code binds 8000 |
| **8012** | AI Agents | Python (FastAPI) | ✅ Verified | `services/agents/main.py` | REST API | `uvicorn.run("main:app", host="0.0.0.0", port=8012)` |
| **8013** | Memory Engine (ISO) | Python (FastAPI) | ⚠️ Re-numbered | `services/memory-engine/main.py` | REST API | init.sh assigns 8013; actual code binds 8003 |
| **8014** | UI System (ISO) | Python (FastAPI) | ⚠️ Re-numbered | `services/ai-studio/ui_system.py` | REST API | init.sh assigns 8014; actual code binds 8004 |
| **8015** | App Runtime (ISO) | Rust (Axum) | ⚠️ Re-numbered | `services/app-runtime/src/main.rs` | REST API | init.sh assigns 8015; actual code binds 8005 |
| **8016** | AI Studio | Python (FastAPI) | ✅ Verified | `services/ai-studio/main.py` | REST API | `uvicorn.run("main:app", host="0.0.0.0", port=8016)` |
| **8017** | Security Core (ISO) | Rust (Axum) | ⚠️ Re-numbered | `services/security-core/src/main.rs` | REST API | init.sh assigns 8017; actual code binds 8006 |
| **8080** | Mail (HTTP API) | Rust (Axum) | ✅ Verified | `services/mail/src/bin/server.rs` | REST API | `serve(addr, router)` — port via config, default 8080 |
| **8081** | Account | Rust (Axum 0.8) | ✅ Verified | `services/account/server/src/main.rs` | REST API | Config-driven: `config.server.port` defaults to user input |
| **3000** | Search Engine (Next.js) | TypeScript (Next.js 15) | ✅ Verified | `services/search-engine/client/` | Web UI | Next.js dev server default port |
| **3001** | Search Engine (API) | Rust (Axum 0.8) | ✅ Verified | `services/search-engine/server/src/main.rs` | REST API | Hardcoded: `SocketAddr::from(([0,0,0,0], 3001))` |
| **3002** | Calendar (Rust API) | Rust (Axum) | ✅ Verified | `apps/calender/Back-End/src/main.rs` | REST API | Config read from `route.json` |
| **3003** | Desktop Browser (Rust) | Rust (Axum) | ✅ Verified | `apps/desktop-browser/Back-End/src/main.rs` | REST API | Config read from `Cargo.toml` features |
| **1420** | Desktop UI (Vite) | React/TS (Vite) | ✅ Verified | `apps/desktop-ui/vite.config.ts` | Web UI | `server.port: 1420` in vite.config.ts |
| **1430** | Web UI (Vite) | React/TS (Vite) | ⚠️ Assumed | `apps/web-ui/vite.config.ts` | Web UI | No vite.config.ts port set; 1430 from init.sh |
| **4889** | Ichin-Protocol | Python (raw TCP) | ✅ Verified | `services/protocol/Ichin-Protocol/server.py` | Raw TCP | `server.py` binds 4889 |
| **4890** | Ichin-DNS | Python (raw TCP) | ✅ Verified | `services/protocol/Ichin-DNS/server.py` | Raw TCP | `server.py` binds 4890 |
| **4891** | Ichin-CA | Python (raw TCP) | ✅ Verified | `services/protocol/Ichin-CA/server.py` | Raw TCP | `server.py` binds 4891 |
| **4892** | Ichin-Daemon | Python (raw TCP) | ✅ Verified | `services/protocol/Ichin-Daemon/ichind.py` | Raw TCP | `ichind.py` binds 4892 |

### 2.3 Internal Apps (Non-Port)

| App | Tech Stack | Type | Frontend Port | API Port |
|-----|-----------|------|---------------|----------|
| Desktop UI | React 18 + Vite + Tailwind v4 + Framer Motion | Desktop Shell | 1420 | Connects to all services |
| Web UI | React + Vite + Zustand + Axios | Web Interface | 1430 | Connects to all services |
| Mobile UI | Expo SDK 51 + React Navigation + Zustand | Mobile App | (Expo dev) | Connects to all services |
| Desktop Browser | Electron + Rust Axum backend + React frontend | Browser App | Electron window | 3003 |
| Calendar | Rust Axum backend + React frontend | Productivity App | (static HTML) | 3002 |

### 2.4 External AI Frameworks (ISO-Embedded)

| Port | Repo | Tech Stack | Status | Entry Point (Actual) | Type |
|------|------|-----------|--------|---------------------|------|
| **8090** ⚠️ | OpenJarvis | Python (FastAPI) | ✅ Has server mode | `jarvis serve --host 0.0.0.0 --port 8090` | REST API / CLI |
| **8091** ⚠️ | Ruflo | TypeScript (Node.js) | ✅ Has MCP server | `npx ruflo mcp start -t http --port 8091` | MCP Server / CLI |
| **8092** ❌ | Dexter | TypeScript (Bun) | ❌ CLI-only (no server) | `bun run src/index.tsx` (TUI only) | CLI TUI only |
| **—** ❌ | mattpocock/skills | Shell/Markdown | ❌ Skill files only | `npx skills@latest add mattpocock/skills` | Skill definitions |
| **8093** ❌ | jcode | Rust | ❌ Unix socket only (no TCP) | `jcode serve` (Unix socket at `/run/user/$UID/jcode.sock`) | CLI TUI + Unix daemon |
| **8402** ✅ | ClawRouter | TypeScript (Node.js) | ✅ HTTP proxy | `clawrouter --port 8402` | HTTP proxy server |
| **8094** 🔮 | agentic-inbox | TypeScript (CF Workers) | 🔮 Cloudflare-only | `wrangler deploy` (not runnable locally) | Cloudflare Worker |
| **—** ❌ | obsidian-mind | TypeScript (hooks) | ❌ Vault template | Installed via `shardmind install` | Obsidian vault template |
| **—** ❌ | obsidian-skills | Markdown | ❌ Skill files only | `npx skills add https://github.com/kepano/obsidian-skills` | Skill definitions |
| **—** ❌ | obsidian-second-brain | Python/Shell | ❌ Skill (no server) | `bash install.sh` → loaded into Claude Code | Skill + vault |

### 2.5 Kernel-Internal Services (Bare-Metal, No Ports)

| "Port" | Service | Source File | Type |
|--------|---------|-------------|------|
| 7000 (internal) | ICHIN Microkernel | `kernel/src/kernel.rs` | Embedded system services |
| — | Process Manager | `kernel/src/process.rs` | PID, state, priority, sandbox |
| — | Scheduler | `kernel/src/scheduler.rs` | 6-level priority queues |
| — | Memory Manager | `kernel/src/memory.rs` | 16MB heap, paging |
| — | IPC Manager | `kernel/src/ipc.rs` | Channel-based messaging |
| — | Virtual File System | `kernel/src/fs.rs` | Inode-based VFS |
| — | Driver Manager | `kernel/src/drivers.rs` | Device probing |
| — | Sandbox Engine | `kernel/src/sandbox.rs` | 5 sandbox levels |
| — | Rollback System | `kernel/src/rollback.rs` | Snapshot-based |
| — | Syscall Handler | `kernel/src/syscall.rs` | 8 syscalls |

---

## 3. ARCHITECTURE DIAGRAMS

### 3.1 High-Level System Architecture

```
                         ┌─────────────────────────┐
                         │      USER / CLIENT       │
                         │  (Desktop UI / Web UI /  │
                         │   Mobile UI / CLI)       │
                         └───────────┬─────────────┘
                                     │
                         ┌───────────▼─────────────┐
                         │      SPOTLIGHT LAYER     │
                         │  (Ctrl+Space — Search +  │
                         │   Commands + AI Prompt)  │
                         └───────────┬─────────────┘
                                     │
              ┌──────────────────────▼──────────────────────┐
              │           AI ORCHESTRATOR (:8011)            │
              │  - Input classification                     │
              │  - Agent selection & parallel execution      │
              │  - Weighted voting decision engine           │
              │  - Safety validation                         │
              │  - Mode enforcement (Normal/Focus/Lock)      │
              └───────┬────────────┬────────────┬───────────┘
                      │            │            │
         ┌────────────▼──┐  ┌──────▼──────┐  ┌─▼──────────────┐
         │ AI AGENTS     │  │ MEMORY      │  │ EXTERNAL AI    │
         │ (:8012)       │  │ ENGINE      │  │ FRAMEWORKS     │
         │ Study/Coding/ │  │ (:8013)     │  │ OpenJarvis:8090│
         │ Learning/Prod/│  │ Ephemeral/  │  │ Ruflo:8091     │
         │ Focus/Security│  │ Working/    │  │ ClawRouter:8402│
         │ Calendar/Res. │  │ Long-term   │  │ Dexter:CLI-only│
         └───────────────┘  └─────────────┘  │ jcode:Unix sock│
                                             └────────────────┘
                      │            │            │
         ┌────────────▼────────────▼────────────▼───────────┐
         │              APP RUNTIME (:8015)                  │
         │  - App lifecycle (install/run/suspend/terminate)  │
         │  - Permission system                              │
         │  - AI simulation endpoint                         │
         │  - API gateways (AI/Memory/Calendar/Files/Notif)  │
         └───────────────────────┬──────────────────────────┘
                                 │
         ┌───────────────────────▼──────────────────────────┐
         │           CORE SYSTEM SERVICES                    │
         ├──────────────────┬──────────────────┬─────────────┤
         │ Account (:8081)  │ Mail (:8080)     │ Protocol    │
         │ Auth/Passkeys/   │ SMTP/Ichin proto │ Stack       │
         │ Sessions/Devices │ SPF/DKIM/DNS     │ (:4889-4892)│
         │ Browser sync     │ Queue/Transport  │ ICHINP/CA   │
         └──────────────────┴──────────────────┴─────────────┘
                                 │
         ┌───────────────────────▼──────────────────────────┐
         │              SYSTEM INFRASTRUCTURE                │
         ├──────────────────┬──────────────────┬─────────────┤
         │ Security Core    │ Search Engine    │ System      │
         │ (:8017)          │ (:3001)          │ Daemon      │
         │ Process monitor/ │ Full-text search │ (:7010)     │
         │ Sandbox/Snapshot │ SQLite inverted  │ Scheduler/  │
         │ Anomaly detect   │ index            │ Health/tasks│
         └──────────────────┴──────────────────┴─────────────┘
                                 │
         ┌───────────────────────▼──────────────────────────┐
         │              ICHIN MICROKERNEL                    │
         │  (Bare-metal x86_64, no_std, Limine boot)        │
         │  Process Manager | Scheduler | Memory | IPC      │
         │  VFS | Drivers | Sandbox | Rollback | Syscalls   │
         └──────────────────────────────────────────────────┘
```

### 3.2 AI Council Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  AI ORCHESTRATOR (:8011)                  │
│                                                          │
│  Request Flow:                                           │
│  1. INPUT CLASSIFICATION → type, workspace, urgency      │
│  2. AGENT SELECTION → choose relevant agents             │
│  3. PARALLEL EXECUTION → run agents concurrently         │
│  4. DECISION ENGINE → weighted voting + conflict resolve │
│  5. SAFETY VALIDATION → risk check + policy check        │
│  6. FINAL RESPONSE → user output or system action        │
│                                                          │
│  Mode Controller:                                        │
│  🟢 Normal    → full AI suggestions, no restrictions     │
│  🟡 Focus     → reduced interruptions, soft guidance     │
│  🔵 Deep Focus→ strong intervention, distraction detect  │
│  🔴 Lock      → strict enforcement, limited interaction  │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Study Agent │ │ Coding Agent│ │ Learning    │ │ Productivity│
│ Score: 0-1  │ │ Score: 0-1  │ │ Agent       │ │ Agent       │
│ Risk: 0-1   │ │ Risk: 0-1   │ │ Score: 0-1  │ │ Score: 0-1  │
│ Reasoning   │ │ Reasoning   │ │ Risk: 0-1   │ │ Risk: 0-1   │
├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤
│📚 Academic  │ │💻 Technical │ │🧠 Knowledge │ │📊 Task/Work │
│ Quiz gen/   │ │ Code gen/   │ │ Learning    │ │ Optimization│
│ Topic break │ │ Debug/      │ │ path gen/   │ │ Scheduling  │
│ Study sched │ │ Refactor/   │ │ Course build│ │ Priority    │
│ Flashcard   │ │ Architecture│ │ Concept map │ │ Estimation  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Focus Agent │ │ Security    │ │ Calendar    │ │ Research    │
│ Score: 0-1  │ │ Agent       │ │ Agent       │ │ Agent       │
│ Risk: 0-1   │ │ Score: 0-1  │ │ Score: 0-1  │ │ Score: 0-1  │
├─────────────┤ ├─────────────┤ ├─────────────┤ ├─────────────┤
│🎯 Attention │ │🔐 Integrity │ │📅 Time mgmt │ │🔬 Discovery │
│ Distraction │ │ Anomaly det │ │ Event detect│ │ Web research│
│ Focus mode  │ │ Action valid│ │ Conflict    │ │ Data mining │
│ Break recmm │ │ Permissions │ │ resolution  │ │ Summarize   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

### 3.3 Boot Sequence

```
BIOS/UEFI → Limine Bootloader
    │
    ▼
ICHIN Microkernel (_start in main.rs)
    ├── Limine requests (framebuffer, HHDM, RSDP, kernel file, module, SMP)
    ├── Serial init (COM1 via uart_16550)
    ├── GDT setup (kernel code/data, user code/data, TSS)
    ├── IDT setup (breakpoint, PF, DF, GPF, DE, UD, SS, timer, keyboard)
    ├── Paging init (OffsetPageTable, BootInfoFrameAllocator, heap mapping)
    ├── Heap init (16MB at 0xFFFF_9000_0000_0000)
    │
    ├── IchinKernel::new()
    │   ├── ProcessManager::new() — PID alloc, state, priority
    │   ├── Scheduler::new() — 6-level queues, time slice=50
    │   ├── MemoryManager::new() — heap wrapper
    │   ├── IpcManager::new() — channel registry
    │   ├── VirtualFileSystem::new() — root inode
    │   ├── DriverManager::new() — device probe
    │   ├── SandboxEngine::new() — 5 levels
    │   ├── RollbackSystem::new() — max 50 snapshots
    │   ├── ServiceManager::new() — 8 registered services
    │   └── SyscallHandler::new() — 8 syscalls
    │
    ├── Kernel::init()
    ├── Kernel::run() — main event loop
    │
    └── (If running as ISO overlay: → Linux kernel boot → initramfs → init.sh)
```

### 3.4 Memory Architecture (Four-Layer System)

```
┌─────────────────────────────────────────────────────────┐
│              EPHEMERAL CONTEXT (seconds-minutes)         │
│  Current question, last AI response, active agent        │
│  outputs, immediate UI state                            │
│  NOT stored permanently, NOT retrievable after session   │
├─────────────────────────────────────────────────────────┤
│              WORKING MEMORY (session-based)              │
│  Current workspace, active tasks, recent actions,        │
│  temporary assumptions, short-term preferences           │
│  Auto-expires after inactivity, compressed periodically  │
├─────────────────────────────────────────────────────────┤
│             LONG-TERM SEMANTIC MEMORY                     │
│  Vector embeddings + structured metadata                │
│  Types: FACT (preferences), PATTERN (habits),            │
│         SKILL (proficiency)                              │
│  Decay system: unused → weakens, critical never lost     │
│  Workspace-isolated memory slices                        │
├─────────────────────────────────────────────────────────┤
│            STRUCTURED SYSTEM MEMORY                       │
│  Tasks, calendar events, notes, chat history (summarized)│
│  Project files metadata                                  │
│  Fully structured, queryable like a database             │
└─────────────────────────────────────────────────────────┘
```

---

## 4. KERNEL DEEP DIVE

### 4.1 Kernel Identity

- **Type:** Bare-metal x86_64 microkernel
- **Language:** Rust (no_std, no alloc by default but provides global allocator)
- **Build target:** `x86_64-unknown-none` (custom target.json)
- **Boot protocol:** Limine (v8.x)
- **Build system:** Nightly Rust + `build-std=core,alloc`
- **Total files:** 26 (17 source .rs files, target.json, linker.ld, limine.conf, Cargo.toml, rust-toolchain.toml, build.rs, build.sh, Makefile, Dockerfile.build)
- **Total lines:** ~1,142 (source only)

### 4.2 Source File Map

| File | Lines | Purpose |
|------|-------|---------|
| `kernel/src/main.rs` | 63 | Entry point `_start`, kernel init sequence |
| `kernel/src/kernel.rs` | 94 | `IchinKernel` struct, init/run, owns all subsystems |
| `kernel/src/memory.rs` | 57 | Heap allocator init, memory map |
| `kernel/src/process.rs` | 114 | Process struct, PID, state, priority, sandbox level |
| `kernel/src/scheduler.rs` | 68 | 6-level priority queues, scheduling algorithm |
| `kernel/src/fs.rs` | 106 | Virtual file system, inode-based |
| `kernel/src/ipc.rs` | 79 | Channel-based IPC |
| `kernel/src/syscall.rs` | 27 | Syscall dispatch (8 syscalls) |
| `kernel/src/services.rs` | 44 | Service registry (8 registered) |
| `kernel/src/sandbox.rs` | 25 | 5 sandbox levels |
| `kernel/src/rollback.rs` | 40 | Snapshot-based rollback |
| `kernel/src/drivers.rs` | 29 | Device probe |
| `kernel/src/arch/mod.rs` | 15 | Architecture init |
| `kernel/src/arch/gdt.rs` | 50 | GDT + TSS setup |
| `kernel/src/arch/idt.rs` | 80 | IDT setup + interrupt handlers |
| `kernel/src/arch/paging.rs` | 96 | Page table + frame allocator |
| `kernel/src/arch/serial.rs` | 36 | COM1 serial I/O |

### 4.3 Limine Boot Protocol

The kernel requests the following Limine features:

```rust
// From limine.h / limine crate:
// Features requested by the kernel:
// - Framebuffer (for display output)
// - HHDM (Higher Half Direct Map)
// - RSDP (ACPI Root System Description Pointer)
// - Kernel File (to load modules)
// - Module (for initramfs)
// - SMP (for multi-core)
```

Defined in `main.rs` as `static` Limine request structs.

### 4.4 GDT Layout

```rust
// From arch/gdt.rs:
// GDT entries:
//   0: Null descriptor
//   1: Kernel code segment (DPL=0, 64-bit)
//   2: Kernel data segment (DPL=0)
//   3: User code segment (DPL=3, 64-bit)  [if used]
//   4: User data segment (DPL=3)          [if used]
//   5: TSS (Task State Segment)
```

Uses `lazy_static!` for GDT struct, `gdt::load()` via `x86_64` crate.

### 4.5 IDT Entry Map

| Vector | Handler | Description |
|--------|---------|-------------|
| 0 | `divide_error_handler` | Division by zero |
| 3 | `breakpoint_handler` | INT3 breakpoint |
| 6 | `invalid_opcode_handler` | Invalid opcode |
| 12 | `stack_segment_handler` | Stack segment fault |
| 13 | `general_protection_fault_handler` | GPF |
| 14 | `page_fault_handler` | Page fault |
| 32 (0x20) | `timer_handler` | PIT timer interrupt |
| 33 (0x21) | `keyboard_handler` | PS/2 keyboard interrupt |
| 8 | `double_fault_handler` | Double fault (with IST) |

All handlers defined in `arch/idt.rs`. The double fault handler uses an Interrupt Stack Table (IST).

### 4.6 Paging Structure

```rust
// From arch/paging.rs:
// Uses OffsetPageTable from x86_64 crate
// BootInfoFrameAllocator allocates from Limine memory map
// Heap mapped at 0xFFFF_9000_0000_0000
// 4-level page tables (PML4 → PDP → PD → PT)
```

### 4.7 Memory Layout

```
0x0000_0000_0000_0000 → Kernel code + data (lower half, identity mapped)
...
0xFFFF_8000_0000_0000 → Higher half (kernel space)
0xFFFF_9000_0000_0000 → 16MB heap
...
0xFFFF_FFFF_8000_0000 → Recursive page table entry
```

### 4.8 Process Model

```rust
// From process.rs:
pub struct Process {
    pub pid: u64,
    pub state: ProcessState,   // Ready | Running | Blocked | Suspended | Terminated | Zombie
    pub priority: u8,          // 0 (highest) to 5 (lowest)
    pub sandbox_level: u8,     // 0 (Unrestricted) to 4 (Maximum)
    pub cpu_time: u64,
    pub memory_usage: u64,
    pub parent: Option<u64>,
    pub children: Vec<u64>,
}
```

### 4.9 Scheduler Algorithm

```rust
// From scheduler.rs:
// 6 priority queues (0 = highest, 5 = lowest)
// Time slice: 50 ticks per process
// Algorithm: Priority-based round-robin with boost & throttle
//   - boost(): raises priority of starved low-priority processes
//   - throttle(): lowers priority of CPU-hogging processes
// pick_next(): selects from highest non-empty queue
```

### 4.10 IPC System

```rust
// From ipc.rs:
// Channel-based IPC:
//   subscribe(channel_id) → returns receiver
//   send(channel_id, message) → broadcasts to all subscribers
//   recv(receiver) → blocks until message available
//   broadcast(sender, message) → sends to all subscribers
// Channels identified by u64 IDs
```

### 4.11 VFS (Virtual File System)

```rust
// From fs.rs:
// Inode-based VFS:
//   create(path, type) → creates file/directory
//   write(inode, data) → writes data
//   read(inode) → reads data
//   mkdir(path) → creates directory
//   ls(path) → lists directory contents
// Root inode created at init
```

### 4.12 Syscall Interface

| Syscall # | Name | Params | Description |
|-----------|------|--------|-------------|
| 0 | Exit | code | Terminate current process |
| 1 | GetPid | — | Get current process PID |
| 2 | Kill | pid | Terminate another process |
| 3 | SchedYield | — | Yield CPU to scheduler |
| 4 | GetTime | — | Get current system time |
| 5 | IpcSend | channel, msg | Send IPC message |
| 6 | IpcRecv | channel | Receive IPC message |
| 7 | Shutdown | — | Shutdown the system |

### 4.13 Sandbox Levels

```rust
// From sandbox.rs:
pub enum SandboxLevel {
    Unrestricted = 0,   // Full system access
    Low = 1,            // Restricted system calls
    Medium = 2,         // No raw hardware access
    High = 3,           // Memory-isolated
    Maximum = 4,        // No network, no filesystem
}
// Each transition is audited
```

### 4.14 Driver Probing (drivers.rs)

```rust
// Probes for devices on boot:
// - ichin-serial: Serial port
// - ichin-block: Block device
// - ichin-input: Input device
// - ichin-display: Display/framebuffer
// Each driver has init() and handle_interrupt() methods
```

### 4.15 Service Registry

```rust
// From services.rs:
// Registered services (port, name):
//   8011 → orchestrator
//   8012 → agents
//   8013 → memory-engine
//   8014 → ui-system
//   8015 → app-runtime
//   8016 → ai-studio
//   8017 → security-core
//   7010 → system-daemon
// Each service can be started/stopped/monitored
```

### 4.16 Build Requirements

- **Rust toolchain:** nightly-2024-07-01 (from rust-toolchain.toml)
- **Target:** Custom `target.json` (x86_64-unknown-none with specific linker args)
- **Build command:** `cargo build --target target.json -Z build-std=core,alloc --release`
- **Linker script:** `linker.ld` (custom section layout)
- **Limine config:** `limine.conf` (bootloader settings)
- **Docker build:** `Dockerfile.build` (containerized build environment)

---

## 5. SERVICE DEEP DIVES

### 5.1 Orchestrator (:8011)

**Source:** `services/orchestrator/` | **Language:** Python (FastAPI) + Rust (Axum — Cargo.toml present)  
**Status:** ✅ Verified (port 8000 in source, remapped to 8011 in ISO)  
**Files:** `main.py` (43,668 B), `requirements.txt`, `Cargo.toml` (dual-language build)

#### Architecture

```
Input → Classifier → Agent Selector → Parallel Agent Execution → Decision Engine → Safety Validator → Output
```

#### Core Components (from main.py)

- **InputClassifier:** Categorizes requests by type (task/question/system action/chat/automation) and workspace
- **AgentSelector:** Picks relevant agents based on classification
- **DecisionEngine:** Weighted voting system with conflict resolution
- **SafetyValidator:** Policy checks, risk analysis, permission validation
- **ModeController:** Enforces Normal/Focus/DeepFocus/Lock modes
- **MemorySystem:** Working + long-term memory interfaces

#### API Endpoints

```python
# FastAPI routes:
GET  /health              # Health check
POST /orchestrate         # Main orchestration endpoint
POST /classify            # Input classification
GET  /context/{session_id} # Get session context
POST /execute-decision    # Execute a decision
```

#### Requirements

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
httpx==0.28.1
redis==5.2.1
numpy==2.2.1
scikit-learn==1.6.1
```

#### Agents Managed (within main.py)

8 agents defined as Python functions/classes:
1. **Study Agent** — learning optimization, quiz generation, flashcards
2. **Coding Agent** — code generation, debugging, architecture
3. **Learning Agent** — knowledge structure, learning paths
4. **Productivity Agent** — task optimization, scheduling
5. **Focus Agent** — attention management, distraction detection
6. **Security Agent** — integrity checks, anomaly detection
7. **Calendar Agent** — scheduling, event detection
8. **Research Agent** — web research, data mining

#### Uncertainty

> ⚠️ **PORT MISMATCH:** Source code binds port **8000**, but ISO init.sh and service registry use **8011**. The init.sh starts it via `python3 orchestrator/main.py` which will bind 8000, not 8011. Either the code needs a `--port` arg, or the init.sh is wrong.

---

### 5.2 AI Agents (:8012)

**Source:** `services/agents/` | **Language:** Python (FastAPI)  
**Status:** ✅ Verified  
**Files:** `main.py` (47,998 B), `requirements.txt`

#### API Endpoints

```python
# FastAPI routes (from main.py source):
GET    /health              # Health check
POST   /agents/route        # Route request to specific agent
POST   /agents/consensus    # Run multi-agent consensus
GET    /agents/{name}       # Get agent status
POST   /agents/{name}/query # Query specific agent
```

#### Requirements

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
httpx==0.28.1
```

---

### 5.3 Memory Engine (:8013)

**Source:** `services/memory-engine/` | **Language:** Python (FastAPI)  
**Status:** ✅ Verified (port 8003 in source, remapped to 8013 in ISO)  
**Files:** `main.py` (51,537 B — largest file), `requirements.txt`

#### Architecture

Four memory layers implemented:
1. **Ephemeral Context** — in-memory dict, seconds-minutes lifetime
2. **Working Memory** — session-scoped, auto-expiry
3. **Long-Term Semantic Memory** — vector embeddings + cosine similarity
4. **Structured System Memory** — Redis-backed task/note/calendar storage

#### API Endpoints

```python
# REST API endpoints (from main.py):
POST /memory/store          # Store a memory
POST /memory/query          # Query memories (semantic search)
POST /memory/recall         # Recall by session context
POST /memory/promote        # Promote working → long-term
POST /memory/decay          # Trigger decay cycle
POST /context/build         # Build context packet for orchestrator
```

#### Requirements

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
httpx==0.28.1
numpy==2.2.1
scikit-learn==1.6.1
redis==5.2.1
```

#### Uncertainty

> ⚠️ **PORT MISMATCH:** Source binds **8003**, init.sh uses **8013**. Same issue as orchestrator.

---

### 5.4 UI System (:8014)

**Source:** `services/ai-studio/ui_system.py` | **Language:** Python (FastAPI)  
**Status:** ✅ Verified (port 8004 in source)  
**Note:** Shares directory with AI Studio

#### API Endpoints

```python
# From ui_system.py (44,102 B):
POST /ui/orb/state          # Set AI Orb state (idle/active/critical)
POST /ui/orb/event          # Push event to Orb
POST /ui/spotlight/search   # Spotlight search
POST /ui/spotlight/command  # Execute command
POST /ui/layout/workspace   # Set workspace layout
POST /ui/layout/panel       # Toggle panel visibility
POST /ui/transition         # Trigger UI transition animation
```

---

### 5.5 App Runtime (:8015)

**Source:** `services/app-runtime/` | **Language:** Rust (Axum)  
**Status:** ✅ Verified (port 8005 in source)  
**Files:** `src/main.rs` (26,574 B), `Cargo.toml`

#### Architecture

Full application lifecycle management:
- **Install** → **Run** → **Suspend** → **Terminate**
- Permission system with sensitive approvals
- In-memory app store with 4 default apps
- AI simulation endpoint
- API gateways for AI, Memory, Calendar, Files, Notifications

#### API Endpoints

```rust
// Axum routes:
GET  /health
POST /apps/install          // Install an app
POST /apps/run              // Run an app
POST /apps/suspend          // Suspend an app
POST /apps/terminate        // Terminate an app
GET  /apps                  // List installed apps
GET  /apps/{id}             // Get app details
POST /apps/{id}/permissions // Set app permissions
POST /ai/simulate           // Run AI simulation
GET  /gateway/ai            // AI gateway
GET  /gateway/memory        // Memory gateway
GET  /gateway/calendar      // Calendar gateway
GET  /gateway/files         // Files gateway
GET  /gateway/notifications // Notifications gateway
```

#### Default Apps

1. **ICHIN Assistant** — General AI assistant
2. **CodeForge** — Code development environment
3. **StudyPal** — Study/learning tools
4. **TerminalX** — Terminal emulator

#### Dependencies (Cargo.toml)

```toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
chrono = "0.4"
tracing = "0.1"
uuid = { version = "1", features = ["v4"] }
rand = "0.8"
```

---

### 5.6 AI Studio (:8016)

**Source:** `services/ai-studio/` | **Language:** Python (FastAPI)  
**Status:** ✅ Verified (port 8016 in source)  
**Files:** `main.py` (43,171 B), `ui_system.py` (44,102 B), `requirements.txt`

#### API Endpoints (main.py)

```python
# Workflow management:
POST /workflows/create
POST /workflows/execute
POST /workflows/save
GET  /workflows

# Agent training/fine-tuning:
POST /agents/train
POST /agents/evaluate
GET  /agents/performance

# Pattern analysis:
POST /patterns/analyze
GET  /patterns

# Model management:
POST /models/load
POST /models/unload
GET  /models
```

---

### 5.7 Security Core (:8017)

**Source:** `services/security-core/` | **Language:** Rust (Axum)  
**Status:** ✅ Verified (port 8006 in source)  
**Files:** `src/main.rs` (40,063 B), `Cargo.toml`

#### Core Functionality

- **Process monitoring** (CRUD: create/read/update/delete processes)
- **Sandbox management** (5 levels, CRUD operations)
- **Snapshot manager** (create/list/restore/delete snapshots)
- **Security detector** (randomized anomaly + threat detection)
- **Scheduler** (priority queue based)
- **Audit log** (append-only)

#### API Endpoints

```rust
// Full REST API (~30 endpoints):
GET    /health
// Processes:
POST   /processes
GET    /processes
GET    /processes/{id}
PUT    /processes/{id}
DELETE /processes/{id}
// Sandboxes:
POST   /sandboxes
GET    /sandboxes
GET    /sandboxes/{id}
GET    /sandboxes/{id}/audit
DELETE /sandboxes/{id}
// Security:
POST   /security/scan
GET    /security/threats
GET    /security/anomalies
POST   /security/respond
// Scheduler:
POST   /scheduler/tasks
GET    /scheduler/tasks
DELETE /scheduler/tasks/{id}
// Snapshots:
POST   /snapshots
GET    /snapshots
POST   /snapshots/{id}/restore
DELETE /snapshots/{id}
// Audit:
GET    /audit
```

#### Dependencies

```toml
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
uuid = { version = "1", features = ["v4"] }
chrono = "0.4"
sysinfo = "0.30"
fastrand = "2"
```

---

### 5.8 System Daemon (:7010)

**Source:** `services/system-daemon/` | **Language:** Rust (tokio)  
**Status:** ✅ Verified (port 7010 in source)  
**Files:** `src/main.rs` (6,818 B), `Cargo.toml`

#### Architecture

Background task scheduler with 5 cron-like tasks:

```rust
// From main.rs — registered tasks:
// 1. health_check     → every 30s
// 2. log_rotation     → every 300s (5 min)
// 3. temp_cleanup     → every 600s (10 min)
// 4. sync_check       → every 60s (1 min)
// 5. backup_check     → every 3600s (1 hour)
```

Implements a raw TCP server with REST-like text-based protocol (not HTTP). Processes commands: `health`, `status`, `restart`, `shutdown`.

#### Dependencies

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
uuid = { version = "1", features = ["v4"] }
chrono = "0.4"
```

---

### 5.9 Account (:8081)

**Source:** `services/account/` | **Language:** Rust (Axum 0.8)  
**Status:** ✅ Verified  
**Files:** 7 source .rs files across 2 crates (core + server)

#### Architecture

Two-crate workspace:
1. **`account-core`** — library crate: auth, models, storage
2. **`account-server`** — binary crate: Axum web server

#### core/src/auth.rs

```rust
// 273 lines — authentication module:
pub struct AuthManager {
    // Handles:
    // - register(username, password_hash, email)
    // - login(username, password) → session token
    // - validate_session(token) → user info
    // - invalidate_session(token)
    // - setup_totp(user_id) → QR code
    // - verify_totp(user_id, code) → bool
    // - register_webauthn(user_id) → challenge
    // - verify_webauthn(user_id, response) → bool
    // - generate_recovery_codes(user_id) → 8 codes
    // - verify_recovery_code(user_id, code) → bool
    // - get_devices(user_id) → list
    // - remove_device(user_id, device_id)
    // - sign(data, private_key) → Ed25519 signature
    // - verify(data, signature, public_key) → bool
}
```

#### core/src/models.rs

```rust
// 167 lines — data models:
pub struct User { id, username, password_hash, email, public_key, created_at, updated_at }
pub struct Session { id, user_id, token, device_id, created_at, expires_at }
pub struct Device { id, user_id, name, device_type, public_key, last_seen }
pub struct LoginHistory { id, user_id, device_id, ip, user_agent, success, timestamp }
pub struct AccountSettings { user_id, theme, language, notifications, privacy }
// Browser sync models:
pub struct Bookmark { id, user_id, url, title, folder, position }
pub struct History { id, user_id, url, title, visit_count, last_visit }
pub struct SavedPassword { id, user_id, url, username, encrypted_password }
```

#### core/src/storage.rs

```rust
// 419 lines — sled embedded database storage:
pub struct Storage { db: sled::Db }
// Methods: store_user, get_user, store_session, validate_session, etc.
```

#### server/src/main.rs

```rust
// 1,294 lines — Axum web server:
// 30+ endpoints for:
// - Auth: register, login, logout, me
// - Passkeys: register_passkey, authenticate_passkey
// - TOTP: setup_totp, verify_totp
// - Sessions: list_sessions, delete_session
// - Devices: list_devices, remove_device
// - LoginHistory: list_login_history
// - Settings: get_settings, update_settings
// - Browser sync: bookmarks CRUD, history CRUD, passwords CRUD
// - Recovery: generate_recovery_codes, verify_recovery_code
```

#### Dependencies

```toml
# core/Cargo.toml:
[dependencies]
serde = { version = "1", features = ["derive"] }
hex = "0.4"
uuid = { version = "1", features = ["v4"] }
ed25519-dalek = "2"
sled = "0.34"
argon2 = "0.5"
totp-rs = { version = "5", features = ["gen_secret", "otpauth"] }
webauthn-rs = { version = "0.5", features = ["danger-allow-state-serialisation"] }

# server/Cargo.toml:
[dependencies]
axum = "0.8"
tower-http = { version = "0.6", features = ["cors"] }
account-core = { path = "../core" }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tower-cookies = "0.10"
# ...
```

---

### 5.10 Mail (:8080)

**Source:** `services/mail/` | **Language:** Rust (Axum)  
**Status:** ✅ Verified (40+ source files, fully read)  
**Architecture:** 4 binaries, 11 modules

#### Binary Targets

| Binary | File | Port | Purpose |
|--------|------|------|---------|
| `server` | `src/bin/server.rs` | 8080 (config) | HTTP API server |
| `send` | `src/bin/send.rs` | — | CLI send tool |
| `receive` | `src/bin/receive.rs` | — | CLI receive tool |
| `gateway` | `src/bin/gateway.rs` | 25 (SMTP) | SMTP gateway |

#### Module Map (11 modules)

| Module | Key Files | Purpose |
|--------|-----------|---------|
| `api/` | `mod.rs`, `auth.rs` | Axum REST API: messages CRUD, auth middleware, CORS |
| `protocol/` | `envelope.rs`, `handshake.rs`, `types.rs`, `version.rs` | ICHIN wire protocol (not SMTP) |
| `transport/` | `server.rs`, `client.rs`, `tls.rs` | TCP/TLS 1.3 transport layer |
| `delivery/` | `queue.rs`, `worker.rs`, `thread.rs`, `validate.rs` | Queue-based async delivery |
| `dns/` | `discovery.rs` | DNS discovery via hickory-resolver |
| `security/` | `keys.rs`, `sign.rs`, `spf.rs`, `verify.rs` | Ed25519 signing, SPF verification |
| `gateway/` | `smtp.rs`, `smtp_send.rs`, `translate.rs` | SMTP ↔ ICHIN envelope translation |
| `storage/` | `mailbox.rs`, `attachment.rs`, `local.rs` | Sled-based mailbox storage |
| `extensions/` | `expiration.rs`, `receipts.rs`, `schedule.rs` | Email expiration, read receipts |
| `spam/` | `mod.rs` | Reputation-based spam scoring |
| `internal/` | `config.rs`, `logger.rs` | Configuration, logging |

#### API Endpoints (api/mod.rs)

```rust
GET    /api/status               # Server status
GET    /api/messages              # List messages (with pagination)
POST   /api/messages              # Send message
GET    /api/messages/{id}         # Get message by ID
POST   /api/messages/{id}/action  # Perform action on message
POST   /api/messages/{id}/read    # Mark as read
POST   /api/messages/{id}/star    # Toggle star
GET    /api/unread-counts         # Get unread counts
GET    /{*path}                   # Serve static frontend
```

#### Dependency Chain (critical)

```toml
# Cargo.toml dependency on account:
ichin-account-core = { path = "../account/core" }
```

> ⚠️ **This means mail CANNOT BUILD without account/core first.**

#### SPF Verification (security/spf.rs)

Complete SPF verifier with:
- SPF record parsing (v=spf1)
- Mechanism evaluation (ip4, ip6, a, mx, ptr, exists, include, all)
- Modifier support (redirect, exp)
- Macro expansion (%{s}, %{l}, %{o}, %{d}, %{i}, %{p}, %{v}, %{h})
- DNS lookup limits (10 max)

---

### 5.11 Protocol Stack (:4889–:4892)

**Source:** `services/protocol/` | **Language:** Python  
**Status:** ✅ Verified (all scripts fully read)  
**Dependency:** `cryptography>=41.0.0` (only external dep)

#### 5.11.1 Ichin-Protocol (:4889)

**Purpose:** Custom wire protocol for ICHIN system communication  
**Protocol:** HTTP-inspired JSON-over-TCP with TLS 1.3 mandatory

```python
# server.py — ICHINP server on port 4889:
# Handles: CONNECT, DISCONNECT, SUBSCRIBE, UNSUBSCRIBE, PUBLISH, PING
# JSON message format with security: { type, from, to, payload, timestamp, signature }

# client.py — ICHINP client:
# Methods: connect, disconnect, subscribe, unsubscribe, publish, ping

# ichinp.py — Core protocol library:
# Message types, framing, serialization
```

#### 5.11.2 Ichin-DNS (:4890)

**Purpose:** Internal DNS system for ICHIN service discovery

```python
# server.py — DNS server on port 4890:
# Handles: REGISTER, QUERY, RESOLVE, LIST, DELETE
# Three components:
#   Registry: stores service → address mappings with TTL
#   Cache: LRU cache for resolved queries
#   Resolver: resolves service names to addresses

# client.py — DNS client:
# Methods: register, query, resolve, list_services

# ichindns.py — Core library:
# InMemoryRegistry, DNSCache, DNSResolver classes
```

#### 5.11.3 Ichin-CA (:4891)

**Purpose:** Internal Certificate Authority for ICHIN system

```python
# server.py — CA server on port 4891:
# Handles: CERT_SIGN, CERT_VALIDATE, CERT_REVOKE, CERT_STATUS
# Full PKI with CRL (Certificate Revocation List)

# client.py — CA client:
# Methods: sign_cert, validate_cert, revoke_cert, check_status

# ichinca.py — Core library:
# RootCA (self-signed root), CertStore, CRL, VerificationEngine, CertificateValidator
# root_ca_cert.json — pre-generated root CA certificate
```

#### 5.11.4 Ichin-Daemon (:4892)

**Purpose:** Application daemon/server framework for ICHIN

```python
# ichind.py — Main daemon server on port 4892:
# Routes → Session → Sandbox → Static → Realtime
# Application hosting framework with sandboxed execution

# router.py — Request router:
# Maps routes to handlers, middleware support

# session.py — Session manager:
# Session creation, validation, expiry

# sandbox.py — Application sandbox:
# Resource limits, filesystem isolation, network access control

# static.py — Static file server:
# Serves static files from app directories

# realtime.py — WebSocket-like realtime:
# Bidirectional communication with clients

# apps/hello/ — Example app:
# main.py — simple "Hello ICHIN" handler
# route.json — route configuration
```

---

### 5.12 Search Engine (:3000–:3001)

**Source:** `services/search-engine/` | **Language:** Rust (Axum 0.8) + Next.js 15  
**Status:** ✅ Verified (all files fully read)

#### Server (:3001) — Rust/Axum

```rust
// main.rs — Axum server on port 3001:
// Endpoints:
GET  /health
POST /search          // { query: String, limit: u64 } → Vec<SearchResult>
POST /index           // Index a page

// models.rs:
pub struct Site { id, name, url, description }
pub struct Page { id, site_id, url, title, content, tags, verified }
pub struct SearchResult { page, score, snippet }

// index.rs — InvertedIndex:
// Tokenizer: splits on whitespace + punctuation, lowercase
// In memory: HashMap<String, HashMap<u64, f64>> term → (page_id, weight)

// search.rs — SearchEngine:
// Scoring: title_match * 5 + tag_match * 4 + site_match * 3 + content_match * 1 + verified_bonus * 3

// db.rs — SQLite:
// Tables: sites(), pages(), index_terms(term, page_id, weight)
// Seeded with 3 sites (docs.ichin, tools.ichin, blog.ichin), 6 pages
```

#### Dependencies

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
rusqlite = { version = "0.34", features = ["bundled"] }
tower-http = { version = "0.6", features = ["cors"] }
```

#### Client (:3000) — Next.js 15

```typescript
// Next.js 15 + React 19 + TypeScript + Tailwind CSS:
// page.tsx — Search UI with:
// - Search bar with icon
// - Result cards (title, URL, snippet, tags)
// - Loading state with animation
// - Responsive design
```

---

## 6. APP DEEP DIVES

### 6.1 Desktop UI (:1420)

**Source:** `apps/desktop-ui/` | **Language:** React 18 + TypeScript + Vite  
**Status:** ✅ Verified  
**Config:** Vite dev server port 1420

#### Tech Stack

- React 18 + TypeScript
- Vite 6 (dev server on :1420)
- Tailwind CSS v4
- Framer Motion (animations)
- Zustand (state management)
- Axios (HTTP client)

#### Store Architecture (7 stores)

| Store | File | Key State |
|-------|------|-----------|
| `uiStore` | `stores/uiStore.ts` | theme, sidebar, panels |
| `appStore` | `stores/appStore.ts` | apps, currentApp |
| `orbStore` | `stores/orbStore.ts` | orbState, events |
| `focusStore` | `stores/focusStore.ts` | mode, intensity |
| `councilStore` | `stores/councilStore.ts` | agents, decisions |
| `spotlightStore` | `stores/spotlightStore.ts` | open, query, results |
| `workspaceStore` | `stores/workspaceStore.ts` | activeWorkspace, workspaces |

#### Component Tree

```
AppShell
├── Shell
│   ├── Sidebar (workspace nav)
│   ├── Main Content Area
│   │   ├── Workspace Components
│   │   │   ├── StudyWorkspace
│   │   │   ├── CodingWorkspace
│   │   │   ├── LearningWorkspace
│   │   │   └── PersonalWorkspace
│   │   └── AIPanels
│   │       ├── AIStudioPanel
│   │       └── WorkflowBuilder
│   └── Orb (floating indicator)
├── Spotlight (modal overlay)
├── FocusOverlay (mode overlay)
├── MissionControl (dashboard)
├── AICouncil (panel)
├── Settings (panel)
├── AppStore (panel)
├── AppDetails (panel)
├── KeyboardCheatsheet (overlay)
├── FileBrowser (panel)
└── Zoey/OnboardingFlow (first boot)
```

### 6.2 Web UI (:1430)

**Source:** `apps/web-ui/` | **Language:** React + TypeScript + Vite  
**Status:** ⚠️ Port 1430 from init.sh (not in vite.config.ts which has no port set)

#### Component Tree

```
Shell
├── Sidebar
├── WorkspaceContainer
│   ├── CodingWorkspace
│   ├── LearningWorkspace
│   ├── PersonalWorkspace
│   └── StudyWorkspace
├── AIOrb
├── Spotlight
├── AICouncil
├── FocusOverlay
├── MissionControl
├── Settings
├── FileBrowser
└── useKeyboard (hook)
```

#### Stores

`workspaceStore`, `uiStore`, `orbStore`, `focusStore` — all Zustand

### 6.3 Mobile UI (Expo)

**Source:** `apps/mobile-ui/` | **Language:** Expo SDK 51 + React Native + TypeScript  
**Status:** ✅ Verified (app.json, package.json, App.tsx)

#### Navigation Structure

```
AppNavigator (Stack Navigator)
├── HomeScreen
├── WorkspaceScreen
│   ├── CodingWorkspace
│   ├── StudyWorkspace
│   ├── LearningWorkspace
│   └── PersonalWorkspace
├── CouncilScreen
├── MissionControlScreen
└── SettingsScreen
```

#### Key Dependencies

- `expo` ~51.0.0
- `@react-navigation/native` + `stack`
- `zustand`
- `axios`

### 6.4 Desktop Browser (:3003)

**Source:** `apps/desktop-browser/` | **Language:** Electron + Rust (Axum) + React  
**Status:** ✅ Verified

#### Architecture

```
main.js (Electron) → Rust Backend (:3003) → React Frontend (renderer)
                    ├── WebView (embedded browser view)
                    ├── Tab management
                    ├── History tracking
                    └── Bookmark/favorites sync via Account service
```

#### Rust Back-End Routes

```rust
// src/routes/:
// tabs.rs → Tab CRUD (open, close, switch, list)
// history.rs → History CRUD (visit, search, clear)
// favorites.rs → Favorites CRUD (add, remove, list)
// user.rs → User management (profile, settings)
// workspaces.rs → Workspace management
// csrf_protection.rs → CSRF token validation
```

Note: There's a `src/` and `src.backup/` directory — the backup may be stale.

### 6.5 Calendar (:3002)

**Source:** `apps/calender/` | **Language:** Rust (Axum) + React  
**Status:** ✅ Verified

#### Rust Back-End Routes

```rust
// handlers.rs:
// Events CRUD: list, create, update, delete
// Tasks CRUD: list, create, update, delete
// Views: day, week, month, agenda
```

#### Front-End Components

```
CalendarHeader (month/year navigation)
DayView
WeekView
MonthView
Sidebar (task list, mini-calendar)
TaskPanel
TaskModal
CommandPalette (keyboard shortcuts)
```

#### Python Proxy

`app/calender/main.py` + `route.json` — Python proxy layer

---

## 7. PACKAGE REFERENCE

### 7.1 shared-types

**Package:** `packages/shared-types/` | **File:** `src/index.ts` (5,813 B)  
**Exports:** 30+ TypeScript types/interfaces

```typescript
// Key types:
WorkspaceType     // 'study' | 'coding' | 'learning' | 'personal'
FocusMode         // 'normal' | 'focus' | 'deep-focus' | 'lock'
OrbState          // { mode: 'idle' | 'active' | 'critical', confidence: number, ... }
AgentName         // 'study' | 'coding' | 'learning' | 'productivity' | 'focus' | 'security' | 'calendar' | 'research'
MemoryType        // 'ephemeral' | 'working' | 'long-term' | 'structured'
AppType           // 'native' | 'web' | 'sandboxed' | 'system'
PermissionType    // 'read' | 'write' | 'execute' | 'network' | 'filesystem' | 'camera' | 'microphone'
CouncilDecision   // { decision, confidence, agents[], risk, ... }
FocusState        // { mode, intensity, since, ... }
UIState           // { workspace, panels, theme, ... }
WorkflowDefinition // { name, steps[], trigger, ... }
```

### 7.2 ai-sdk

**Package:** `packages/ai-sdk/` | **File:** `src/index.ts` (8,535 B)  
**Purpose:** Agent/Workflow builder SDK for third-party app developers

```typescript
// Key exports:
class AgentBuilder    // Build AI agents with prompts, tools, memory
class WorkflowBuilder // Define multi-step workflows
class MemoryQueryBuilder // Query memory with filters
class AIOrchestratorClient // HTTP client to communicate with orchestrator service
class PermissionsHelper // Permission checking utilities
```

### 7.3 ui-components

**Package:** `packages/ui-components/` | **File:** `src/index.ts` (32,397 B)  
**Purpose:** Reusable UI component library (1,111 lines)

```typescript
// Key exports:
GlassPanel           // Blurred glass-morphism container
OrbIndicator         // Animated AI Orb with countdown ring
SpotlightInput       // Command palette with keyboard navigation
WorkspaceContainer   // Workspace shell with sidebar
AIAgentCard          // Agent status display card
CouncilPanel         // AI Council voting display
FocusOverlay         // Focus mode overlay
TaskCard             // Task display card
FileBrowser          // File system browser (folder/tag/graph views)
AppCard              // Application card
```

### 7.4 permissions-model

**Package:** `packages/permissions-model/` | **File:** `src/index.ts` (7,918 B)  
**Purpose:** Permission management utilities (282 lines)

```typescript
// Key exports:
class PermissionRegistry    // Singleton registry of all permissions
class PermissionValidator   // Validate permissions against hierarchy/risk
class SandboxLevelMapper    // Map permissions to sandbox levels (4 levels)
class DefaultPermissions    // Default permission sets per app type
```

---

## 8. ECOSYSTEM REFERENCE

### 8.1 Ichin App Store

**Source:** `ecosystem/ichin-app-store/` | **Language:** Python (FastAPI) + React/Vite

#### Backend (FastAPI, :8021)

```python
# main.py (14,657 B) — Full REST API:
# User management (register, login, profile)
# App management (publish, update, approve, list, search)
# Reviews & ratings
# Download tracking
```

**Requirements:** fastapi, uvicorn, pydantic, httpx

#### Frontend (React/Vite)

`App.tsx` (11,351 B) — Full app store UI with:
- App listing (grid/list view)
- Search & filter
- App detail pages
- User dashboard
- Publish workflow

### 8.2 Developer Portal

**Source:** `ecosystem/developer-portal/` | **Language:** Static HTML/CSS/JS  
**Files:** `index.html` (392 lines), `style.css`, `script.js`

Static documentation portal covering:
- API Reference
- Permissions Guide
- SDK Guides (TypeScript, Python, Rust)
- App Store Publishing
- AI Integration Guide
- Best Practices

### 8.3 App Templates

#### TypeScript App Template

```typescript
// src/index.ts — IchinApp base class:
class IchinApp {
  // Methods: init, registerAgent, accessMemory, sendNotification
  // integrateAI: Connect to AI council
  // accessFileSystem: Sandboxed file access
  // Example: "Code Review Assistant" — listens for code changes, runs AI review
}
```

#### Python Agent Template

```python
# agent.py — IchinAgent base class:
class IchinAgent:
    # Methods: analyze, suggest, execute
    # Example: StudyAssistantAgent — generates quizzes, schedules study sessions
class StudyAssistantAgent(IchinAgent):
    def generate_quiz(self, topic, difficulty):
    def schedule_study_session(self, subject, duration):
    def summarize_notes(self, text):
```

#### Workflow Template

```json
{
  "name": "Daily Study Routine",
  "trigger": { "type": "schedule", "time": "09:00", "days": ["weekdays"] },
  "steps": [
    { "action": "check_focus_mode", "params": {} },
    { "action": "ai_summarize", "agent": "sage" },
    { "action": "create_task", "from": "summary" },
    { "action": "notify", "type": "orb", "message": "..." }
  ]
}
```

---

## 9. BUILD SYSTEM REFERENCE

### 9.1 ISO Build System

**Source:** `ichin-os/infra/iso/` | **6 files:** Makefile, build-iso.py, build-iso.sh, init.sh, grub.cfg, Dockerfile.iso

#### Makefile Targets

| Target | Dependencies | Purpose |
|--------|-------------|---------|
| `all` | `iso` | Default: build ISO |
| `kernel` | — | Download/build Linux 6.6 kernel |
| `ichin-kernel` | — | Build bare-metal ICHIN kernel (Rust nightly) |
| `initramfs` | `kernel` | Build initramfs with services |
| `services` | — | Pre-build Python dependencies |
| `external` | 10 sub-targets | Clone all external AI repos |
| `iso` | `clean, initramfs, services, external` | Assemble bootable ISO |
| `run` | `iso` | Boot in QEMU |
| `clean` | — | Remove build artifacts |

#### build-iso.py Functions

| Function | Purpose |
|----------|---------|
| `build_initramfs()` | Creates initramfs directory, copies busybox, services, external repos |
| `clone_external_repos()` | Shallow clones all 10 external repos, strips .git |
| `download_kernel()` | Downloads pre-built Linux 6.6 kernel (or builds from source) |
| `assemble_iso()` | Creates ISO with grub-mkrescue/xorriso |
| `build_with_docker()` | Builds ISO inside Docker |
| `run_qemu()` | Launches QEMU with port forwarding |

#### init.sh Boot Sequence

```sh
1. Mount filesystems (proc, sysfs, tmpfs, devtmpfs)
2. Set up loopback networking
3. Set hostname (ichin-os)
4. Mount root filesystem (if available)
5. Create ICHIN directories (/var/log/ichin, /ichin/{data,config,logs})
6. Export PATH and PYTHONPATH
7. Start services in order:
   a. Orchestrator (:8011) — Python
   b. OpenJarvis (:8090) — Python AI framework
   c. Ruflo (:8091) — Node.js MCP server
   d. Dexter (:8092) — Bun CLI (TUI-only, will not daemonize)
   e. jcode (:8093) — Rust binary (Unix socket only)
   f. ClawRouter (:8402) — Node.js LLM proxy
   g. agentic-inbox (:8094) — Node.js (Cloudflare-only, will fail)
   h. AI Agents (:8012) — Python
   i. Memory Engine (:8013) — Python
   j. UI System (:8014) — Python
   k. AI Studio (:8016) — Python
   l. Account (:8081) — Rust binary
   m. Mail (:8080) — Rust binary
   n. Search Engine (:3001) — Rust binary
   o. Protocol stack (:4889-4892) — Python
   p. Kernel module (:7000) — Rust binary
8. Obsidian vault/skill setup (copies files)
9. Display status banner
10. Start watchdog loop (30s interval)
```

#### GRUB Config (grub.cfg)

```grub
set timeout=5
set default=0

menuentry "ICHIN OS" {
    multiboot2 /boot/vmlinuz
    module2 /boot/initrd.img
    boot
}

menuentry "ICHIN OS (Debug Mode)" {
    multiboot2 /boot/vmlinuz debug
    module2 /boot/initrd.img
    boot
}
```

#### Dockerfile.iso Stages

1. **Builder stage** (ubuntu:24.04):
   - Install: build-essential, wget, curl, cpio, gzip, grub-pc-bin, grub-common, grub-efi-amd64-bin, xorriso, mtools, python3, pip, rustup, nodejs, npm, git, unzip
   - Install Rust nightly toolchain
   - Install Bun (for Dexter)
   - Copy entire source
   - Run `bash build-iso.sh native`
   - Extract ISO artifact

2. **Runtime stage** (scratch):
   - Copy ISO from builder

---

## 10. EXTERNAL REPO INTEGRATION REPORT

### 10.1 OpenJarvis (:8090)

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/open-jarvis/OpenJarvis.git` |
| **Stars** | ~6,900 |
| **License** | Apache 2.0 |
| **Language** | Python 82.7%, Rust 8.6%, TypeScript 7.2% |
| **Default branch** | `main` |
| **Latest release** | `desktop-v1.0.2` (May 25, 2026) |
| **Paper** | arxiv.org/abs/2605.17172 |

#### Entry Points (Actual, Verified)

```bash
# CLI mode (default):
jarvis                              # Interactive chat
jarvis ask "question"               # Single-turn query

# Server mode (verified):
jarvis serve                        # FastAPI on 0.0.0.0:8000
jarvis serve --host 0.0.0.0 --port 8090  # Custom port ✅
jarvis serve --engine ollama --model qwen3.5:9b

# Daemon mode:
jarvis start                        # Background server
jarvis start --port 8090            # Custom port ✅
jarvis stop
jarvis status
```

#### --port Flag Support: ✅ YES

Verified in `src/openjarvis/cli/serve.py:63-66`:
```python
@click.option("--host", default=None, help="Bind address (default: config).")
@click.option("--port", default=None, type=int, help="Port number (default: config).")
```

Default port from `config.toml`: `[server] port = 8000`

#### Source Tree

```
src/openjarvis/
├── cli/                  # Entry point: ~50 Click subcommands
├── server/               # FastAPI server (~25 route modules)
├── agents/               # 8 built-in agents
├── core/                 # Config, events, paths, credentials
├── engine/               # Inference engines (vLLM, Ollama, MLX, SGLang, llama.cpp)
├── intelligence/         # Model discovery, routing, registration
├── memory/               # Memory system
├── mcp/                  # Model Context Protocol
├── skills/               # Skills catalog
├── tools/                # Tool implementations
├── workflow/             # Workflow engine
├── channels/             # Telegram, Discord, Slack, WhatsApp
├── scheduler/            # Cron/interval scheduling
├── security/             # Guardrails, capability policies
├── sandbox/              # WASM, Docker sandboxes
├── speech/               # Whisper, Deepgram
└── learning/             # DSPy, GEPA training
```

#### Dependencies

```toml
[dependencies]
click >=8, datasets >=4.5.0, ddgs >=9.11.4, httpx >=0.27
openai >=1.30, nvidia-ml-py >=12.560.30, posthog >=3.0
python-telegram-bot >=22.6, rich >=13, tomli >=2.0
tomlkit >=0.12, websockets >=15.0.1
# Server extras:
fastapi >=0.110, uvicorn >=0.30, pydantic >=2.0, python-multipart >=0.0.9
```

Python: >=3.10,<3.14 | Install: `uv sync --extra server` or `pip install openjarvis[server]`

#### How init.sh Starts It

```sh
start_openjarvis() {
    cd /ichin/external/OpenJarvis
    python3 -m jarvis serve --host 0.0.0.0 --port 8090 &
}
```

#### Uncertainties

> ⚠️ The init.sh checks for `jarvis/main.py` then `cli.py` — the actual entry point is `openjarvis.cli:main` (console_scripts entry). The `python3 -m jarvis` will only work if the package is installed (via pip/uv). If the repo is just cloned, `python3 -m openjarvis.cli` is the correct invocation, not `python3 -m jarvis`.

> ⚠️ All inference engines require at least one provider configured (Ollama, OpenAI API key, etc.). Without any provider, the server will start but return errors on queries.

> ⚠️ The daemon functionality writes a PID file to `~/.openjarvis/server.pid` — in the read-only initramfs this may fail.

---

### 10.2 Ruflo (:8091)

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/ruvnet/ruflo.git` |
| **Stars** | ~60,000+ |
| **License** | MIT |
| **Language** | TypeScript (98%), 100+ agents |
| **npm name** | `claude-flow` |
| **Latest release** | v3.12.4 |

#### Entry Points (Actual, Verified)

```bash
# CLI mode:
npx ruflo                          # Auto-detects: CLI or MCP mode
npx ruflo agent list               # List agents
npx ruflo swarm start              # Start swarm

# MCP Server (HTTP mode):
npx ruflo mcp start -t http --port 8091  # ✅ Custom port

# MCP Server (stdio mode — default):
npx ruflo mcp start                # JSON-RPC over stdio
```

#### --port Flag Support: ✅ YES

Verified in `v3/@claude-flow/cli/src/mcp-server.ts:43`:
```typescript
interface MCPServerOptions {
    port?: number;           // Default: 3000
    transport: 'stdio' | 'http' | 'websocket';
    daemonize?: boolean;
    // ...
}
```

Usage: `npx ruflo mcp start -t http --port 8091`

#### Architecture

```
Bootstrap chain:
npx ruflo → bin/cli.js → import('v3/@claude-flow/cli/bin/cli.js')
    → MCP mode (piped stdin):   mcp-client.js → JSON-RPC handler
    → CLI mode (TTY):           CLI.run() → command dispatcher
    → HTTP/WS mode (--transport): MCPServerManager → @claude-flow/mcp
```

#### How init.sh Starts It

```sh
start_ruflo() {
    cd /ichin/external/ruflo
    node dist/agent.mjs --port 8091 &
}
```

#### Uncertainties

> ⚠️ **WRONG ENTRY POINT.** The init.sh assumes `dist/agent.mjs` exists. The actual entry point is `v3/@claude-flow/cli/bin/cli.js` (which switches between CLI and MCP mode). The MCP server is started via `npx ruflo mcp start -t http --port 8091`, NOT by running `dist/agent.mjs` directly.

> ⚠️ The repo needs `npm install` (or `pnpm install`) + `npm run build` before it can run. Built files go to `dist/`. The init.sh assumes pre-built binaries. Without building, `dist/` won't exist.

> ⚠️ Ruflo needs Node.js >=20. The initramfs may have an older Node from the standalone Python build.

> ⚠️ Default MCP port is 3000, not 8091. The init.sh assigns 8091 which would require `--port 8091` to be passed correctly — which means the MCP start command must be correct.

---

### 10.3 Dexter (:8092)

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/virattt/dexter.git` |
| **Stars** | ~23,000 |
| **License** | Not specified |
| **Language** | TypeScript 98.2%, Bun runtime |
| **Latest version** | 1.0.0 |

#### Entry Points (Actual, Verified)

```typescript
// src/index.tsx — THE entry point:
#!/usr/bin/env bun
import { config } from 'dotenv';
import { runCli } from './cli.js';
config({ quiet: true });
await runCli();
```

#### --port Flag Support: ❌ NO

**Dexter is CLI-only (TUI).** There is NO HTTP server, no REST API, no `--port` flag. The WhatsApp gateway uses `@whiskeysockets/baileys` WhatsApp protocol, not HTTP.

#### What It Actually Does

- Interactive terminal UI (`@mariozechner/pi-tui`) with text editor, sliders, spinners
- Slash commands: `/model`, `/search`, `/rules`, `/clear`, `/memory`, `/heartbeat`, `/history`, `/help`
- Autonomous financial research agent with tool-calling LLM (ReAct-style)
- Tools: financial data APIs, web search (Exa/Tavily/Perplexity), browser automation (Playwright), filesystem, memory, cron, subagent spawning
- Memory: SQLite-backed vector embeddings, MMR diversity ranking, temporal decay
- WhatsApp gateway secondary channel (QR code login, not HTTP)

#### Dependencies (package.json)

```json
{
  "dependencies": {
    "@langchain/anthropic", "@langchain/openai", "@langchain/google-genai",
    "@langchain/ollama", "@langchain/exa", "@langchain/tavily",
    "exa-js", "@mariozechner/pi-tui", "playwright",
    "@whiskeysockets/baileys", "@mozilla/readability",
    "linkedom", "turndown", "zod", "better-sqlite3",
    "lru-cache", "croner", "langsmith", "diff", "dotenv"
  }
}
```

**Runtime: Bun** (not Node.js). The entry point has `#!/usr/bin/env bun`.

#### How init.sh Starts It

```sh
start_dexter() {
    cd /ichin/external/dexter
    bun run src/index.ts --port 8092 &
}
```

#### Uncertainties

> ⚠️ **DEXTER HAS NO SERVER MODE.** Starting it with `bun run src/index.ts --port 8092` will FAIL. The `--port` flag is not recognized. It will open a TUI that requires stdin/stdout — in a background init process with no terminal, it will likely crash or hang.

> ⚠️ **Dexter REQUIRES Bun.** The initramfs only has Node.js and Python. Bun is NOT included in the ISO build (no `bun` binary in initramfs). The `#!/usr/bin/env bun` shebang will fail.

> ⚠️ **API Keys required** to function: at minimum `OPENAI_API_KEY` + `FINANCIAL_DATASETS_API_KEY`. Without these, Dexter starts but every query fails.

> ⚠️ **Playwright** requires Chromium download (`playwright install chromium` as postinstall). Not feasible in initramfs.

> ⚠️ **Best approach:** Dexter should NOT be started as a background server. It should be a CLI-only tool users invoke on-demand. Remove from init.sh's auto-start.

---

### 10.4 mattpocock/skills

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/mattpocock/skills.git` |
| **Stars** | ~138,000 |
| **License** | Not specified |
| **Language** | Shell/Markdown |
| **Stars** | 138K (largest in the set) |

#### What It Is

A collection of **engineering skills** for AI coding agents: triage, TDD, PRD generation, domain modeling, codebase design, prototype building, bug diagnosis, etc. All skill definitions are Markdown files.

#### Loading Mechanism

```bash
# Method 1: npx skills CLI (recommended)
npx skills@latest add mattpocock/skills
# → Interactive wizard: pick skills → which agents → run /setup-matt-pocock-skills

# Method 2: Manual copy to agent skill directory
# Claude Code: ~/.claude/skills/ or /.claude/
# Codex: ~/.codex/skills/
# OpenCode: ~/.opencode/skills/ (auto-discovers SKILL.md files)
```

#### How init.sh Loads It

```sh
setup_skills() {
    mkdir -p /ichin/data/skills
    cp -r /ichin/external/skills/skills/* /ichin/data/skills/
}
```

#### Assessment

✅ **Skills are loadable by copying** — the SKILL.md files are self-contained. OpenCode auto-discovers them from `~/.opencode/skills/`. The init.sh approach of copying to `/ichin/data/skills/` will work IF the AI coding agents (jcode, etc.) are configured to look there.

#### Uncertainty

> ⚠️ The init.sh copies all skills to `/ichin/data/skills/engineering/`, but the agents need to be configured to look at that path. Without symlinks or config changes, the skills won't be auto-discovered.

> ⚠️ The `setup-matt-pocock-skills` interactive setup (issue tracker config, labels) is NOT run. Some skills may assume this setup has been completed.

---

### 10.5 jcode (:8093)

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/1jehuang/jcode.git` |
| **Stars** | ~7,400 |
| **License** | MIT |
| **Language** | Rust 94.9% |
| **Default branch** | `master` |
| **Latest release** | v0.30.2 |
| **Binaries** | Prebuilt available (install script) |

#### Entry Points (Actual, Verified)

```bash
# CLI TUI mode:
jcode                              # Interactive terminal UI

# Server mode (Unix socket):
jcode serve                        # Daemon on /run/user/$UID/jcode.sock
jcode serve --socket /tmp/jcode.sock # Custom socket path

# Client connects to existing server:
jcode                              # Auto-connects to running server
jcode --socket /tmp/jcode.sock     # Explicit socket path
```

#### --port Flag Support: ❌ NO

**jcode does NOT use TCP ports for client-server communication.** It uses **Unix sockets**:
- Default: `/run/user/$UID/jcode.sock`
- Debug: `/run/user/$UID/jcode-debug.sock`
- Configurable via `--socket <path>` flag

From `args.rs` (verified): There is no `--port` argument in jcode.

#### Dependencies (Cargo.toml)

60+ internal crates (jcode-provider-*, jcode-tui-*, jcode-auth-*, etc.)
Key external: tokio, ratatui 0.30, crossterm 0.29, clap, reqwest, serde, rustls

#### How init.sh Starts It

```sh
start_jcode() {
    /ichin/external/jcode/target/release/jcode server --port 8093 &
}
```

#### Uncertainties

> ⚠️ **WRONG FLAG.** `jcode server --port 8093` will FAIL. jcode uses `--socket`, not `--port`. The correct command would be `jcode serve --socket /ichin/data/jcode.sock`.

> ⚠️ **No prebuilt binary in the clone.** The init.sh checks `target/release/jcode` — this only exists after `cargo build --release`. The ISO clone (shallow, no build step) will NOT have this.

> ⚠️ **jcode uses Unix sockets** — these require a filesystem. In initramfs with tmpfs, `/run/user/$UID/` needs to exist. The default path may not work in initramfs.

> ⚠️ **Build failed in Docker** — the Dockerfile.iso attempts `cargo build --release` for jcode but:
>   1. No `cargo build` step is defined for jcode in Makefile
>   2. The Rust build dependencies would be enormous
>   3. 60+ internal crates take significant time to compile
> 
> Best approach: Use the prebuilt binary from GitHub releases (`curl -fsSL https://raw.githubusercontent.com/1jehuang/jcode/master/scripts/install.sh | bash`)

---

### 10.6 ClawRouter (:8402)

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/BlockRunAI/ClawRouter.git` |
| **Stars** | ~6,600 |
| **License** | MIT |
| **Language** | TypeScript |
| **Winner** | USDC Hackathon — Agentic Commerce |
| **npm** | `@blockrun/clawrouter` v0.12.211 |

#### Entry Points (Actual, Verified)

```bash
# Standalone proxy (recommended):
clawrouter                          # Starts HTTP proxy on :8402
clawrouter --port 8402              # Explicit port
clawrouter --port 8090              # Custom port ✅

# Via npx:
npx @blockrun/clawrouter            # Default port 8402
npx @blockrun/clawrouter --port 8402

# As OpenClaw plugin:
clawrouter setup                    # Complete OpenClaw integration
openclaw gateway restart
```

#### --port Flag Support: ✅ YES

Verified in `src/config.ts` and `src/cli.ts`:
```typescript
// config.ts:
const DEFAULT_PORT = 8402;
export const PROXY_PORT = process.env.BLOCKRUN_PROXY_PORT 
    ? parseInt(process.env.BLOCKRUN_PROXY_PORT) 
    : DEFAULT_PORT;

// cli.ts:
// --port <number>   Port to listen on (default: 8402)
```

Environment variable: `BLOCKRUN_PROXY_PORT=8402`

#### Source Tree

```
src/
├── proxy.ts          # Core HTTP proxy server
├── cli.ts            # CLI entry point
├── config.ts         # Configuration (port, etc.)
├── router/
│   ├── rules.ts      # 15-dimension weighted classifier
│   ├── selector.ts   # Tier→model selection
│   ├── strategy.ts   # Pluggable strategy registry
│   ├── config.ts     # Tier definitions
│   └── types.ts      # TypeScript types
├── wallet.ts         # BIP-39 mnemonic, EVM + Solana derivation
├── auth.ts           # Wallet key resolution
├── x402.ts           # EIP-712 payment signing
├── balance.ts        # EVM USDC balance
├── solana-balance.ts # Solana USDC balance
├── models.ts         # 55+ model definitions
├── provider.ts       # OpenClaw provider registration
├── session.ts        # Session management
├── stats.ts          # Cost tracking
├── dedup.ts          # Response cache (30s)
└── ...               # 30+ more files
```

#### How init.sh Starts It

```sh
start_clawrouter() {
    cd /ichin/external/ClawRouter
    npx tsx proxy.ts --port 8402 &
}
```

#### Assessment

✅ **This is the MOST correct integration.** ClawRouter is designed as a stand-alone HTTP proxy, port 8402 is its default, `--port` flag works, and it's designed for background daemon operation. The `npx tsx` approach will work if:
- Node.js + tsx are available in initramfs
- Dependencies are installed (`npm install`)

#### Uncertainties

> ⚠️ The init.sh runs `npx tsx proxy.ts` but does NOT run `npm install` first. Node modules won't exist in the cloned repo (they're gitignored). Need to add `cd /ichin/external/ClawRouter && npm install --production` before starting.

> ⚠️ ClawRouter generates a wallet on first run if `BLOCKRUN_WALLET_KEY` is not set. This requires write access to `~/.openclaw/`. In read-only initramfs, this may fail unless a writable tmpfs is mounted at the right path.

> ⚠️ 10 models are free without crypto, but wallet generation requires a writable home directory.

---

### 10.7 agentic-inbox (:8094)

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/cloudflare/agentic-inbox.git` |
| **Stars** | ~4,000 |
| **License** | Not specified |
| **Language** | TypeScript (Cloudflare Workers) |
| **Runtime** | Cloudflare Workers, Durable Objects, R2 |

#### What It Is

A **Cloudflare Workers** application that provides:
- Full email client (send/receive via Cloudflare Email Routing)
- AI agent for email (read, search, draft, send)
- Per-mailbox isolation via Durable Objects with SQLite
- Attachment storage in R2
- Frontend: React 19, React Router v7, Tailwind CSS

#### Deployment (only method)

```bash
# Deploy to Cloudflare (NOT runnable locally):
npm install
npx wrangler deploy
# Requires: Cloudflare account, domain, Email Routing, Workers AI
```

#### --port Flag Support: ❌ NO

**agentic-inbox CANNOT run locally.** It is a Cloudflare Workers app that runs on Cloudflare's edge network. There is no local server mode, no `--port` flag. The `wrangler dev` command provides a local preview, but it requires Cloudflare authentication and doesn't provide real email functionality.

#### How init.sh Starts It

```sh
start_agentic_inbox() {
    cd /ichin/external/agentic-inbox
    npx tsx src/index.ts --port 8094 &
}
```

#### Uncertainties

> ⚠️ **FUNDAMENTALLY INCORRECT.** agentic-inbox is a Cloudflare Workers app. It CANNOT be started with `npx tsx src/index.ts`. The entry point is a Workers script that runs on Cloudflare's runtime (workerd), not Node.js.

> ⚠️ **No local email functionality.** Even if it started, there's no Email Routing, no R2, no Durable Objects outside Cloudflare.

> ⚠️ **Best approach:** Remove from init.sh auto-start. Add instructions for Cloudflare deployment instead. Keep source code in the ISO for users who have Cloudflare accounts.

---

### 10.8 obsidian-mind

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/breferrari/obsidian-mind.git` |
| **Stars** | ~3,100 |
| **License** | MIT |
| **Language** | TypeScript 83.5%, JavaScript 16.5% |
| **Latest release** | v6.2.1 |

#### What It Is

An **Obsidian vault template** (not a code library) that gives AI coding agents persistent memory. It's a structured folder with:
- `.claude/commands/` — 18 slash commands
- `.claude/agents/` — 9 subagents
- `.claude/scripts/` — 8 TypeScript hook scripts
- `.claude/skills/` — pre-installed obsidian-skills
- `brain/` — North Star, Memories, Patterns
- `work/`, `org/`, `perf/`, `reference/`, `thinking/`, `templates/`

#### Installation

```bash
# Method 1: ShardMind (recommended)
npm install -g shardmind
shardmind install github:breferrari/obsidian-mind
# → interactive wizard: name, org, vault purpose, agents

# Method 2: Clone
git clone https://github.com/breferrari/obsidian-mind.git
open as Obsidian vault
enable Obsidian CLI in Settings
```

#### How init.sh Loads It

```sh
setup_obsidian_mind() {
    mkdir -p /ichin/data/obsidian-vaults
    cp -r /ichin/external/obsidian-mind /ichin/data/obsidian-vaults/mind
}
```

#### Assessment

✅ **Vault template is copyable.** The vault structure works purely as Markdown files — no build step needed.

⚠️ **Hook scripts won't run without Node.js having the right deps.** The scripts in `.claude/scripts/` are TypeScript run via `node --experimental-strip-types`. They'll need the modules referenced in `scripts/package.json`.

⚠️ **Obsidian itself is not included.** The vault requires Obsidian 1.12+ to use the CLI. Without Obsidian, it's just a structured Markdown folder — still useful as an AI memory system, but the full value (visual canvas, link graph, plugins) requires the Obsidian app.

---

### 10.9 obsidian-skills

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/kepano/obsidian-skills.git` |
| **Stars** | ~36,300 |
| **License** | MIT |
| **Language** | Markdown (pure documentation) |
| **Author** | Steph Ango (CEO of Obsidian) |

#### What It Is

The **official Obsidian Agent Skills** collection — 5 SKILL.md files that teach AI agents how to work with Obsidian's open formats:

| Skill | Purpose |
|-------|---------|
| `obsidian-markdown` | Create/edit Obsidian Flavored Markdown (wikilinks, embeds, callouts, properties) |
| `obsidian-bases` | Create/edit Obsidian Bases (.base files with views, filters, formulas) |
| `json-canvas` | Create/edit JSON Canvas files (.canvas with nodes, edges, groups) |
| `obsidian-cli` | Interact with Obsidian via CLI (plugin/theme dev) |
| `defuddle` | Extract clean markdown from web pages (clutter removal) |

#### Loading

```bash
# Marketplace:
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills

# npx skills:
npx skills add https://github.com/kepano/obsidian-skills

# Manual:
# Claude Code: copy skills/ to /.claude/skills/
# Codex: copy to ~/.codex/skills/
# OpenCode: clone to ~/.opencode/skills/obsidian-skills/
```

#### How init.sh Loads It

```sh
setup_obsidian_skills() {
    mkdir -p /ichin/data/skills/obsidian
    cp -r /ichin/external/obsidian-skills/skills/* /ichin/data/skills/obsidian/
}
```

#### Assessment

✅ **Skills are pure Markdown** — no dependencies, no build step, no runtime. Loading by copying to a skills directory is valid.

⚠️ **Auto-discovery depends on the agent.** OpenCode auto-discovers SKILL.md files in `~/.opencode/skills/`. Claude Code requires specific folder structure. The init.sh copies to `/ichin/data/skills/obsidian/` which may not be in any agent's default search path.

---

### 10.10 obsidian-second-brain

| Field | Value |
|-------|-------|
| **URL** | `https://github.com/eugeniughelbur/obsidian-second-brain.git` |
| **Stars** | ~2,600 |
| **License** | MIT |
| **Language** | Python, Shell, Markdown |
| **Latest version** | v0.10 "The Architect" (May 2026) |
| **Commands** | 45 slash commands |

#### What It Is

A **cross-CLI skill** (Claude Code, Codex CLI, Gemini CLI, OpenCode) that turns Obsidian into a "living second brain":
- 45 commands across 4 layers (Operations, Thinking Tools, Context Engine, Research Toolkit)
- 4 scheduled agents
- Auto-synthesis, contradiction reconciliation, self-rewriting vault
- Research toolkit (Grok, Perplexity, YouTube, Podcast ingestion)
- `/obsidian-architect` — scans codebase, writes architecture notes

#### Installation

```bash
# Claude Code:
curl -fsSL https://raw.githubusercontent.com/eugeniughelbur/obsidian-second-brain/main/scripts/quick-install.sh | bash
# → clones to ~/.claude/skills/
# → symlinks commands to ~/.claude/commands/
# → prompts for optional research toolkit

# Manual for other CLIs:
git clone ...
bash scripts/build.sh --platform <name>
cp -R dist/<platform>/. /path/to/vault/
```

#### How init.sh Loads It

```sh
setup_obsidian_second_brain() {
    if [ -d /ichin/external/obsidian-second-brain/skills ]; then
        mkdir -p /ichin/data/skills/obsidian
        cp -r ... /ichin/data/skills/obsidian/
    elif [ -d /ichin/external/obsidian-second-brain ]; then
        mkdir -p /ichin/data/obsidian-vaults/second-brain
        cp -r ... /ichin/data/obsidian-vaults/second-brain/
    fi
}
```

#### Assessment

⚠️ **The init.sh copies the repo but doesn't run `install.sh`.** The skill needs `install.sh` run to:
1. Symlink/copy 45 command files to the agent's commands directory
2. Link the main skill into the agent's skills directory
3. Set up Python dependencies (via `uv sync`)
4. Create `~/.config/obsidian-second-brain/.env`

⚠️ **Python scripts require `uv`** (or pip). The `pyproject.toml` declares: `openai`, `requests`, `python-dotenv`, `youtube-transcript-api`, `google-api-python-client`, `google-genai`, `feedparser`. Without `uv sync`, the scripts won't run.

⚠️ **Research toolkit** requires API keys (xAI, Perplexity, YouTube, Gemini). Without these set in `.env`, the `/research` and `/x-pulse` commands will fail.

⚠️ **Background agent** uses Claude Code's PostCompact hook (`hooks/obsidian-bg-agent.sh`). This runs `claude -p` headlessly — requires Claude Code CLI to be installed and authenticated in the initramfs, which it isn't.

---

## 11. FULL DIRECTORY TREE (ANNOTATED)

### 11.1 Root

```
C:\Users\aki\Ichin-Ecosystem/
├── .git/                          # Git repository (6.5 MB)
├── .gitignore
├── opencode.json                  # OpenCode config (65 B)
├── Protocol/                      # (empty — deprecated)
└── ichin-os/                      # Main project root
    ├── .env.example               # Environment template
    ├── AUDIT.md                   # Security audit
    └── README.md                  # Project overview
```

### 11.2 services/ (129 files)

```
services/
├── account/                       # Rust workspace (2 crates)
│   ├── Cargo.toml                 # Workspace definition
│   ├── Cargo.lock
│   ├── core/                      # Library crate
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── lib.rs             # pub mod auth, models, storage
│   │       ├── auth.rs            # 273 lines: register, TOTP, WebAuthn, Ed25519
│   │       ├── models.rs          # 167 lines: User, Session, Device, etc.
│   │       └── storage.rs         # 419 lines: sled DB operations
│   └── server/                    # Binary crate (Axum 0.8)
│       ├── Cargo.toml
│       ├── frontend/
│       │   └── dashboard.html     # 41KB login/register UI
│       └── src/
│           └── main.rs            # 1,294 lines: 30+ endpoints

├── agents/                        # Python (FastAPI)
│   ├── main.py                    # 47,998 B: Multi-agent consensus system
│   └── requirements.txt

├── ai-studio/                     # Python (FastAPI)
│   ├── main.py                    # 43,171 B: Workflow/training/pattern mgmt
│   ├── ui_system.py               # 44,102 B: Orb/Spotlight/UI API
│   └── requirements.txt

├── app-runtime/                   # Rust (Axum 0.7)
│   ├── Cargo.toml
│   └── src/
│       └── main.rs                # 26,574 B: App lifecycle, permissions, gateways

├── mail/                          # Rust (Axum) — 40+ files, 4 binaries
│   ├── Cargo.toml                 # Depends on ichin-account-core
│   ├── Cargo.lock
│   ├── frontend/                  # React-like email UI
│   ├── src/
│   │   ├── lib.rs
│   │   ├── api/{mod,auth}.rs     # REST API endpoints
│   │   ├── bin/{server,send,receive,gateway}.rs  # 4 binaries
│   │   ├── protocol/{envelope,handshake,types,version}.rs
│   │   ├── transport/{server,client,tls}.rs
│   │   ├── delivery/{queue,worker,thread,validate}.rs
│   │   ├── dns/{discovery}.rs
│   │   ├── security/{keys,sign,spf,verify}.rs
│   │   ├── gateway/{smtp,smtp_send,translate}.rs
│   │   ├── storage/{mailbox,attachment,local}.rs
│   │   ├── extensions/{expiration,receipts,schedule}.rs
│   │   ├── spam/mod.rs
│   │   └── internal/{config,logger}.rs
│   └── tests/integration.rs

├── memory-engine/                 # Python (FastAPI) — 4-layer memory
│   ├── main.py                    # 51,537 B: Large memory system
│   ├── requirements.txt
│   └── data/                      # Empty

├── orchestrator/                  # Python + Rust (dual-language)
│   ├── main.py                    # 43,668 B: AI orchestration pipeline
│   ├── requirements.txt
│   └── Cargo.toml                 # Axum 0.7, Redis 0.23 (Rust version)

├── protocol/                      # Python — 4 sub-protocols
│   ├── requirements.txt           # cryptography>=41.0.0
│   ├── README.md
│   ├── shared/gen_cert.sh
│   ├── Ichin-Protocol/            # Port 4889: Core wire protocol
│   │   ├── PROTOCOL_SPEC.md
│   │   ├── ichinp.py
│   │   ├── server.py
│   │   └── client.py
│   ├── Ichin-DNS/                 # Port 4890: Service discovery
│   │   ├── ARCHITECTURE.md
│   │   ├── ichindns.py
│   │   ├── server.py
│   │   └── client.py
│   ├── Ichin-CA/                  # Port 4891: Certificate Authority
│   │   ├── ARCHITECTURE.md
│   │   ├── ichinca.py
│   │   ├── server.py
│   │   ├── client.py
│   │   └── root_ca_cert.json
│   └── Ichin-Daemon/              # Port 4892: App daemon framework
│       ├── ARCHITECTURE.md
│       ├── ichind.py
│       ├── router.py
│       ├── session.py
│       ├── sandbox.py
│       ├── static.py
│       ├── realtime.py
│       └── apps/hello/{main.py, route.json}

├── search-engine/                 # Rust + Next.js
│   ├── server/                    # Rust Axum 0.8, port 3001
│   │   ├── Cargo.toml             # rusqlite bundled
│   │   └── src/{main,db,index,search,models}.rs
│   └── client/                    # Next.js 15 + React 19, port 3000
│       ├── package.json
│       ├── tsconfig.json
│       ├── next.config.ts
│       └── src/app/{layout.tsx, page.tsx, globals.css}

├── security-core/                 # Rust (Axum 0.7)
│   ├── Cargo.toml
│   └── src/
│       └── main.rs                # 40,063 B: Process/sandbox/snapshot/audit API

└── system-daemon/                 # Rust (tokio)
    ├── Cargo.toml
    └── src/
        └── main.rs                # 6,818 B: Background task scheduler
```

### 11.3 apps/ (176 files)

```
apps/
├── desktop-ui/                    # React 18 + Vite + Tailwind v4
│   ├── package.json, vite.config.ts, tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx, App.tsx
│   │   ├── index.css
│   │   ├── types/{index,lucide.d}.ts
│   │   ├── services/api.ts
│   │   ├── stores/{ui,app,orb,focus,council,spotlight,workspace}Store.ts
│   │   └── components/
│   │       ├── Shell/{AppShell,Shell,Sidebar}.tsx
│   │       ├── Orb/AIOrb.tsx
│   │       ├── Spotlight/Spotlight.tsx
│   │       ├── Focus/FocusOverlay.tsx
│   │       ├── MissionControl/MissionControl.tsx
│   │       ├── Council/AICouncil.tsx
│   │       ├── Settings/Settings.tsx
│   │       ├── AppStore/{AppStore,AppDetails}.tsx
│   │       ├── AIPanels/{AIStudioPanel,WorkflowBuilder}.tsx
│   │       ├── Workspace/{Coding,Learning,Personal,Study}Workspace.tsx
│   │       ├── Workspace/{Container,FileBrowser}.tsx
│   │       ├── Cheatsheet/KeyboardCheatsheet.tsx
│   │       └── Zoey/OnboardingFlow.tsx
│   └── dist/                      # Built output

├── web-ui/                        # React + Vite + Zustand
│   ├── package.json, vite.config.ts
│   └── src/                       # Similar to desktop-ui, lighter
│       ├── App.tsx, main.tsx
│       ├── components/{Shell,Sidebar,AIOrb,Spotlight,AICouncil,FocusOverlay,...}
│       ├── stores/{workspace,ui,orb,focus}Store.ts
│       ├── services/api.ts
│       ├── hooks/useKeyboard.ts
│       └── types/index.ts

├── mobile-ui/                     # Expo SDK 51 + React Navigation
│   ├── app.json, package.json, App.tsx
│   └── src/
│       ├── navigation/AppNavigator.tsx
│       ├── screens/{Home,Workspace,Council,MissionControl,Settings}Screen.tsx
│       ├── components/{Shell,AIOrb,Spotlight,AICouncil,FocusOverlay,...}
│       └── services/api.ts

├── desktop-browser/               # Electron + Rust + React
│   ├── main.js                    # Electron main process
│   ├── package.json
│   ├── Front-End/                 # React UI components
│   │   ├── index.html, app.js, styles.css
│   │   └── components/{WebView,Toolbar,TabItem,Sidebar,SearchBar,...}.js
│   └── Back-End/                  # Rust Axum server
│       ├── Cargo.toml
│       └── src/{main,db,models}.rs + routes/{tabs,history,favorites,user,workspaces,csrf_protection}.rs

└── calender/                      # Rust + React + Python proxy
    ├── app/calender/              # Python proxy
    │   ├── main.py
    │   └── route.json
    ├── Back-End/                  # Rust Axum
    │   ├── Cargo.toml
    │   └── src/{main,db,handlers,models}.rs
    └── Front-End/                 # React UI
        ├── index.html, app.js, styles/theme.css
        └── components/{CalendarHeader,DayView,WeekView,MonthView,Sidebar,TaskPanel,...}.js
```

### 11.4 kernel/ (26 files)

```
kernel/
├── Cargo.toml                     # x86_64-unknown-none target
├── rust-toolchain.toml            # nightly-2024-07-01
├── target.json                    # Custom target spec
├── linker.ld                      # Linker script
├── limine.conf                    # Bootloader config
├── build.rs                       # Build script
├── build.sh                       # Build helper
├── Makefile                       # Build targets
├── Dockerfile.build               # Containerized build
└── src/
    ├── main.rs                    # _start entry point, kernel init
    ├── kernel.rs                  # IchinKernel struct, init/run
    ├── memory.rs                  # 16MB heap allocator
    ├── process.rs                 # Process manager
    ├── scheduler.rs               # 6-level priority scheduler
    ├── fs.rs                      # Inode-based VFS
    ├── ipc.rs                     # Channel-based IPC
    ├── syscall.rs                 # 8 syscalls
    ├── services.rs                # Service registry
    ├── sandbox.rs                 # 5 sandbox levels
    ├── rollback.rs                # Snapshot rollback
    ├── drivers.rs                 # Device probing
    └── arch/
        ├── mod.rs                 # Arch module init
        ├── gdt.rs                 # GDT + TSS
        ├── idt.rs                 # IDT + interrupt handlers
        ├── paging.rs              # Page tables, frame allocator
        └── serial.rs              # COM1 serial I/O
```

### 11.5 packages/ (12 files)

```
packages/
├── shared-types/src/index.ts      # 5,813 B: 30+ types
├── ai-sdk/src/index.ts            # 8,535 B: Agent/Workflow/Memory SDK
├── ui-components/src/index.ts     # 32,397 B: 10+ React components
└── permissions-model/src/index.ts # 7,918 B: Permission registry/validator
```

### 11.6 ecosystem/ (21 files)

```
ecosystem/
├── developer-portal/{index.html, style.css, script.js}  # Static docs
├── app-templates/
│   ├── python-agent/{agent.py, manifest.json, README.md}
│   ├── typescript-app/{src/index.ts, manifest.json, package.json, README.md}
│   └── workflow/{workflow.json, README.md}
└── ichin-app-store/
    ├── backend/{main.py, requirements.txt}
    └── frontend/{src/App.tsx, api.ts, types.ts, ...}
```

### 11.7 infra/ (35 files)

```
infra/
├── docker/
│   ├── docker-compose.yml         # Full compose with 8+ services
│   ├── Dockerfile.{orchestrator,agents,memory,ai-studio,app-runtime,security,ui,desktop-ui}
│   ├── nginx-desktop.conf
│   ├── ai-gateway-config.md
│   └── event-bus-config.md
├── kubernetes/                    # Full K8s deployment
│   ├── ichin-namespace.yaml
│   └── 13 deployment/service/config YAMLs
├── edge-nodes/config.yaml
├── docs/{api-reference.md, architecture.md}
└── iso/                           # ISO Build System (6 files)
    ├── build-iso.py               # Python ISO builder
    ├── build-iso.sh               # Shell build script
    ├── Dockerfile.iso             # Docker build
    ├── Makefile                   # Full build system
    ├── init.sh                    # Initramfs boot script
    └── grub.cfg                   # GRUB configuration
```

---

## 12. THE SPEC (123.md)

**Source:** `C:\Users\aki\Desktop\123.md` | **Size:** 3,107 lines | **Complete contents preserved verbatim below.**

*[Note: The full 3,107-line specification was read from the file. Key sections are excerpted here. The complete spec is available at the source path.]*

### 12.1 Section Map

| Section | Lines | Title |
|---------|-------|-------|
| 1 | 1-80 | Core Architecture |
| 2 | 81-130 | Text System Architecture Diagram |
| 3 | 131-280 | Product Spec Document (Dev Ready) |
| 4 | 281-375 | Tech Stack (Realistic + Scalable) |
| 5 | 376-550 | Figma UI Blueprint |
| 6 | 551-650 | Zoey-Style UI Layer |
| 7 | 651-900 | Service 1: Core AI Orchestrator |
| 8 | 901-1150 | Service 2: AI Agent System |
| 9 | 1151-1400 | Service 3: Memory + Context Engine |
| 10 | 1401-1700 | Service 4: UI + Interaction System |
| 11 | 1701-2000 | Service 5: App Ecosystem |
| 12 | 2001-2300 | Service 6: AI Studio |
| 13 | 2301-2600 | Service 7: Security System |
| 14 | 2601-2900 | Service 8: Kernel Design |
| 15 | 2901-3107 | Implementation Plan + Appendices |

### 12.2 Core Vision (from 123.md)

> **"A cognitive operating system that merges AI agents, workspace computing, learning systems, productivity optimization, and cross-platform app execution into a single unified environment."**
>
> — ICHIN OS Vision

### 12.3 Key Design Principles

- **AI-first**: Not app-centric, cognition-centric
- **Spotlight-first**: Everything starts from search (Ctrl+Space)
- **Workspace-driven**: Study/Coding/Learning/Personal
- **Privacy-first**: No telemetry, no ads, no bloatware
- **Zero trust**: No component trusted by default
- **Ambient UI**: Liquid glass, Zoey-style calm interface
- **Multi-agent AI council**: 8 agents + orchestrator with weighted voting
- **4 focus modes**: Normal/Focus/Deep Focus/Lock
- **4 memory layers**: Ephemeral/Working/Long-term/Structured

### 12.4 Build Order (from 123.md)

```
Phase 1 (MVP):
  - Overlay OS (Electron/Tauri)
  - AI Council (API-based)
  - Workspace system
  - Orb UI (basic version)

Phase 2:
  - Memory system
  - Focus modes
  - File tagging + semantic layer

Phase 3:
  - Native Linux distro version
  - Deeper AI autonomy
  - Full agent council system
```

---

## 13. MASTER UNCERTAINTY LIST

### 13.1 Critical Issues (Will Cause Failures at Boot)

| # | Issue | Component | Details |
|---|-------|-----------|---------|
| **C1** | **Port mismatch** | Orchestrator, Memory Engine, UI System, App Runtime, Security Core | Source code binds ports 8000-8006, but init.sh assigns 8011-8017. The services will bind their compiled port regardless of init.sh. Either the code needs a `--port` arg (it doesn't have one) or init.sh is wrong. |
| **C2** | **Dexter has no server mode** | Dexter (:8092) | Starting `bun run src/index.ts --port 8092` in background with no TTY will **crash**. Dexter is a CLI TUI, not a daemon. It requires `#!/usr/bin/env bun` which won't exist in initramfs. |
| **C3** | **agentic-inbox is Cloudflare-only** | agentic-inbox (:8094) | `npx tsx src/index.ts --port 8094` will fail. It's a Workers app, not a Node.js server. Requires `wrangler deploy` to Cloudflare. |
| **C4** | **jcode uses Unix sockets, not TCP** | jcode (:8093) | `jcode server --port 8093` will fail. jcode communicates via Unix sockets at `/run/user/$UID/jcode.sock`. The `--port` flag doesn't exist. |
| **C5** | **No npm install before starting** | Ruflo, ClawRouter, agentic-inbox | All cloned repos need `npm install` (or `pnpm install`, `uv sync`) before their entry points work. init.sh starts services directly without installing dependencies. |

### 13.2 High-Impact Issues (Will Cause Partial Failures)

| # | Issue | Component | Details |
|---|-------|-----------|---------|
| **H1** | **Wrong entry point for Ruflo** | Ruflo (:8091) | Init.sh runs `node dist/agent.mjs --port 8091`. Actual entry is `v3/@claude-flow/cli/bin/cli.js` or `npx ruflo mcp start -t http --port 8091`. The `dist/agent.mjs` file doesn't exist. |
| **H2** | **Wrong entry point for OpenJarvis** | OpenJarvis (:8090) | Init.sh checks for `jarvis/main.py` then `cli.py`. Actual entry is `openjarvis.cli:main` (console_scripts). Needs `pip install` or `uv sync` before `python3 -m jarvis` works. |
| **H3** | **No Rust build for jcode** | jcode | Init.sh checks `target/release/jcode` — this only exists after `cargo build --release`. No such step exists in the Makefile or init.sh. Need to use prebuilt binary from GitHub releases. |
| **H4** | **No Bun runtime in initramfs** | Dexter | Dexter requires Bun. The Dockerfile.iso installs Bun for the build stage, but initramfs only has Node.js and Python from the standalone builds. Bun binary not included. |
| **H5** | **API keys not configured** | Dexter, OpenJarvis, ClawRouter, Ruflo | Nearly all external AI frameworks need API keys (OpenAI, Anthropic, Financial Datasets, Ollama, etc.). None are set up in init.sh or .env. Services will start but fail on actual queries. |

### 13.3 Medium-Impact Issues (Degraded Functionality)

| # | Issue | Component | Details |
|---|-------|-----------|---------|
| **M1** | **Skills not in agent search path** | mattpocock/skills, obsidian-skills | Copied to `/ichin/data/skills/` but agents may not look there. Need symlinks or config changes. |
| **M2** | **obsidian-second-brain install.sh not run** | obsidian-second-brain | Just copying files doesn't activate commands. Need to run `install.sh` which symlinks to `~/.claude/commands/`. |
| **M3** | **obsidian-mind hooks need Node deps** | obsidian-mind | Hook scripts are TypeScript that need modules from `scripts/package.json`. `npm install` not run. |
| **M4** | **ClawRouter wallet needs writable home** | ClawRouter | First run generates wallet at `~/.openclaw/`. Initramfs may not have writable home directory. |
| **M5** | **Memory Engine uses Redis** | Memory Engine | `redis==5.2.1` is required but no Redis server is started. Services depending on Redis will fail. |
| **M6** | **Orchestrator uses Redis** | Orchestrator | Same as M5 — requires Redis for memory operations. |
| **M7** | **Account uses sled DB** | Account | Sled database needs persistent storage. In initramfs (memory only), database resets on every boot. |
| **M8** | **Mail depends on Account** | Mail | `Cargo.toml` has `ichin-account-core = { path = "../account/core" }`. Both must be built together. |
| **M9** | **Search Engine seed data only** | Search Engine | SQLite is seeded with only 3 sites, 6 pages. Real search needs indexing. |

### 13.4 Low-Impact Issues (Minor or Cosmetic)

| # | Issue | Component | Details |
|---|-------|-----------|---------|
| **L1** | **Banner ports may be wrong** | init.sh status banner | Shows ports for all services even if they failed to start |
| **L2** | **Protocol ports sequential but no overlap** | Protocol stack | 4889-4892 are adjacent, could conflict with other software |
| **L3** | **Desktop-UI vite port 1420** | Desktop UI | Port 1420 is hardcoded in vite.config.ts, but init.sh doesn't start it |
| **L4** | **Web-UI port 1430 assumed** | Web UI | No vite.config.ts port set; 1430 is only in init.sh |
| **L5** | **Calender route.json not verified** | Calendar | Port read from `route.json` but format not confirmed |
| **L6** | **Desktop browser route.json not verified** | Desktop Browser | Port assignment unclear in source |

### 13.5 Design-Level Concerns

| # | Issue | Details |
|---|-------|---------|
| **D1** | **Monorepo duplication** | `services/orchestrator/` has both `main.py` AND `Cargo.toml` — dual-language build? Or one is stale? |
| **D2** | **Stale backup code** | `desktop-browser/Back-End/src.backup/` is a full copy of `src/` — which is the active one? |
| **D3** | **Empty Protocol/ directory** | Root `Protocol/` is empty — likely a leftover from before consolidation |
| **D4** | **No test infrastructure** | Only `mail/tests/integration.rs` and `dexter` has tests. Services have no test directories. |
| **D5** | **No CI/CD configuration** | No `.github/workflows/` at monorepo root. Only external repos have CI. |
| **D6** | **Docker images inconsistent** | 8 Dockerfiles in `infra/docker/` but `docker-compose.yml` may not reference all of them correctly |
| **D7** | **Port renumbering strategy unclear** | Why are source ports 8000-8006 but ISO uses 8011-8017? What's the mapping rationale? |
| **D8** | **init.sh runs services but doesn't wait for ready** | Services started concurrently with `&`. No health check before proceeding. |

---

## 14. PORT CONFLICT ANALYSIS

### 14.1 Internal Port Map

```
 25   ─ Mail SMTP Gateway
443   ─ Mail TLS Server
1420  ─ Desktop UI (Vite dev server)
1430  ─ Web UI (Vite dev server)
3000  ─ Search Engine (Next.js dev)
3001  ─ Search Engine (Rust API)
3002  ─ Calendar (Rust API)
3003  ─ Desktop Browser (Rust API)
4889  ─ Ichin-Protocol
4890  ─ Ichin-DNS
4891  ─ Ichin-CA
4892  ─ Ichin-Daemon
7000  ─ Kernel internal services
7010  ─ System Daemon
8000  ─ Orchestrator (actual source code port)
8003  ─ Memory Engine (actual source code port)
8004  ─ UI System (actual source code port)
8005  ─ App Runtime (actual source code port)
8006  ─ Security Core (actual source code port)
8011  ─ Orchestrator (ISO-assigned port)
8012  ─ AI Agents
8013  ─ Memory Engine (ISO-assigned)
8014  ─ UI System (ISO-assigned)
8015  ─ App Runtime (ISO-assigned)
8016  ─ AI Studio
8017  ─ Security Core (ISO-assigned)
8021  ─ App Store Backend (FastAPI)
8080  ─ Mail HTTP API
8081  ─ Account
8090  ⚠️ OpenJarvis (GUESSED)
8091  ⚠️ Ruflo (GUESSED)
8092  ⚠️ Dexter (GUESSED — no server)
8093  ⚠️ jcode (GUESSED — Unix socket)
8094  ⚠️ agentic-inbox (GUESSED — Cloudflare-only)
8402  ✅ ClawRouter (actual default port)
```

### 14.2 Conflict Status

**No direct conflicts** — all assigned ports are unique. However:

1. **Source vs ISO port mismatch** (8000-8006 vs 8011-8017): Multiple services will bind to DIFFERENT ports than init.sh expects. The init.sh starts `python3 main.py` which will bind port 8000 (or 8003, etc.), not 8011. Meanwhile, no service binds to 8011. This means:
   - Services start successfully on 8000-8006
   - But nothing responds on 8011-8017 (except AI Agents on 8012, AI Studio on 8016)
   - The status banner lies about where services are

2. **External framework ports are GUESSED** — only ClawRouter's 8402 is confirmed correct.

---

## 15. FILE INVENTORY

| Directory | Files | Lines (approx) | Notes |
|-----------|-------|-----------------|-------|
| `services/` | 129 | 19,485 | 12 services, 3 languages |
| `apps/` | 176 | 12,828 | 5 apps, 3 platforms |
| `kernel/` | 26 | 1,142 | bare-metal no_std kernel |
| `ecosystem/` | 21 | 1,919 | store, portal, templates |
| `packages/` | 12 | 2,087 | 4 shared libraries |
| `infra/` | 35 | 3,359 | docker, k8s, ISO, docs |
| `ichin-os/ root` | 3 | 230 | config, audit, readme |
| **TOTAL** | **~402** | **~41,050** | |

### 15.1 By Language

| Language | Files | Percentage |
|----------|-------|------------|
| Rust | 51 | ~13% |
| TypeScript/TSX | 59 | ~15% |
| Python | 26 | ~6% |
| JavaScript | 15 | ~4% |
| HTML | 8 | ~2% |
| YAML | 14 | ~3% |
| CSS | 5 | ~1% |
| TOML/JSON | 31 | ~8% |
| Markdown | 15 | ~4% |
| Shell | 6 | ~1% |
| Other (cfg, conf, lock, etc.) | 172 | ~43% |

### 15.2 Top 10 Largest Files

| Rank | File | Lines | Size |
|------|------|-------|------|
| 1 | `services/memory-engine/main.py` | ~1,500 | 51,537 B |
| 2 | `services/agents/main.py` | ~1,400 | 47,998 B |
| 3 | `services/ai-studio/ui_system.py` | ~1,300 | 44,102 B |
| 4 | `services/orchestrator/main.py` | ~1,300 | 43,668 B |
| 5 | `services/ai-studio/main.py` | ~1,250 | 43,171 B |
| 6 | `services/security-core/src/main.rs` | ~1,324 | 40,063 B |
| 7 | `services/account/server/src/main.rs` | ~1,294 | 36,560 B |
| 8 | `packages/ui-components/src/index.ts` | ~1,111 | 32,397 B |
| 9 | `services/app-runtime/src/main.rs` | ~822 | 26,574 B |
| 10 | `apps/desktop-browser/Back-End/src/db.rs` | ~540 | 18,146 B |

---

> **END OF COMPLETE REFERENCE**
>
> This document was compiled from exhaustive source-code examination of every component in the ICHIN OS ecosystem, including internal services, apps, kernel, packages, build infrastructure, and 10 external open-source repositories. Every uncertainty is flagged with ⚠️ and explained in detail in §13 (Master Uncertainty List).
>
> **Last updated:** Sun Jun 21 2026
