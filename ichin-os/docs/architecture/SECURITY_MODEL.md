# Security Model

## Zero Trust Architecture

Ichin OS implements Zero Trust: no request is trusted by default, regardless of origin.

```
                   ┌─────────────┐
                   │  Identity   │
                   │  Provider   │
                   └──────┬──────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
     ▼                    ▼                    ▼
┌──────────┐      ┌──────────────┐      ┌──────────┐
│  User    │      │  Service A   │      │  App     │
└────┬─────┘      └──────┬───────┘      └────┬─────┘
     │                   │                   │
     └───────────────────┼───────────────────┘
                         │
                         ▼
               ┌─────────────────┐
               │  Security Core  │
               │  (PDP/PEP)      │
               └─────────────────┘
```

## Security Layers

### 1. Kernel Security
- **Secure Boot** — UEFI Secure Boot with custom MOK keys
- **TPM 2.0** — Measured boot, disk encryption key sealing
- **LSM** — AppArmor mandatory access control
- **seccomp** — System call filtering for sandboxed apps
- **cgroups v2** — Resource isolation
- **namespaces** — PID, net, mount, user namespace isolation

### 2. Encryption
- **At rest**: LUKS2 for root, swap, and home partitions
- **Per-user**: Encrypted home directories with separate keys
- **In transit**: TLS 1.3 for all inter-service communication
- **End-to-end**: Ichin Protocol encryption for sync
- **Key management**: TPM-sealed keys, optional FIDO2/HSM

### 3. Sandboxing
Every application runs in a sandbox with:
- Dedicated user namespace
- Network namespace (optional, controllable)
- Mount namespace (limited filesystem access)
- seccomp filter (restricted syscalls)
- AppArmor profile
- Resource limits (CPU, memory, I/O)
- Permission manifest (declared at install time)

### 4. Permission Model

| Permission | Description | Default |
|------------|-------------|---------|
| `network` | Internet access | Prompt |
| `filesystem.read` | Read user files | Prompt |
| `filesystem.write` | Write user files | Prompt |
| `microphone` | Audio input | Prompt |
| `camera` | Video input | Prompt |
| `location` | Geolocation | Prompt |
| `notifications` | Send notifications | Allow |
| `ai.local` | Use local AI models | Allow |
| `ai.cloud` | Use cloud AI models | Deny |
| `browser.automate` | Control browser | Prompt |
| `voice.speak` | Text-to-speech | Allow |
| `voice.listen` | Speech-to-text | Prompt |

### 5. AI-Assisted Threat Detection
- Behavioral analysis of process activity
- Anomaly detection in network traffic
- File integrity monitoring
- Real-time alerting via AI Orb
- Automatic quarantine of suspicious processes

### 6. Code Signing
- All `.ichinpkg` packages signed with developer certificates
- Signature verification at install and runtime
- Certificate revocation lists
- Hardware-backed key storage (TPM)

### 7. Audit
- Comprehensive audit logging
- Tamper-proof log storage
- AI-driven log analysis
- User-facing security dashboard
