pub mod attachment;
pub mod local;
pub mod mailbox;

use async_trait::async_trait;

#[async_trait]
pub trait AttachmentStorage: Send + Sync {
    async fn store(&self, filename: &str, data: &[u8], mime_type: &str) -> Result<String, anyhow::Error>;
    async fn retrieve(&self, hash: &str) -> Result<Option<Vec<u8>>, anyhow::Error>;
    async fn delete(&self, hash: &str) -> Result<(), anyhow::Error>;
    async fn exists(&self, hash: &str) -> Result<bool, anyhow::Error>;
}

pub use mailbox::Mailbox;
