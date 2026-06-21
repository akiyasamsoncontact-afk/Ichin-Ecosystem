# ICHIN OS AI Integration Layer — Gateway Configuration

## Overview

The AI Gateway is the single entry point (`/ai/query`) for all AI operations.
It routes requests to the appropriate internal service based on task type,
model requirements, and current load.

```
           ┌─────────────────────────────────────┐
           │         AI Gateway (/ai/query)       │
           │  ┌─────────┐ ┌──────┐ ┌──────────┐  │
           │  │ Router   │→│Queue │→│ Rate     │  │
           │  │(type)    │ │(LB)  │ │ Limiter  │  │
           │  └─────────┘ └──────┘ └──────────┘  │
           └──────┬──────────┬──────────┬─────────┘
                  │          │          │
           ┌──────▼──┐ ┌────▼───┐ ┌───▼────────┐
           │Small    │ │Cloud   │ │Specialized  │
           │Local    │ │LLM     │ │Coding       │
           │Model    │ │(GPT-4) │ │(Claude)     │
           └──────┬──┘ └────┬───┘ └───┬────────┘
                  │          │          │
           ┌──────▼──────────▼──────────▼────────┐
           │         Internal Services           │
           │  orchestrator │ agents │ memory     │
           └─────────────────────────────────────┘
```

## Model Routing Rules

| Task Type              | Route To      | Model                | Priority |
|------------------------|---------------|----------------------|----------|
| Fast / simple queries  | Small Local   | phi-3-mini, TinyLlama| High     |
| Complex reasoning      | Cloud LLM     | GPT-4, Claude 3      | Medium   |
| Code generation        | Specialized   | Claude 3, CodeLLaMA  | Medium   |
| Memory / embedding     | Embedding     | text-embedding-ada   | Low      |
| Agent orchestration    | Orchestrator  | GPT-4o               | High     |
| Multi-modal            | Cloud LLM     | GPT-4V, Gemini       | Low      |

## Single Entry Point: `/ai/query`

### Request Format
```json
{
  "query": "Plan my study schedule for biology",
  "user_id": "uuid",
  "session_id": "uuid",
  "mode": "fast | balanced | deep",
  "context": {
    "previous_messages": [],
    "user_preferences": {},
    "current_workflow_id": "uuid"
  },
  "attachments": []
}
```

### Response Format
```json
{
  "response_id": "uuid",
  "text": "Here is your study schedule...",
  "sources": ["memory:biology_notes_2024", "web:khan_academy"],
  "model_used": "gpt-4",
  "processing_time_ms": 2340,
  "follow_up_actions": [
    {"type": "save_memory", "data": {}},
    {"type": "create_calendar_event", "data": {}}
  ]
}
```

## Internal Routing

The gateway classifies each query and routes internally:

```
/ai/query → AI Gateway
  ├─ mode=fast           → phi-3-mini (local container)
  ├─ mode=balanced       → orchestrator → GPT-4o
  ├─ mode=deep           → orchestrator → agents → Claude 3
  ├─ intent=memory       → memory-engine → embedding model
  └─ intent=coding       → ai-studio → Claude 3 / CodeLLaMA
```

## Configuration

```yaml
ai_gateway:
  enabled: true
  endpoint: "/ai/query"

  rate_limiting:
    requests_per_minute: 60
    burst: 10
    strategy: "token_bucket"

  models:
    local:
      - name: "phi-3-mini"
        endpoint: "http://localhost:8080/v1/chat/completions"
        max_tokens: 4096
        timeout_ms: 5000
        priority: ["fast", "simple"]
    cloud:
      - name: "gpt-4"
        provider: "openai"
        api_key: "${OPENAI_API_KEY}"
        max_tokens: 8192
        timeout_ms: 30000
        priority: ["reasoning", "planning"]
      - name: "claude-3"
        provider: "anthropic"
        api_key: "${ANTHROPIC_API_KEY}"
        max_tokens: 8192
        timeout_ms: 30000
        priority: ["coding", "analysis"]
    embedding:
      - name: "text-embedding-ada"
        provider: "openai"
        dimensions: 1536
        timeout_ms: 3000

  fallback:
    strategy: "degraded"  # degraded | error | queue
    local_only: true
    queue_overflow: "reject"
```
