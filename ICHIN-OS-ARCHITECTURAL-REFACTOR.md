# ICHIN OS — Complete Architectural Refactoring

> **Audience:** Principal Systems Architects, Security Engineers, OS Engineers  
> **Scope:** Full architectural refactoring preserving ICHIN vision while achieving production-grade readiness  
> **Status:** Proposal  
> **Date:** 2026-06-21

---

## Table of Contents

1. [Replace AI with Deterministic Software](#1-replace-ai-with-deterministic-software)
2. [Redesign the AI Agent System](#2-redesign-the-ai-agent-system)
3. [Redesign the AI Council](#3-redesign-the-ai-council)
4. [Redesign Memory](#4-redesign-memory)
5. [Introduce a Knowledge Graph](#5-introduce-a-knowledge-graph)
6. [Redesign UI Adaptation](#6-redesign-ui-adaptation)
7. [Improve Focus Mode](#7-improve-focus-mode)
8. [Create an AI Routing Layer](#8-create-an-ai-routing-layer)
9. [Introduce Strict Service Boundaries](#9-introduce-strict-service-boundaries)
10. [Create Platform Infrastructure](#10-create-platform-infrastructure)
11. [Create Search Infrastructure](#11-create-search-infrastructure)
12. [Create Sync Infrastructure](#12-create-sync-infrastructure)
13. [Create File System Architecture](#13-create-file-system-architecture)
14. [Create Notification Infrastructure](#14-create-notification-infrastructure)
15. [Create Package Management](#15-create-package-management)
16. [Create Observability](#16-create-observability)
17. [Accessibility](#17-accessibility)
18. [Networking Layer](#18-networking-layer)
19. [Security Improvements](#19-security-improvements)
20. [Developer Platform](#20-developer-platform)
21. [Performance](#21-performance)
22. [Testing](#22-testing)
23. [Deployment](#23-deployment)
24. [Output Requirements](#24-output-requirements)

---

## 1. Replace AI with Deterministic Software

### Current State

Every core service uses AI for almost everything. The Orchestrator AI-classifies every request through 8 agents. The Memory Engine uses embeddings for all queries. The UI System uses "intent detection" for every layout change. This is extremely expensive, slow, and unnecessary.

### Refactored Design

Replace AI with deterministic logic in these domains:

| Domain | Current (AI) | Replacement (Deterministic) | Service |
|--------|-------------|----------------------------|---------|
| Input classification | 8-agent voting pool | Regex + keyword trie + intent pattern matching | Orchestrator Classifier |
| Request routing | AI council vote | Configurable rule table (agent → task type map) | Orchestrator Router |
| Focus mode enforcement | AI distraction detection | Hard blocklist + allowlist + time-based rules | Focus Service |
| Notification routing | AI priority scoring | Priority queue (static rules: sender, type, workspace) | Notification Service |
| UI layout adaptation | Intent-to-UI mapping | Workspace templates + user preferences | Layout Engine |
| File indexing | Semantic embeddings | Inverted index + metadata index | Search Engine |
| System settings | AI recommendation | Heuristic + user history | Settings Service |
| Scheduling | AI calendar agent | Deterministic rule engine (cron-like) + constraint solver | Calendar Service |
| Memory decay | Embedding decay curve | Timestamp-based TTL + access count LRU | Memory Engine |
| Search ranking | Embedding similarity | TF-IDF + recency + authority + exact match boost | Search Engine |
| Agent selection | Weighted voting | Task → agent mapping table (O(1) lookup) | Agent Registry |
| Conflict resolution | Cross-agent consensus | Priority-based override (highest-confidence wins) | Decision Engine |
| Permission evaluation | AI policy reasoning | RBAC matrix (O(1) check) | Permission Engine |
| Anomaly detection | ML anomaly scoring | Rule-based heuristic + threshold alerts | Security Core |
| Workflow suggestions | Pattern mining | Frequency analysis + template matching | Workflow Engine |
| Spotlight suggestions | AI contextual | Recently used + pinned + workspace-common | Spotlight Service |
| Spam filtering | Reputation scoring (AI-like) | Bayesian filter + sender reputation DB | Mail Spam |
| Session timeout | AI behavior prediction | Fixed TTL + activity timer | Session Manager |
| Device sync conflict | AI resolution | Last-write-wins + vector clock + manual prompt | Sync Service |
| Email categorization | AI agent | Rule-based filter (sender, subject keywords, ML-lite) | Mail Filter |

### Impact

- **AI cost reduction:** ~80% of current AI calls eliminated
- **Latency reduction:** Deterministic ops in microseconds vs AI in seconds
- **Predictability:** No stochastic failures for basic operations
- **Offline resilience:** Core features work without any AI model

### Implementation

Introduce a `DecisionService` (port 8310) that acts as a pre-filter:

```
User Input → DecisionService
  ├─ Deterministic match? → Route directly (no AI)
  ├─ Needs simple AI? → Route to single agent (Level 2)
  └─ Needs Council? → Route to Orchestrator (Level 3)
```

---

## 2. Redesign the AI Agent System

### Current State

8 permanent agents (Orion/Nova/Sage/Pulse/Echo/Iris/Atlas/Aegis) implemented identically in both `services/orchestrator/main.py` (1157 lines) and `services/agents/main.py` (1240 lines). Massive code duplication. All agents loaded at all times. Each agent has redundant reasoning logic.

### Refactored Design

Three-tier hierarchical agent architecture:

```
                    ┌─────────────────────────────┐
                    │     Agent Registry (new)     │
                    │   deterministic routing map  │
                    └──────────┬──────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Core Agents  │  │Workspace Ag. │  │  Temp Agents  │
   │  (always on)  │  │(per-workspace)│  │(on-demand)    │
   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
          │                 │                  │
          ▼                 ▼                  ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ • Reasoning  │  │ • Study     │  │ • App-reg.   │
   │ • Planning   │  │ • Coding    │  │   specialist │
   │ • Execution  │  │ • Learning  │  │ • User-def.  │
   │ • Memory     │  │ • Personal  │  │ • Workflow   │
   │ • Security   │  │             │  │   agent      │
   │ • Research   │  │             │  │              │
   └──────────────┘  └──────────────┘  └──────────────┘
```

### 2.1 Core System Agents (6 total, always active)

These are the ONLY permanently running agents. Each is a lightweight Python process (~200 LOC).

| Agent | Function | Model Tier | Why Always On |
|-------|----------|-----------|---------------|
| **Reasoning** | Complex multi-step inference, tool selection, decomposition | Medium Local | Needed by all workspaces |
| **Planning** | Break goals into steps, schedule tasks, track progress | Medium Local | Continuous planning requirement |
| **Execution** | Run plans, monitor output, handle errors, retry logic | Tiny Local | Real-time feedback loop |
| **Memory** | Store/query/promote/decay, cross-session linking | Tiny Local | Every operation touches memory |
| **Security** | Validate all AI actions, sandbox enforcement, anomaly flagging | Tiny Local | Must never be offline |
| **Research** | Web searching, knowledge synthesis, source verification | Large Local / Cloud | Heavy, but foundational |

### 2.2 Workspace Agents (loaded per workspace, max 4)

Each workspace (Study/Coding/Learning/Personal) gets a lightweight specialist agent loaded **only when that workspace is active**. Agents are swapped on workspace switch (200ms async load).

| Workspace | Agent | Specialty |
|-----------|-------|-----------|
| Study | StudyAgent | Deep learning, SRS scheduling, concept mapping |
| Coding | CodingAgent | Code gen, debugging, PR review, architecture |
| Learning | LearningAgent | Skill trees, progress tracking, resource curation |
| Personal | ProductivityAgent | Task management, calendar, email triage |

### 2.3 Temporary Task Agents (on-demand, ephemeral)

Any application or workflow can register a temporary agent via API. These are micro-agents (Python AST-level, ~50 LOC) that exist only for the duration of a task and are garbage-collected after.

**Registration API:**

```rust
POST /v1/agents/register
{
  "id": "uuid",
  "workflow_id": "uuid",
  "capability": "email_summarizer",
  "max_lifetime_secs": 300,
  "entry_point": "agent_module.py::run",
  "required_tools": ["email_read", "summarize_text"]
}
```

### 2.4 Agent Manager (new service, port 8210)

**Consolidates:** Agent lifecycle, routing, health, scaling  
**Replaces:** Duplicated agent code in orchestrator + agents services  
**Language:** Rust (Axum 0.8) for performance

Responsibilities:
- Maintain agent registry (Core + Workspace + Temp)
- Route requests to correct agent tier (O(1) lookup)
- Health-check agents every 15s, restart on failure
- Scale temp agent pool based on queue depth
- API for apps to register/deregister temp agents

### 2.5 Elimination of Duplication

The current `services/agents/main.py` (1240 lines) and the agent code in `services/orchestrator/main.py` (1157 lines) are ~70% duplicated. Refactoring:

1. **`services/agents-agent-manager/`** — New Rust service (port 8210) handles all agent lifecycle
2. **`services/orchestrator/`** — Slimmed to decision routing + council convocation only (~200 lines)
3. **`services/agents/`** — Removed entirely (functionality absorbed by Agent Manager)

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Permanent agents | 8 | 6 (Core) |
| Memory per idle agent | ~150MB each | ~30MB each (Core) |
| Total idle memory | ~1.2GB | ~180MB |
| Code duplication | ~1800 lines | 0 |
| Cold boot time | ~15s agent init | ~2s Core init |
| Temp agent spawn | N/A | <50ms |

---

## 3. Redesign the AI Council

### Current State

The AI Council (all 8 agents voting) is invoked for every `POST /orchestrate` request. This means 8 agents reason on every input, consuming enormous compute and latency even for trivial tasks like "open my code workspace".

### Refactored Design

Three decision levels. The system escalates only when necessary.

```
                    User Input
                         │
                         ▼
            ┌────────────────────┐
            │  DecisionService   │
            │  (port 8310)       │
            │  ┌──────────────┐  │
            │  │ Classifier   │──┼──► Level 1: Deterministic
            │  │ (determin.) │  │         (microseconds)
            │  └──────┬───────┘  │
            │         │ needs AI │
            │         ▼          │
            │  ┌──────────────┐  │
            │  │ Complexity   │──┼──► Level 2: Single Agent
            │  │ Estimator    │  │         (milliseconds)
            │  └──────┬───────┘  │
            │         │ complex  │
            │         ▼          │
            │  ┌──────────────┐  │
            │  │ Council Flag │──┼──► Level 3: Full Council
            │  └──────────────┘  │         (seconds)
            └────────────────────┘
```

### 3.1 Level 1 — Deterministic (handles ~70% of requests)

**No AI invoked.** Pure rule-based routing and execution.

| Request Type | Handler | Max Latency |
|-------------|---------|-------------|
| Open workspace | Layout engine lookup | 5µs |
| Search local files | Inverted index query | 100µs |
| Sort tasks by date | SQL ORDER BY | 50µs |
| Set focus mode | Config write + UI push | 100µs |
| List apps | App registry query | 50µs |
| Toggle setting | Config value flip | 20µs |
| Filter notifications | Rule engine | 50µs |
| Create file | VFS create | 200µs |
| Delete temporary | VFS delete | 100µs |
| Schedule event | Calendar DB insert | 100µs |

### 3.2 Level 2 — Single Agent (handles ~25% of requests)

**One AI agent invoked.** Selected by the DecisionService based on request type.

| Request Type | Agent | Max Latency |
|-------------|-------|-------------|
| "Explain this code" | Reasoning Agent | 2-5s |
| "Summarize my notes" | Research Agent | 3-8s |
| "Draft an email" | Execution Agent | 2-4s |
| "Create study plan" | Planning Agent | 3-6s |
| "Find related papers" | Research Agent | 5-15s |
| "Debug this error" | Reasoning Agent | 3-10s |

### 3.3 Level 3 — Full Council (handles ~5% of requests)

**Multiple agents reason and vote.** Convoked only when:

| Trigger Condition | Evaluation |
|------------------|------------|
| Request confidence < 0.3 | High uncertainty |
| Security risk score > 7/10 | Needs security agent review |
| Planning scope > 5 steps | Large planning task |
| System modification requested | Config/install/uninstall |
| Multiple agents give conflicting Level 2 results | Conflict resolution |
| User explicitly requests "council" | User preference |
| Cross-workspace impact detected | Side-effect analysis |

**Council Protocol (optimized):**

1. **Parallel reasoning** — All relevant agents reason simultaneously (not sequentially)
2. **Weighted voting** — Pre-computed weights based on agent-task affinity
3. **Confidence threshold** — If max vote > 0.8, accept immediately
4. **Escalation** — If no consensus, human-in-the-loop prompt

### 3.4 DecisionService (new service, port 8310)

**Language:** Rust (Axum 0.8)  
**Purpose:** Pre-filter all requests to determine escalation level  
**Implementation:**

```rust
enum DecisionLevel {
    Deterministic,   // Level 1 — no AI
    SingleAgent,     // Level 2 — one agent
    FullCouncil,     // Level 3 — multi-agent vote
}

struct DecisionService {
    classifier: RegexTrieClassifier,   // O(n) pattern matching
    complexity: ComplexityEstimator,   // Token count + dependency graph
    router: AgentRouter,               // Task type → agent ID
}
```

### Impact

| Metric | Before | After |
|--------|--------|-------|
| AI invocations per request | 8 (all agents) | 0 (70%), 1 (25%), 8 (5%) |
| Average latency | ~8s | ~200ms (weighted) |
| AI cost (relative) | 100% | ~12% |
| Power usage | High (all agents) | Low (rare council) |

---

## 4. Redesign Memory

### Current State

4-layer memory (Ephemeral → Working → Long-term → Structured) with:
- Linear decay (30-day half-life on embeddings)
- Simple importance scoring
- No automatic deduplication/consolidation
- Raw event storage grows unbounded

### Refactored Design

Six-level memory hierarchy with automatic decay, strengthening, and consolidation:

```
Raw Events (time-series log)
    │ TTL: 24h, then consolidated
    ▼
Session Memory (active context)
    │ TTL: session duration, then summarized
    ▼
Working Memory (short-term)
    │ TTL: 7 days, promoted if accessed >3x
    ▼
Long-term Knowledge (persistent)
    │ Consolidated monthly, weakened if untouched >90d
    ▼
Behavior Patterns (learned)
    │ Updated weekly, decay if behavior changes
    ▼
Core Identity (user genome)
    │ Never deleted, versioned
```

### 4.1 Memory Decay Algorithm

Replace the current "30-day half-life on embeddings" with a production-grade decay:

```
score(t) = base_score × access_count × 2^(-t / half_life)

Where:
  - base_score: initial importance (1-10) assigned by creator context
  - access_count: number of times recalled (capped at 100)
  - half_life:
    • Raw Events: 1 hour
    • Session Memory: 24 hours
    • Working Memory: 7 days
    • Long-term: 365 days
    • Behavior Patterns: 180 days
    • Core Identity: ∞ (never decays)

Consolidation triggers:
  - When avg score of layer < 0.3 → consolidate to next layer
  - When total items in layer > threshold → prune lowest-scored 20%
```

### 4.2 Memory Service Consolidation

**Current:** `services/memory-engine/main.py` (1316 lines) — all 4 layers in one file  
**Refactored:**

| Module | Responsibility | Port |
|--------|---------------|------|
| `memory-ingester` | Raw event ingestion, buffering, batching | Internal |
| `memory-store` | CRUD on all 6 layers, decay engine | 8013 (unchanged) |
| `memory-consolidator` | Background consolidation, summary generation, pruning | Internal |
| `memory-query` | Multi-layer search, context assembly, token budget | Internal |
| `memory-graph` | Entity/relationship extraction and knowledge graph sync | Internal |

### 4.3 Context Assembly Pipeline

Current: Single `POST /context/build` endpoint with simple concatenation  
Refactored:

```
Request + Workspace
    │
    ▼
┌─────────────────────────────────────┐
│ Context Builder                     │
│ 1. Fetch Recent (session memory)    │
│ 2. Fetch Relevant (vector search)   │
│ 3. Fetch Graph (knowledge graph)    │
│ 4. Fetch Structured (database)      │
│ 5. Rank by Recency × Relevance      │
│ 6. Token Budget Manager             │
│    - Allocate: 40% recent, 30% rel, │
│                20% graph, 10% struct│
│    - If over budget: truncate low   │
│      priority items                 │
│ 7. Assemble Context Packet          │
└─────────────────────────────────────┘
    │
    ▼
Context Packet → Agent (max 8K tokens, configurable)
```

### 4.4 Meaning Extraction (New)

Replace "store everything" with "store meaning":

```
Raw Log Entry
    │
    ▼
Meaning Extractor (background worker, batch every 60s)
    ├─ Entity extraction (person, place, concept, project)
    ├─ Relationship extraction (X relates to Y via Z)
    ├─ Importance scoring (is this worth keeping?)
    ├─ Deduplication (is this a duplicate of existing memory?)
    └─ Contradiction detection (does this conflict with existing?)
    │
    ▼
Knowledge Graph Update + Memory Store
```

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Memory layers | 4 | 6 |
| Max raw event retention | Forever | 24h |
| Long-term storage growth | ~1GB/month/user | ~50MB/month/user |
| Context assembly latency | ~500ms | ~100ms |
| Query relevance (est.) | 60% | 85%+ |

---

## 5. Introduce a Knowledge Graph

### Current State

The Memory Engine uses only 128-dimensional embedding vectors for all retrieval. No structured knowledge representation. No entity resolution. No relationship tracking.

### Refactored Design

Multi-modal retrieval combining four methods:

```
                    ┌─────────────────────┐
                    │   Query Router      │
                    │ (query type → strat)│
                    └──┬──────┬──────┬───┘
                       │      │      │
         ┌─────────────┼──────┼──────┼─────────────┐
         ▼             ▼      ▼      ▼             ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
   │  Vector  │ │Knowledge │ │ Keyword  │ │Structured│
   │  Search  │ │  Graph   │ │  Search  │ │Database  │
   │(Qdrant)  │ │(Neo4j)   │ │(Tantivy) │ │(Postgres)│
   └──────────┘ └──────────┘ └──────────┘ └──────────┘
         │             │            │            │
         └─────────────┴────────────┴────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Fusion Engine │
              │  (reciprocal   │
              │   rank fusion) │
              └────────────────┘
                       │
                       ▼
                  Final Results
```

### 5.1 Seven Sub-Graphs

The Knowledge Graph (runs on embedded `redb` or optional Neo4j) contains:

| Graph | Nodes | Edges | Purpose |
|-------|-------|-------|---------|
| **Entity Graph** | People, places, orgs, concepts | `related_to`, `part_of`, `opposes` | Core knowledge representation |
| **Relationship Graph** | Pairs of entities | Relationship types | Explicit relationship mapping |
| **Workspace Graph** | Files, apps, notes, configs | `contains`, `used_in`, `linked_to` | Workspace structure |
| **Learning Graph** | Skills, topics, resources | `prerequisite`, `teaches`, `extends` | Learning path tracking |
| **Project Graph** | Tasks, milestones, dependencies | `blocks`, `depends_on`, `subtask_of` | Project management |
| **Task Graph** | Actions, contexts, outcomes | `triggered_by`, `results_in` | Task execution history |
| **Concept Graph** | Abstract ideas, principles | `generalizes`, `specializes`, `contradicts` | Deep understanding |

### 5.2 Query Router

```
Query Type            Strategy
─────────────────────────────────────────────────
"What is X?"          Entity Graph + Vector
"How does X work?"    Concept Graph + Vector
"Find files about X"  Workspace Graph + Keyword
"Related to Y"        Entity Graph + Relationship
"What do I know?"     All graphs + Summaries
"Plan Z"              Project Graph + Task Graph
"Learn X"             Learning Graph + Concept Graph
"Summary of work"     Temporal + Task Graph + Entity
```

### 5.3 Knowledge Graph Service (new, port 8320)

**Language:** Rust (Axum 0.8)  
**Backend:** `redb` (embedded, no external dependency) with optional Neo4j for cloud  
**Functions:**
- Entity CRUD with resolution (merge duplicates)
- Relationship CRUD with weight + direction
- Graph traversal (BFS, shortest path, subgraph extraction)
- Query routing to correct sub-graph
- Bidirectional sync with Memory Engine

### Impact

| Metric | Embeddings Only | + Knowledge Graph |
|--------|----------------|-------------------|
| Query accuracy (est.) | ~60% | ~90%+ |
| Cold start problem | Severe | None (structure first) |
| Storage per user | ~500MB vectors | +50MB graph |
| Query latency | ~50ms | ~80ms (all 4 methods) |
| Training requirement | Large | Minimal |

---

## 6. Redesign UI Adaptation

### Current State

The UI System (`services/ai-studio/ui_system.py`, 1112 lines) uses "intent detection" (AI) for every workspace and focus change. Ambient behavior auto-collapses panels after 30s idle, fully hides after 120s — disrupting muscle memory.

### Refactored Design

Three stability tiers, enforced in order:

```
1. Layout Stability    (MUST be predictable)
2. Adaptive Personalization  (MAY auto-adapt)
3. AI Suggestions      (SHOULD ask first)
```

### 6.1 Layout Stability Rules

| Rule | Enforcement |
|------|------------|
| Workspace layout never changes without user action | Hard — panels cannot auto-rearrange |
| Spotlight position is fixed (Ctrl+Space) | Hard — no AI relocation |
| Keyboard shortcuts are invariant | Hard — system-wide, not context-dependent |
| Orb position is configurable but never auto-moves | Hard — user sets once |
| Panel open/close is always user-initiated | Hard — no auto-show/hide |
| Transitions ≤300ms for direct actions | Performance target |

### 6.2 Adaptive Personalization (May Auto-Adapt)

| Adaptation | Trigger | Requires Approval? |
|-----------|---------|-------------------|
| Most-used panel opens faster | After 10+ uses | No (minor) |
| Least-used panel moves down in list | After 30+ days unused | No (minor) |
| Spotlight shows recent files first | Usage pattern | No (minor) |
| Workspace wallpaper matches time of day | Time-based | Yes (first time only) |
| Font size adjusts for reading | Screen time >2hr continuous | Yes (prompt) |
| Sidebar groups reorder by frequency | Weekly analysis | Yes (weekly digest) |

### 6.3 AI Suggestions (Must Ask First)

| Suggestion | Prompt Type | Frequency |
|-----------|-------------|-----------|
| "Switch to Focus mode?" | Toast with 5s timeout | Max 1/hr |
| "Enable Deep Focus for this task?" | Spotlight notification | Max 1/session |
| "Move project panel to Coding workspace?" | Dialog with preview | Max 1/day |
| "Create shortcut for this action?" | One-click prompt | When action repeated 5x |

### 6.4 Ambient Behavior (Revised)

Replace the current aggressive auto-collapse:

| Idle Time | Before (Current) | After (Refactored) |
|-----------|------------------|-------------------|
| 30s | Panels auto-collapse | Dim panels by 20% (configurable) |
| 120s | Panels fully hidden | Dim by 50%, reduce glow |
| 300s | — | Dim by 80%, minimal UI |
| Any | — | On user input: 200ms restore animation |
| 30min | — | Screen dim (power saving) |

### 6.5 UI System Refactoring

**Current:** `services/ai-studio/ui_system.py` (1112 lines) — monolithic  
**Refactored:**

| Component | Lines | Responsibility |
|-----------|-------|---------------|
| Layout Engine | 150 | Workspace layout management |
| Focus Controller | 100 | Focus mode enforcement |
| Orb Manager | 80 | AI Orb state + notifications |
| Ambient Controller | 60 | Idle dimming + transitions |
| Spotlight Service | 120 | Search + commands + suggestions |
| Component Registry | 40 | Z-index + component lifecycle |
| Intent Handler | 50 | Route intents to deterministic handlers |

### Impact

| Metric | Before | After |
|--------|--------|-------|
| AI usage per UI event | 1 intent detection | 0 (all deterministic) |
| Unwanted layout changes | Frequent | None |
| Muscle memory breaks | High | None |
| Panel auto-collapse frustration | High | Resolved (dim only) |
| Cold boot to usable UI | ~5s | ~500ms |

---

## 7. Improve Focus Mode

### Current State

4 modes (Normal/Focus/Deep Focus/Lock) with blanket blocking. Focus mode blocks ALL notifications. Deep Focus blocks EVERYTHING. No per-workspace configuration. No graduated intervention.

### Refactored Design

Five intervention levels, independently configurable per workspace:

```
Passive      ─►  Suggest       ─►  Strong      ─►  Strict      ─►  Lock
(monitor)        (recommend)       (nudge)         (enforce)        (maximum)
```

### 7.1 Intervention Levels

| Level | Notifications | Distractions | App Access | AI Suggestions | Visual |
|-------|--------------|--------------|------------|----------------|--------|
| **Passive** | Show all | Track but allow | Full | Normal | Normal |
| **Suggest** | Show with delay | Toast warnings | Full | Reduced | Subtle dim |
| **Strong** | Silent stack | Auto-dismiss after 5s | Non-essential blocked | Minimal | Dim + glow |
| **Strict** | Block all | Block all | Workspace apps only | Blocked | Dark + no glow |
| **Lock** | Block all | Block all | 1 active app only | Blocked | Zen mode |

### 7.2 Per-Workspace Configuration

Each workspace can set its own focus profile:

```json
{
  "study": {
    "intervention": "strict",
    "allowed_apps": ["pdf-viewer", "anki", "notion"],
    "allowed_notifications": ["emergency"],
    "schedule": { "mon-fri": "09:00-12:00", "auto": true }
  },
  "coding": {
    "intervention": "suggest",
    "allowed_apps": ["vscode", "terminal", "browser-dev"],
    "allowed_notifications": ["build-complete", "deploy-status"],
    "schedule": null
  }
}
```

### 7.3 Focus Controller Service (port 8220)

**Language:** Rust (Axum 0.8)  
**Replaces:** Focus mode logic in `ui_system.py`  
**Responsibilities:**
- Enforce intervention level at system level (not just UI)
- Intercept notification delivery, block/queue based on level
- Manage app allowlist/blocklist per workspace
- Handle scheduled auto-switching
- API for apps to check current focus level

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Focus modes | 4 | 5 (graduated) |
| Configurable per workspace | No | Yes |
| User control | Blunt on/off | Fine-grained |
| Notification granularity | All/nothing | 5 levels |
| Scheduled auto-focus | No | Yes |

---

## 8. Create an AI Routing Layer

### Current State

No intelligent model selection. The Orchestrator always uses the same model/agent for all requests. Edge config supports `phi-3-mini` and `tinyllama` but routing is static.

### Refactored Design

Six-tier AI routing with automatic selection based on cost, latency, privacy, and complexity:

```
                     ┌─────────────────┐
                     │  AI Router      │
                     │  (port 8330)    │
                     └────────┬────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Model Pool  │    │  Routing Policy  │    │  Cost Tracker    │
│  (backends)  │    │  (rule engine)   │    │  (budget mgmt)   │
└──────┬───────┘    └──────────────────┘    └──────────────────┘
       │
       ├─────────────────────────────────────────────────────┐
       │                                                     │
       ▼                                                     ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│Tiny Local   │  │Medium Local │  │Large Local  │  │Cloud LLM    │
│(500M params)│  │(3B params)  │  │(7B params)  │  │(GPT-4o,     │
│             │  │             │  │             │  │ Claude, etc)│
│Use: classify,│  │Use: reason, │  │Use: complex │  │Use: creative │
│extract,      │  │plan,        │  │analysis,    │  │writing,     │
│route         │  │summarize    │  │code gen     │  │research     │
└──────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
                                                          │
                                                          ▼
                                                 ┌──────────────────┐
                                                 │ Specialized APIs │
                                                 │ (Wolfram Alpha,  │
                                                 │  GitHub Copilot, │
                                                 │  Perplexity, etc)│
                                                 └──────────────────┘
```

### 8.1 Routing Decision Matrix

| Task Type | Tiny Local | Medium Local | Large Local | Cloud LLM | Specialized |
|-----------|-----------|-------------|-------------|-----------|-------------|
| Input classification | ✅ | — | — | — | — |
| Entity extraction | ✅ | — | — | — | — |
| Simple Q&A | ✅ | — | — | — | — |
| Summarization | — | ✅ | — | — | — |
| Code completion | — | ✅ | — | — | — |
| Planning | — | ✅ | ✅ | — | — |
| Complex reasoning | — | — | ✅ | — | — |
| Code generation (complex) | — | — | ✅ | — | — |
| Creative writing | — | — | — | ✅ | — |
| Web research | — | — | — | ✅ | — |
| Image generation | — | — | — | ✅ | — |
| Math computation | — | — | — | — | ✅ |
| Code search | — | — | — | — | ✅ |
| Translation | — | — | ✅ | ✅ | — |

### 8.2 AI Router Service (new, port 8330)

**Language:** Rust (Axum 0.8)  
**Purpose:** Intelligent model selection, request routing, cost management

```rust
struct AIRouter {
    models: Vec<ModelEndpoint>,
    policy: RoutingPolicy,        // cost, latency, privacy, or balanced
    cost_tracker: CostBudget,     // monthly token budget tracking
    cache: ResponseCache,         // LRU cache for deterministic outputs
}

enum RoutingPolicy {
    CostOptimized,    // cheapest model that meets requirements
    LatencyOptimized, // fastest model that meets requirements
    PrivacyFirst,     // local models only, no cloud
    QualityFirst,     // best model regardless of cost
    Balanced,         // default: weighted score
}
```

### 8.3 Cost & Privacy Controls

| Setting | Effect |
|---------|--------|
| `ai_routing.policy: "privacy_first"` | Never sends data to cloud APIs |
| `ai_routing.max_monthly_cost: 10.00` | Hard budget cap in USD |
| `ai_routing.offline_mode: true` | Local models only |
| `ai_routing.preferred_provider: "ollama"` | Preferred local runtime |

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Cloud AI cost | 100% (all requests) | ~15% (complex only) |
| Offline capability | None | Full (local models) |
| Average latency (simple tasks) | ~5s | ~100ms (tiny local) |
| Privacy | Always sends to cloud | 70% local-only |
| Monthly cost/user (est.) | ~$20 | ~$3 |

---

## 9. Introduce Strict Service Boundaries

### Current State

Services communicate via HTTP/REST but with several violations:
- `services/mail/Cargo.toml` depends directly on `services/account/core` (crate dependency, not API)
- No authentication between services
- Some services share mutable state
- Event bus is documented but not implemented

### Refactored Design

Every service communicates ONLY through APIs. No direct database access, no shared mutable state, no service bypass.

### 9.1 Communication Rules

| Rule | Enforcement |
|------|------------|
| No service may import another service's code | CI lint — only allowed for shared types packages |
| All inter-service communication via REST/gRPC | NetworkPolicy (K8s) + internal TLS |
| No service may access another service's database | Separate DB per service (or schema with RLS) |
| All state changes published as events | Event bus (NATS/Redis Streams) |
| No synchronous blocking chains >3 deep | Async with eventual consistency |

### 9.2 Event Bus Architecture

**Replace** the documented-but-unimplemented event bus with NATS (or embedded Redis Streams):

```
Service A ──► Event Bus ──► Service B
  │                               │
  │  ┌──── Publish ────┐          │
  │  │                 │          │
  ▼  ▼                 ▼          ▼
┌──────────────┐  ┌──────────────┐
│ Event Types  │  │ Handlers     │
├──────────────┤  ├──────────────┤
│ ai.request   │  │ Orchestrator │
│ memory.write │  │ Memory Engine│
│ app.install  │  │ App Runtime  │
│ security.alert│  │ Security Core│
│ ui.state     │  │ UI System    │
│ focus.change │  │ Focus Ctrl   │
│ file.event   │  │ VFS          │
│ config.set   │  │ Config Store │
│ sync.trigger │  │ Sync Service │
└──────────────┘  └──────────────┘
```

### 9.3 Service Mesh Authentication

Every inter-service request requires:

```
Header: X-Ichin-Service: <service-name>
Header: X-Ichin-Timestamp: <unix-ms>
Header: X-Ichin-Signature: <ed25519-sig(service-name + timestamp + body)>
```

Each service has an Ed25519 keypair. Signatures verified by receiving service. Keys rotated daily.

### 9.4 Dependency Resolution

**Current violations to fix:**
1. `services/mail` depends on `services/account/core` — mail should call account API (port 8081)
2. `services/orchestrator` directly imports agent code — should call agent-manager API (port 8210)
3. `services/agents` duplicates orchestrator agent code — removed entirely
4. Shared database access — enforce per-service schemas in Postgres

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Cross-service coupling | Tight (direct crate deps) | Loose (API only) |
| Authentication | None | Ed25519 per-request |
| State sharing | Mutable shared state | Event-driven |
| Failure isolation | Cascading | Bounded (circuit breakers) |
| Testing difficulty | High (entangled services) | Low (mock APIs) |

---

## 10. Create Platform Infrastructure

### Current State

- Account service exists (port 8081) with basic auth (WebAuthn, TOTP, Ed25519)
- No central identity service
- No device registry
- No session management (separate per service)
- No organization support
- No permission engine (app runtime has basic perms)

### Refactored Design

Platform Infrastructure as a set of foundational services:

```
                    ┌─────────────────────────────────────┐
                    │        Identity Service             │
                    │        (port 8100)                  │
                    │  ┌─────────┐ ┌──────────┐ ┌──────┐ │
                    │  │  AuthN  │ │  AuthZ   │ │Users │ │
                    │  │WebAuthn │ │RBAC/ABAC │ │Orgs  │ │
                    │  │TOTP     │ │Policies  │ │Groups│ │
                    │  │Passkeys │ │Audit     │ │Roles │ │
                    │  └─────────┘ └──────────┘ └──────┘ │
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐          ┌──────────────────┐       ┌──────────────────┐
│Device Registry│          │Session Manager   │       │Permission Engine │
│(port 8101)   │          │(port 8102)       │       │(port 8103)       │
├──────────────┤          ├──────────────────┤       ├──────────────────┤
│ • Device CRUD│          │ • Token issue     │       │ • RBAC matrix   │
│ • Trust level│          │ • Refresh/revoke  │       │ • Policy eval   │
│ • Fingerprint│          │ • Multi-device    │       │ • OPA-like      │
│ • Push tokens│          │ • Concurrent lim  │       │ • Audit log     │
└──────────────┘          └──────────────────┘       └──────────────────┘
```

### 10.1 Identity Service (port 8100) — Rust/Axum

| Feature | Detail |
|---------|--------|
| Authentication | WebAuthn (passkeys), TOTP (backup codes), hardware keys (YubiKey), password (fallback, bcrypt) |
| Authorization | RBAC (role-based) + ABAC (attribute-based) — evaluated via OPA-like policy engine |
| User management | Register, profile, preferences, SSH keys, API tokens |
| Organization | Multi-tenant orgs with team/project hierarchy |
| Federation | OpenID Connect provider (optional) |
| Audit | All auth events logged to immutable audit store |

### 10.2 Device Registry (port 8101) — Rust/Axum

| Feature | Detail |
|---------|--------|
| Device CRUD | Register, list, update, revoke |
| Trust scoring | Recent auth, geolocation match, device fingerprint |
| Push tokens | FCM/APNs for mobile notifications |
| Concurrent limit | Max N devices per user (default 10) |
| Remote wipe | Trigger device data deletion |

### 10.3 Session Manager (port 8102) — Rust/Axum

| Feature | Detail |
|---------|--------|
| Token format | PASETO (not JWT — more secure, no None algorithm) |
| Refresh flow | 15min access + 7-day refresh tokens |
| Revocation | Server-side revoke list (bloom filter for perf) |
| Multi-device | One session per device, concurrent sessions tracked |
| Timeout | Activity-based (30min idle) + absolute (24h max) |

### 10.4 Permission Engine (port 8103) — Rust/Axum

**Replaces** `packages/permissions-model/` (TypeScript, 282 lines) with a proper service:

```rust
struct PermissionEngine {
    policies: Vec<Policy>,     // stored in sled/redb
    cache: LruCache<String, bool>,  // 10K entry LRU
}

struct Policy {
    id: Uuid,
    effect: Effect,            // Allow | Deny
    actions: Vec<String>,      // ["file:read", "app:install"]
    resources: Vec<String>,    // ["workspace:study/*", "app:code-forge"]
    principals: Vec<String>,   // ["role:admin", "user:uuid"]
    conditions: Vec<Condition>, // time, location, device trust
}
```

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Central identity | Account service (basic) | Full Identity Service |
| Device management | None | Device Registry (port 8101) |
| Session management | Per-service ad hoc | Central Session Manager |
| Permission evaluation | JS package (in-browser only) | Server-side engine (consistent) |
| Organization support | None | Multi-tenant |
| Federation | None | OpenID Connect |
| Auth token format | (none) | PASETO |

---

## 11. Create Search Infrastructure

### Current State

Single search engine (`services/search-engine/`, Rust + Next.js, port 3001) with basic inverted index and multi-factor ranking. No semantic search, no cross-service search, no caching.

### Refactored Design

Unified search infrastructure:

```
                    ┌────────────────────────────────────┐
                    │         Search Gateway             │
                    │         (port 8340)                │
                    │  Unified query API + routing       │
                    └──────┬─────────────────────┬───────┘
                           │                     │
            ┌──────────────┼─────────────────────┼──────────────┐
            │              │                     │              │
            ▼              ▼                     ▼              ▼
    ┌────────────┐ ┌────────────┐ ┌────────────────┐ ┌────────────────┐
    │File Indexer│ │Semantic    │ │Keyword Search  │ │Ranking Engine  │
    │(port 8341) │ │Search      │ │(port 8343)     │ │(port 8344)     │
    │            │ │(port 8342) │ │                │ │                │
    │• File walk │ │• Embedding │ │• Inverted idx  │ │• Multi-factor  │
    │• Metadata  │ │• Vector DB │ │• TF-IDF        │ │• Personal boost│
    │• Git-aware │ │• Hybrid    │ │• Fuzzy match   │ │• Learning rank │
    │• Real-time │ │  search    │ │• Autocomplete  │ │• Freshness     │
    └────────────┘ └────────────┘ └────────────────┘ └────────────────┘
                           │
                           ▼
                    ┌────────────────────────────────────┐
                    │            Cache Layer              │
                    │  (Redis, 5min TTL, invalidate on   │
                    │   write, 80% hit rate target)      │
                    └────────────────────────────────────┘
```

### 11.1 Search Types

| Search Type | Backend | Latency | Use Case |
|------------|---------|---------|----------|
| File name | File Indexer | 5ms | Quick file lookup |
| File content | Keyword Search | 20ms | In-file text search |
| Semantic | Vector Search | 50ms | "Documents about X concept" |
| Cross-workspace | All indices | 100ms | "Everything I know about Y" |
| Memory | Memory Engine query | 50ms | "What did I learn about Z?" |
| Knowledge | Knowledge Graph | 30ms | "How does A relate to B?" |
| Code | Code-aware index | 20ms | Function/class/variable search |
| Universal | Fusion (all) | 200ms | "Find everything related to X" |

### 11.2 Ranking Engine (port 8344)

Multi-factor ranking replaces the current simple scoring:

```
score = 0.3 × keyword_relevance
      + 0.2 × semantic_similarity
      + 0.2 × recency_factor (log decay, 30-day half-life)
      + 0.1 × authority_score (access count, user rating)
      + 0.1 × personal_boost (workspace match, past clicks)
      + 0.1 × exact_match_bonus
```

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Search types | 1 (inverted index) | 8 |
| Average latency | ~100ms | ~30ms (cached) |
| Cache | None | Redis (80% hit rate) |
| Cross-service search | No | Yes (Search Gateway) |
| Ranking factors | 5 (hardcoded) | 6 (configurable) |
| Autocomplete | No | Yes (prefix trie) |

---

## 12. Create Sync Infrastructure

### Current State

No sync infrastructure. Each service manages its own data with no cross-device synchronization. The browser app has a "sync" concept but it's not implemented.

### Refactored Design

Unified sync service (port 8350):

```
                    ┌─────────────────────────────────────┐
                    │         Sync Service                │
                    │         (port 8350)                 │
                    │  Rust/Axum + CRDT + Vector Clocks   │
                    └──────┬──────────────────────┬───────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐      ┌────────────────┐
                    │  Local Sync  │      │  Cloud Sync    │
                    │  (LAN P2P)   │      │  (central srv) │
                    └──────────────┘      └────────────────┘
                           │                      │
                           ▼                      ▼
                    ┌─────────────────────────────────────┐
                    │         Conflict Resolution         │
                    │  ┌───────────┐ ┌──────────────────┐ │
                    │  │Automated  │ │Manual (UI prompt)│ │
                    │  │Last-write │ │3-way merge       │ │
                    │  │wins (90%) │ │diff view (10%)   │ │
                    │  └───────────┘ └──────────────────┘ │
                    └─────────────────────────────────────┘
```

### 12.1 Sync Capabilities

| Feature | Detail |
|---------|--------|
| **Offline mode** | Local-first architecture. Writes go to local DB first, sync in background |
| **Conflict resolution** | CRDT for collaborative data (notes, lists). LWW for settings. Manual merge for documents |
| **Delta synchronization** | Only changed bytes sent (rsync-like rolling hash) |
| **Encrypted sync** | End-to-end encrypted (XChaCha20-Poly1305). Server has zero knowledge |
| **Background sync** | Sync runs when network available. Exponential backoff on failure (1s, 10s, 60s, 300s, max 1hr) |
| **Multi-device** | Unlimited devices. Device registry manages trust |

### 12.2 Data Types Synced

| Data | Sync Strategy | Priority |
|------|--------------|----------|
| Workspace configs | LWW | High |
| Notes/markdown | CRDT | High |
| Tasks | CRDT | High |
| Settings | LWW | Medium |
| Bookmarks | LWW | Medium |
| Browser history | Append-only | Low |
| Focus schedules | LWW | Medium |
| Agent preferences | LWW | Low |
| Memory (session) | Local only | None |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Offline mode | None | Full local-first |
| Multi-device sync | None | All devices |
| Conflict resolution | N/A | CRDT + manual |
| Bandwidth efficiency | N/A | Delta sync |
| E2E encryption | N/A | XChaCha20 |

---

## 13. Create File System Architecture

### Current State

Kernel VFS (`kernel/src/fs.rs`, 106 lines) is a simple inode-based tree with `/dev`, `/proc`, `/sys`, `/tmp`, `/home`. No AI metadata, no versioning, no virtual files.

### Refactored Design

Layered file system:

```
                    ┌─────────────────────────────────────┐
                    │     Virtual File System (VFS)       │
                    │  (kernel + userspace FUSE layer)    │
                    └──────┬──────────────────────┬───────┘
                           │                      │
              ┌────────────┼──────────────────────┼────────────┐
              │            │                      │            │
              ▼            ▼                      ▼            ▼
    ┌────────────┐ ┌────────────┐ ┌────────────────┐ ┌────────────┐
    │Physical FS │ │Versioning  │ │AI Metadata FS  │ │Virtual FS  │
    │(ext4/btrfs)│ │(port 8360) │ │(port 8361)     │ │(port 8362) │
    │           │ │           │ │                │ │           │
    │• Block dev│ │• Snapshots│ │• Tags/entities │ │• Workspace│
    │• Partitions│ │• History  │ │• Summaries     │ │  links    │
    │• Encryption│ │• Diff     │ │• Relationships │ │• Search   │
    │           │ │• Rollback │ │• Priority      │ │  results  │
    └────────────┘ └────────────┘ └────────────────┘ └────────────┘
```

### 13.1 AI Metadata Filesystem (FUSE, port 8361)

Every file gets an associated `.ichin` metadata file (hidden, stored alongside or in sidecar DB):

```json
// file: notes/project-idea.md
// metadata: .ichin/notes/project-idea.md.ichin
{
  "tags": ["project", "idea", "architecture"],
  "entities": ["ICHIN", "microkernel"],
  "summary": "Proposal to redesign the IPC system",
  "importance": 0.85,
  "workspace": "coding",
  "relationships": [
    {"type": "related_to", "target": "/docs/architecture.md", "weight": 0.9}
  ],
  "versions": 3,
  "last_accessed": "2026-06-21T10:30:00Z",
  "access_count": 12
}
```

### 13.2 Filesystem Operations

| Operation | VFS Layer | Description |
|-----------|-----------|-------------|
| Read/Write | Physical FS | Standard file I/O |
| Create/Delete | Physical FS | Standard file ops |
| Snapshot | Versioning | Point-in-time snapshot |
| Diff | Versioning | Line-level diff between versions |
| Rollback | Versioning | Restore file to previous version |
| Tag | AI Metadata | Add/remove tags |
| Search | Virtual FS | Query by tag, entity, content |
| Link | Virtual FS | Cross-workspace symlinks |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Versioning | Rollback system (kernel only) | Full file versioning |
| AI metadata | None | Tags, entities, summaries |
| Virtual files | None | Search results, workspace links |
| Encryption | None | Per-file or per-directory |

---

## 14. Create Notification Infrastructure

### Current State

Notifications are managed ad-hoc. The UI system has some notification handling. No priority levels, no bundling, no focus-awareness, no scheduling.

### Refactored Design

Central notification service (port 8370):

```
                    ┌─────────────────────────────────────┐
                    │    Notification Service             │
                    │    (port 8370)                      │
                    │  Rust/Axum + Redis Streams          │
                    └──────┬──────────────────────┬───────┘
                           │                      │
              ┌────────────┼──────────────────────┼────────────┐
              │            │                      │            │
              ▼            ▼                      ▼            ▼
    ┌────────────┐ ┌────────────┐ ┌────────────────┐ ┌────────────┐
    │Priority    │ │Bundling    │ │Focus Filter    │ │Delivery    │
    │Engine      │ │Engine      │ │(port 8220)     │ │Channel     │
    │           │ │           │ │                │ │           │
    │• Emergency│ │• Same-src │ │• Pass/Queue    │ │• Websocket│
    │• High     │ │• Time-win │ │• Silent/Block  │ │• Push (FCM)│
    │• Normal   │ │• Summary  │ │• Schedule      │ │• Email     │
    │• Low      │ │• Digest   │ │                │ │• In-app   │
    └────────────┘ └────────────┘ └────────────────┘ └────────────┘
```

### 14.1 Priority Levels

| Level | Color | Behavior | Examples |
|-------|-------|----------|----------|
| Emergency | Red | Always delivered, bypasses focus, sound | Security alert, system crash, critical error |
| High | Orange | Delivered in all modes except Lock | Build failure, deploy issue, meeting start |
| Normal | Blue | Queued in Focus/Deep Focus, delivered otherwise | Task reminder, message, status update |
| Low | Gray | Bundled in digest, never urgent | Newsletter, weekly summary, tip |

### 14.2 Bundling Rules

| Rule | Behavior |
|------|----------|
| Same sender | Bundle into single notification ("5 messages from Slack") |
| Same type | Bundle into summary ("3 build completions") |
| Time window | Every 5 minutes, bundle all Low priority into digest |
| Daily digest | All Low notifications sent as end-of-day summary |

### 14.3 Focus-Aware Routing

Integration with Focus Controller (port 8220):

```
Incoming Notification
    │
    ▼
Priority: Emergency? ──Yes──► Deliver immediately
    │ No
    ▼
Check Focus Level (port 8220)
    │
    ├─ Passive  → Deliver all
    ├─ Suggest  → Deliver High+, queue Normal/Low with toast
    ├─ Strong   → Deliver Emergency only, queue everything
    ├─ Strict   → Block all, queue everything
    └─ Lock     → Block all, no queue
```

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Priority levels | None | 4 (Emergency/High/Normal/Low) |
| Bundling | None | Same-source + time-window + daily digest |
| Focus integration | Basic block/unblock | 5-level graduated filtering |
| Delivery channels | In-app only | WebSocket + Push + Email |
| Scheduling | None | Quiet hours + daily digest |

---

## 15. Create Package Management

### Current State

The App Runtime (`services/app-runtime/`, 822 lines) has basic app lifecycle (install → init → run → suspend → terminate) and an app store with 4 default apps. No dependency resolution, versioning, rollback, or integrity verification.

### Refactored Design

Package management subsystem:

```
                    ┌─────────────────────────────────────┐
                    │     Package Manager                 │
                    │     (port 8380)                     │
                    └──────┬──────────────────────┬───────┘
                           │                      │
              ┌────────────┼──────────────────────┼────────────┐
              │            │                      │            │
              ▼            ▼                      ▼            ▼
    ┌────────────┐ ┌────────────┐ ┌────────────────┐ ┌────────────┐
    │Dependency  │ │Package Repo│ │Sandbox         │ │Integrity   │
    │Resolver    │ │(port 8381) │ │Installer       │ │Verifier    │
    │           │ │           │ │(port 8382)     │ │           │
    │• DAG       │ │• Hosted    │ │• Container     │ │• Sig check │
    │• Version   │ │• Peer-to-  │ │• cgroups       │ │• Hash vrfy │
    │  solving   │ │  peer      │ │• Seccomp       │ │• Manifest  │
    │• Cycles    │ │• Verifictn │ │• Resource lim  │ │• Audit     │
    └────────────┘ └────────────┘ └────────────────┘ └────────────┘
```

### 15.1 Package Format

```
ichin-app.tar.gz
├── manifest.json       # name, version, deps, permissions, entry_point
├── signature.sig       # Ed25519 signature (signer key from trusted registry)
├── app/                # Application code
│   ├── main.py         # or main.rs, main.ts, etc.
│   └── ...             # Supporting files
├── assets/             # Icons, screenshots, etc.
├── sandbox.profile     # Seccomp/AppArmor profile
└── tests/              # Bundled tests
```

### 15.2 Registry (port 8381)

| Feature | Detail |
|---------|--------|
| Package registry | Hosted registry (default: registry.ichin.ai) |
| Peer discovery | LAN-based P2P for offline/air-gapped |
| Versioning | Semver 2.0.0 |
| Integrity | SHA-256 checksums + Ed25519 signatures |
| Code signing | Signing key must be registered with Identity Service |
| Rollback | Previous version preserved. `ichin pkg rollback <name>` |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Dependency resolution | None | Full DAG resolver |
| Versioning | None | Semver |
| Integrity | None | SHA-256 + Ed25519 |
| Sandboxed install | None | Container + seccomp |
| Rollback | Manual | One-command |

---

## 16. Create Observability

### Current State

No structured logging, no metrics, no tracing. The System Daemon has basic health check logging. Services log to stdout without structure.

### Refactored Design

Three pillars of observability + diagnostics:

```
                    ┌─────────────────────────────────────┐
                    │         Observability Stack         │
                    └──────┬──────────────────────┬───────┘
                           │                      │
              ┌────────────┼──────────────────────┼────────────┐
              │            │                      │            │
              ▼            ▼                      ▼            ▼
    ┌────────────┐ ┌────────────┐ ┌────────────────┐ ┌────────────┐
    │Structured  │ │Metrics     │ │Distributed     │ │Diagnostics │
    │Logging     │ │(port 8391) │ │Tracing         │ │(port 8393) │
    │(port 8390) │ │           │ │(port 8392)     │ │           │
    │           │ │           │ │                │ │           │
    │• JSON cols │ │• Prometheus│ │• OpenTelemetry │ │• Health   │
    │• Log level │ │• CPU/mem  │ │• Per-request   │ │• Profile  │
    │• Rotation  │ │• Request  │ │• Service map   │ │• Dump     │
    │• Retention │ │  counting │ │• Span analysis │ │• Core dump│
    └────────────┘ └────────────┘ └────────────────┘ └────────────┘
```

### 16.1 Structured Logging (port 8390)

Every service emits JSON logs:

```json
{
  "timestamp": "2026-06-21T10:30:00.123Z",
  "level": "info",
  "service": "orchestrator",
  "request_id": "req_abc123",
  "user_id": "user_xyz",
  "message": "Request classified as deterministic",
  "latency_ms": 1.2,
  "decision_level": "level_1",
  "tags": ["classification", "deterministic"]
}
```

Log levels: `trace`, `debug`, `info`, `warn`, `error`, `fatal`

### 16.2 Metrics (port 8391, Prometheus format)

| Metric | Type | Description |
|--------|------|-------------|
| `ichin_service_uptime_seconds` | Gauge | Service uptime |
| `ichin_requests_total` | Counter | Request count by service + status |
| `ichin_request_duration_ms` | Histogram | Latency distribution |
| `ichin_ai_cost_total` | Counter | Cumulative AI cost in USD |
| `ichin_memory_items_total` | Gauge | Memory items by layer |
| `ichin_focus_current_level` | Gauge | Current focus level (0-4) |
| `ichin_agents_active` | Gauge | Number of active agents |
| `ichin_errors_total` | Counter | Error count by type |

### 16.3 Tracing (port 8392, OpenTelemetry)

Every user request gets a trace through the system:

```
User Request ─► Orchestrator ─► Agent Manager ─► Memory Engine ─► Response
    │               │                │                │
    ▼               ▼                ▼                ▼
  Span 1         Span 2            Span 3           Span 4
{classify}    {route_agent}     {query_memory}   {assemble}
 5µs             2µs              45µs             12µs
```

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Logging | Plain stdout | Structured JSON + log service |
| Metrics | None | Prometheus + Grafana |
| Tracing | None | OpenTelemetry distributed |
| Diagnostics | None | Health + profile + dump |
| Debugging | Blind | Full request tracing |

---

## 17. Accessibility

### Current State

No accessibility features beyond basic keyboard navigation (Ctrl+Space spotlight, some keyboard shortcuts).

### Refactored Design

Full accessibility baked into every component:

| Feature | Implementation | Standard |
|---------|---------------|----------|
| **Keyboard-first** | Every action has a keyboard shortcut. No mouse-only operations. Focus indicators on all interactive elements. | WCAG 2.2 |
| **Screen reader** | ARIA labels on all components. Semantic HTML. Alt text on all icons/images. Live regions for dynamic content. | WCAG 2.2 A/AA |
| **Voice control** | Local voice recognition (whisper.cpp) for all system actions. "Open Coding workspace", "Search for X", "Set focus to strict" | Self-voiced |
| **Reduced motion** | `prefers-reduced-motion` respected. Animations disabled or reduced. Transitions snap instead of animate. | WCAG 2.2 |
| **High contrast** | High-contrast theme. All text meets 7:1 contrast ratio. Focus indicators at 3:1. | WCAG 2.2 AAA |
| **Font scaling** | 200% text zoom without loss of content or functionality. Fluid typography. | WCAG 2.2 |
| **Localization** | i18n framework (ICU message format). RTL support. Right-to-left layout mirroring. | CLDR |

### 17.1 Keyboard-First Architecture

```
                          ┌─────────────────────┐
                          │ Keyboard Engine     │
                          │ (port 8400)         │
                          └──────────┬──────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Shortcut Registry│     │ Chord Detector   │     │ Context Router   │
│ • System         │     │ • Key combos     │     │ • Workspace maps │
│ • Workspace      │     │ • Sequence       │     │ • Focus-aware    │
│ • App-defined    │     │ • Hold timing    │     │ • Mode-specific  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 17.2 Localization Infrastructure

| Feature | Detail |
|---------|--------|
| Framework | ICU MessageFormat (via intl-messageformat) |
| Initial languages | en, ja, zh, ko, es, fr, de |
| RTL support | Arabic, Hebrew layout mirroring |
| Number/date format | CLDR-compliant per locale |
| Translation service | AI-assisted translation via local model (on-device) |
| Community | Crowdin/Weblate integration for community translations |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Keyboard navigation | Partial (spotlight only) | Full (every action) |
| Screen reader | None | Full ARIA + semantic HTML |
| Voice control | None | Local whisper.cpp |
| High contrast | None | Full AAA compliance |
| Reduced motion | None | Respects user preference |
| Localization | English only | 6 initial languages, RTL |

---

## 18. Networking Layer

### Current State

Basic HTTP networking. Protocol stack on ports 4889-4892 (ICHINP, DNS, CA, Daemon). TLS on mail. No firewall, no VPN, no P2P.

### Refactored Design

Full networking stack:

```
                    ┌─────────────────────────────────────┐
                    │      Network Manager                │
                    │      (port 8401, Kernel+Userspace)  │
                    └──────┬──────────────────────┬───────┘
                           │                      │
        ┌──────────────────┼──────────────────────┼──────────────────┐
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Firewall      │  │Tunnel Manager│  │Service Mesh    │  │P2P Network   │
│(kernel+users)│  │(VPN/WireGuard)│ │(mTLS mesh)     │  │(libp2p)      │
│             │  │             │  │                │  │             │
│• Packet fltr│  │• WireGuard  │  │• Service-to-   │  │• LAN discov  │
│• App rules  │  │• Tailscale  │  │  service mTLS  │  │• DHT         │
│• DNS filter │  │  integratio │  │• Cert rotation  │  │• Relayed    │
│• Rate limit │  │• Split tun  │  │• Policy-based  │  │  connection  │
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
```

### 18.1 Firewall Rules

| Rule Type | Default | Configurable |
|-----------|---------|-------------|
| Outbound service traffic | Allow (all) | Block specific services |
| Inbound service traffic | Allow (mesh only) | Block external |
| Internet access per app | Allow (all) | Per-app allowlist |
| DNS filtering | None | Custom blocklist |
| Rate limiting | 1000 req/s per service | Configurable threshold |

### 18.2 Service Mesh (mTLS)

**Replace** the current per-request Ed25519 signing (Section 9.3) with a full mTLS mesh:

| Component | Detail |
|-----------|--------|
| Certificate | Internal CA (Ichin-CA, port 4891) issues per-service certificates |
| Rotation | Every 24 hours, automatic |
| Authentication | mTLS handshake on every inter-service connection |
| Authorization | SAN-based (Subject Alternative Name = service name) |
| Enforcement | Enforced at network level (iptools/eBPF on Linux, WinFilter on Windows) |

### 18.3 P2P Layer

| Feature | Detail |
|---------|--------|
| LAN discovery | mDNS/DNS-SD for service discovery on LAN |
| DHT | Kademlia DHT for P2P peer discovery |
| Relay | TURN-style relay for NAT traversal |
| Encryption | Noise protocol (like libp2p) |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Firewall | None | Per-app + system rules |
| VPN | None | WireGuard integration |
| Service auth | Ed25519 headers | Full mTLS mesh |
| P2P | None | LAN discovery + DHT |
| DNS filtering | None | Blocklist support |

---

## 19. Security Improvements

### Current State

The Security Core (port 8017) has process monitoring, sandbox management (5 levels), anomaly/threat detection, and audit logging. The kernel has sandbox levels (0-4). However:
- No hardware-backed encryption
- No secure boot
- No TPM integration
- Code signing exists in design but not enforced
- AI safety boundaries exist in kernel but not used

### Refactored Design

Zero Trust + hardware-backed security:

```
                    ┌─────────────────────────────────────┐
                    │       Security Controller           │
                    │       (Kernel + Service, port 8017) │
                    └──────┬──────────────────────┬───────┘
                           │                      │
        ┌──────────────────┼──────────────────────┼──────────────────┐
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Hardware Root │  │Runtime Guard │  │AI Safety       │  │Audit Engine  │
│of Trust      │  │             │  │Boundary        │  │             │
│             │  │             │  │                │  │             │
│• TPM 2.0    │  • Memory iso  │  │• Agent sandbox │  │• Immutable  │
│• Secure Boot│  │• Exec guard  │  │• Action scrub  │  │  log        │
│• Measured   │  │• Seccomp     │  │• Privilege     │  │• Tamper-ev  │
│  boot       │  │• Landlock    │  │  escalation    │  │• Forward    │
│• HSM/Wallet │  │• ASLR + CFI  │  │  prevention   │  │  integrity  │
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
```

### 19.1 Hardware Root of Trust

| Component | Implementation | Status |
|-----------|---------------|--------|
| TPM 2.0 | Measured boot, disk encryption key sealed to PCR | Integration target |
| Secure Boot | Shim + signed kernel + signed initramfs | Integration target |
| Measured Boot | TPM PCR 0-7 measurement chain | Integration target |
| HSM | Optional YubiKey/smartcard for key storage | Optional |

### 19.2 Runtime Protection

| Mechanism | Description | Level |
|-----------|-------------|-------|
| Memory isolation | Kernel enforces per-process page tables (no shared memory between sandboxes) | Kernel |
| Execution guard | W^X memory policy: pages are either writable or executable, never both | Kernel |
| Seccomp | System call filtering for user-space services | Userspace |
| Landlock | Filesystem access control for user-space services | Userspace |
| ASLR | Kernel-level address space layout randomization | Kernel |
| CFI | Control flow integrity (Rust's safe patterns + LLVM CFI) | Compiler |
| Stack canaries | Compiler-inserted stack overflow protection | Compiler |

### 19.3 AI Safety Boundaries

Enforced at the kernel level (already partially in `kernel/src/sandbox.rs`):

| Rule | Enforcement |
|------|-------------|
| AI cannot escalate sandbox level | Kernel checks sandbox level on all privilege syscalls |
| AI cannot modify kernel code | Kernel page tables mark kernel pages as non-writable from user space |
| AI cannot disable security | Security Core runs at higher sandbox level than any AI agent |
| AI cannot access another workspace's memory | Memory isolation enforced at page table level |
| AI has max CPU budget | Scheduler enforces per-process tick limits |
| AI has max memory budget | Memory manager enforces per-process page limits |
| AI has no network access by default | Sandbox level determines network permissions |

### 19.4 Audit Engine (Immutable Log)

| Feature | Detail |
|---------|--------|
| Storage | Append-only, write-once (WORM) storage |
| Forward integrity | Each log entry contains hash of previous entry (hash chain) |
| Tamper evidence | Any modification breaks hash chain — detectable on verification |
| Signing | Each entry signed with HSM-backed key |
| Retention | 90 days default, configurable |
| Export | Structured JSON export for SIEM integration |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Secure Boot | None | TPM + measured boot |
| Disk encryption | None | TPM-sealed LUKS |
| Code signing | Design only | Enforced at install |
| AI safety | Basic sandbox | Full kernel-enforced boundaries |
| Audit | Plain text log | Immutable hash chain |
| Runtime protection | None | ASLR + W^X + CFI + seccomp |

---

## 20. Developer Platform

### Current State

The App Runtime has a basic `/developer/docs` and `/developer/simulate` endpoint. The `packages/ai-sdk/` (313 lines) has AgentBuilder, WorkflowBuilder, and CouncilClient. No CLI, no testing framework, no OpenAPI docs, no plugin SDK.

### Refactored Design

Full developer platform:

```
                    ┌─────────────────────────────────────┐
                    │       Developer Platform            │
                    └──────┬──────────────────────┬───────┘
                           │                      │
        ┌──────────────────┼──────────────────────┼──────────────────┐
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Versioned APIs│  │ICHIN CLI     │  │Plugin SDK      │  │Testing       │
│(port 8420)   │  │(ichin)       │  │(port 8421)     │  │Framework     │
│             │  │             │  │                │  │(port 8422)   │
│• OpenAPI 3.1│  │• ichin pkg  │  │• Extension API │  │• Mock svcs  │
│• GraphQL    │  │• ichin svc  │  │• Hook system  │  │• Integration│
│• Versioning │  │• ichin wf   │  │• Lifecycle    │  │• Performance│
│• Deprecation│  │• ichin conf │  │• Manifest     │  │• AI eval    │
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
        │                  │                      │                  │
        └──────────────────┴──────────────────────┴──────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │SDK Packages  │
                    │             │
                    │• TypeScript │
                    │• Python     │
                    │• Rust       │
                    │• REST API   │
                    └──────────────┘
```

### 20.1 Versioned APIs

| Version | Status | Changes |
|---------|--------|---------|
| v1 (current) | Deprecated June 2026 | All current endpoints |
| v2 | Current (June 2026) | Refactored services, new endpoints |
| v3 | Planned (Dec 2026) | gRPC, streaming |

### 20.2 ICHIN CLI

```bash
ichin pkg install <name>     # Install package
ichin pkg publish <dir>      # Publish package to registry
ichin pkg rollback <name>    # Rollback to previous version

ichin svc status             # List all services
ichin svc restart <name>     # Restart service
ichin svc logs <name>        # Tail service logs

ichin wf create <file>       # Create workflow from YAML
ichin wf run <id>            # Run workflow
ichin wf list                # List workflows

ichin conf get <key>         # Get config value
ichin conf set <key> <val>   # Set config value

ichin dev sim <app>          # Simulate app in sandbox
ichin dev test <app>         # Run app tests
ichin dev docs               # Open API docs

ichin ai status              # AI model status
ichin ai switch <model>      # Switch active model

ichin focus status           # Current focus level
ichin focus set <level>      # Set focus level

ichin debug trace            # Start trace capture
ichin debug metrics          # Show live metrics

ichin sync status            # Sync status
ichin sync force             # Force sync

ichin help                   # Show all commands
```

### 20.3 Testing Framework (port 8422)

| Test Type | Description | Tooling |
|-----------|-------------|---------|
| Unit tests | Per-module tests | Language-native (cargo test, pytest, vitest) |
| Integration tests | Service-to-service API tests | Python (pytest + httpx) |
| Kernel tests | Bare-metal kernel tests | QEMU + custom test runner |
| Security tests | Penetration tests, fuzzing | OWASP ZAP, cargo-fuzz |
| Agent simulation | Multi-agent scenario tests | AI SDK simulator |
| Load testing | Performance benchmarks | k6, locust |
| AI evaluation | Accuracy, latency, cost bench | Custom eval suite |

### 20.4 SDK Packages

| SDK | Language | Package |
|-----|----------|---------|
| ichin-sdk-ts | TypeScript | `@ichin/sdk` (npm) |
| ichin-sdk-py | Python | `ichin-sdk` (PyPI) |
| ichin-sdk-rs | Rust | `ichin-sdk` (crates.io) |
| ichin-sdk-rest | Any REST | OpenAPI 3.1 spec |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| API versioning | None | v1 deprecation + v2 current + v3 planned |
| CLI | None | Full `ichin` CLI |
| Plugin SDK | Partial (AI SDK only) | Full extension API |
| Testing framework | None | Unit + integration + kernel + security + AI eval |
| SDK packages | 1 (TypeScript AI SDK) | 4 (TS + Python + Rust + REST) |

---

## 21. Performance

### Current State

No performance optimization strategy. Cold boot loads all services sequentially. No caching strategy. All agents loaded at all times. No lazy loading. No GPU acceleration.

### Refactored Design

Performance targets for production:

| Metric | Target | Current (est.) | Improvement |
|--------|--------|---------------|-------------|
| Cold boot (kernel → UI) | <2s | ~30s | 15x |
| Service startup (all) | <5s | ~60s | 12x |
| AI response (Level 1) | <50ms | ~8s | 160x |
| AI response (Level 2) | <2s | ~8s | 4x |
| AI response (Level 3) | <10s | ~15s | 1.5x |
| Memory usage (idle) | <500MB | ~2GB | 4x |
| Disk I/O (sequential) | 500MB/s | Unknown | — |
| UI frame rate | 60fps | 30fps | 2x |
| Transition animations | <300ms | <900ms | 3x |

### 21.1 Optimization Strategies

| Strategy | Application | Impact |
|----------|-------------|--------|
| **Lazy loading** | Workspace agents, temp agents, apps | 70% reduction in startup memory |
| **Parallel boot** | Use systemd/init parallelism for service startup | 4x faster boot |
| **Predictive loading** | Load likely workspace based on time/day/schedule | Instant workspace switch |
| **Tiered caching** | L1: in-process, L2: Redis, L3: disk | 80% cache hit rate |
| **Resource budgeting** | Per-service CPU/memory limits (cgroups) | No single service can starve others |
| **GPU acceleration** | Local model inference on GPU (CUDA/Vulkan) | 5-10x faster inference |
| **Compilation** | JIT for Python services (PyPy/numba) | 2x faster execution |
| **Connection pooling** | Database and service connections | 50% reduction in connection overhead |
| **Zero-copy IPC** | Shared memory for kernel-to-service communication | Microsecond latency |

### 21.2 Cold Boot Sequence (Optimized)

```
T=0ms     Kernel init (GDT/IDT/paging) — 50ms
T=50ms    Hardware probe — 100ms
T=150ms   Scheduler start — 10ms
T=160ms   Memory manager init — 20ms
T=180ms   IPC init — 10ms
T=190ms   VFS mount — 50ms
T=240ms   Service manager start — 20ms
          │
          ├── Parallel: Load Core Agents
          │   T=260ms    Reasoning agent — 200ms
          │   T=260ms    Planning agent — 200ms
          │   T=260ms    Execution agent — 200ms
          │   T=260ms    Memory agent — 200ms
          │   T=260ms    Security agent — 200ms
          │   T=260ms    Research agent — 200ms (lazy: request-time)
          │
          ├── Parallel: Start system services
          │   T=260ms    Security Core — 300ms
          │   T=260ms    System Daemon — 100ms
          │   T=260ms    Identity Service — 200ms
          │   T=260ms    Event Bus — 100ms
          │
          └── Parallel: GPU model preload
              T=260ms    Tiny local model — 500ms
                         Medium local model — 2s (background)
          
T=760ms   UI System init — 200ms
T=960ms   Workspace default load — 100ms
T=1060ms  UI rendered, system ready

Total: ~1.1s to usable desktop
```

### Impact

| Metric | Before | After |
|--------|--------|-------|
| Cold boot | ~30s | ~1.1s |
| Idle memory | ~2GB | ~300MB |
| AI response (avg) | ~8s | ~500ms (weighted) |
| UI frame rate | ~30fps | 60fps |
| Cache hit rate | None | 80% |

---

## 22. Testing

### Current State

No test infrastructure. `AUDIT.md` mentions Python syntax checks and Rust compilation checks but no actual test suites.

### Refactored Design

Comprehensive testing at every level:

```
                    ┌─────────────────────────────────────┐
                    │       Test Infrastructure          │
                    │       (CI pipeline)                │
                    └──────┬──────────────────────┬───────┘
                           │                      │
        ┌──────────────────┼──────────────────────┼──────────────────┐
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Unit Tests    │  │Integration   │  │System Tests    │  │AI Eval       │
│             │  │Tests         │  │               │  │Benchmarks    │
│• cargo test │  │• API contract│  │• Full boot    │  │             │
│• pytest     │  │• Cross-svc   │  │• Service heal │  │• Accuracy   │
│• vitest     │  │• Event flow  │  │• Focus mode   │  │• Latency    │
│• Immediate  │  │• Data flow   │  │• Workspace    │  │• Cost       │
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
        │                  │                      │                  │
        └──────────────────┴──────────────────────┴──────────────────┘
                           │
                           ▼
                    ┌─────────────────────────────────────┐
                    │         CI Pipeline (GitHub Actions)│
                    │  lint → unit → build → integration │
                    │  → system → security → AI eval →   │
                    │  image → deploy                     │
                    └─────────────────────────────────────┘
```

### 22.1 Test Categories

| Category | Coverage Target | Tools | Frequency |
|----------|----------------|-------|-----------|
| **Unit tests** | 90%+ line coverage | cargo test, pytest, vitest | Every commit |
| **Integration tests** | Every API endpoint | Python (pytest + httpx) | Every PR |
| **Kernel tests** | Every syscall, every scheduler path | QEMU + custom runner | Every PR |
| **Security tests** | OWASP Top 10 | OWASP ZAP, cargo-fuzz | Daily |
| **Agent simulation** | 100+ multi-agent scenarios | AI SDK simulator | Weekly |
| **Load testing** | 1000 concurrent users | k6, locust | Bi-weekly |
| **AI evaluation** | Accuracy, latency, cost | Custom eval suite | Weekly |
| **Regression testing** | All known bugs | Historical bug tracker | Every PR |

### 22.2 AI Evaluation Benchmarks

| Benchmark | Metric | Target |
|-----------|--------|--------|
| Classification accuracy | Correctness | >95% |
| Agent response latency | P50/P95/P99 | <2s / <5s / <10s |
| Council accuracy | Correctness vs human baseline | >90% |
| Memory retrieval precision | Precision@10 | >0.8 |
| Memory retrieval recall | Recall@10 | >0.75 |
| Focus mode compliance | Enforcement bypass rate | <0.01% |
| Routing efficiency | Level 1/2/3 ratio | 70/25/5% |
| Cost per request | USD | <$0.001 |

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Unit tests | None | 90%+ coverage |
| Integration tests | None | Full API coverage |
| AI evaluation | None | 8 benchmarks |
| CI pipeline | None | Full 8-stage pipeline |
| Security testing | None | OWASP + fuzz |

---

## 23. Deployment

### Current State

Multiple deployment modes documented (Docker Compose, K8s, Edge nodes, ISO builder) but no cohesive strategy.

### Refactored Design

Six deployment profiles:

```
                    ┌─────────────────────────────────────┐
                    │       Deployment Manager            │
                    │       (port 8430)                   │
                    └──────┬──────────────────────┬───────┘
                           │                      │
        ┌──────────────────┼──────────────────────┼──────────────────┐
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Development   │  │Local         │  │Cloud           │  │Enterprise    │
│(dev)         │  │(single node) │  │(multi-node)    │  │(on-prem)     │
│             │  │             │  │                │  │             │
│• Hot reload │  │• Docker Comp│  │• K8s (EKS/GKE)│  │• Air-gapped  │
│• Mock svcs  │  │• SQLite     │  │• Managed DB   │  │• Self-hosted │
│• Debug mode │  │• Local AI   │  │• Cloud AI     │  │• On-prem AI  │
│• Verbose log│  │• Offline    │  │• Auto-scaling │  │• HA config   │
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│Education     │  │Offline       │  │Hybrid          │  │ISO (baremetal)│
│(learning)    │  │(air-gapped)  │  │(edge+cloud)    │  │             │
│             │  │             │  │                │  │             │
│• Guided     │  • No network  │  │• Local UI      │  • Bootable   │
│  setup      │  • Full-local  │  │• Cloud AI      │  • Linux init │
│• Tutorials  │  • USB boot    │  │• Async sync    │  • Kernel opt │
│• Sandboxed  │  • Minimal deps│  │• Fallback      │  • GRUB       │
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
```

### 23.1 Deployment Profiles

| Profile | RAM | Disk | CPU | AI Models | Network |
|---------|-----|------|-----|-----------|---------|
| Development | 4GB | 10GB | 2 cores | Tiny only (mock cloud) | Required |
| Local | 8GB | 20GB | 4 cores | Tiny + Medium | Optional (offline) |
| Cloud | 16GB+ | 100GB+ | 8+ cores | All (cloud primary) | Required |
| Enterprise | 32GB+ | 500GB+ | 16+ cores | All (on-prem) | Optional |
| Education | 4GB | 10GB | 2 cores | Tiny only | Optional |
| Offline | 8GB | 20GB | 4 cores | Tiny + Medium | None |
| Hybrid | 8GB | 20GB | 4 cores | Tiny local + cloud fallback | Required |
| ISO (baremetal) | 2GB+ | 10GB+ | x86_64 | Tiny only | Optional |

### 23.2 Deployment Manager (port 8430)

New service that manages deployment configuration:

```rust
struct DeploymentManager {
    profile: DeploymentProfile,     // which profile is active
    nodes: Vec<Node>,               // cluster nodes (if multi-node)
    local_models: Vec<Model>,       // locally available AI models
    sync_config: SyncConfig,        // sync settings
    upgrade_plan: Option<Upgrade>,   // pending upgrade
}
```

### Impact

| Capability | Before | After |
|-----------|--------|-------|
| Deployment profiles | None (ad hoc) | 8 defined profiles |
| Offline mode | Partial | Full offline capability |
| Education mode | None | Guided setup + tutorials |
| Enterprise | None | Air-gapped + on-prem AI |
| Upgrade management | None | Rolling upgrade plans |

---

## 24. Output Requirements

### 24.1 Revised Architecture

Documented throughout this document. Key changes:

1. **New services:** DecisionService (8310), Agent Manager (8210), Focus Controller (8220), AI Router (8330), Knowledge Graph (8320), Identity Service (8100), Device Registry (8101), Session Manager (8102), Permission Engine (8103), Search Gateway (8340), File Indexer (8341), Semantic Search (8342), Keyword Search (8343), Ranking Engine (8344), Sync Service (8350), Notification Service (8370), Package Manager (8380), Log Service (8390), Metrics Service (8391), Trace Service (8392), Diagnostics Service (8393), Deployment Manager (8430), Keyboard Engine (8400), Network Manager (8401), Developer API Gateway (8420)

2. **Deprecated services (merged/replaced):** `services/agents/` (absorbed by Agent Manager), `services/memory-engine/` functionality split into 5 modules, `services/search-engine/` absorbed into Search Gateway infra

3. **Refactored services:** `services/orchestrator/` slimmed to decision routing only, `services/system-daemon/` functionality absorbed into Observability stack

### 24.2 Updated System Diagram (Text)

```
┌─────────────────────────────────────────────────────────────────┐
│                      KERNEL LAYER (bare-metal)                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │GDT/IDT│ │Memory│ │Sched│ │IPC  │ │VFS  │ │Drvrs│ │Sandbx││
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM LAYER (infrastructure)                │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐  │
│  │Identity │ │Session  │ │Device  │ │Perm      │ │Search    │  │
│  │Service  │ │Manager  │ │Registry│ │Engine    │ │Gateway   │  │
│  │:8100    │ │:8102    │ │:8101   │ │:8103     │ │:8340     │  │
│  └─────────┘ └─────────┘ └────────┘ └──────────┘ └──────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐  │
│  │Sync     │ │Package  │ │Net     │ │Notify    │ │Observab  │  │
│  │:8350    │ │Mgr:8380 │ │Mgr:8401│ │:8370     │ │:8390-93  │  │
│  └─────────┘ └─────────┘ └────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI LAYER (intelligence)                      │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐  │
│  │Decision │ │Agent    │ │AI      │ │Knowledge │ │Memory    │  │
│  │:8310    │ │Mgr:8210 │ │Router  │ │Graph:8320│ │Engine    │  │
│  └─────────┘ └─────────┘ └────────┘ └──────────┘ └──────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐              │
│  │Orchest. │ │Council  │ │6 Core  │ │Workspace │              │
│  │:8011    │ │(Level 3)│ │Agents  │ │Agents x4 │              │
│  └─────────┘ └─────────┘ └────────┘ └──────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                              │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐  │
│  │Desktop  │ │Web UI   │ │Mobile  │ │Developer │ │App       │  │
│  │UI:1420  │ │:1430    │ │(Expo)  │ │Portal    │ │Runtime   │  │
│  └─────────┘ └─────────┘ └────────┘ └──────────┘ └──────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐              │
│  │Browser  │ │Calendar │ │Mail    │ │Account   │              │
│  │:3003    │ │:3002    │ │:8080   │ │:8081     │              │
│  └─────────┘ └─────────┘ └────────┘ └──────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      UI LAYER (frontend)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  React Shell (Desktop UI / Web UI / Mobile UI)              │ │
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐          │ │
│  │  │Workspace│ │Spotlight│ │AI Orb  │ │Focus Over│          │ │
│  │  │View     │ │Search   │ │Indicatr│ │lay      │          │ │
│  │  └─────────┘ └─────────┘ └────────┘ └──────────┘          │ │
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐          │ │
│  │  │Settings │ │Mission  │ │Sidebar │ │Keyboard  │          │ │
│  │  │Panel    │ │Control  │ │Nav     │ │Engine    │          │ │
│  │  └─────────┘ └─────────┘ └────────┘ └──────────┘          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 24.3 Updated Service Architecture

| # | Service | Port | Language | Status | Purpose |
|---|---------|------|----------|--------|---------|
| — | **PLATFORM SERVICES** | | | | |
| 1 | Identity Service | 8100 | Rust/Axum 0.8 | NEW | AuthN/AuthZ, users, orgs |
| 2 | Device Registry | 8101 | Rust/Axum 0.8 | NEW | Device management |
| 3 | Session Manager | 8102 | Rust/Axum 0.8 | NEW | PASETO tokens, sessions |
| 4 | Permission Engine | 8103 | Rust/Axum 0.8 | NEW | RBAC/ABAC policy engine |
| 5 | Search Gateway | 8340 | Rust/Axum 0.8 | NEW | Unified search API |
| 6 | Sync Service | 8350 | Rust/Axum 0.8 | NEW | Offline sync, CRDT |
| 7 | Notification Service | 8370 | Rust/Axum 0.8 | NEW | Priority, bundling, focus |
| 8 | Package Manager | 8380 | Rust/Axum 0.8 | NEW | App packaging, registry |
| 9 | Network Manager | 8401 | Rust/Axum 0.8 | NEW | Firewall, VPN, mTLS |
| 10 | Deployment Manager | 8430 | Rust/Axum 0.8 | NEW | Deployment profiles |
| — | **AI SERVICES** | | | | |
| 11 | DecisionService | 8310 | Rust/Axum 0.8 | NEW | Pre-filter, escalation |
| 12 | Agent Manager | 8210 | Rust/Axum 0.8 | NEW | Agent lifecycle, routing |
| 13 | AI Router | 8330 | Rust/Axum 0.8 | NEW | Model selection, cost mgmt |
| 14 | Knowledge Graph | 8320 | Rust/Axum 0.8 | NEW | Entity/relation store |
| 15 | Memory Engine | 8013 | Python FastAPI | REFACTORED | 5 internal modules |
| 16 | Orchestrator | 8011 | Python FastAPI | REFACTORED | Slimmed (routing only) |
| 17 | AI Studio | 8016 | Python FastAPI | REFACTORED | Workflow builder |
| — | **CORE SERVICES (system)** | | | | |
| 18 | Security Core | 8017 | Rust/Axum 0.7 | REFACTORED | Immutable audit, runtime |
| 19 | Focus Controller | 8220 | Rust/Axum 0.8 | NEW | Focus mode enforcement |
| 20 | UI System | 8014 | Python FastAPI | REFACTORED | Layout, orb, ambient |
| 21 | App Runtime | 8015 | Rust/Axum 0.7 | REFACTORED | Per-app lifecycle |
| — | **EXISTING SERVICES (unchanged)** | | | | |
| 22 | Account | 8081 | Rust/Axum 0.8 | UNCHANGED | User account/mfa |
| 23 | Mail | 8080 | Rust/Axum 0.8 | UNCHANGED | Email system |
| 24 | Calendar | 3002 | Rust/Axum | UNCHANGED | Task/calendar |
| 25 | Browser | 3003 | Rust/Axum | UNCHANGED | Browser backend |
| 26 | Protocol | 4889-92 | Python | UNCHANGED | ICHINP stack |
| 27 | System Daemon | 7010 | Rust/Tokio | UNCHANGED | Background tasks |
| — | **REMOVED/MERGED** | | | | |
| — | AI Agents | 8012 | Python FastAPI | REMOVED | Absorbed by Agent Manager |
| — | Search Engine | 3001 | Rust/Axum | REMOVED | Absorbed by Search Gateway |

### 24.4 Dependency Graph

```
Identity (:8100)           ─┬─ Session Manager (:8102)
                            ├─ Permission Engine (:8103)
                            └─ Device Registry (:8101)

Session Manager (:8102)    ─┬─ All services (token validation)
                            └─ Permission Engine (policy check)

Permission Engine (:8103)   ── App Runtime, Security Core, Agent Manager

Search Gateway (:8340)     ─┬─ File Indexer (:8341)
                            ├─ Semantic Search (:8342) → Memory Engine
                            ├─ Keyword Search (:8343)
                            └─ Ranking Engine (:8344)

Knowledge Graph (:8320)    ─┬─ Memory Engine (sync)
                            ├─ Search Gateway (graph queries)
                            └─ Agent Manager (entity lookup)

Memory Engine (:8013)      ─┬─ Knowledge Graph (entity extraction)
                            ├─ Orchestrator (context building)
                            └─ All AI agents (memory store/query)

DecisionService (:8310)    ─┬─ Level 1: Deterministic handler
                            ├─ Level 2: Agent Manager → single agent
                            └─ Level 3: Orchestrator → Council

Agent Manager (:8210)      ─┬─ Core Agents (6)
                            ├─ Workspace Agents (4, lazy)
                            ├─ Temp Agents (on-demand)
                            └─ AI Router (model selection)

AI Router (:8330)          ─┬─ Tiny Local Model (500M)
                            ├─ Medium Local Model (3B)
                            ├─ Large Local Model (7B)
                            └─ Cloud LLM (GPT-4o, Claude)

Orchestrator (:8011)       ── Council convocation (Level 3 only)

Focus Controller (:8220)   ─┬─ Notification Service (filtering)
                            ├─ UI System (visual enforcement)
                            └─ App Runtime (app restrictions)

Notification (:8370)       ─┬─ Focus Controller (routing)
                            ├─ UI System (in-app delivery)
                            └─ All services (publish events)

Sync Service (:8350)       ── Identity Service (device list)

Package Manager (:8380)    ─┬─ App Runtime (app lifecycle)
                            ├─ Security Core (sandbox enforcement)
                            └─ Identity Service (signing keys)

Network Manager (:8401)    ── All services (mTLS mesh, firewall)

Observability (:8390-93)   ── All services (logs, metrics, traces)

Event Bus (NATS/Redis)     ── All services (async communication)
```

### 24.5 Event Flow

```
User Action (e.g., "explain this code")
    │
    ▼
Desktop UI ──HTTP──► DecisionService (:8310)
    │                       │
    │                       ├─ Level 1: Deterministic? (no — needs AI)
    │                       ├─ Level 2: Route to Reasoning Agent
    │                       │
    │                       ▼
    │               Agent Manager (:8210)
    │                       │
    │                       ├─ Select: Reasoning Agent (Core, loaded)
    │                       ├─ AI Router (:8330): Medium Local (3B)
    │                       │
    │                       ▼
    │               Reasoning Agent
    │                       │
    │                       ├─ Memory Engine (:8013): GET context
    │                       │       └─ Knowledge Graph: relevant entities
    │                       ├─ Execute reasoning (model inference)
    │                       ├─ Memory Engine: STORE result
    │                       │
    │                       ▼
    │               Response ──► DecisionService ──► Desktop UI
    │
    ▼
Event Bus (async):
    ├─ event: ai.request.completed {agent: "reasoning", latency_ms: 3400}
    ├─ event: memory.written {layer: "working", type: "reasoning_result"}
    └─ event: observability.metric {name: "ai_latency", value: 3400}
```

### 24.6 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ DATA STORES                                                     │
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐          │
│  │Postgres │  │Redis    │  │Qdrant   │  │redb      │          │
│  │(struct) │  │(cache)  │  │(vectors)│  │(embedded)│          │
│  ├─────────┤  ├─────────┤  ├─────────┤  ├──────────┤          │
│  │Identity │  │Session  │  │Memory   │  │Knowledge │          │
│  │Users    │  │Cache    │  │Embeddings│  │Graph     │          │
│  │Orgs     │  │Pub/Sub  │  │Semantic │  │Entities  │          │
│  │Devices  │  │Rate Lim │  │Search   │  │Relations │          │
│  │Mail     │  │Queue    │  │         │  │Workspace │          │
│  │Calendar │  │         │  │         │  │Structure │          │
│  │Settings │  │         │  │         │  │          │          │
│  └─────────┘  └─────────┘  └─────────┘  └──────────┘          │
│                                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│  │Sled     │  │SQLite   │  │Local FS │                         │
│  │(embedded)│  │(search) │  │(files)  │                         │
│  ├─────────┤  ├─────────┤  ├─────────┤                         │
│  │Account  │  │Inverted │  │AI Meta  │                         │
│  │Mail     │  │Index    │  │data     │                         │
│  │Audit    │  │FTS      │  │User docs│                         │
│  │Sync meta│  │         │  │Versions │                         │
│  └─────────┘  └─────────┘  └─────────┘                         │
└─────────────────────────────────────────────────────────────────┘

Key rules:
  1. Each service owns its data (no cross-service DB access)
  2. Query only through service APIs
  3. State changes published as events
  4. Cache invalidated via event stream
```

### 24.7 API Boundaries

| Service | API Format | Auth Required | Rate Limit |
|---------|-----------|---------------|------------|
| Identity (:8100) | REST/JSON | No (registration), Yes (all other) | 10/s |
| Session (:8102) | REST/JSON | Yes (paseto) | 100/s |
| Permission (:8103) | REST/JSON | Yes (service mTLS) | 1000/s |
| Decision (:8310) | REST/JSON | Yes (user token) | 50/s |
| Agent Manager (:8210) | REST/JSON | Yes (user token) | 20/s |
| AI Router (:8330) | REST/JSON | Yes (service mTLS) | 100/s |
| Knowledge Graph (:8320) | REST/JSON | Yes (service mTLS) | 500/s |
| Memory (:8013) | REST/JSON | Yes (user token) | 100/s |
| Search (:8340) | REST/JSON | Yes (user token) | 30/s |
| Sync (:8350) | WebSocket/REST | Yes (user token) | Per-device |
| Notify (:8370) | WebSocket/REST | Yes (user token) | 50/s |
| Package (:8380) | REST/JSON | Yes (user + signing key) | 10/s |
| Network (:8401) | gRPC | Yes (service mTLS) | 1000/s |
| Focus (:8220) | REST/JSON | Yes (user token) | 30/s |
| UI (:8014) | WebSocket/REST | Yes (session) | 60/s |
| Security (:8017) | gRPC | Yes (service mTLS) | 1000/s |
| Event Bus | NATS/Redis | Yes (service mTLS) | Unlimited |

### 24.8 Security Model

```
User ─── App ─── Auth (Identity Service)
                  │
                  ├── User token (PASETO, 15min TTL)
                  ├── Device trust (Device Registry)
                  ├── Session validation (Session Manager)
                  └── Permission check (Permission Engine)
                        │
                        ▼
                ┌────────────────┐
                │  Zero Trust    │
                │  Architecture  │
                ├────────────────┤
                │ 1. Always auth │
                │ 2. Least priv  │
                │ 3. Assume breac│
                │ 4. Verify every│
                │ 5. Never trust │
                └────────────────┘
                        │
                        ▼
            Service Mesh (mTLS)
            ┌─────────────────────┐
            │ • Per-service cert  │
            │ • 24h rotation      │
            │ • SAN = service name│
            │ • Enforced by kernel│
            └─────────────────────┘
                        │
                        ▼
            ┌─────────────────────┐
            │ Sandbox Enforcement │
            │ • 5 levels (0-4)   │
            │ • AI at max level 2│
            │ • Kernel at level 4│
            │ • User data at lvl 1│
            └─────────────────────┘
                        │
                        ▼
            ┌─────────────────────┐
            │ Immutable Audit     │
            │ • Hash chain        │
            │ • HSM-signed        │
            │ • Tamper-evident    │
            │ • 90-day retention  │
            └─────────────────────┘
```

### 24.9 Performance Model

| Component | Max Latency | Throughput | Scaling |
|-----------|-------------|------------|---------|
| Kernel syscall | 1µs | 1M/s | Single core |
| IPC (user→user) | 5µs | 200K/s | Per channel |
| REST API (internal) | 10ms | 10K/s per service | Horizontal (K8s) |
| AI inference (tiny) | 100ms | 100/s (GPU) | Vertical (GPU) |
| AI inference (medium) | 2s | 10/s (GPU) | Horizontal (multi-GPU) |
| AI inference (cloud) | 5s | 100/s | Cloud auto-scale |
| Database read | 5ms | 10K/s | Read replicas |
| Database write | 10ms | 5K/s | Sharding |
| Memory query | 50ms | 500/s | Shard by workspace |
| Search query | 100ms | 200/s | Shard by index |
| Sync operation | 500ms | 50/s per device | Per-device channels |
| Notification delivery | 100ms | 1K/s | Horizon (fan-out) |
| Event bus publish | 5ms | 50K/s | NATS cluster |
| UI render (desktop) | 16ms (60fps) | N/A | GPU compositing |

### 24.10 Memory Model

| Component | Base Memory | Per-User | Scaling |
|-----------|-------------|----------|---------|
| Kernel | 64MB | 0 | Fixed |
| Platform Services (7) | 350MB | 0 | Fixed |
| AI Services (7) | 500MB | 0 | Fixed (models shared) |
| Core Agents (6) | 180MB | 0 | Fixed |
| Workspace Agent (1 active) | 30MB | 0 | Per workspace (lazy) |
| Temp Agent | ~5MB | 0 | Ephemeral |
| User session | 0 | ~10MB | Per active user |
| Per-workspace memory | 0 | ~50MB | Per workspace |
| Cache (Redis) | 256MB | 0 | Configurable |
| **Total (1 user, idle)** | **~1.2GB** | | |
| **Total (1 user, active)** | **~1.5GB** | | |
| **Total (100 users)** | **~3.5GB** | | Shared services dominate |

### 24.11 AI Routing Architecture

(See Section 8 for full detail — this is the summary diagram)

```
Request → DecisionService (:8310)
  ├─ Level 1: No AI (70%)
  ├─ Level 2: Agent Manager (:8210) → AI Router (:8330)
  │             │
  │             ├─ Tiny Local (500M): classify, extract, route
  │             ├─ Medium Local (3B): reason, plan, summarize
  │             ├─ Large Local (7B): complex analysis, code gen
  │             └─ Cloud LLM: creative, research (cost-aware)
  │
  └─ Level 3: Orchestrator (:8011) → Council (multi-agent)
                │
                └─ Parallel reasoning → Weighted vote → Response
```

### 24.12 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       SINGLE NODE (Local)                        │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ichin (binary)                                          │    │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │    │
│  │  │Kernel│ │Plat  │ │AI    │ │App   │ │UI    │ │DB    │ │    │
│  │  │Layer │ │Svcs  │ │Svcs  │ │Engine│ │Layer │ │(emb) │ │    │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  OS: Linux (Debian/Ubuntu/Fedora) or macOS or Windows (WSL2)    │
│  CPU: x86_64 or ARM64 (Apple Silicon)                           │
│  RAM: 8GB minimum, 16GB recommended                             │
│  Disk: 20GB minimum, SSD recommended                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      MULTI NODE (Cloud)                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Control     │  │  Worker Pool │  │  Data Layer  │          │
│  │  Plane       │  │              │  │              │          │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │          │
│  │ │Orchestrat│ │  │ │Platform  │ │  │ │Postgres  │ │          │
│  │ │Identity  │ │  │ │Services  │ │  │ │(Primary) │ │          │
│  │ │Agent Mgr │ │  │ │AI Models │ │  │ │Redis     │ │          │
│  │ │Deploy Mgr│ │  │ │App Engine│ │  │ │Qdrant    │ │          │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  Orchestration: Kubernetes (EKS/GKE/AKS)                        │
│  Auto-scaling: Horizontal Pod Autoscaler (CPU/Memory)           │
│  Service mesh: Istio/Linkerd (mTLS)                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     HYBRID (Edge + Cloud)                        │
│                                                                  │
│  ┌──────────────┐                    ┌──────────────┐           │
│  │  Edge Node   │    mTLS tunnel     │  Cloud       │           │
│  │  (Local)     │◄──────────────────►│  (Remote)    │           │
│  │              │                    │              │           │
│  │ • UI Layer   │                    │ • AI Router  │           │
│  │ • Local AI   │                    │ • Large LLM  │           │
│  │ • Cache      │                    │ • Knowledge  │           │
│  │ • App Engine │                    │ • Heavy comp │           │
│  │ • Offline    │                    │ • Backup     │           │
│  └──────────────┘                    └──────────────┘           │
│                                                                  │
│  Sync: CRDT-based (offline queue → delta sync)                  │
│  AI Fallback: Local tiny model when offline                     │
└─────────────────────────────────────────────────────────────────┘
```

### 24.13 Infrastructure Architecture

| Component | Local | Cloud | Enterprise |
|-----------|-------|-------|------------|
| **Container runtime** | Podman/Docker | Docker | containerd |
| **Orchestration** | docker-compose | Kubernetes | OpenShift/Rancher |
| **Service mesh** | None | Istio | Istio + mTLS |
| **Database** | SQLite/Sled (embedded) | PostgreSQL (RDS) | PostgreSQL (HA) |
| **Cache** | Redis (container) | ElastiCache | Redis (sentinel) |
| **Vector DB** | Qdrant (container) | Qdrant Cloud | Self-hosted Qdrant |
| **AI inference** | Ollama/local | SageMaker/Bedrock | Self-hosted (Triton) |
| **Storage** | Local SSD | EBS/PersistentVolume | SAN/NFS HA |
| **Monitoring** | Prometheus + Grafana | CloudWatch/Grafana | Prometheus + Thanos |
| **Logging** | JSON files | CloudWatch Logs | ELK/Splunk |
| **Tracing** | Jaeger (container) | X-Ray | Jaeger/Honeycomb |
| **Backup** | Local snapshot | S3/Velero | Veeam/CommVault |
| **CI/CD** | GitHub Actions | GitHub Actions | GitLab CI/ArgoCD |
| **DNS** | CoreDNS (local) | Route53/Cloud DNS | Internal DNS |
| **Certificate** | mkcert (dev) | AWS ACM | Internal CA + HSM |
| **Network** | Docker bridge | VPC + ALB/NLB | SDN + Firewall |

### 24.14 Developer Architecture

```
                    ┌─────────────────────────────────────┐
                    │       Developer Platform            │
                    │       (port 8420)                   │
                    └──────┬──────────────────────┬───────┘
                           │                      │
        ┌──────────────────┼──────────────────────┼──────────────────┐
        │                  │                      │                  │
        ▼                  ▼                      ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│API Gateway   │  │ICHIN CLI     │  │SDK Packages    │  │Doc Engine    │
│(REST/gRPC)   │  │(ichin)       │  │(TS/Py/Rust/REST)│  │(OpenAPI)     │
│             │  │             │  │                │  │             │
│• Versioned  │  │• pkg/svc/wf │  │• @ichin/sdk   │  │• Auto-genera │
│• Rate limit │  │  conf/dev   │  │• ichin-sdk-py  │  │• Interactive │
│• Auth       │  │  ai/focus   │  │• ichin-sdk-rs  │  │• Try it now  │
│• Deprecation│  │  sync/debug │  │• OpenAPI spec  │  │• SDK examples│
└──────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
        │                  │                      │                  │
        └──────────────────┴──────────────────────┴──────────────────┘
                           │
                           ▼
                    ┌─────────────────────────────────────┐
                    │       Developer Workflow             │
                    │                                       │
                    │  1. `ichin dev init`                  │
                    │  2. Write app in TS/Py/Rust           │
                    │  3. `ichin dev sim` (sandbox test)    │
                    │  4. `ichin dev test` (run tests)      │
                    │  5. `ichin pkg publish` (to registry) │
                    └─────────────────────────────────────┘
```

### 24.15 Scalability Strategy

| Dimension | Strategy | Implementation |
|-----------|----------|---------------|
| **Users** | Horizontal scaling via K8s | Stateless services scale with HPA. Stateful services use read replicas |
| **AI compute** | Model tiering + queue | Tiny/Medium models local (GPU). Large/Cloud async with queue |
| **Storage** | Per-service DB + sharding | Each service owns its data. Shard by workspace_id |
| **Memory** | Layered with decay + pruning | 6-layer hierarchy, automatic consolidation (Section 4) |
| **Search** | Shard by index type + workspace | File/Semantic/Keyword indices partitioned by workspace |
| **Notifications** | Fan-out via event bus | Redis Streams consumer groups for multi-subscriber delivery |
| **Sync** | Per-device delta streams | CRDT with vector clocks, no central bottleneck |
| **Kernel** | Per-CPU run queues + NUMA | One scheduler queue per CPU core. NUMA-aware memory allocation |

**Target: 100K concurrent users (cloud deployment)**

| Bottleneck | Limit | Solution |
|-----------|-------|----------|
| AI inference | 100 req/s (single GPU) | Scale out GPU pool, queue with priority |
| Database writes | 5K/s per shard | Shard by workspace_id (assumes 10 workspaces/user) |
| Event bus | 50K/s per NATS node | NATS cluster with leaf nodes |
| API gateway | 10K/s per instance | Horizontal scale (K8s HPA) |
| Sync | 50 ops/s per device | Per-device channel, delta compression |

### 24.16 Migration Plan

**Phase 1: Foundation (Months 1-2)**

| Step | Action | Services Affected |
|------|--------|-------------------|
| 1.1 | Create Identity Service (port 8100) | Auth extracted from Account service |
| 1.2 | Create Session Manager (port 8102) | Token management extracted |
| 1.3 | Create Permission Engine (port 8103) | Replace JS `packages/permissions-model/` |
| 1.4 | Implement service-to-service mTLS | All services |
| 1.5 | Create Event Bus (NATS/Redis Streams) | Event-driven foundation |

**Phase 2: AI Restructuring (Months 2-3)**

| Step | Action | Services Affected |
|------|--------|-------------------|
| 2.1 | Create Agent Manager (port 8210) | Replace `services/agents/` |
| 2.2 | Create DecisionService (port 8310) | Add pre-filter before Orchestrator |
| 2.3 | Slim Orchestrator to Level 3 only | Remove Level 1/2 logic |
| 2.4 | Create AI Router (port 8330) | Model selection |
| 2.5 | Implement 3-tier escalation | All Level 1/2 handlers |

**Phase 3: Memory & Knowledge (Months 3-4)**

| Step | Action | Services Affected |
|------|--------|-------------------|
| 3.1 | Create Knowledge Graph (port 8320) | New redb-based graph store |
| 3.2 | Refactor Memory Engine to 6 layers | Add consolidation + decay |
| 3.3 | Implement multi-modal search | Vector + Graph + Keyword + DB |
| 3.4 | Create Search Gateway (port 8340) | Unified search API |

**Phase 4: Infrastructure (Months 4-5)**

| Step | Action | Services Affected |
|------|--------|-------------------|
| 4.1 | Create Notification Service (port 8370) | Central notification |
| 4.2 | Create Sync Service (port 8350) | Multi-device sync |
| 4.3 | Create Package Manager (port 8380) | App packaging |
| 4.4 | Create Focus Controller (port 8220) | Graduated focus |

**Phase 5: Observability & Polish (Months 5-6)**

| Step | Action | Services Affected |
|------|--------|-------------------|
| 5.1 | Create Observability stack (ports 8390-93) | Logging, metrics, tracing |
| 5.2 | Create Deployment Manager (port 8430) | Deployment profiles |
| 5.3 | Implement full test suite | All services |
| 5.4 | Accessibility audit + fixes | UI layers |
| 5.5 | Performance optimization | All services |

### 24.17 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **New service count too high** | High | Medium | Combine platform services (e.g., Identity + Session + Device), prioritize by criticality |
| **Python-to-Rust migration cost** | High | High | Keep Python for AI services, only rewrite platform layer in Rust |
| **mTLS mesh complexity** | Medium | High | Start with Ed25519 headers, migrate to mTLS after stable |
| **Knowledge Graph storage cost** | Medium | Medium | Use embedded redb, Neo4j only for enterprise |
| **Agent Manager as SPOF** | Medium | High | Active-passive HA with Redis leader election |
| **AI Router model availability** | Medium | Medium | Graceful fallback: cloud → large local → medium local → tiny |
| **CRDT complexity for sync** | Medium | Medium | Start with LWW for settings, CRDT only for collaborative data |
| **Kernel bare-metal bugs** | High (development) | High | Extensive QEMU test harness, gradual deployment |
| **User adoption** | Low | High | Focus on offline-first + keyboard-first (developer appeal) |
| **Port conflicts with existing software** | Low | Medium | Configurable port range, documented ports |

### 24.18 Trade-off Analysis

| Decision | Option A | Option B | Chosen | Rationale |
|----------|----------|----------|--------|-----------|
| **Service language** | All Python | Rust for platform + Python for AI | Hybrid | Platform needs performance/correctness; AI needs ecosystem speed |
| **Service mesh** | Ed25519 headers | mTLS | mTLS (Phase 2) | Ed25519 as interim for Phase 1 |
| **Knowledge graph backend** | Neo4j | redb | redb (embedded) | No external dependency; Neo4j optional |
| **Event bus** | Redis Streams | NATS | NATS (preferred) | NATS has better reliability, Redis as fallback |
| **Sync CRDT** | Custom | Automerge/Yrs | Custom (simple) | Only need basic CRDT, not full collaborative editing |
| **AI routing** | Rule-based | ML-based | Rule-based | Deterministic, verifiable, no cold start |
| **Memory decay** | Fixed half-life | Learned decay | Fixed + learned | Fixed for predictability, learned to tune over time |
| **Auth token** | JWT | PASETO | PASETO | More secure (no None algorithm, simpler crypto) |
| **Testing framework** | Custom | pytest/k6/etc | Standard tools | Ecosystem maturity, no need to reinvent |

### 24.19 Future Roadmap

| Timeframe | Milestone | Deliverables |
|-----------|-----------|--------------|
| **Q3 2026** | Foundation complete | Identity, Session, Permission, Event Bus, mTLS migration |
| **Q4 2026** | AI restructured | Agent Manager, DecisionService, AI Router, slim Orchestrator |
| **Q1 2027** | Memory 2.0 | Knowledge Graph, 6-layer memory, multi-modal search |
| **Q2 2027** | Infrastructure complete | Notifications, Sync, Package Manager, Focus Controller |
| **Q3 2027** | Production ready | Observability, Deployment Manager, full test suite, a11y |
| **Q4 2027** | Beta release | ISO builder with refactored code, cloud deployment |
| **2028+** | Post-release | Native mobile apps, plugin marketplace, enterprise SSO, AI fine-tuning studio, WASM app support |

### 24.20 Production Readiness Checklist

**Security**
- [ ] All services authenticate via mTLS or Ed25519
- [ ] Permission Engine enforces RBAC/ABAC
- [ ] Audit log is immutable (hash chain)
- [ ] AI cannot escalate privilege (kernel-enforced)
- [ ] All inter-service traffic encrypted
- [ ] Code signing enforced for app installation
- [ ] Secure Boot + TPM measured boot (bare-metal)
- [ ] Memory isolation between sandboxes (kernel-enforced)
- [ ] Secrets managed via vault (not env files)

**Performance**
- [ ] Cold boot < 2s to usable desktop
- [ ] AI Level 1 latency < 50ms (deterministic)
- [ ] AI Level 2 latency < 2s
- [ ] AI Level 3 latency < 10s
- [ ] UI at 60fps
- [ ] Idle memory < 500MB
- [ ] No single service can starve resources (cgroups)
- [ ] Cache hit rate > 80%

**Reliability**
- [ ] All services have health checks
- [ ] Dead services auto-restart (watchdog)
- [ ] Database backups automated
- [ ] No single point of failure (K8s HA)
- [ ] Graceful degradation (offline mode)
- [ ] Rate limiting on all APIs
- [ ] Circuit breakers for inter-service calls
- [ ] Retry with exponential backoff on failure

**Testing**
- [ ] Unit test coverage > 90%
- [ ] Integration tests for every API endpoint
- [ ] Security tests pass (OWASP Top 10)
- [ ] Load test at 1000 concurrent users
- [ ] AI evaluation benchmarks passing
- [ ] Kernel tests in QEMU (every syscall)
- [ ] Regression test suite for all known bugs

**Observability**
- [ ] All services emit structured JSON logs
- [ ] Key metrics exported to Prometheus
- [ ] Distributed tracing across all services
- [ ] Alerting configured for critical conditions
- [ ] Dashboard for system health overview
- [ ] Log retention and rotation configured
- [ ] Crash reporting with core dumps

**Developer Experience**
- [ ] API documentation auto-generated (OpenAPI)
- [ ] CLI tool functional (ichin --help)
- [ ] SDK packages published (TS/Py/Rust)
- [ ] App templates for common patterns
- [ ] Integration test mock services available
- [ ] Clear migration guide from v1 to v2
- [ ] Changelog maintained

**Deployment**
- [ ] Docker images build and push via CI
- [ ] K8s manifests validated
- [ ] ISO builder produces bootable image
- [ ] Edge node configuration tested
- [ ] Upgrade path from v1 to v2 documented
- [ ] Rollback procedure documented and tested
- [ ] Backup and restore procedure documented

---

## Summary

The ICHIN OS architectural refactoring preserves the full vision — AI-first, minimalist ambient interface, privacy-first, modular, multi-agent intelligence — while achieving production-grade readiness through:

1. **-80% AI cost** by replacing AI with deterministic software in 20+ domains
2. **-88% AI invocations** through 3-tier decision escalation (70/25/5 split)
3. **-85% idle memory** from hierarchical agent architecture (6 core + 4 lazy workspace + ephemeral temp)
4. **100x faster cold boot** through parallel initialization and lazy loading
5. **New platform layer** with identity, device management, sessions, permissions
6. **Knowledge Graph + Vector + Keyword + DB** multi-modal search
7. **Six-level memory hierarchy** with automatic decay, consolidation, and meaning extraction
8. **Five-level graduated focus mode** per workspace with scheduled auto-switching
9. **Six-tier AI routing** for optimal cost/latency/privacy trade-offs
10. **Strict service boundaries** with mTLS, event-driven architecture, and zero shared state
11. **Full observability** with structured logging, metrics, tracing, and immutable audit
12. **Accessible, localized, keyboard-first** UI with i18n and WCAG 2.2 AA/AAA compliance
13. **Six deployment profiles** from development to enterprise air-gapped
14. **20-item production readiness checklist** covering security, performance, reliability, testing, observability, developer experience, and deployment

**New services created:** 17  
**Services removed/merged:** 2  
**Services refactored:** 5  
**Total service count (new normal):** 27  
**Lines of code estimated:** ~50,000 new, ~15,000 removed, ~10,000 refactored  
**Engineering effort estimate:** 6 months (3 senior engineers)
