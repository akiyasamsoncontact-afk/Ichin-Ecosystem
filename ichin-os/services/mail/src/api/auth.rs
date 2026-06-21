use axum::{
    extract::{State, Request},
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::Response,
    Json,
};
use ichin_account_core::storage::AccountStore;
use std::sync::Arc;

#[derive(Clone)]
pub struct AuthState {
    pub store: AccountStore,
}

pub async fn auth_middleware(
    State(auth): State<Arc<AuthState>>,
    headers: HeaderMap,
    mut req: Request,
    next: Next,
) -> Result<Response, (StatusCode, Json<serde_json::Value>)> {
    let token = headers
        .get("Authorization")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .map(|s| s.to_string());

    match token {
        Some(t) => {
            match auth.store.get_session_by_token(&t) {
                Ok(Some(session)) if session.is_active => {
                    req.extensions_mut().insert(session);
                    Ok(next.run(req).await)
                }
                _ => Err((
                    StatusCode::UNAUTHORIZED,
                    Json(serde_json::json!({"error": "Invalid or expired session"})),
                )),
            }
        }
        None => {
            // Allow unauthenticated access to status and static files
            let path = req.uri().path().to_string();
            if path == "/api/status" || path == "/" || path.starts_with("/settings") || !path.starts_with("/api/") {
                return Ok(next.run(req).await);
            }
            Err((
                StatusCode::UNAUTHORIZED,
                Json(serde_json::json!({"error": "Missing authorization token"})),
            ))
        }
    }
}
