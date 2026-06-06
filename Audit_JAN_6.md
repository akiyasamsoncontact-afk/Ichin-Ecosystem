# Ichin Ecosystem Audit — June 6, 2026

## Overview

Comprehensive codebase scan of all 6 components across the Ichin ecosystem.

### Summary

| Severity | Count | Key Areas |
|----------|-------|-----------|
| CRITICAL | 7 | WebView, stubs, compilation errors, dead backends |
| HIGH | 15 | TLS, secrets, missing auth, port conflicts, SPF |
| MEDIUM | 10 | CDN deps, DNS config, privileged ports, path harcodes |
| LOW | 3 | Missing CRUD routes, dead models, default emails |
| FIXED | 3 | Routes wired, DB tables added |

---

## CRITICAL

### C1. Browser WebView renders "Preview Mode" — never loads any URL
- **File:** `browser/Front-End/components/WebView.js:9-21`
- **Issue:** The WebView renders a gradient div with "Preview Mode" text. No iframe, no fetch, no URL loading. The `url` prop is only displayed as text.
- **Fix:** Needs actual content rendering (iframe or DOM parser).

### C2. Browser navigation buttons are all no-ops
- **File:** `browser/Front-End/app.js:71-77`
- **Issue:** `onBack={() => {}}`, `onForward={() => {}}`, `onRefresh={() => {}}`, `canGoBack=false`, `canGoForward=false`. Navigation controls are purely decorative.

### C3. Local JS "libraries" are 214-byte stubs
- **Files:** `browser/Front-End/local-assets/js/react.production.min.js`, `react-dom.production.min.js`, `babel.min.js`, `tailwindcss.js`, `framer-motion.js`
- **Issue:** All 5 files are ~200 bytes containing only `console.log('Ichin ... loaded from local assets')`. Real React is ~130KB, Tailwind is ~4MB. Browser will not render any JSX.
- **Note:** `fonts/` directory is empty. `fonts.css` still imports Google Fonts via CDN anyway.

### C4. Mail `start_api_server` signature mismatch — compilation error
- **Files:** `Mail/src/api/mod.rs:349` vs `Mail/src/bin/server.rs:127`
- **Issue:** `start_api_server()` takes 4 params (`addr, mailbox, delivery_queue, server_keys`) but `bin/server.rs` calls it with 5 params (adds `account_store`). **Will not compile.**
- **Root cause:** `api/mod.rs` (older) and `api/handler.rs` (newer) are duplicate API implementations. The newer `handler.rs` uses `ApiState` which includes `server_name` and `account_store`, but `mod.rs` still uses old `AppState`. Only one of these should exist.

### C5. Mail auth middleware exists but is never applied
- **Files:** `Mail/src/api/auth.rs:16` defines `auth_middleware`, but `Mail/src/api/mod.rs:135` (`create_routes`) never applies it.
- **Issue:** All Mail API endpoints are accessible without any authentication. No token validation, no session check, no login required.
- **Impact:** Anyone can read/send/delete any message.

### C6. Calander front-end uses localStorage only — backend is dead code
- **Files:** `Calander/Front-End/utils/storage.js` (localStorage CRUD) vs `Calander/Back-End/src/main.rs` (REST API)
- **Issue:** The front-end never calls the backend API. All task data lives in `localStorage` only. The backend with full CRUD routes is completely unused.
- **Impact:** Data is single-browser only, no sync, no persistence across sessions.

### C7. Two duplicate Mail API implementations
- **Files:** `Mail/src/api/mod.rs` (old, uses `AppState` with `mailbox, delivery_queue, server_keys`) vs `Mail/src/api/handler.rs` (new, uses `ApiState` with `mailbox, delivery_queue, server_keys, server_name, account_store`)
- **Issue:** Both define the same routes (`/api/status`, `/api/messages`, etc.) with different state types. One set is dead code. The `start_api_server` function in `mod.rs` has the wrong signature for the caller in `bin/server.rs`.
- **Fix:** Consolidate to one API module.

---

## HIGH

### H1. Mail SPF `evaluate_spf` always returns true
- **File:** `Mail/src/security/spf.rs:33-46`
- **Issue:** The function never checks `sender_ip` against the SPF record's `ip4:`/`ip6:`/`include:` mechanisms. It returns `true` regardless of SPF content, treating `-all` (hard fail) the same as `+all` (pass all).
- **Fix:** Implement proper SPF mechanism parsing and IP matching.

### H2. All Python Protocol clients disable TLS certificate verification
- **Files:**
  - `Protocol/Ichin-DNS/client.py:14-15`
  - `Protocol/Ichin-CA/client.py:11-13`
  - `Protocol/Ichin-CA/ichinca.py:232-233` (IchinDNSClient._connect)
  - `Protocol/Ichin-Protocol/ichinp.py:88-89` (create_ssl_context client-side)
- **Issue:** All clients use `ctx.check_hostname = False` and `ctx.verify_mode = ssl.CERT_NONE`. This disables all TLS certificate validation, making connections vulnerable to MITM.
- **Note:** Self-signed certs in `Protocol/shared/cert.pem` exist; clients should load and verify against them.

### H3. DNS HMAC secret has hardcoded default
- **File:** `Protocol/Ichin-DNS/ichindns.py:13`
- **Issue:** `SECRET_KEY = os.environ.get("ICHINDNS_SECRET", "ichin-dns-dev-secret")` — if env var is not set, uses a known dev secret. Anyone who knows this can forge DNS responses.
- **Fix:** Require env var, fail if not set.

### H4. CA root private key stored unencrypted
- **File:** `Protocol/Ichin-CA/ichinca.py:113`
- **Issue:** `encryption_algorithm=serialization.NoEncryption()` — the root CA private key is written to disk in PEM format with no encryption. Only file permissions (0o400) protect it.
- **Fix:** Use `BestAvailableEncryption(b"password")` or load password from env.

### H5. Search Engine references nonexistent GurtDNS/GurtCA
- **File:** `Search-Engine/server/src/main.rs:54,64-65,102-106,130-136`
- **Issue:** Seed data content references "GurtDNS" and "GurtCA" — services that do not exist in the codebase. Users reading search results will be misled.
- **Fix:** Replace with references to the actual Ichin DNS and Ichin CA services.

### H6. Search Engine has no crawler — only 3 manually seeded pages
- **File:** `Search-Engine/server/src/main.rs:38-136`
- **Issue:** The search index only contains the 3 pages hardcoded in `main.rs`. There is no crawler, no sitemap parser, no discovery mechanism. The search engine cannot find any new content.
- **Fix:** Add a crawler component.

### H7. Browser Backend and Search Engine both bind port 3001
- **Files:** `browser/Back-End/src/main.rs:25` and `Search-Engine/server/src/main.rs:152`
- **Issue:** Both bind to `127.0.0.1:3001`. They cannot run simultaneously.

### H8. Mail SMTP Gateway has no TLS
- **File:** `Mail/src/gateway/smtp.rs:10`
- **Issue:** `SmtpGateway` binds to a raw TCP listener with no TLS. Standard SMTP requires STARTTLS or SMTPS.

### H9. Account server exists but is never launched
- **File:** `Account/server/src/main.rs` (1290 lines)
- **Issue:** The Account server has full registration, login, session management, passkey (WebAuthn), TOTP 2FA, device management, and login history. But no workflow starts this server. Mail's `bin/server.rs` uses `AccountStore` directly from the library crate, but the HTTP server that exposes registration/login endpoints is never started.

### H10. Mail default config binds privileged ports
- **File:** `Mail/src/internal/config.rs:20,25`
- **Issue:** Default listen port is `0.0.0.0:443` (requires root) and SMTP gateway is `0.0.0.0:25` (requires root).

### H11. Mail default config hardcodes system paths
- **File:** `Mail/src/internal/config.rs:21-24,39-42,44-46`
- **Issue:** Default TLS cert path is `/etc/ichin/cert.pem`, DB path is `/var/lib/ichin/db`. These paths will fail on systems without these directories.

### H12. Browser local-assets/fonts directory is empty
- **File:** `browser/Front-End/local-assets/fonts/`
- **Issue:** The directory exists but contains zero font files. The `fonts.css` loads Inter and JetBrains Mono from Google Fonts CDN as a fallback, but even that fails because the `@import url(...)` is in a CSS file served locally.

### H13. CORS set to permissive on Mail API
- **File:** `Mail/src/api/mod.rs:147`
- **Issue:** `CorsLayer::permissive()` allows all origins, all methods, all headers. Combined with no auth middleware, any website can make API calls to the Mail server.

### H14. Protocol Daemon has no access control
- **File:** `Protocol/Ichin-Daemon/ichind.py:55-65`
- **Issue:** Any client that connects via TLS can access any registered app's routes. No authentication, no authorization, no session validation beyond creation.

### H15. Mail DNS discovery uses public internet DNS
- **File:** `Mail/src/dns/discovery.rs:12-15`
- **Issue:** `TokioResolver::builder_with_config(ResolverConfig::default(), ...)` uses the system's public DNS resolvers. For an Ichin-only network, it should query the Ichin DNS server at `127.0.0.1:4890`.

---

## MEDIUM

### M1. Default browser tabs and favorites hardcode public Internet URLs
- **Files:** `browser/Front-End/utils/constants.js:8-20`
- **Issue:** 5 default tabs point to github.com, notion.so, linear.app, figma.com, vercel.com. 3 favorites point to stackoverflow.com, MDN, twitter.com.

### M2. Mail front-end loads from external CDNs
- **File:** `Mail/frontend/index.html:14-18`
- **Issue:** React 18, ReactDOM, Babel, Tailwind CSS, and Lucide icons all loaded from `resource.trickle.so` and `cdn.tailwindcss.com`.

### M3. Calander front-end loads from external CDNs
- **File:** `Calander/Front-End/index.html:14-18`
- **Issue:** Identical CDN dependency chain as Mail frontend (trickle.so, cdn.tailwindcss.com).

### M4. Mail TLS client trusts system CA store
- **File:** `Mail/src/transport/tls.rs:43`
- **Issue:** `root_certs()` loads `/etc/ssl/certs/ca-certificates.crt` — the public internet CA bundle. For Ichin-only communication, it should trust the Ichin CA root certificate.

### M5. Protocol Daemon rate limit has no time window
- **File:** `Protocol/Ichin-Daemon/router.py:96-100`
- **Issue:** Rate limit is set at 100 requests total per session with no time window or reset. Once a session hits 100 requests, it's permanently rate-limited.

### M6. Browser `fonts.css` still imports Google Fonts
- **File:** `browser/Front-End/local-assets/css/fonts.css:1`
- **Issue:** `@import url('https://fonts.googleapis.com/css2?family=Inter...')` — even though the file is supposed to be a local asset, it fetches from Google CDN.

### M7. No orchestration for multi-server startup
- **Issue:** The ecosystem has 6 servers (Browser BE, Mail, Search, Calander, Account, DNS, CA, Daemon) with no docker-compose, supervisord config, or startup script.

### M8. Calander no front-end-to-backend connection
- **File:** `Calander/Front-End/app.js` (uses `utils/storage.js` for localStorage only)
- **Issue:** Backend task CRUD exists but is not wired to the frontend. The frontend uses `localStorage` exclusively.

---

## LOW

### L1. Mail `handle_send_message` defaults to `me@ichin.network`
- **File:** `Mail/src/api/mod.rs:205-208`
- **Issue:** If the client sends an empty `from` field, the server fills in `me@ichin.network` instead of rejecting the request.

### L2. Browser `models.rs` is empty
- **File:** `browser/Back-End/src/models.rs:1-2`
- **Issue:** Contains only the comment "Models are defined in db.rs for simplicity". Could be removed.

### L3. Missing GET-by-id routes in Browser backend
- **File:** `browser/Back-End/src/routes/`
- **Issue:** No `get_workspace(id)`, `get_tab(id)`, `get_favorite(id)`, `get_history_item(id)` routes. Only full-list CRUD exists.

---

## FIXED (this session)

### F1. Browser backend routes are now wired
- **File:** `browser/Back-End/src/main.rs`
- **Change:** Replaced placeholder with full route wiring — all 10 API endpoints registered with security headers, tracing, and CSRF middleware.

### F2. Missing `history` and `user_profile` table creation added
- **File:** `browser/Back-End/src/db.rs`
- **Change:** Added `CREATE TABLE IF NOT EXISTS history` and `CREATE TABLE IF NOT EXISTS user_profile` to `init()`.

---

## Status by Component

| Component | Source Files | CRITICAL | HIGH | MEDIUM | LOW | Verdict |
|-----------|-------------|----------|------|--------|-----|---------|
| Browser (FE) | 14 JS/HTML/CSS | 3 | 2 | 2 | 0 | Shell — no content renders |
| Browser (BE) | 10 Rust | 0 | 0 | 0 | 2 | 2 fixed, working |
| Mail (BE) | 36 Rust | 3 | 5 | 2 | 1 | Auth gap, SPF no-op, dead code |
| Mail (FE) | 7 JS/HTML | 0 | 0 | 1 | 0 | Works, uses CDN |
| Calander (BE) | 3 Rust | 1 | 1 | 0 | 0 | Backend unused by frontend |
| Calander (FE) | 10 JS/HTML/CSS | 1 | 1 | 1 | 0 | localStorage only, uses CDN |
| Search Engine | 5 Rust | 0 | 3 | 0 | 0 | No crawler, port conflict, bad refs |
| Protocol | 16 Python | 0 | 3 | 1 | 0 | No TLS verify, hardcoded secrets |
| Account | 4 Rust + 1 server | 0 | 1 | 0 | 0 | Server never started, code quality OK |
