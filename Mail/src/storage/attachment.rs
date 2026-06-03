use sha2::{Digest, Sha256};
use std::path::PathBuf;

use super::AttachmentStorage;

pub const MAX_ATTACHMENT_SIZE: u64 = 100 * 1024 * 1024; // 100MB
pub const MAX_ATTACHMENTS: usize = 50;

pub struct Attachment {
    pub filename: String,
    pub mime_type: String,
    pub size_bytes: u64,
    pub hash: String,
    pub url: String,
}

pub fn compute_hash(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex::encode(hasher.finalize())
}

pub struct LocalStorage {
    base_path: PathBuf,
}

impl LocalStorage {
    pub fn new(base_path: &str) -> Self {
        let path = PathBuf::from(base_path);
        std::fs::create_dir_all(&path).ok();
        Self { base_path: path }
    }
}

#[async_trait::async_trait]
impl AttachmentStorage for LocalStorage {
    async fn store(&self, filename: &str, data: &[u8], mime_type: &str) -> Result<String, anyhow::Error> {
        let hash = compute_hash(data);
        let subdir = &hash[..2];
        let dir = self.base_path.join(subdir);
        std::fs::create_dir_all(&dir)?;

        let file_path = dir.join(&hash);
        tokio::fs::write(&file_path, data).await?;

        // Store metadata
        let meta_path = dir.join(format!("{}.meta", hash));
        let meta = serde_json::json!({
            "filename": filename,
            "mime_type": mime_type,
            "size_bytes": data.len(),
            "hash": hash,
        });
        tokio::fs::write(&meta_path, meta.to_string()).await?;

        Ok(hash)
    }

    async fn retrieve(&self, hash: &str) -> Result<Option<Vec<u8>>, anyhow::Error> {
        let subdir = &hash[..2];
        let file_path = self.base_path.join(subdir).join(hash);
        match tokio::fs::read(&file_path).await {
            Ok(data) => Ok(Some(data)),
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(None),
            Err(e) => Err(e.into()),
        }
    }

    async fn delete(&self, hash: &str) -> Result<(), anyhow::Error> {
        let subdir = &hash[..2];
        let file_path = self.base_path.join(subdir).join(hash);
        let meta_path = self.base_path.join(subdir).join(format!("{}.meta", hash));
        tokio::fs::remove_file(file_path).await.ok();
        tokio::fs::remove_file(meta_path).await.ok();
        Ok(())
    }

    async fn exists(&self, hash: &str) -> Result<bool, anyhow::Error> {
        let subdir = &hash[..2];
        let file_path = self.base_path.join(subdir).join(hash);
        Ok(file_path.exists())
    }
}


