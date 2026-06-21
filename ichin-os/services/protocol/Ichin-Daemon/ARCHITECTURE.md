# IchinD — Server Architecture

## 1. System Overview

IchinD is the core application runtime and web server for the ICHIN ecosystem. It accepts ICHINP connections, routes requests to handlers, executes application logic, and manages real-time connections.

```
┌─────────────────────────────────────────────────────────┐
│                    IchinD Server                         │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Network   │  │ Router   │  │ Middle-  │  │ Session  │ │
│  │ Layer     │─▶│          │─▶│ ware     │─▶│ Manager  │ │
│  │ (ICHINP)  │  │          │  │ Pipeline │  │          │ │
│  └──────────┘  └────┬─────┘  └──────────┘  └──────────┘ │
│                      │                                    │
│                      ▼                                    │
│  ┌────────────────────────────────────────────┐          │
│  │            Handler Dispatch                  │          │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────────┐ │          │
│  │  │Static   │ │Sandbox   │ │Realtime      │ │          │
│  │  │File     │ │Runtime   │ │Event System  │ │          │
│  │  │Server   │ │(Plugins) │ │              │ │          │
│  │  └─────────┘ └──────────┘ └──────────────┘ │          │
│  └────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌────────────┐
   │ IchinDNS │  │ IchinCA  │  │ ICHINP     │
   │ (port    │  │ (port    │  │ (port 4889) │
   │  4890)   │  │  4891)   │  │            │
   └──────────┘  └──────────┘  └────────────┘
```

---

## 2. Server Lifecycle

```
START → LOAD_APPS → BIND → ACCEPT → HANDLE → SHUTDOWN
```

| Phase | Description |
|-------|-------------|
| **START** | Load config, init modules |
| **LOAD_APPS** | Discover and load app plugins from `apps/` |
| **BIND** | Start TCP listener on port 4889 with TLS |
| **ACCEPT** | Accept ICHINP connections |
| **HANDLE** | Process request → route → middleware → handler → respond |
| **SHUTDOWN** | Save state, close connections |

---

## 3. Routing System

The router maps `(method, path)` pairs to handlers with middleware support.

### Static Routes
```
GET  /               → static_home
POST /api/data       → api_handler
```

### Parameterized Routes
```
GET  /user/:id        → user_handler(params={id: ...})
GET  /blog/:slug      → blog_handler(params={slug: ...})
```

### Route Resolution
1. Try exact match first
2. Try parameterized match
3. Return 404 if no match

---

## 4. Middleware Pipeline

```
Request → [Logger] → [Auth] → [RateLimit] → Handler → Response
```

Each middleware can:
- Modify the request (add headers, validate tokens)
- Short-circuit with an error response
- Pass through to the next middleware or handler

Built-in middleware:
- **Logger**: Logs method, path, duration, status
- **Auth**: Validates session tokens
- **RateLimit**: Per-session request rate limiting

---

## 5. Sandbox (Plugin Runtime)

Apps are Python modules in `apps/<app_name>/main.py` that expose handler functions.

```
apps/hello/
├── main.py       # Handler functions
├── route.json    # Route definitions
└── static/       # Static assets
```

### Handler signature
```python
def handler(request, params, session):
    return {"status": 200, "body": {"message": "Hello"}}
```

### route.json format
```json
{
  "routes": [
    {"method": "GET", "path": "/", "handler": "index"},
    {"method": "POST", "path": "/echo", "handler": "echo"}
  ]
}
```

---

## 6. Static File Server

- Serves files from `apps/<app_name>/static/`
- MIME type detection by extension
- Cache with TTL (default: 300s)
- Returns 404 for missing files

---

## 7. Real-Time Event System

Persistent connections that support event-based messaging:

```
Client connects   →  "connected" event
Client sends msg  →  "message" event with payload
Server broadcasts →  "broadcast" event to all clients
Client disconnects →  "disconnected" event
```

---

## 8. Integration with ICHIN Ecosystem

| Service | Role | Port |
|---------|------|------|
| **ICHINP** | Wire protocol for all communication | 4889 |
| **IchinDNS** | Resolves `.ichin` domains to addresses | 4890 |
| **IchinCA** | Issues and validates TLS certificates | 4891 |
| **IchinD** | Application runtime and web server | 4889 |

IchinD uses IchinDNS for domain resolution and IchinCA for certificate validation during the request flow.
