use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use serde::Serialize;
use std::sync::Arc;
use crate::db::Database;
use crate::db::HistoryItem;

#[derive(Serialize)]
struct HistoryResponse {
    history: Vec<HistoryItem>,
}

pub async fn list_history(
    State(db): State<Arc<Database>>,
) -> Result<Json<HistoryResponse>, StatusCode> {
    db.get_history(100) // Default limit of 100
        .map(|history| Json(HistoryResponse { history }))
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn add_history(
    State(db): State<Arc<Database>>,
    Json(history): Json<HistoryItem>,
) -> Result<Json<HistoryItem>, StatusCode> {
    db.add_history(history)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn delete_history(
    State(db): State<Arc<Database>>,
    axum::extract::Path(id): axum::extract::Path<String>,
) -> StatusCode {
    db.delete_history(&id)
        .map(|_| StatusCode::OK)
        .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
}