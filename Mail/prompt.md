ICHIN MAIL — SYSTEM DESIGN PROMPT

You are designing Ichin Mail, a modern, secure, and interoperable messaging protocol that upgrades legacy email systems while remaining compatible with existing SMTP infrastructure.

GOAL
Build a real-world messaging system, not a conceptual or experimental toy. It must prioritize reliability, security, scalability, and interoperability over novelty features.

CORE PRINCIPLES
- Must remain compatible with SMTP email systems via a gateway layer
- Must use structured JSON message envelopes internally
- Must rely on existing DNS infrastructure (MX/SRV records)
- Must support gradual adoption, not forced replacement
- Must ensure deterministic message delivery and rendering

MESSAGE FORMAT
All messages must use a JSON envelope containing:
- message_id (UUID)
- from (standard email address format)
- to (list of recipients)
- timestamp (UNIX epoch)
- subject (string)
- body (plain text required, optional HTML)
- attachments (external references only via hash or secure URL)

TRANSPORT LAYER
- Use TCP or QUIC over TLS 1.3 (default port 443)
- Discover servers via DNS MX records
- Optional SRV records for Ichin Mail endpoints
- Mandatory fallback to SMTP if recipient does not support Ichin Mail
- Handshake must include capability negotiation and protocol version agreement

SECURITY MODEL
- TLS 1.3 required for all connections
- DKIM-like cryptographic message signing mandatory
- SPF-like sender verification required
- Optional DMARC-style policy enforcement
- Messages must be integrity-verified before acceptance

DELIVERY SYSTEM
- Idempotent message delivery (no duplicates on retry)
- Recipient validation before acceptance
- Threading handled via reply_to_id linking
- Delivery confirmations optional and server-controlled

ATTACHMENTS
- Must be stored externally (object storage system)
- Referenced via secure URL or cryptographic hash
- No binary data inside message payload
- Server-enforced size and count limits

FEATURE EXTENSIONS (METADATA ONLY)
Supported optional features via metadata:
- message expiration (server enforced)
- read receipts (opt-in only)
- scheduled delivery
- delivery status tracking

SPAM AND ABUSE PREVENTION
- Rate limiting per sender and domain
- Reputation scoring system for domains/IPs
- Behavioral spam detection
- Optional lightweight proof-of-work (not default, not required)

COMPATIBILITY LAYER (CRITICAL)
- Must include SMTP ↔ Ichin Mail translation gateway
- Must support bidirectional compatibility where possible
- Must allow gradual ecosystem migration

CLIENT FEATURES (OPTIONAL, NOT PROTOCOL CORE)
- Threaded inbox views
- Message categorization
- Split-pane UI support
- Real-time notifications via WebSocket

PROHIBITED DESIGN ELEMENTS
- No IQ-based or user ability restrictions
- No hidden or theme-dependent message content
- No real-time chat embedded in core protocol
- No non-deterministic message rendering
- No client-dependent protocol interpretation
- No gimmick features that break interoperability

FINAL GOAL
Ichin Mail is a production-grade messaging protocol layer that modernizes email without breaking global communication systems.
