# AI Platform Architecture

## Overview

The AI platform is the brain of Ichin OS. It provides unified AI capabilities to every service through a modular, layered architecture.

```
┌────────────────────────────────────────────────────────┐
│                    User Interfaces                      │
│   Desktop · Browser · CLI · Voice · API · Mobile       │
└────────────────────────┬───────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│                  Orchestrator                           │
│   Request routing · Agent selection · Mode weighting   │
│   Conflict resolution · Context building               │
└────────────────────────┬───────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│                    Agent System                         │
│   Study · Coding · Learning · Productivity · Focus     │
│   Security · Calendar · Research · Browser · Voice     │
│   Metasearch                                           │
└────────────────────────┬───────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│                  AI Router                              │
│   Provider abstraction · Routing strategies            │
│   Failover · Rate limiting · Offline fallback          │
└────────────────────────┬───────────────────────────────┘
                         │
┌───────────┬────────────┼────────────┬──────────────────┐
│           │            │            │                  │
▼           ▼            ▼            ▼                  ▼
┌──────┐ ┌──────┐  ┌────────┐  ┌────────┐  ┌──────────────┐
│Local │ │Cloud │  │Embedded│  │Special │  │  Fallback    │
│Models│ │Models│  │Models  │  │Engines │  │  (Rule-based)│
└──────┘ └──────┘  └────────┘  └────────┘  └──────────────┘
```

## Components

### 1. AI Router (Port 8020)
- **8 providers**: OpenAI, Anthropic, Google, Groq, Mistral, DeepSeek, Ollama, llama.cpp
- **5 routing strategies**: latency, cost, quality, privacy, balanced
- **Auto-failover**: transparent fallback on provider failure
- **Rate limiting**: per-provider and per-user quotas
- **Health checks**: continuous provider monitoring
- **Offline fallback**: rule-based responses when no provider available
- **Streaming**: SSE support for real-time responses

### 2. Agent System (Port 8012)

| Agent | Capability | Confidence | Risk |
|-------|------------|------------|------|
| Study | Learning optimization, quiz generation | 0.90 | 0.10 |
| Coding | Code generation, debugging, review | 0.85 | 0.20 |
| Learning | Concept explanation, skill trees | 0.88 | 0.08 |
| Productivity | Task management, workflow optimization | 0.85 | 0.15 |
| Focus | Distraction blocking, deep work | 0.80 | 0.12 |
| Security | Threat detection, permission auditing | 0.92 | 0.25 |
| Calendar | Scheduling, event detection | 0.95 | 0.05 |
| Research | Information gathering, source synthesis | 0.90 | 0.10 |
| Browser | Browser automation, content extraction | 0.88 | 0.20 |
| Voice | TTS/STT, personality management | 0.90 | 0.10 |
| Metasearch | Multi-engine search aggregation | 0.92 | 0.05 |

Workspace-to-agent mapping:
- **Study**: study, learning, productivity, focus, research
- **Coding**: coding, research, productivity, focus, security
- **Learning**: learning, study, research, productivity
- **Productivity**: productivity, calendar, focus, research
- **Research**: research, learning, study, productivity

### 3. Memory Engine (Port 8013)
- **Multi-layer architecture**: Ephemeral → Working → Long-term → Structured
- **Decay system**: memories fade over time unless reinforced
- **Importance scoring**: more accessed = more retained
- **Quality scoring**: coherence, utility, recency, source diversity
- **Automatic promotion**: important memories move to higher layers

### 4. Knowledge Graph (Port 8070)
- **7 node types**: concept, topic, skill, project, note, task, person, tool, resource, category, goal, habit, insight
- **14 edge types**: relates_to, prerequisite, extends, part_of, example_of, used_by, created_by, references, depends_on, similar_to, opposite_of, next_step, mastered, learning, interested
- **Pseudo-embeddings**: 128-dimensional vectors for semantic search
- **Multi-depth traversal**: BFS with configurable depth
- **Workspace-specific maps**: each workspace has its own knowledge graph

### 5. Voice Engine (Port 8030)
- **6 TTS engines**: kokoro, piper, XTTS v2, OpenAI, ElevenLabs, edge-tts
- **4 STT engines**: whisper (local), whisper (API), deepgram, vosk
- **8 voice personalities**: neutral, warm, professional, energetic, calm, socratic, mentor, friend
- **AI Orb state management**: visual feedback for voice state
- **WebSocket streaming**: low-latency real-time audio
- **Local-first**: default to local execution; cloud only when explicitly enabled

### 6. Browser Engine (Port 8040)
- **15 browser actions**: navigate, click, type, extract, screenshot, scroll, etc.
- **Page Understanding Engine**: metadata, content, links, tables, forms, readability
- **Multi-step research engine**: iterative browsing and synthesis
- **Permission-based sandboxing**: passive/active/destructive levels

### 7. AI Metasearch (Port 8050)
- **15 search engines**: DuckDuckGo, Wikipedia, GitHub, Brave, Reddit, Hacker News + internal (memory, workspace, knowledge, tasks, calendar, email)
- **Deduplication**: fuzzy matching to remove duplicates
- **Weighted merge**: rank results by relevance
- **Spotlight API**: unified search across all engines and internal services

## AI Orchestration Flow

```
User Request
    │
    ▼
Orchestrator.classify() → RequestType
    │
    ▼
Orchestrator.select_agents() → List<Agent>
    │
    ▼
Agents run in parallel → List<AgentOutput>
    │
    ▼
Orchestrator.resolve_conflicts() → Unified response
    │
    ▼
Memory Engine.store() → Knowledge Graph.update()
    │
    ▼
Response to user
```

## Model Selection Strategy

The AI Router selects the best model based on:
1. **Privacy mode**: local models only
2. **Offline mode**: no cloud providers
3. **Cost optimization**: cheapest capable model
4. **Latency optimization**: fastest capable model
5. **Quality optimization**: most capable model
6. **Balanced**: weighted combination of all factors

## Offline Capabilities

- All agents can operate without internet using local models (Ollama/llama.cpp)
- Voice engine uses local TTS/STT (kokoro, piper, vosk)
- Knowledge Graph runs entirely locally
- Memory Engine runs entirely locally
- AI Metasearch falls back to internal engines (memory, workspace, knowledge graph)
- Orchestrator uses rule-based fallback when no AI provider available
