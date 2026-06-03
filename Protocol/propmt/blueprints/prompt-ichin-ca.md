You are designing the **ICHIN Certificate Authority (IchinCA)** for a fictional secure internet ecosystem called **ICHIN**.

Your task is to design a full certificate authority system that issues, verifies, and revokes digital certificates used to secure all ICHIN network communication.

---

# CORE PURPOSE

IchinCA is responsible for:

* Verifying ownership of `.ichin` domains
* Issuing TLS certificates for ICHIN services
* Ensuring trust between clients and servers in the ICHIN network
* Preventing impersonation and spoofing

This is the foundation of security inside ICHIN.

---

# SYSTEM DESIGN

## 1. Certificate Structure

Each certificate must include:

```json
{
  "domain": "example.ichin",
  "public_key": "base64-encoded-key",
  "issuer": "IchinCA Root",
  "issued_at": "timestamp",
  "expires_at": "timestamp",
  "serial_number": "unique-id",
  "signature": "CA-signed-hash"
}
```

---

## 2. Root Certificate Authority

* IchinCA has a **Root CA key pair**
* Root key is never exposed publicly
* All certificates must chain back to Root CA
* System supports intermediate CAs (optional extension)

---

## 3. Domain Verification System

Before issuing a certificate, ownership must be verified using IchinDNS:

### Verification Methods:

* TXT record challenge:

  * CA generates a token
  * Domain must publish it in TXT record via IchinDNS
* OR cryptographic proof (advanced mode)

Example:

```
ichinca-verify=abc123token
```

---

## 4. Certificate Issuance Flow

1. Client requests certificate for `site.ichin`
2. IchinCA generates verification token
3. Client publishes token in IchinDNS TXT record
4. IchinCA queries IchinDNS to verify
5. If valid → certificate is issued
6. Certificate is signed using CA private key

---

## 5. Certificate Validation Flow

When a client connects:

* Server sends certificate
* Client verifies:

  * signature validity
  * expiration date
  * domain match
  * CA trust chain

If any check fails → connection is rejected.

---

## 6. Revocation System

Support certificate revocation:

### CRL (Certificate Revocation List)

* Stores revoked serial numbers
* Queried during handshake

### Online Revocation Check (optional)

* Real-time validation endpoint

---

## 7. API DESIGN

### Request certificate:

```json
{
  "action": "request_cert",
  "domain": "example.ichin",
  "public_key": "..."
}
```

### Response:

```json
{
  "status": "pending_verification",
  "challenge": "ichinca-verify=abc123"
}
```

---

### Verify domain:

```json
{
  "action": "verify_domain",
  "domain": "example.ichin"
}
```

### Issue certificate:

```json
{
  "status": "issued",
  "certificate": { ... }
}
```

---

# SECURITY MODEL

* All certificates are cryptographically signed
* Root CA private key must never leave secure storage
* Replay attacks must be prevented using timestamps
* Certificate binding must include domain + public key
* All verification requests must be rate-limited

---

# SYSTEM COMPONENTS

You must design:

## 1. CA Server

* Handles issuance requests
* Manages signing operations
* Stores certificate database

## 2. Verification Engine

* Talks to IchinDNS
* Confirms TXT records

## 3. Certificate Store

* Persistent storage (file or database)
* Indexed by domain + serial number

## 4. Revocation System

* Tracks revoked certificates
* Ensures invalid certs are rejected

---

# REQUIRED OUTPUT

Your response must include:

1. System architecture diagram (text form is fine)
2. Certificate lifecycle explanation
3. Domain verification flow (step-by-step)
4. Minimal CA server implementation (Python / Rust / Go)
5. Example certificate generation output
6. Security considerations and attack prevention

---

# DESIGN GOAL

IchinCA should behave like:

* a simplified Let's Encrypt
* fully self-contained inside the ICHIN ecosystem
* secure enough to prevent fake servers
* easy enough to understand for learning purposes

---

# IMPORTANT CONSTRAINTS

* Do NOT use real-world CA infrastructure
* Do NOT rely on external certificate authorities
* Must only trust IchinCA root system

