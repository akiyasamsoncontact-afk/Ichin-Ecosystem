# IchinDNS — System Architecture

## 1. Overview

IchinDNS is a self-contained DNS-like resolution system for the ICHIN private ecosystem. It maps `.ichin` domains to IP addresses and ICHINP endpoints with no external dependencies.

```
┌─────────────┐     ICHINP (TLS 1.3)     ┌──────────────────┐
│  ICHINP     │ ◄─────────────────────────► │  IchinDNS Server │
│  Client     │    {"query":"site.ichin",    │  (port 4890)     │
│             │     "type":"A"}              │                  │
└─────────────┘                              └────────┬─────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────┐
                                              │  Domain Registry │
                                              │  (in-memory +    │
                                              │   JSON persist)  │
                                              └──────────────────┘
```

---

## 2. Record Types

| Type | Value Format | Example |
|------|-------------|---------|
| `A` | IPv4 address | `192.168.1.1` |
| `AAAA` | IPv6 address | `::1` |
| `CNAME` | Canonical domain | `site.ichin` |
| `TXT` | Arbitrary text | `verification=ichin-ca` |
| `ICHIN` | ICHINP URI | `ichinp://10.0.0.1:4889/app` |

---

## 3. Resolution Algorithm

```
resolve(domain: str, type: str) → Record[]

 1. domain = strip_trailing_dot(domain.lower())
 2. if domain ends with ".ichin" or has no dot → treat as .ichin domain
 3. Lookup domain+type in cache (return if fresh)
 4. Lookup exact match in registry
 5. If found → cache + return
 6. If not found, lookup CNAME for domain
 7. If CNAME exists → recursive resolution on CNAME target
 8. Detect loops via visited set → return ERR_LOOP_DETECTED
 9. If domain not found → return NXDOMAIN
```

---

## 4. Caching

- In-memory dictionary keyed by `(domain, type)`
- Each entry stores `(records, expiry_timestamp)`
- TTL per record (default: 3600s)
- Cache is checked before registry lookup
- On record update/delete, related cache entries are invalidated

---

## 5. Domain Registry

- Flat dictionary: `domain → [Record, ...]`
- Domain uniqueness enforced at registration
- Supports register, list, update, delete operations
- Optional approval mode (manual/auto)
- JSON persistence (`registry.json`) loaded on startup, saved on change

---

## 6. Security Model

- All queries over ICHINP (TLS 1.3)
- Response signing via HMAC-SHA256 with server secret key
- Client verifies signature upon receipt
- No external DNS dependency

---

## 7. Integration with ICHINP

IchinDNS runs as a standard ICHINP server on port **4890** (out of band from the main protocol port 4889). It registers ICHINP method handlers:

| ICHINP Method | Path | Purpose |
|---------------|------|---------|
| QUERY | `/dns/query` | Resolve a domain |
| REGISTER | `/dns/register` | Register a domain |
| LIST | `/dns/list` | List records for a domain |
| DELETE | `/dns/delete` | Remove a record |

Custom ICHINP methods `QUERY`, `REGISTER`, `LIST`, `DELETE` are used instead of standard HTTP verbs to keep the protocol DNS-specific.

---

## 8. File Layout

```
ICHIN-DNS/
├── ARCHITECTURE.md    — This document
├── propmt.md          — Original prompt
├── ichindns.py        — Core: models, registry, resolution, caching
├── server.py          — ICHINP-based DNS server
├── client.py          — CLI client for querying
└── registry.json      — Persisted domain records
```

---

## 9. Example Queries

### Resolve A record
```
→ {"method":"QUERY","path":"/dns/query","body":{"query":"site.ichin","type":"A"}}
← {"status":200,"body":{"status":"OK","records":[{"type":"A","value":"10.0.0.1","ttl":3600}]}}
```

### Resolve CNAME chain
```
→ {"method":"QUERY","path":"/dns/query","body":{"query":"blog.ichin","type":"A"}}
← {"status":200,"body":{"status":"OK","records":[{"type":"A","value":"10.0.0.2","ttl":3600}]}}
  (recursively resolved blog.ichin → CNAME → site.ichin → A)

### Non-existent domain
→ {"method":"QUERY","path":"/dns/query","body":{"query":"unknown.ichin","type":"A"}}
← {"status":200,"body":{"status":"NXDOMAIN","records":[]}}
```

---

## 10. Status Responses

| Response Status | Meaning |
|----------------|---------|
| `OK` | Successfully resolved |
| `NXDOMAIN` | Domain does not exist |
| `ERR_LOOP` | CNAME loop detected |
| `ERR_INVALID` | Malformed query |
