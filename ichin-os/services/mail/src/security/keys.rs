use ed25519_dalek::{Signature, Signer, SigningKey, VerifyingKey};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KeyPair {
    pub key_id: String,
    pub public_key: Vec<u8>,
    pub private_key: Vec<u8>,
}

impl KeyPair {
    pub fn generate() -> Self {
        let mut secret = [0u8; 32];
        use rand::RngCore;
        rand::rngs::OsRng.fill_bytes(&mut secret);
        let signing_key = SigningKey::from_bytes(&secret);
        let verifying_key = signing_key.verifying_key();

        let mut hasher = Sha256::new();
        hasher.update(verifying_key.as_bytes());
        let key_id = hex::encode(hasher.finalize())[..16].to_string();

        Self {
            key_id,
            public_key: verifying_key.as_bytes().to_vec(),
            private_key: signing_key.to_bytes().to_vec(),
        }
    }

    pub fn sign(&self, data: &[u8]) -> Result<Vec<u8>, anyhow::Error> {
        let key_bytes: [u8; 32] = self.private_key[..32]
            .try_into()
            .map_err(|_| anyhow::anyhow!("Invalid private key length"))?;
        let signing_key = SigningKey::from_bytes(&key_bytes);
        let signature = signing_key.sign(data);
        Ok(signature.to_bytes().to_vec())
    }

    pub fn verifying_key(&self) -> Result<VerifyingKey, anyhow::Error> {
        let key_bytes: [u8; 32] = self.public_key[..32]
            .try_into()
            .map_err(|_| anyhow::anyhow!("Invalid public key length"))?;
        Ok(VerifyingKey::from_bytes(&key_bytes)?)
    }
}

pub fn verify_signature(
    data: &[u8],
    signature: &[u8],
    public_key: &[u8],
) -> Result<bool, anyhow::Error> {
    let key_bytes: [u8; 32] = public_key[..32]
        .try_into()
        .map_err(|_| anyhow::anyhow!("Invalid public key length"))?;
    let sig_bytes: [u8; 64] = signature[..64]
        .try_into()
        .map_err(|_| anyhow::anyhow!("Invalid signature length"))?;

    let verifying_key = VerifyingKey::from_bytes(&key_bytes)?;
    let sig = Signature::from_bytes(&sig_bytes);

    Ok(verifying_key.verify_strict(data, &sig).is_ok())
}
