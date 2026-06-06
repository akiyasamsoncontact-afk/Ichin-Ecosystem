# Internet

Monorepo for the **Ichin** ecosystem — a private, self-contained network of services communicating over the custom ICHINP protocol over TLS 1.3.

## Projects

### Browser
Electron desktop shell with a Rust/Axum back-end (SQLite) and React 18 front-end. Features tab management, workspaces, favorites, history, command palette, and persistent session state. Enforces Ichin-only URL access.

- **Stack:** Electron, Rust (Axum 0.8), React 18, SQLite
- **Ports:** Back-end on `127.0.0.1:3003`
- **Key files:** `browser/Front-End/app.js`, `browser/Back-End/src/main.rs`

### Mail
Full-featured email system with a Rust back-end and React front-end. Uses the custom ICHIN wire protocol over TLS 1.3 with Ed25519 signing, SPF verification, rate limiting, and reputation-based spam scoring. Supports SMTP gateway.

- **Stack:** Rust (Axum 0.8, Tokio, Sled), React 18, Ed25519 (ed25519-dalek)
- **Port:** API on `0.0.0.0:8080`
- **Binaries:** `ichin-server`, `ichin-send`, `ichin-receive`, `ichin-gateway`
- **Key files:** `Mail/src/api/mod.rs`, `Mail/src/protocol/envelope.rs`

### Account
User account system with passkey and TOTP authentication, session management, device registry, browser sync (bookmarks, history, passwords, tabs), and settings management.

- **Stack:** Rust (Axum 0.8), UUID v7, TOTP
- **Port:** `127.0.0.1:8081`
- **Key files:** `Account/server/src/main.rs`, `Account/core/src/lib.rs`

### Calander
Task/calendar management with a Rust back-end and vanilla JS front-end. Features CRUD operations, recurring tasks, local-first storage with backend sync.

- **Stack:** Rust (Axum 0.8, SQLite), vanilla JS
- **Port:** Back-end on `127.0.0.1:3002`
- **Key files:** `Calander/Back-End/src/main.rs`, `Calander/Front-End/app.js`

### Protocol
Custom protocol suite implementing the Ichin network stack over TCP/TLS 1.3. Includes four components:

- **Ichin-Protocol** — Core ICHINP wire protocol (HTTP-inspired, JSON-based)
- **Ichin-DNS** — Domain resolution for `.ichin` domains with HMAC-SHA256 signing
- **Ichin-CA** — Certificate authority with RSA + SHA-256, DNS-01 challenge verification
- **Ichin-Daemon** — Application runtime with plugin system, routing, sessions, real-time events

- **Stack:** Python 3, `cryptography` library, TLS 1.3
- **Ports:** 4889 (ICHINP), 4890 (DNS), 4891 (CA), 4892 (Daemon)
- **Key files:** `Protocol/Ichin-Protocol/server.py`, `Protocol/Ichin-DNS/server.py`, `Protocol/Ichin-CA/server.py`, `Protocol/Ichin-Daemon/ichind.py`

### Search-Engine
Registry-based search engine with a Rust/Axum back-end and Next.js 15 front-end. Features an inverted index with multi-factor ranking (title, tags, site name, content, verified status).

- **Stack:** Rust (Axum 0.8, SQLite), Next.js 15 (React 19, TypeScript)
- **Port:** API on `0.0.0.0:3001`, client on `localhost:3000`
- **API:** `GET /search?q={query}`
- **Key files:** `Search-Engine/server/src/search.rs`, `Search-Engine/client/src/app/page.tsx`

## Quick Start

```bash
# Install Protocol dependencies
pip install -r Protocol/requirements.txt

# Generate TLS certificates for Protocol testing
bash Protocol/shared/gen_cert.sh

# Set required environment variables
export ICHINDNS_SECRET="your-random-secret-here"

# Run Rust services (each in its own terminal)
cd Mail && cargo run
cd Account/server && cargo run
cd Calander/Back-End && cargo run
cd browser/Back-End && cargo run
cd Search-Engine/server && cargo run

# Run Protocol services
python Protocol/Ichin-Protocol/server.py
python Protocol/Ichin-DNS/server.py
python Protocol/Ichin-CA/server.py
python Protocol/Ichin-Daemon/ichind.py
```

See `.env.example` for all configuration variables.

## Port Map

| Service | Port |
|---|---|
| Mail API | `:8080` |
| Account Server | `:8081` |
| Search Engine API | `:3001` |
| Calander Back-End | `:3002` |
| Browser Back-End | `:3003` |
| Search Client (Next.js) | `:3000` |
| Ichin-Protocol | `:4889` |
| Ichin-DNS | `:4890` |
| Ichin-CA | `:4891` |
| Ichin-Daemon | `:4892` |

---

*Made in collaboration with AI.*
