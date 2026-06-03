# ICHIN Protocol Ecosystem

A private, secure, self-contained networking protocol stack for the ICHIN ecosystem.

## Structure

```
Protocol/
├── shared/              — Shared TLS certs and tooling
├── Ichin-Protocol/      — Wire protocol spec + reference implementation (port 4889)
├── Ichin-DNS/           — Domain name resolution (port 4890)
├── Ichin-CA/            — Certificate authority (port 4891)
└── Ichin-Daemon/        — Application runtime server (port 4889)
```

## Port Map

| Service | Port | Description |
|---------|------|-------------|
| Ichin Protocol / IchinD | 4889 | ICHINP wire protocol + app runtime |
| IchinDNS | 4890 | Domain resolution for `.ichin` domains |
| IchinCA | 4891 | Certificate issuance and validation |

## Component Convention

Each component follows the same structure:

```
Ichin-<Name>/
├── ARCHITECTURE.md    — System design overview
├── prompt.md          — Original specification prompt
├── server.py          — ICHINP-based server
├── client.py          — CLI/tooling client
└── <core>.py          — Core library
```

## Adding a New Component

1. Create `Ichin-<Name>/` following the convention above
2. Register a unique port in the port map
3. Reference certs from `shared/` as `os.path.join(SCRIPT_DIR, "..", "shared", "cert.pem")`
4. Use ICHINP as the wire protocol for all communication
