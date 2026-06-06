# Internet

Monorepo for the **Ichin** ecosystem — a private, self-contained network of services communicating over the custom ICHINP protocol over TLS 1.3.

## Projects

### Browser
Electron desktop shell with a Rust/Axum back-end (SQLite) and React 18 front-end. Features tab management, workspaces, favorites, history, command palette, and persistent session state. Enforces Ichin-only URL access with CSP security headers and CSRF protection.

- **Stack:** Electron, Rust (Axum 0.7), React 18, SQLite, Tailwind CSS
- **Ports:** Back-end on `127.0.0.1:3001`
- **Key files:** `main.js`, `Back-End/src/main.rs`, `Front-End/app.js`

### Mail
Full-featured email system with a Rust back-end and React front-end. Uses the custom ICHIN wire protocol over TLS 1.3 with Ed25519 cryptographic signing, SPF-like sender verification, rate limiting, and reputation-based spam scoring. Supports SMTP gateway for legacy interoperability.

- **Stack:** Rust (Axum 0.8, Tokio, Sled), React 18, Ed25519 (ed25519-dalek), Hickory DNS
- **Binaries:** `ichin-server`, `ichin-send`, `ichin-receive`, `ichin-gateway`
- **Key files:** `src/lib.rs`, `src/api/mod.rs`, `src/protocol/envelope.rs`, `frontend/app.js`

### Protocol
Custom protocol suite implementing the Ichin network stack over TCP/TLS 1.3. Includes four components:

- **Ichin-Protocol** — Core ICHINP wire protocol (HTTP-inspired, JSON-based, 3-stage lifecycle: handshake → secure → established)
- **Ichin-DNS** — Domain resolution for `.ichin` domains with HMAC-SHA256 response signing
- **Ichin-CA** — Certificate authority with RSA + SHA-256, DNS-01 challenge verification, and CRL revocation
- **Ichin-Daemon** — Application runtime with plugin system, routing, sessions, real-time events, and static file serving

- **Stack:** Python 3, `cryptography` library, TLS 1.3
- **Ports:** 4889 (ICHINP/Daemon), 4890 (DNS), 4891 (CA)

### Search-Engine
Registry-based search engine with a Rust/Axum back-end and Next.js 15 front-end. Features an inverted index with multi-factor ranking (title, tags, site name, content, verified status).

- **Stack:** Rust (Axum 0.8, SQLite), Next.js 15 (React 19, TypeScript)
- **API:** `GET /search?q={query}` returns ranked JSON results
- **Key files:** `server/src/search.rs`, `server/src/main.rs`, `client/src/app/page.tsx`

## Infrastructure

All services communicate over TLS 1.3 using the custom ICHINP protocol. The browser enforces strict isolation to Ichin-only resources with no external CDN dependencies. The ecosystem includes its own DNS, certificate authority, and messaging infrastructure.

## Status

Project state per recent audit:
- Architecture: 68/100
- Security: 62/100
- Scalability: 45/100
- Maintainability: 70/100
- Production Readiness: 52/100

See `INICHIN_AUDIT_REPORT.md` for full audit details and `propmt check .md` for the audit specification.

---

*Made in collaboration with AI.*

## Download

- **[ichin-browser v1.0.0 (.deb)](https://github.com/akiyasamsoncontact-afk/Internet/releases/tag/v1.0.0)** — Debian package for the Ichin Browser.
- **[ichin-mail v0.1.0 (.deb)](https://github.com/akiyasamsoncontact-afk/Internet/releases/tag/mail-v0.1.0)** — Debian package for Ichin Mail (server, send, receive, gateway).
