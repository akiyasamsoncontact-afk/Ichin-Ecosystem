use std::collections::HashMap;
use std::sync::Arc;

use tokio::sync::Mutex;
use uuid::Uuid;

use crate::protocol::envelope::Envelope;

#[derive(Debug, Clone)]
pub struct DeliveryStatus {
    pub message_id: Uuid,
    pub status: String,
    pub attempts: u32,
    pub last_error: Option<String>,
}

pub struct DeliveryQueue {
    db: sled::Db,
    delivery_status: Arc<Mutex<HashMap<Uuid, DeliveryStatus>>>,
}

impl DeliveryQueue {
    pub fn open(path: &str) -> Result<Self, anyhow::Error> {
        let db = sled::open(path)?;
        Ok(Self {
            db,
            delivery_status: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn enqueue(&self, envelope: &Envelope) -> Result<(), anyhow::Error> {
        let key = envelope.message_id.as_bytes();
        let value = serde_json::to_vec(envelope)?;

        // Idempotent: check if already queued
        if self.db.contains_key(key)? {
            tracing::info!("Message {} already queued, skipping", envelope.message_id);
            return Ok(());
        }

        self.db.insert(key, value)?;
        self.db.flush()?;
        tracing::info!("Enqueued message {}", envelope.message_id);
        Ok(())
    }

    pub fn dequeue(&self) -> Result<Option<Envelope>, anyhow::Error> {
        if let Some(item) = self.db.iter().next() {
            let (key, value) = item?;
            self.db.remove(key)?;
            let envelope: Envelope = serde_json::from_slice(&value)?;
            return Ok(Some(envelope));
        }
        Ok(None)
    }

    pub fn peek_all(&self) -> Result<Vec<Envelope>, anyhow::Error> {
        let mut messages = Vec::new();
        for item in self.db.iter() {
            let (_, value) = item?;
            let envelope: Envelope = serde_json::from_slice(&value)?;
            messages.push(envelope);
        }
        Ok(messages)
    }

    pub fn len(&self) -> usize {
        self.db.len()
    }

    pub async fn update_status(
        &self,
        message_id: Uuid,
        status: String,
        error: Option<String>,
    ) {
        let mut statuses = self.delivery_status.lock().await;
        let entry = statuses.entry(message_id).or_insert(DeliveryStatus {
            message_id,
            status: "pending".to_string(),
            attempts: 0,
            last_error: None,
        });
        entry.status = status;
        entry.attempts += 1;
        entry.last_error = error;
    }
}
