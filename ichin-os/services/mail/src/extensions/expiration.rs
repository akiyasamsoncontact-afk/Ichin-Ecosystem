use chrono::Utc;

use crate::protocol::envelope::Envelope;

pub fn is_expired(envelope: &Envelope) -> bool {
    match envelope.metadata.expiration {
        Some(expires_at) => Utc::now().timestamp() > expires_at,
        None => false,
    }
}

pub fn set_expiration(envelope: &mut Envelope, ttl_secs: i64) {
    envelope.metadata.expiration = Some(Utc::now().timestamp() + ttl_secs);
}
