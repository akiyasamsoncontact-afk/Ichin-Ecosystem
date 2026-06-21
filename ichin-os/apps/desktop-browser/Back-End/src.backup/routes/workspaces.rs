use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use serde::Serialize;
use std::sync::Arc;
use crate::db::Database;
use crate::db::Workspace;

#[derive(Serialize)]
struct WorkspaceResponse {
    workspaces: Vec<Workspace>,
}

pub async fn list_workspaces(
    State(db): State<Arc<Database>>,
) -> Result<Json<WorkspaceResponse>, StatusCode> {
    db.get_workspaces()
        .map(|workspaces| Json(WorkspaceResponse { workspaces }))
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn create_workspace(
    State(db): State<Arc<Database>>,
    Json(workspace): Json<Workspace>,
) -> Result<Json<Workspace>, StatusCode> {
    db.create_workspace(workspace)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn update_workspace(
    State(db): State<Arc<Database>>,
    axum::extract::Path(id): axum::extract::Path<String>,
    Json(workspace): Json<Workspace>,
) -> Result<Json<Workspace>, StatusCode> {
    db.update_workspace(&id, workspace)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn delete_workspace(
    State(db): State<Arc<Database>>,
    axum::extract::Path(id): axum::extract::Path<String>,
) -> StatusCode {
    db.delete_workspace(&id)
        .map(|_| StatusCode::OK)
        .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
}