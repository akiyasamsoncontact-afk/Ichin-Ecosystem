# ICHIN OS Event Bus Configuration

## Architecture

The ICHIN OS event bus is a publish-subscribe message broker that enables
decoupled communication between all microservices. The system uses a
Kafka/NATS-style topology with topics, partitions, and consumer groups.

```
Service → Event Bus (topic) → Subscribers
         ↘ Event Log (persistent store) → Replay / Audit
```

## 7 Core Event Types

### 1. AI_REQUEST
- **Topic**: `ichin.events.ai.request`
- **Publisher**: orchestrator, ai-studio, ui-system
- **Description**: Fired when an AI inference request is made
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "AI_REQUEST",
    "timestamp": "ISO8601",
    "source": "orchestrator",
    "payload": {
      "request_id": "uuid",
      "model": "gpt-4 | phi-3 | claude-3",
      "input": { "messages": [], "context": {} },
      "parameters": { "temperature": 0.7, "max_tokens": 2048 }
    },
    "metadata": { "user_id": "uuid", "session_id": "uuid" }
  }
  ```
- **Consumers**: agents, memory-engine, ai-studio

### 2. AGENT_RESPONSE
- **Topic**: `ichin.events.agent.response`
- **Publisher**: agents, orchestrator
- **Description**: Published when an agent completes a task
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "AGENT_RESPONSE",
    "timestamp": "ISO8601",
    "source": "agents",
    "payload": {
      "agent_id": "string",
      "task_id": "uuid",
      "status": "completed | failed | partial",
      "output": {},
      "duration_ms": 1234
    }
  }
  ```
- **Consumers**: orchestrator, ui-system, memory-engine

### 3. MEMORY_UPDATE
- **Topic**: `ichin.events.memory.update`
- **Publisher**: memory-engine, orchestrator
- **Description**: Triggered when memory is stored, updated, or retrieved
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "MEMORY_UPDATE",
    "timestamp": "ISO8601",
    "source": "memory-engine",
    "payload": {
      "operation": "store | update | delete | query",
      "memory_id": "uuid",
      "content": {},
      "embedding_vector": [0.01, ...],
      "retrieved_results": []
    }
  }
  ```
- **Consumers**: orchestrator, agents, ai-studio

### 4. APP_EVENT
- **Topic**: `ichin.events.app`
- **Publisher**: app-runtime, desktop-ui, ui-system
- **Description**: Application lifecycle events (install, launch, crash, uninstall)
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "APP_EVENT",
    "timestamp": "ISO8601",
    "source": "app-runtime",
    "payload": {
      "app_id": "string",
      "event": "launched | crashed | installed | uninstalled",
      "details": {}
    }
  }
  ```
- **Consumers**: orchestrator, security-core, ui-system

### 5. WORKFLOW_TRIGGER
- **Topic**: `ichin.events.workflow`
- **Publisher**: orchestrator
- **Description**: Multi-step workflow orchestration events
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "WORKFLOW_TRIGGER",
    "timestamp": "ISO8601",
    "source": "orchestrator",
    "payload": {
      "workflow_id": "uuid",
      "step": "start | progress | complete | fail",
      "workflow_type": "multi_agent | pipeline | scheduled",
      "context": {},
      "next_steps": ["agent:search", "memory:store"]
    }
  }
  ```
- **Consumers**: agents, memory-engine, app-runtime, ai-studio

### 6. SECURITY_ALERT
- **Topic**: `ichin.events.security`
- **Publisher**: security-core
- **Description**: Security events and policy violations
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "SECURITY_ALERT",
    "timestamp": "ISO8601",
    "source": "security-core",
    "payload": {
      "alert_id": "uuid",
      "severity": "low | medium | high | critical",
      "category": "auth | sandbox | policy | audit",
      "message": "string",
      "affected_service": "string",
      "action_taken": "blocked | logged | flagged"
    }
  }
  ```
- **Consumers**: orchestrator, ui-system, all services

### 7. UI_STATE_CHANGE
- **Topic**: `ichin.events.ui.state`
- **Publisher**: ui-system, desktop-ui
- **Description**: UI state synchronization events
- **Schema**:
  ```json
  {
    "event_id": "uuid",
    "type": "UI_STATE_CHANGE",
    "timestamp": "ISO8601",
    "source": "ui-system",
    "payload": {
      "component": "string",
      "action": "navigate | update | focus | dismiss",
      "state": {},
      "viewport": "desktop | mobile | web"
    }
  }
  ```
- **Consumers**: ui-system, orchestrator, desktop-ui

## Event Flow for Each Type

```
AI_REQUEST:
  User Input → orchestrator publishes AI_REQUEST
    → agents picks up → processes → publishes AGENT_RESPONSE
    → memory-engine logs interaction → publishes MEMORY_UPDATE
    → ui-system receives AGENT_RESPONSE → publishes UI_STATE_CHANGE

SECURITY_ALERT:
  security-core detects violation → publishes SECURITY_ALERT
    → orchestrator pauses related workflows
    → ui-system shows notification
    → memory-engine logs for audit

WORKFLOW_TRIGGER:
  orchestrator starts workflow → publishes WORKFLOW_TRIGGER (step: start)
    → agents receive next steps → process → publish AGENT_RESPONSE
    → orchestrator advances workflow → publishes next WORKFLOW_TRIGGER
    → repeats until complete
```

## Subscription Model

### Fan-out (Broadcast)
- All subscribers in a consumer group receive every message
- Used for: SECURITY_ALERT, UI_STATE_CHANGE

### Queue (Competing Consumers)
- Messages are distributed across subscribers in a group
- Used for: AI_REQUEST, AGENT_RESPONSE (load-balanced worker pools)

### Keyed (Partitioned)
- Messages with same key go to same partition/subscriber
- Used for: MEMORY_UPDATE (by user_id), APP_EVENT (by app_id)

## Configuration

```yaml
event_bus:
  type: "nats"  # nats | kafka | redis
  url: "${EVENT_BUS_URL:nats://ichin-nats:4222}"
  consumer_group: "ichin-${SERVICE_NAME}"

  topics:
    ai_request: "ichin.events.ai.request"
    agent_response: "ichin.events.agent.response"
    memory_update: "ichin.events.memory.update"
    app_event: "ichin.events.app"
    workflow_trigger: "ichin.events.workflow"
    security_alert: "ichin.events.security"
    ui_state_change: "ichin.events.ui.state"

  persistence:
    retention_hours: 168  # 7 days
    max_message_bytes: 1048576  # 1MB
    replication_factor: 3
```
