use crate::protocol::envelope::Envelope;
use crate::security::keys::verify_signature;

pub fn verify_envelope(
    envelope: &Envelope,
    public_key: &[u8],
) -> Result<bool, anyhow::Error> {
    let signature = match &envelope.signature {
        Some(sig) => base64::Engine::decode(
            &base64::engine::general_purpose::STANDARD,
            sig,
        )?,
        None => return Ok(false),
    };

    let canonical = envelope.canonical_bytes();
    verify_signature(&canonical, &signature, public_key)
}
