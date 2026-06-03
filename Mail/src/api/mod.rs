use std::sync::Arc;

use axum::extract::{Path as RoutePath, Query, State};
use axum::http::StatusCode;
use axum::response::{Html, IntoResponse, Json, Response};
use axum::routing::{get, post};
use axum::Router;
use chrono::Utc;
use serde::{Deserialize, Serialize};
use tower_http::cors::CorsLayer;

use crate::delivery::queue::DeliveryQueue;
use crate::protocol::envelope::Envelope;
use crate::security::keys::KeyPair;
use crate::security::sign::sign_envelope;
use crate::storage::mailbox::{Mailbox, Message, Recipient};

#[derive(Clone)]
pub struct AppState {
    pub mailbox: Arc<Mailbox>,
    pub delivery_queue: Arc<DeliveryQueue>,
    pub server_keys: Arc<KeyPair>,
}

#[derive(Deserialize)]
pub struct FolderQuery {
    folder: Option<String>,
}

#[derive(Deserialize)]
pub struct SendRequest {
    pub to: Vec<String>,
    pub subject: String,
    pub body: String,
    pub from: String,
}

#[derive(Deserialize)]
pub struct ActionRequest {
    pub action: String,
}

#[derive(Serialize)]
pub struct StatusResponse {
    pub status: String,
    pub version: String,
    pub uptime: i64,
}

#[derive(Serialize)]
pub struct ApiMessage {
    pub id: String,
    pub sender: SenderInfo,
    pub to: Vec<RecipientInfo>,
    pub subject: String,
    pub preview: String,
    pub body: String,
    pub timestamp: String,
    pub unread: bool,
    pub starred: bool,
    pub attachments: Vec<AttachmentInfo>,
    pub folder: String,
}

#[derive(Serialize)]
pub struct SenderInfo {
    pub name: String,
    pub email: String,
    pub avatar: String,
}

#[derive(Serialize)]
pub struct RecipientInfo {
    pub name: String,
    pub email: String,
}

#[derive(Serialize)]
pub struct AttachmentInfo {
    pub name: String,
    pub size: String,
}

pub fn get_avatar_initials(name: &str) -> String {
    let parts: Vec<&str> = name.split_whitespace().collect();
    parts.iter()
        .filter_map(|p| p.chars().next())
        .take(2)
        .collect::<String>()
        .to_uppercase()
}

fn serve_frontend(path: &str) -> Response {
    let frontend_dir = if let Ok(dir) = std::env::var("ICHIN_FRONTEND_DIR") {
        dir
    } else {
        let crate_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
        format!("{}/frontend", crate_dir)
    };

    let file_path = std::path::Path::new(&frontend_dir).join(path);
    if file_path.exists() && file_path.is_file() {
        let content = std::fs::read_to_string(&file_path).unwrap_or_default();
        let mime = mime_guess::from_path(&file_path).first_or_octet_stream();
        let content_type = mime.to_string();
        Response::builder()
            .header("Content-Type", content_type)
            .body(axum::body::Body::from(content))
            .unwrap()
    } else {
        let not_found = Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(axum::body::Body::from("Not found"))
            .unwrap();
        not_found
    }
}

async fn handle_static(RoutePath(path): RoutePath<String>) -> Response {
    serve_frontend(&path)
}

async fn handle_index() -> Response {
    let frontend_dir = if let Ok(dir) = std::env::var("ICHIN_FRONTEND_DIR") {
        dir
    } else {
        let crate_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
        format!("{}/frontend", crate_dir)
    };
    let index_path = std::path::Path::new(&frontend_dir).join("index.html");
    let content = std::fs::read_to_string(&index_path).unwrap_or_else(|_| "<html><body>Frontend not found</body></html>".to_string());
    Html(content).into_response()
}

pub fn create_routes(state: AppState) -> Router {
    Router::new()
        .route("/api/status", get(handle_status))
        .route("/api/messages", get(handle_list_messages).post(handle_send_message))
        .route("/api/messages/{id}", get(handle_get_message))
        .route("/api/messages/{id}/action", post(handle_message_action))
        .route("/api/messages/{id}/read", post(handle_mark_read))
        .route("/api/messages/{id}/star", post(handle_toggle_star))
        .route("/api/unread-counts", get(handle_unread_counts))
        .route("/", get(handle_index))
        .route("/settings.html", get(handle_settings))
        .route("/{*path}", get(handle_static))
        .layer(CorsLayer::permissive())
        .with_state(state)
}

async fn handle_settings() -> Response {
    let frontend_dir = if let Ok(dir) = std::env::var("ICHIN_FRONTEND_DIR") {
        dir
    } else {
        let crate_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap_or_else(|_| ".".to_string());
        format!("{}/frontend", crate_dir)
    };
    let settings_path = std::path::Path::new(&frontend_dir).join("settings.html");
    let content = std::fs::read_to_string(&settings_path).unwrap_or_else(|_| "<html><body>Settings not found</body></html>".to_string());
    Html(content).into_response()
}

async fn handle_status(
    State(_state): State<AppState>,
) -> Json<StatusResponse> {
    Json(StatusResponse {
        status: "ok".to_string(),
        version: "1.0.0".to_string(),
        uptime: chrono::Utc::now().timestamp(),
    })
}

async fn handle_list_messages(
    State(state): State<AppState>,
    Query(query): Query<FolderQuery>,
) -> Result<Json<Vec<ApiMessage>>, (StatusCode, String)> {
    let folder = query.folder.as_deref().unwrap_or("inbox");
    let messages = state.mailbox.list_folder(folder)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    let api_msgs: Vec<ApiMessage> = messages.into_iter().map(|m| to_api_message(m)).collect();
    Ok(Json(api_msgs))
}

async fn handle_get_message(
    State(state): State<AppState>,
    RoutePath(id): RoutePath<String>,
) -> Result<Json<ApiMessage>, (StatusCode, String)> {
    let msg = state.mailbox.get_message(&id)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?
        .ok_or_else(|| (StatusCode::NOT_FOUND, "Message not found".to_string()))?;

    // Mark as read
    state.mailbox.mark_read(&id, true)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(to_api_message(msg)))
}

async fn handle_send_message(
    State(state): State<AppState>,
    Json(req): Json<SendRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let from_email = if req.from.is_empty() {
        "me@ichin.network".to_string()
    } else {
        req.from.clone()
    };

    let mut envelope = Envelope::new(
        from_email.clone(),
        req.to.clone(),
        req.subject.clone(),
        req.body.clone(),
    );

    // Sign the envelope
    sign_envelope(&mut envelope, &state.server_keys)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // Queue for delivery
    state.delivery_queue.enqueue(&envelope)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    // Store in sent folder
    let msg = Message {
        id: envelope.message_id.to_string(),
        from_name: "Me".to_string(),
        from_email: from_email.clone(),
        to: req.to.iter().map(|t| Recipient {
            name: t.clone(),
            email: t.clone(),
        }).collect(),
        subject: req.subject.clone(),
        body: req.body.clone(),
        timestamp: Utc::now().timestamp(),
        folder: "sent".to_string(),
        unread: false,
        starred: false,
        attachments: vec![],
    };

    state.mailbox.store_message(&msg)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;

    Ok(Json(serde_json::json!({
        "status": "sent",
        "message_id": envelope.message_id.to_string(),
    })))
}

async fn handle_message_action(
    State(state): State<AppState>,
    RoutePath(id): RoutePath<String>,
    Json(req): Json<ActionRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    match req.action.as_str() {
        "archive" => {
            state.mailbox.update_folder(&id, "archive")
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        }
        "trash" => {
            state.mailbox.update_folder(&id, "trash")
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        }
        "delete" => {
            state.mailbox.delete_message(&id)
                .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        }
        _ => return Err((StatusCode::BAD_REQUEST, "Unknown action".to_string())),
    }

    Ok(Json(serde_json::json!({"status": "ok"})))
}

async fn handle_mark_read(
    State(state): State<AppState>,
    RoutePath(id): RoutePath<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    state.mailbox.mark_read(&id, true)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    Ok(Json(serde_json::json!({"status": "ok"})))
}

async fn handle_toggle_star(
    State(state): State<AppState>,
    RoutePath(id): RoutePath<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    state.mailbox.toggle_star(&id)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
    Ok(Json(serde_json::json!({"status": "ok"})))
}

async fn handle_unread_counts(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    let mut counts = serde_json::Map::new();
    for folder in &["inbox", "sent", "drafts", "archive", "trash", "spam"] {
        let count = state.mailbox.unread_count(folder)
            .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()))?;
        counts.insert(folder.to_string(), serde_json::json!(count));
    }
    Ok(Json(serde_json::Value::Object(counts)))
}

fn to_api_message(msg: Message) -> ApiMessage {
    let sender_name = if msg.from_name.contains('@') {
        msg.from_email.split('@').next().unwrap_or("User").to_string()
    } else {
        msg.from_name.clone()
    };

    let preview = msg.body.lines().next().unwrap_or("").to_string();
    let preview = if preview.len() > 100 {
        format!("{}...", &preview[..97])
    } else {
        preview
    };

    let timestamp = chrono::DateTime::from_timestamp(msg.timestamp, 0)
        .map(|dt| dt.to_rfc3339())
        .unwrap_or_else(|| Utc::now().to_rfc3339());

    ApiMessage {
        id: msg.id,
        sender: SenderInfo {
            name: sender_name.clone(),
            email: msg.from_email,
            avatar: get_avatar_initials(&sender_name),
        },
        to: msg.to.into_iter().map(|r| RecipientInfo {
            name: r.name,
            email: r.email,
        }).collect(),
        subject: msg.subject,
        preview,
        body: msg.body,
        timestamp,
        unread: msg.unread,
        starred: msg.starred,
        attachments: msg.attachments.into_iter().map(|a| AttachmentInfo {
            name: a.name,
            size: a.size,
        }).collect(),
        folder: msg.folder,
    }
}

pub async fn start_api_server(
    addr: &str,
    mailbox: Arc<Mailbox>,
    delivery_queue: Arc<DeliveryQueue>,
    server_keys: Arc<KeyPair>,
) -> Result<(), anyhow::Error> {
    let state = AppState {
        mailbox,
        delivery_queue,
        server_keys,
    };

    let app = create_routes(state);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    tracing::info!("API server listening on {}", addr);

    axum::serve(listener, app).await?;
    Ok(())
}
