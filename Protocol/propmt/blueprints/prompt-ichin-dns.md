You are designing the **ICHIN Domain Name System (IchinDNS)** for a fictional private internet ecosystem called **ICHIN**. This system replaces traditional DNS and is responsible for resolving all `.ichin` domains into network addresses within the ICHIN network.

Your goal is to design a **secure, minimal, fully self-contained DNS-like system**.

---

# CORE PURPOSE

IchinDNS maps human-readable domains like:

```
example.ichin
```

into:

* IP addresses (IPv4 / IPv6)
* internal service identifiers
* or ICHIN protocol endpoints

---

# SYSTEM DESIGN

## 1. Domain Structure

* Root zone: `.ichin`
* Only IchinDNS can resolve these domains
* No external DNS dependencies allowed

---

## 2. Record Types

Support the following DNS-like records:

### A RECORD

Maps domain → IPv4

```json
{
  "type": "A",
  "host": "site.ichin",
  "value": "127.0.0.1"
}
```

### AAAA RECORD

Maps domain → IPv6

```json
{
  "type": "AAAA",
  "host": "site.ichin",
  "value": "::1"
}
```

### CNAME RECORD

Alias system

```json
{
  "type": "CNAME",
  "host": "blog.ichin",
  "value": "site.ichin"
}
```

### TXT RECORD

Used for verification and metadata

```json
{
  "type": "TXT",
  "host": "site.ichin",
  "value": "verification=ichin-ca-verified"
}
```

### ICHIN RECORD (custom)

Maps directly to ICHIN protocol endpoints:

```json
{
  "type": "ICHIN",
  "host": "app.ichin",
  "value": "ichinp://127.0.0.1:4889/app"
}
```

---

# CORE FEATURES

## 1. Resolution Engine

* Takes a domain string
* Returns the final resolved endpoint
* Supports recursive resolution (CNAME chaining)
* Detects loops and prevents infinite recursion

---

## 2. Caching System

* Cache resolved domains for performance
* TTL (time-to-live) per record
* Cache invalidation on update

---

## 3. Domain Registry System

* Users can register `.ichin` domains
* Domains must be unique
* Optional approval mode (manual or automatic)
* Prevent spam registrations

---

## 4. Security Model

* All DNS queries are encrypted (ICHINP required)
* Prevent spoofing via cryptographic verification
* Optional integration with IchinCA certificates
* Signed DNS responses (important feature)

---

## 5. Query Format

### Request:

```json
{
  "query": "example.ichin",
  "type": "A"
}
```

### Response:

```json
{
  "status": "OK",
  "query": "example.ichin",
  "records": [
    {
      "type": "A",
      "value": "127.0.0.1"
    }
  ],
  "ttl": 3600
}
```

---

# SYSTEM BEHAVIOR RULES

* If domain does not exist → return `NXDOMAIN`
* If record type mismatch → return empty result
* If loop detected → return `ERR_LOOP_DETECTED`
* Must always prefer exact match over CNAME resolution
* Must be deterministic (same input → same output)

---

# IMPLEMENTATION REQUIREMENTS

You must include:

1. Full system architecture overview
2. Data storage model (in-memory + optional file persistence)
3. Query resolution algorithm (step-by-step)
4. Minimal working server implementation (Rust, Python, or Go preferred)
5. Example queries and responses
6. Explanation of how it integrates with ICHINP

---

# DESIGN GOAL

IchinDNS should feel like:

* a simplified but real DNS system
* fully self-contained inside ICHIN
* fast, predictable, and secure

---

# IMPORTANT CONSTRAINTS

* Do NOT use real-world DNS systems
* Do NOT rely on external internet resolution
* Must operate entirely within the ICHIN ecosystem

