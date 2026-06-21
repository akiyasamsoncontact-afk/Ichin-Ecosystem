# Ichin OS Architecture

## Vision

Ichin OS is an AI-native operating system where every service works together through shared APIs, events, memory, knowledge graphs, and AI orchestration. It is not Linux with AI—it is a unified ecosystem designed for productivity, learning, studying, coding, research, creation, and personal knowledge management.

## System Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    User Interface                      │
│  Desktop Environment · Browser · Mobile · CLI · API   │
├──────────────────────────────────────────────────────┤
│                  Workspace Manager                     │
│  Study · Coding · Learning · Productivity · Research  │
├──────────────────────────────────────────────────────┤
│                 AI Orchestration Layer                 │
│  Orchestrator · Agents · Memory · Knowledge Graph     │
├──────────────────────────────────────────────────────┤
│                    Core Services                       │
│  Mail · Browser · Search · Calendar · Notes · Tasks   │
├──────────────────────────────────────────────────────┤
│                 Platform Services                      │
│  AI Router · Voice Engine · Browser Engine · Mail AI  │
│  Metasearch · Knowledge Graph · Security · App Runtime│
├──────────────────────────────────────────────────────┤
│                    System Layer                        │
│  Init · Package Manager · Protocol · Daemon · Kernel  │
└──────────────────────────────────────────────────────┘
```

## Design Principles

1. **AI-Native** — AI is not bolted on; every service has AI capabilities from the ground up
2. **Modular** — Each service is independent with well-defined APIs
3. **Local-First** — Default to offline execution; cloud only when necessary
4. **Privacy-First** — Zero Trust, encryption at rest and in transit, no data leaves without permission
5. **Unified** — One event bus, one search, one identity, one knowledge graph
6. **Keyboard-First** — Every action accessible via keyboard; Spotlight/command palette always available
7. **Secure** — Sandboxing, permissions, code signing, AI-assisted threat detection

## Service Architecture

### Service Map (Ports)

| Port | Service | Description |
|------|---------|-------------|
| 7000 | Kernel | Microkernel with IPC, process isolation |
| 8000 | Orchestrator | Central AI orchestration and routing |
| 8010 | Protocol | Ichin-Daemon, DNS, CA, Protocol |
| 8011 | Desktop UI | React/TypeScript desktop shell |
| 8012 | Agents | Multi-agent AI system (11 agents) |
| 8013 | Memory Engine | Multi-layer memory with decay |
| 8014 | App Runtime | Application execution sandbox |
| 8015 | Calendar | Calendar and scheduling service |
| 8016 | AI Studio | AI training and workflow builder |
| 8017 | Security Core | Zero Trust, encryption, auditing |
| 8020 | AI Router | 8 provider routing with failover |
| 8030 | Voice Engine | TTS/STT, personalities, AI Orb |
| 8040 | Browser Engine | Automation, page understanding |
| 8050 | AI Metasearch | 15-engine search aggregator |
| 8060 | Mail AI | Smart email processing |
| 8070 | Knowledge Graph | Concept mapping, semantic search |

### Inter-Service Communication

- **REST APIs** for synchronous requests
- **Event Bus** (Redis pub/sub) for async notifications
- **WebSocket** for real-time streaming (voice, browser)
- **Shared Memory** for high-throughput internal data
- **Eventual Consistency** for cross-service state

## Kernel Integration

Based on Linux kernel with:
- Secure Boot + UEFI + TPM
- cgroups v2, namespaces, seccomp, AppArmor
- Custom scheduler optimizations for AI workloads
- GPU acceleration via DRM and compute APIs
- Power management tuned for always-on AI services

## Boot Process

```
UEFI → Shim → GRUB → Linux Kernel → Init (systemd) →
  System Services → Desktop Environment →
  AI Services → Workspace Manager → User Session
```

Target: <10s boot on modern SSDs.

## Security Model

- **Zero Trust** — Every request authenticated and authorized
- **Sandboxing** — Every application in isolated namespace
- **Permissions** — Granular capability-based permissions
- **Encryption** — LUKS for storage, TLS for network, end-to-end for sync
- **Code Signing** — All packages signed and verified
- **AI Threat Detection** — Behavioral analysis for zero-day threats

## Developer Platform

- SDK with REST, WebSocket, GraphQL APIs
- Plugin system for extending any service
- Agent SDK for building custom AI agents
- UI component library matching Ichin design system
- `.ichinpkg` native package format with sandbox manifests

## Performance Targets

- Boot: <10s
- Idle RAM: <2GB (without AI models)
- AI inference latency: <100ms local, <500ms cloud
- Voice latency: <300ms (local), <800ms (cloud)
- Search indexing: incremental, real-time
