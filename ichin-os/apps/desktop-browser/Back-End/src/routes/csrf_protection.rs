use axum::{
    extract::{Request, State},
    http::StatusCode,
    middleware::Next,
    response::Response,
};
use tower_sessions::Session;
use uuid::Uuid;
use crate::AppState;

/// CSRF protection middleware
pub async fn csrf_protection(
    State(state): State<AppState>,
    mut req: Request,
    session: Session,
    next: Next,
) -> Result<Response, (StatusCode, String)> {
    // Skip CSRF check for GET, HEAD, OPTIONS, TRACE methods
    if !req.method().is_safe() {
        // Extract CSRF token from header
        let csrf_token = req
            .headers()
            .get("x-csrf-token")
            .and_then(|value| value.to_str().ok())
            .unwrap_or("");

        // Get CSRF token from session
        let session_token: Option<String> = session
            .get::<String>("csrf_token")
            .map_err(|_| (StatusCode::INTERNAL_SERVER_ERROR, "Failed to read session".to_string()))?;

        // Generate new token if none exists in session
        let session_token = match session_token {
            Some(token) => token,
            None => {
                let new_token = Uuid::new_v4().to_string();
                session
                    .insert("csrf_token", new_token.clone())
                    .map_err(|_| (StatusCode::INTERNAL_SERVER_ERROR, "Failed to write session".to_string()))?;
                new_token
            }
        };

        // Validate CSRF token
        if csrf_token.is_empty() || csrf_token != session_token {
            return Err((
                StatusCode::FORBIDDEN,
                "CSRF token validation failed".to_string(),
            ));
        }
    }

    Ok(next.run(req).await)
}