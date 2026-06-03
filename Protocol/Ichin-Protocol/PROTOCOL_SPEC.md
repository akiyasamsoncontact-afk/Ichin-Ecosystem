# ICHIN Protocol (ICHINP) Specification

## 1. Overview

ICHINP is a secure, minimal, HTTP-inspired application protocol for the ICHIN ecosystem. It runs over TCP with mandatory TLS 1.3 encryption and uses a 3-stage connection lifecycle.

| Property | Value |
|----------|-------|
| Transport | TCP |
| Default Port | 4889 |
| Encryption | TLS 1.3 (mandatory) |
| Encoding | UTF-8 |
| Message Format | Plaintext headers (handshake) → JSON (requests/responses) |

---

## 2. State Diagram

```
CLOSED
  │
  │ TCP connect (with TLS)
  ▼
HANDSHAKE ◄────────────────────────────┐
  │                                     │
  ├── Version match + accept ──┐        │
  │                            │        │
  │                            ▼        │
  │                    SECURE UPGRADE   │
  │                    (implicit via    │
  │                     TLS 1.3)        │
  │                            │        │
  │                            ▼        │
  │                    ESTABLISHED ─────┤
  │                      │  (persistent)│
  │                      │              │
  │                      ├── Request ───┤
  │                      ├── Response ──┤
  │                      │              │
  │                      └── Timeout ───┤
  │                                     │
  ├── Version mismatch ──► CLOSED       │
  └── Reject ───────────► CLOSED        │
                                        │
  ◄─────────────────────────────────────┘
```

### States

| State | Description |
|-------|-------------|
| `CLOSED` | No connection. Initial and terminal state. |
| `HANDSHAKE` | Client sent protocol info, server evaluating. |
| `SECURE_UPGRADE` | TLS 1.3 encryption active; no plaintext beyond this point. |
| `ESTABLISHED` | Session active. Request/Response exchange in progress. |
| `PERSISTENT` | Connection kept alive for multiple exchanges (default behavior). |

---

## 3. Connection Lifecycle

### Phase 1: Handshake

The client initiates a TCP connection, negotiates TLS 1.3, then sends a handshake:

**Client sends:**
```
ICHINP/1.0
target-host: example.ichin
client-id: ichin-client/1.0
```

**Server accepts:**
```
ICHINP/1.0 100 ACCEPT
server-version: ichind/1.0
session-id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
encryption: tls-1.3
```

**Server rejects (version mismatch):**
```
ICHINP/1.0 505 VERSION-MISMATCH
```

On rejection, the server immediately closes the connection.

### Phase 2: Secure Upgrade

Implicitly handled by TLS 1.3 in the initial TCP connection. After the handshake header exchange, all subsequent data is encrypted JSON.

### Phase 3: Request / Response

After handshake acceptance, the client sends JSON requests and the server responds with JSON. Each message is a single line terminated by `\n`.

#### Request Format

```json
{
  "method": "GET",
  "path": "/resource",
  "headers": {
    "content-type": "application/json"
  },
  "body": {},
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Supported methods:** `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`

#### Response Format

```json
{
  "status": 200,
  "message": "OK",
  "headers": {},
  "body": {},
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

## 4. Status Codes

| Code | Message | Description |
|------|---------|-------------|
| 200 | OK | Success |
| 400 | BAD REQUEST | Malformed JSON or invalid request |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Access denied |
| 404 | NOT FOUND | Resource does not exist |
| 500 | INTERNAL ERROR | Server-side failure |

---

## 5. Persistent Connections

Connections are persistent by default. After a response is sent, the connection remains open for the next request. The server may close the connection after a configurable idle timeout (default: 60 seconds). Clients should be prepared to reconnect.

---

## 6. Session Tracking

Each successful handshake assigns a unique `session_id` (UUID v4). The client MUST include this in every subsequent request. The server uses it to maintain session state.

---

## 7. Example Exchange

```
Step 1: TCP connect to 127.0.0.1:4889 + TLS 1.3 handshake
Step 2: Client sends handshake over TLS channel:

  C → S: ICHINP/1.0
  C → S: target-host: ping.ichin
  C → S: client-id: ichin-client/1.0

Step 3: Server responds:

  S → C: ICHINP/1.0 100 ACCEPT
  S → C: server-version: ichind/1.0
  S → C: session-id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
  S → C: encryption: tls-1.3

Step 4: Client sends JSON request:

  C → S: {"method":"PING","path":"/","headers":{},"body":{},"session_id":"a1b2c3d4-e5f6-7890-abcd-ef1234567890"}

Step 5: Server responds:

  S → C: {"status":200,"message":"OK","headers":{},"body":{"reply":"pong"},"session_id":"a1b2c3d4-e5f6-7890-abcd-ef1234567890"}

Step 6: Connection remains open for further requests.
```

---

## 8. Wire Format (Packet-Level)

All data is transmitted over a TLS 1.3 encrypted TCP stream.

### Handshake (plaintext within TLS):
- Line 1: `ICHINP/<major>.<minor>` followed by `\n`
- Line 2: `target-host: <host>` followed by `\n`
- Line 3: `client-id: <id>` followed by `\n`
- Empty line to terminate handshake (optional for future extensibility)

### Request/Response (encrypted JSON):
- Single line of minified JSON terminated by `\n`
- No framing headers; newline acts as delimiter
- Maximum message size: 1 MB (configurable)

---

## 9. Security Considerations

- TLS 1.3 is mandatory. No plaintext fallback is permitted.
- Self-signed certificates are acceptable for experimental use.
- Session IDs should be treated as bearer tokens.
- Rate limiting and request size limits should be enforced by the server.
