use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use serde::Serialize;
use std::sync::Arc;
use crate::db::Database;
use crate::db::Tab;

#[derive(Serialize)]
struct TabsResponse {
    tabs: Vec<Tab>,
}

pub async fn list_tabs(
    State(db): State<Arc<Database>>,
) -> Result<Json<TabsResponse>, StatusCode> {
    db.get_tabs()
        .map(|tabs| Json(TabsResponse { tabs }))
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn list_tabs_by_workspace(
    State(db): State<Arc<Database>>,
    axum::extract::Path(workspace_id): axum::extract::Path<String>,
) -> Result<Json<TabsResponse>, StatusCode> {
    db.get_tabs_by_workspace(&workspace_id)
        .map(|tabs| Json(TabsResponse { tabs }))
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn create_tab(
    State(db): State<Arc<Database>>,
    Json(tab): Json<Tab>,
) -> Result<Json<Tab>, StatusCode> {
    db.create_tab(tab)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn update_tab(
    State(db): State<Arc<Database>>,
    axum::extract::Path(id): axum::extract::Path<String>,
    Json(tab): Json<Tab>,
) -> Result<Json<Tab>, StatusCode> {
    db.update_tab(&id, tab)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn delete_tab(
    State(db): State<Arc<Database>>,
    axum::extract::Path(id): axum::extract::Path<String>,
) -> StatusCode {
    db.delete_tab(&id)
        .map(|_| StatusCode::OK)
        .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn reorder_tabs(
    State(db): State<Arc<Database>>,
    Json(tab_ids): Json<Vec<String>>,
) -> StatusCode {
    db.reorder_tabs(tab_ids)
        .map(|_| StatusCode::OK)
        .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
}