# IchinCA — Certificate Authority Architecture

## 1. System Overview

IchinCA is a self-contained Certificate Authority for the ICHIN private ecosystem. It issues, verifies, and revokes TLS certificates for `.ichin` domains, integrating with IchinDNS for domain ownership verification.

```
┌──────────────┐     ICHINP (TLS 1.3)     ┌──────────────────────┐
│  ICHINP      │ ◄─────────────────────────► │   IchinCA Server     │
│  Client      │    {"action":"request_cert", │   (port 4891)        │
│  (Service)   │     "domain":"site.ichin"}   │                      │
└──────────────┘                              └──────┬──────────────-┘
                                                      │
                                        ┌─────────────┴─────────────┐
                                        │                           │
                                        ▼                           ▼
                               ┌──────────────┐          ┌──────────────────┐
                               │  Root CA Key  │          │  Verification    │
                               │  (offline)    │          │  Engine          │
                               │               │          │  (→ IchinDNS)   │
                               └──────┬───────-┘          └──────────────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  Cert Store      │
                              │  + CRL           │
                              │  (JSON files)    │
                              └──────────────────┘
```

---

## 2. Certificate Lifecycle

```
REQUEST → CHALLENGE → VERIFY → ISSUE → ACTIVE → EXPIRED/REVOKED
```

| Phase | Description |
|-------|-------------|
| **Request** | Client submits domain + public key |
| **Challenge** | CA generates a token; client publishes as IchinDNS TXT record |
| **Verify** | CA queries IchinDNS for the token |
| **Issue** | Token matches → CA signs certificate |
| **Active** | Certificate is valid and usable |
| **Expired** | Past `expires_at` date (default: 365 days) |
| **Revoked** | Explicitly revoked via CRL |

---

## 3. Certificate Structure

```json
{
  "domain": "site.ichin",
  "public_key": "base64-encoded RSA public key",
  "issuer": "IchinCA Root",
  "issued_at": "2026-06-01T12:00:00Z",
  "expires_at": "2027-06-01T12:00:00Z",
  "serial_number": "ichin-ca-0001",
  "signature": "sha256-with-rsa base64 signature"
}
```

---

## 4. Domain Verification Flow

```
Client                     IchinCA                     IchinDNS
  │                          │                           │
  │  1. request_cert         │                           │
  │ ───────────────────────► │                           │
  │                          │                           │
  │  2. challenge token      │                           │
  │ ◄─────────────────────── │                           │
  │                          │                           │
  │  3. publish TXT record   │                           │
  │ ──────────────────────────────────────────────────► │
  │                          │                           │
  │  4. verify_domain        │                           │
  │ ───────────────────────► │                           │
  │                          │  5. query TXT record      │
  │                          │ ────────────────────────► │
  │                          │ ◄──────────────────────── │
  │                          │                           │
  │  6. issued certificate   │                           │
  │ ◄─────────────────────── │                           │
```

---

## 5. Certificate Validation

When a client connects to an ICHINP service, it validates the server's certificate:

1. **Signature**: Verify using Root CA public key (RSA + SHA-256)
2. **Expiry**: Check `expires_at` has not passed
3. **Domain**: Check `domain` matches the connected `.ichin` domain
4. **Revocation**: Check serial not in CRL
5. **Trust chain**: Ensure certificate was signed by the trusted Root CA

---

## 6. Revocation System

- **CRL**: JSON file listing revoked serial numbers with reason and timestamp
- Revoked certs are rejected during validation
- Supports online query via `check_cert` API

---

## 7. ICHINP API

| Action | Path | Description |
|--------|------|-------------|
| `request_cert` | `/ca/request` | Submit CSR, get challenge token |
| `verify_domain` | `/ca/verify` | Verify TXT record, issue cert |
| `revoke_cert` | `/ca/revoke` | Revoke by serial number |
| `check_cert` | `/ca/check` | Validate a certificate |
| `get_crl` | `/ca/crl` | Get revocation list |
| `get_root_cert` | `/ca/root` | Get Root CA public cert |

---

## 8. Security Considerations

- **Root CA key stored securely** (file with restricted permissions)
- **Challenge tokens are time-bound** (5-minute expiry)
- **Rate limiting** on cert requests (configurable)
- **Replay prevention** via timestamp + nonce in challenges
- **All communication over TLS** (ICHINP with mandatory TLS 1.3)
- **Revocation must be checked on every connection**
