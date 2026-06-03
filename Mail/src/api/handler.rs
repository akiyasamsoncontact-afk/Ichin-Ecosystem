use std::sync::Arc;

use axum::extract::{Path, Query, State};
use axum::Json;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::api::ApiState;
use crate::protocol::envelope::Envelope;
use crate::security::sign::sign_envelope;
use crate::storage::mailbox::{AttachmentRef, Message, Recipient};

#[derive(Serialize)]
pub struct StatusResponse {
    pub status: String,
    pub version: String,
    pub server_name: String,
    pub key_id: String,
    pub uptime: i64,
}

lazy_static::lazy_static! {
    static ref START_TIME: i64 = chrono::Utc::now().timestamp();
}

pub async fn status(State(state): State<Arc<ApiState>>) -> Json<StatusResponse> {
    Json(StatusResponse {
        status: "ok".to_string(),
        version: "1.0.0".to_string(),
        server_name: state.server_name.clone(),
        key_id: state.server_keys.key_id.clone(),
        uptime: Utc::now().timestamp() - *START_TIME,
    })
}

#[derive(Deserialize)]
pub struct ListQuery {
    pub folder: Option<String>,
}

pub async fn list_messages(
    State(state): State<Arc<ApiState>>,
    Query(query): Query<ListQuery>,
) -> Json<Vec<Message>> {
    let folder = query.folder.unwrap_or_else(|| "inbox".to_string());
    match state.mailbox.list_folder(&folder) {
        Ok(msgs) => Json(msgs),
        Err(e) => {
            tracing::error!("Failed to list messages: {}", e);
            Json(Vec::new())
        }
    }
}

#[derive(Deserialize)]
pub struct SendRequest {
    pub to: Vec<String>,
    pub subject: String,
    pub body: String,
}

#[derive(Serialize)]
pub struct SendResponse {
    pub id: String,
    pub status: String,
}

pub async fn send_message(
    State(state): State<Arc<ApiState>>,
    Json(req): Json<SendRequest>,
) -> Json<SendResponse> {
    let msg_id = Uuid::new_v4().to_string();

    // Create Ichin envelope
    let from = format!("me@{}", state.server_name);
    let mut envelope = Envelope::new(from.clone(), req.to.clone(), req.subject.clone(), req.body.clone());
    envelope.message_id = Uuid::parse_str(&msg_id).unwrap_or_else(|_| Uuid::new_v4());

    // Sign it
    if let Err(e) = sign_envelope(&mut envelope, &state.server_keys) {
        tracing::error!("Failed to sign message: {}", e);
        return Json(SendResponse {
            id: msg_id,
            status: format!("error: {}", e),
        });
    }

    // Enqueue for delivery
    if let Err(e) = state.delivery_queue.enqueue(&envelope) {
        tracing::error!("Failed to enqueue message: {}", e);
        return Json(SendResponse {
            id: msg_id,
            status: format!("error: {}", e),
        });
    }

    // Store in sent folder
    let msg = Message {
        id: msg_id.clone(),
        from_name: "You".to_string(),
        from_email: from,
        to: req
            .to
            .iter()
            .map(|t| Recipient {
                name: t.clone(),
                email: t.clone(),
            })
            .collect(),
        subject: req.subject,
        body: req.body,
        timestamp: Utc::now().timestamp_millis(),
        folder: "sent".to_string(),
        unread: false,
        starred: false,
        attachments: vec![],
    };

    if let Err(e) = state.mailbox.store_message(&msg) {
        tracing::error!("Failed to store sent message: {}", e);
    }

    Json(SendResponse {
        id: msg_id,
        status: "queued".to_string(),
    })
}

pub async fn get_message(
    State(state): State<Arc<ApiState>>,
    Path(id): Path<String>,
) -> Json<Option<Message>> {
    match state.mailbox.get_message(&id) {
        Ok(msg) => {
            // Mark as read
            if let Some(ref m) = msg {
                if m.unread {
                    let _ = state.mailbox.mark_read(&id, true);
                }
            }
            Json(msg)
        }
        Err(e) => {
            tracing::error!("Failed to get message: {}", e);
            Json(None)
        }
    }
}

#[derive(Deserialize)]
pub struct FolderUpdate {
    pub folder: String,
}

pub async fn update_folder(
    State(state): State<Arc<ApiState>>,
    Path(id): Path<String>,
    Json(req): Json<FolderUpdate>,
) -> Json<&'static str> {
    match state.mailbox.update_folder(&id, &req.folder) {
        Ok(_) => Json("ok"),
        Err(e) => {
            tracing::error!("Failed to update folder: {}", e);
            Json("error")
        }
    }
}

pub async fn toggle_star(
    State(state): State<Arc<ApiState>>,
    Path(id): Path<String>,
) -> Json<&'static str> {
    match state.mailbox.toggle_star(&id) {
        Ok(_) => Json("ok"),
        Err(e) => {
            tracing::error!("Failed to toggle star: {}", e);
            Json("error")
        }
    }
}

pub async fn mark_read(
    State(state): State<Arc<ApiState>>,
    Path(id): Path<String>,
) -> Json<&'static str> {
    match state.mailbox.mark_read(&id, true) {
        Ok(_) => Json("ok"),
        Err(e) => {
            tracing::error!("Failed to mark read: {}", e);
            Json("error")
        }
    }
}

pub async fn delete_message(
    State(state): State<Arc<ApiState>>,
    Path(id): Path<String>,
) -> Json<&'static str> {
    match state.mailbox.delete_message(&id) {
        Ok(_) => Json("ok"),
        Err(e) => {
            tracing::error!("Failed to delete message: {}", e);
            Json("error")
        }
    }
}

#[derive(Serialize)]
pub struct UnreadCounts {
    pub inbox: usize,
    pub sent: usize,
    pub drafts: usize,
    pub spam: usize,
}

pub async fn unread_counts(
    State(state): State<Arc<ApiState>>,
) -> Json<UnreadCounts> {
    let inbox = state.mailbox.unread_count("inbox").unwrap_or(0);
    let sent = state.mailbox.unread_count("sent").unwrap_or(0);
    let drafts = state.mailbox.unread_count("drafts").unwrap_or(0);
    let spam = state.mailbox.unread_count("spam").unwrap_or(0);

    Json(UnreadCounts {
        inbox,
        sent,
        drafts,
        spam,
    })
}
