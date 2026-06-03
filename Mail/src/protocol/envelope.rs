use chrono::Utc;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::types::{Attachment, Metadata};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Envelope {
    pub message_id: Uuid,
    pub from: String,
    pub to: Vec<String>,
    pub timestamp: i64,
    pub subject: String,
    pub body: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body_html: Option<String>,
    #[serde(default)]
    pub attachments: Vec<Attachment>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reply_to_id: Option<Uuid>,
    #[serde(default)]
    pub metadata: Metadata,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signature: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signing_key_id: Option<String>,
}

impl Envelope {
    pub fn new(
        from: String,
        to: Vec<String>,
        subject: String,
        body: String,
    ) -> Self {
        Self {
            message_id: Uuid::new_v4(),
            from,
            to,
            timestamp: Utc::now().timestamp(),
            subject,
            body,
            body_html: None,
            attachments: Vec::new(),
            reply_to_id: None,
            metadata: Metadata::default(),
            signature: None,
            signing_key_id: None,
        }
    }

    pub fn serialize(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }

    pub fn deserialize(data: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(data)
    }

    pub fn canonical_bytes(&self) -> Vec<u8> {
        let mut canonical = self.clone();
        canonical.signature = None;
        canonical.signing_key_id = None;
        serde_json::to_vec(&canonical).unwrap_or_default()
    }

    pub fn verify_integrity(&self) -> bool {
        self.signature.is_some() && self.signing_key_id.is_some()
    }
}
