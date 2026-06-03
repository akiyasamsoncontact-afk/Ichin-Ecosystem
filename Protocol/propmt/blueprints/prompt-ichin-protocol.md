You are designing the core networking protocol for a fictional internet system called **ICHIN**. Your task is to design and implement the **ICHIN Protocol (ICHINP)** — a secure, minimal, HTTP-inspired application protocol.

---

# GOAL

Create a working protocol specification and reference implementation that defines how clients and servers communicate inside the ICHIN ecosystem.

---

# CORE DESIGN

## Transport Layer

* Runs over TCP
* Default port: **4889**
* All communication MUST be encrypted using **TLS 1.3 by default**
* No unencrypted fallback mode is allowed

---

## Connection Lifecycle

Design a strict 3-stage connection flow:

### 1. Handshake Phase

Client sends:

* protocol version (e.g. ICHINP/1.0)
* target host (ichin domain)
* client identity (user agent string or client ID)

Server responds:

* protocol acceptance or rejection
* server version
* session ID
* encryption confirmation

If mismatch occurs → connection is immediately terminated.

---

### 2. Secure Upgrade Phase

* After handshake, communication is fully encrypted
* Session is bound to a cryptographic key
* No plaintext messages allowed beyond this point

---

### 3. Request/Response Phase

Define a structured JSON-based protocol:

### Request format:

```json
{
  "method": "GET | POST | PUT | DELETE | PATCH | OPTIONS",
  "path": "/resource",
  "headers": {
    "key": "value"
  },
  "body": {},
  "session_id": ""
}
```

### Response format:

```json
{
  "status": 200,
  "message": "OK",
  "headers": {},
  "body": {},
  "session_id": ""
}
```

---

# FEATURES

## Required Features:

* Persistent connections (like WebSockets but protocol-native)
* Session tracking
* Request timeout handling
* Error system:

  * 200 success
  * 400 bad request
  * 401 unauthorized
  * 403 forbidden
  * 404 not found
  * 500 internal error

---

## Developer Requirements:

* Provide a minimal client implementation (pseudo-code or real code in Rust/Python/Go)
* Provide a minimal server implementation
* Include a connection example (step-by-step request flow)
* Include packet-level explanation of what is sent over TCP

---

# DESIGN GOAL

This protocol should feel:

* simpler than HTTP
* more structured than raw sockets
* fully controlled inside a private ecosystem

---

# IMPORTANT LIMITATIONS

* Do NOT try to connect it to the real internet
* Do NOT depend on external DNS or HTTP
* This is a closed experimental protocol system

---

# OUTPUT FORMAT REQUIRED

Your response must include:

1. Protocol specification
2. State diagram (text form is fine)
3. Example client-server exchange
4. Minimal implementation code

