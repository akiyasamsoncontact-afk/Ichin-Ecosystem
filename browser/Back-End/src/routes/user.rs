use axum::{
    extract::State,
    http::StatusCode,
    Json,
};
use serde::Serialize;
use std::sync::Arc;
use crate::db::Database;
use crate::db::UserProfile;

#[derive(Serialize)]
struct UserProfileResponse {
    profile: UserProfile,
}

pub async fn get_profile(
    State(db): State<Arc<Database>>,
) -> Result<Json<UserProfileResponse>, StatusCode> {
    db.get_user_profile()
        .map(|profile| Json(UserProfileResponse { profile }))
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}

pub async fn update_profile(
    State(db): State<Arc<Database>>,
    Json(profile): Json<UserProfile>,
) -> Result<Json<UserProfile>, StatusCode> {
    db.update_user_profile(profile)
        .map(Json)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)
}