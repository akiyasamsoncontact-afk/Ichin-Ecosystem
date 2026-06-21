# Ichin OS API Reference

## Service Discovery

All services register with the event bus (Redis). The orchestrator provides service discovery.

```
GET /services/status          → All service health status
POST /services/route          → Route request to specific service
POST /orchestrate/batch       → Multi-service orchestration
```

## Orchestrator API (Port 8000)

```
POST /orchestrate             { request, workspace?, mode? }
POST /classify                { text }
POST /context                 { query }
GET  /services/status
POST /services/route          { service, endpoint, method?, body?, params? }
POST /orchestrate/batch       { request, services, workspace?, mode? }
```

## AI Router API (Port 8020)

```
POST /complete                { prompt, model?, strategy?, stream? }
POST /chat                    { messages, model?, strategy? }
POST /embed                   { text, model? }
GET  /models                  { provider?, strategy? }
GET  /providers               { }
GET  /health
```

## Voice Engine API (Port 8030)

```
POST /api/tts                 { text, voice?, personality?, speed? }
POST /api/stt                 { audio_data, language?, model? }
GET  /api/personalities       { }
POST /api/personalities       { personality }
POST /api/orb/state           { state, color?, brightness? }
GET  /api/orb/state           { }
WS   /ws/audio                WebSocket audio streaming
GET  /health
```

## Browser Engine API (Port 8040)

```
POST /api/navigate            { url, session_id?, wait_until? }
POST /api/click               { selector, session_id? }
POST /api/type                { selector, text, session_id? }
POST /api/extract             { selector?, session_id? }
POST /api/screenshot          { selector?, session_id? }
POST /api/search              { query, session_id? }
POST /api/research            { query, depth?, session_id? }
POST /api/session/create      { }
POST /api/session/close       { session_id }
GET  /api/session/{id}/tabs   { }
GET  /health
```

## AI Metasearch API (Port 8050)

```
POST /api/search              { query, engines?, limit?, page? }
POST /api/spotlight           { query, limit? }
POST /api/engines             { }
GET  /api/engines
GET  /api/cache/stats
GET  /health
```

## Mail AI API (Port 8060)

```
POST /api/process             { email }
POST /api/categorize          { email }
POST /api/summarize           { email_content }
POST /api/actions             { email_content }
POST /api/reply               { email, style?, tone? }
POST /api/rules               { rules }
GET  /health
```

## Knowledge Graph API (Port 8070)

```
POST /api/query               { query, workspace?, depth?, limit? }
POST /api/workspace           { workspace }
POST /api/node                { id, type, label, properties? }
POST /api/edge                { source, target, type, properties? }
POST /api/embed               { text }
GET  /api/node/{id}
GET  /api/node/{id}/neighbors { depth? }
GET  /api/workspace/{name}
DELETE /api/node/{id}
DELETE /api/edge/{id}
GET  /health
```

## Agents API (Port 8012)

```
POST /agents/{name}/reason    { input, context? }
POST /agents/orchestrate      { input, agents?, mode? }
POST /agents/resolve          { outputs, strategy? }
GET  /agents                  { }
GET  /agents/{name}
GET  /health
```

## Memory Engine API (Port 8013)

```
POST /memory/store            { content, workspace?, metadata?, tags? }
POST /memory/query            { query, top_k?, workspace? }
POST /memory/promote          { memory_id, source_layer?, target_layer? }
POST /memory/decay            { }
POST /memory/voice            { session_id, text?, stt_latency_ms?, tts_latency_ms?, personality_used? }
POST /memory/browser          { session_id, url?, title?, content?, research_findings? }
GET  /memory/{memory_id}
GET  /memory/voice/{session_id}
GET  /memory/browser/{session_id}
DELETE /memory/{memory_id}
GET  /memory/layers
GET  /health
```

## Event Bus (Redis Pub/Sub)

```
Channel: ichin:events
Channel: ichin:notifications
Channel: ichin:voice
Channel: ichin:browser
Channel: ichin:search
Channel: ichin:orchestrator
```

## Authentication

All API requests require authentication via:
- **Bearer token** (JWT) for service-to-service
- **Session cookie** for user-to-service
- **API key** for external integrations

```
Authorization: Bearer <ichin-jwt-token>
Authorization: ApiKey <ichin-api-key>
```

## Error Responses

```json
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service temporarily unavailable",
    "details": {},
    "request_id": "uuid"
  }
}
```

## Rate Limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1620000000
```
