use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use serde::Serialize;
use std::sync::Arc;
use crate::db::Database;
use crate::db::Favorite;

#[derive(Serialize)]
struct FavoritesResponse {
    favorites: Vec<Favorite>,
}

pub async fn list_favorites(
    State(db): State<Arc<Database>>,
) -> Result<Json<FavoritesResponse>, StatusCode> {
    db.get_favorites()
        .map(|favorites| Json(FavoritesResponse { favorites }))
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn create_favorite(
    State(db): State<Arc<Database>>,
    Json(favorite): Json<Favorite>,
) -> Result<Json<Favorite>, StatusCode> {
    db.create_favorite(favorite)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn delete_favorite(
    State(db): State<Arc<Database>>,
    axum::extract::Path(id): axum::extract::Path<String>,
) -> StatusCode {
    db.delete_favorite(&id)
        .map(|_| StatusCode::OK)
        .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
}