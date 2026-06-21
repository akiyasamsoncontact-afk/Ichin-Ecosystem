use crate::protocol::envelope::Envelope;
use crate::security::keys::KeyPair;

pub fn sign_envelope(
    envelope: &mut Envelope,
    key_pair: &KeyPair,
) -> Result<(), anyhow::Error> {
    let canonical = envelope.canonical_bytes();
    let signature = key_pair.sign(&canonical)?;
    envelope.signature = Some(base64::Engine::encode(&base64::engine::general_purpose::STANDARD, &signature));
    envelope.signing_key_id = Some(key_pair.key_id.clone());
    Ok(())
}
