use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attachment {
    pub filename: String,
    pub mime_type: String,
    pub size_bytes: u64,
    pub hash: String,
    pub url: String,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Metadata {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expiration: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub read_receipt: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scheduled_delivery: Option<i64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub delivery_status: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeliveryStatus {
    Pending,
    Delivered,
    Failed(String),
}
