# Ichin Ecosystem Audit

Generated: 2026-06-06 — Full scan of all 6 subsystems (Browser, Mail, Account, Calander, Search-Engine, Protocol).

## Port Map

| Service | Port | File | Status |
|---|---|---|---|
| Mail API | `0.0.0.0:8080` | `Mail/src/bin/server.rs:128` | ✅ |
| Account Server | `127.0.0.1:8081` | `Account/server/src/main.rs:1285` | ✅ |
| Search Engine API | `0.0.0.0:3001` | `Search-Engine/server/src/main.rs:152` | ✅ |
| Calander Back-End | `127.0.0.1:3002` | `Calander/Back-End/src/main.rs:49` | ✅ |
| Browser Back-End | `127.0.0.1:3003` | `browser/Back-End/src/main.rs:24` | ✅ |
| Search Client (Next.js) | `localhost:3000` | `Search-Engine/client/package.json:6` | ✅ |
| Ichin-Protocol | `0.0.0.0:4889` | `Protocol/Ichin-Protocol/ichinp.py:7` | ✅ |
| Ichin-DNS | `0.0.0.0:4890` | `Protocol/Ichin-DNS/ichindns.py:10` | ✅ |
| Ichin-CA | `0.0.0.0:4891` | `Protocol/Ichin-CA/ichinca.py:11` | ✅ |
| Ichin-Daemon | `0.0.0.0:4892` | `Protocol/Ichin-Daemon/ichind.py:12` | ✅ |

No port conflicts.

---

## Compilation Status

| Project | Language | Files | Status |
|---|---|---|---|
| Mail | Rust | `Mail/` | ✅ 0 errors |
| Account (core + server) | Rust | `Account/` | ✅ 0 errors |
| Calander Back-End | Rust | `Calander/Back-End/` | ✅ 0 errors |
| Browser Back-End | Rust | `browser/Back-End/` | ✅ 0 errors |
| Search Engine | Rust | `Search-Engine/server/` | ✅ 0 errors (2 dead-code warnings) |
| Protocol (4 subsystems) | Python | `Protocol/` | ✅ All 12 files pass syntax check |

---

## CRITICAL Issues

### C1 — Private keys tracked in git
**Files:** `Protocol/Ichin-CA/root_ca_key.pem`, `Protocol/Ichin-Protocol/key.pem`, `Protocol/shared/key.pem`
**Risk:** CA root private key, TLS private keys committed to public repo.
**Fix:** `git rm --cached` the key files, add `**/*.pem` and `**/*.key` to `.gitignore`, regenerate keys.

### C2 — SQLite database tracked in git
**File:** `Search-Engine/server/search.db` (29 KB)
**Risk:** Binary database with seed data tracked, grows with every change.
**Fix:** `git rm --cached search.db` (`.gitignore` already has `search.db`).

### C3 — `.deb` package tracked in git
**File:** `calentask_1.0.0_amd64.deb` (3.2 MB)
**Risk:** Large binary artifact bloating repo.
**Fix:** `git rm --cached` and add `*.deb` to `.gitignore` (root `.gitignore` already has `*.deb` but tracked file needs removal).

### C4 — `__pycache__` bytecode tracked in git
**Files:** 6 `.pyc` files across `Protocol/Ichin-Daemon/`, `browser/Back-End/`
**Risk:** Platform-specific bytecode in repo.
**Fix:** `git rm --cached` (`.gitignore` already has `**/__pycache__/`).

---

## HIGH Issues

### H1 — Orphan/backup files tracked
**Files:** `browser/Back-End/Cargo.toml.backup`, `browser/Back-End/Cargo.toml.minimal`
**Fix:** `git rm` — these are not needed.

### H2 — Account SigningKey not persisted
**File:** `Account/core/src/auth.rs:20-23`
**Issue:** `SigningKey` generated from a random seed on every startup. Session tokens invalidated on restart.
**Fix:** Save seed to disk on first launch; load on subsequent starts.

### H3 — Account data path hardcoded
**File:** `Account/server/src/main.rs:1242`
**Issue:** `AccountStore::new("account_data")` — not configurable via env var.
**Fix:** Make path configurable via `ICHIN_ACCOUNT_DATA_PATH` env var.

### H4 — Mail Cargo.toml uses edition "2024"
**File:** `Mail/Cargo.toml:4`
**Issue:** Edition 2024 requires Rust 1.85+. May cause build failures on older toolchains.
**Fix:** Change to `edition = "2021"` or ensure CI uses Rust 1.85+.

---

## MEDIUM Issues

### M1 — Duplicate `main.minimal.rs` in Browser BE
**File:** `browser/Back-End/src/main.minimal.rs` (identical backup of earlier variant)
**Fix:** Remove the file.

### M2 — Browser BE `models.rs` is unused
**File:** `browser/Back-End/src/models.rs`
**Issue:** Not imported or referenced by `main.rs`. Dead code.
**Fix:** Remove or integrate.

### M3 — Duplicate Axum 0.7 `Handler` import in Mail
**File:** `Mail/src/protocol/ichin.rs:4-5`
**Issue:** `use axum::handler::Handler` is from axum 0.7; Mail uses axum 0.8 elsewhere.
**Fix:** Remove unused import.

---

## LOW Issues

### L1 — Search Engine unused load() method
**File:** `Search-Engine/server/src/search.rs:24`
**Issue:** `load()` loads index from DB but is never called (seed data hardcoded in `main()`).
**Fix:** Call `load()` before seed data, or remove method.

### L2 — Search Engine unused DB query methods
**File:** `Search-Engine/server/src/db.rs:49, 69, 146, 157, 179`
**Issue:** `get_sites`, `get_pages`, `get_page_ids_for_term`, `get_page_by_id`, `get_site_by_id` never called.
**Fix:** Remove or keep for future use.

### L3 — `browser/build/` and `browser/dist/` untracked but present
**Issue:** Build artifacts from Electron-builder. Not tracked but should be in `.gitignore`.
**Note:** Already excluded by `**/node_modules/` rule. No action needed unless they appear in status.

---

## Configuration

All environment variables documented in `.env.example` at repository root.

## Summary

- **CRITICAL:** 4 (secrets, binary artifacts in git)
- **HIGH:** 4 (orphan files, session persistence, hardcoded config, edition)
- **MEDIUM:** 3 (duplicate file, dead code, unused import)
- **LOW:** 3 (unused methods, build artifacts)
