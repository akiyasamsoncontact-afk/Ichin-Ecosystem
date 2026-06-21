# ICHIN OS — System Architecture

## System Overview

ICHIN OS is an AI-native operating system built on a microservices architecture.
It orchestrates a constellation of 7 core services, 3 data stores, and an
event-driven communication layer to provide a unified AI-powered experience.

```
┌──────────────────────────────────────────────────────┐
│                     DESKTOP UI                        │
│              (React + TypeScript + WebSocket)         │
│                     Port 3000                          │
└────────────────────────┬─────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│                  AI GATEWAY (/ai/query)               │
│     Routes: fast → local model | deep → cloud LLM    │
└────────┬──────────┬──────────┬──────────┬────────────┘
         │          │          │          │
    ┌────▼───┐ ┌───▼────┐ ┌──▼────┐ ┌──▼──────┐
    │Orch.   │ │Agents  │ │Memory │ │AI Studio│
    │:8011   │ │:8012   │ │:8013  │ │:8016    │
    │FastAPI │ │FastAPI │ │FastAPI│ │FastAPI  │
    └────┬───┘ └───┬────┘ └──┬────┘ └──┬──────┘
         │          │          │          │
    ┌────▼───┐ ┌───▼────┐    │     ┌────▼──────┐
    │Security│ │App     │    │     │Event Bus  │
    │:8017   │ │Runtime │    │     │(NATS/Kafka│
    │Rust    │ │:8015   │    │     │ /Redis)   │
    └────────┘ │Rust    │    │     └───────────┘
               └────────┘    │
                         ┌───▼──────────┐
                         │  Data Stores  │
                         │ ┌──────────┐ │
                         │ │ Postgres │ │
                         │ │ (SQL)    │ │
                         │ ├──────────┤ │
                         │ │ Redis    │ │
                         │ │ (Cache)  │ │
                         │ ├──────────┤ │
                         │ │ Qdrant   │ │
                         │ │ (Vectors)│ │
                         │ └──────────┘ │
                         └──────────────┘
```

## Services and Responsibilities

| Service         | Port  | Language   | Responsibility                                    |
|-----------------|-------|------------|---------------------------------------------------|
| Orchestrator    | 8011  | Python     | Workflow engine, task routing, system coordinator |
| Agents          | 8012  | Python     | Agent lifecycle, tool execution, inter-agent comm |
| Memory Engine   | 8013  | Python     | Vector storage, semantic search, memory mgmt     |
| UI System       | 8014  | Python     | WebSocket gateway, session state, notifications   |
| App Runtime     | 8015  | Rust       | Sandboxed app execution, process lifecycle        |
| AI Studio       | 8016  | Python     | Model fine-tuning, prompt engineering, eval       |
| Security Core   | 8017  | Rust       | Zero-trust auth, audit, policy enforcement        |
| Redis           | 6379  | —          | Session cache, pub/sub message broker             |
| PostgreSQL      | 5432  | —          | Structured data, user accounts, metadata          |
| Qdrant          | 6333  | —          | Vector embeddings, semantic similarity search     |

## Event-Driven Architecture

Communication between services follows an event-driven pattern using
a publish-subscribe message bus (NATS by default, with Kafka and Redis
as alternatives).

```
┌─────────┐   publish    ┌───────────┐   subscribe   ┌──────────┐
│ Service ├──────────────►│ Event Bus ├──────────────►│ Service  │
│ A       │              │  (NATS)   │               │ B        │
└─────────┘              └───────────┘               └──────────┘
                               │
                         ┌─────▼──────┐
                         │ Event Log  │
                         │ (Persist)  │
                         └────────────┘
```

**Event Types:**
1. **AI_REQUEST** — AI inference request published by orchestrator
2. **AGENT_RESPONSE** — Agent completion result
3. **MEMORY_UPDATE** — Memory store/query events
4. **APP_EVENT** — Application lifecycle events
5. **WORKFLOW_TRIGGER** — Multi-step workflow progression
6. **SECURITY_ALERT** — Security policy violations
7. **UI_STATE_CHANGE** — UI synchronization events

### Why Event-Driven?
- **Decoupling**: Services don't need to know about each other
- **Resilience**: Failed consumers don't block producers
- **Scalability**: Multiple consumers can process events in parallel
- **Auditability**: Full event log for replay and debugging

## AI Integration Layer

The AI Gateway at `/ai/query` provides a single point of entry for all
AI operations. It classifies queries and routes them to the optimal
model and service based on:

| Query Type    | Route To         | Model              |
|---------------|------------------|--------------------|
| Fast/Simple   | Local Container  | phi-3-mini         |
| Reasoning     | Cloud LLM        | GPT-4 / Claude 3   |
| Coding        | AI Studio        | Claude 3 / CodeLLM |
| Memory Query  | Memory Engine    | text-embedding-ada |

Routing logic:
- `mode=fast` → local model (sub-second latency)
- `mode=balanced` → orchestrator → GPT-4o
- `mode=deep` → orchestrator → agents → Claude 3 (multi-step)

## Security Model

### Zero Trust Architecture
- Every request is authenticated, authorized, and encrypted
- No implicit trust between services (mutual TLS)
- All inter-service calls go through security-core for validation

### Sandboxing
- App Runtime executes all user applications in isolated sandboxes
- Linux namespaces + seccomp for container-grade isolation
- Resource limits enforced per process (CPU, memory, network)
- Network egress is firewalled per application manifest

### Audit
- Every system interaction is logged to the audit trail
- Logs are immutable and cryptographically signed
- Retention: 90 days hot, 1 year warm, 7 years cold storage
- Real-time alerting on anomalous patterns (SIEM integration)

### Key Security Flows
```
User Request → Auth (JWT + MFA) → Policy Check → Rate Limit
  → Sandbox (if app) → Execute → Audit Log
```

## Deployment Modes

### 1. Local OS Mode
All services run on the user's device.
- **Best for**: Privacy, offline capability, low latency
- **Requirements**: 16GB+ RAM, 50GB+ storage, GPU preferred
- **Stack**: Docker Compose or native binaries
- **Data**: Fully local, no cloud dependencies

```
[Browser] → [localhost:8011] → [all services]
                                    ↓
                              [local models]
```

### 2. Cloud Overlay Mode
All services run in Kubernetes cluster.
- **Best for**: Scalability, team collaboration, heavy AI workloads
- **Requirements**: Kubernetes cluster (min 4 nodes)
- **Stack**: Helm charts, K8s manifests
- **Data**: Managed Postgres + Qdrant + Redis

```
[User] → [ingress.ichin.ai] → [K8s services] → [cloud AI APIs]
```

### 3. Hybrid Mode (Recommended)
Local UI + cloud AI compute, with offline fallback.
- **Best for**: Responsive UI with powerful AI backend
- **Edge Node**: Desktop UI + cache + local models
- **Cloud Offload**: Heavy AI reasoning, memory search
- **Sync**: Real-time WebSocket with offline queue

```
[Edge: Desktop UI + Cache] ←→ [Cloud: K8s Services]
       ↓                              ↓
  [Local Models]              [Cloud LLMs + Vector DB]
```

## End-to-End System Flow

### Example: "Plan my study schedule for biology"

```
1. User types query in Desktop UI
2. Desktop UI sends POST /ai/query to orchestrator via nginx
3. Orchestrator classifies query (mode=deep, intent=planning)
4. Orchestrator publishes AI_REQUEST event → Agents picks it up
5. Orchestrator queries Memory Engine for user context: past study
   sessions, biology notes, preferences
6. Memory Engine returns semantic search results (previous biology
   topics, learning pace, weak areas)
7. Agents execute: search_bio_topics tool, create_timeline tool
8. Agents publish AGENT_RESPONSE with draft schedule
9. Orchestrator routes to AI Gateway for refinement (GPT-4)
10. AI Gateway returns polished study plan with sources
11. Orchestrator stores plan in Memory Engine (MEMORY_UPDATE)
12. Orchestrator returns response to Desktop UI
13. UI System broadcasts UI_STATE_CHANGE to update calendar view
14. Security Core audits the entire interaction

Total time: ~3-5 seconds (depending on model calls)
```
