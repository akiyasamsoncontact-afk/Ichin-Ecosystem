use std::sync::Arc;

use axum::{
    extract::{Extension, Path, State},
    http::{HeaderMap, StatusCode},
    middleware,
    response::IntoResponse,
    routing::{delete, get, post, put},
    Json, Router,
};
use chrono::Utc;
use ichin_account_core::auth::AuthManager;
use ichin_account_core::models::*;
use ichin_account_core::storage::AccountStore;
use serde::{Deserialize, Serialize};
use tower_http::cors::CorsLayer;
use tracing::info;
use uuid::Uuid;

#[derive(Clone)]
struct AppState {
    store: AccountStore,
    auth: Arc<AuthManager>,
}

// --- Request/Response types ---

#[derive(Deserialize)]
struct RegisterRequest {
    username: String,
    display_name: String,
    email: String,
}

#[derive(Serialize)]
struct RegisterResponse {
    user_id: Uuid,
    session_token: String,
    recovery_codes: Vec<String>,
}

#[derive(Deserialize)]
struct LoginPasskeyRequest {
    username: String,
    credential_id: String,
    ip_address: Option<String>,
    user_agent: Option<String>,
    device_id: Option<Uuid>,
}

#[derive(Deserialize)]
struct LoginTOTPRequest {
    username: String,
    code: String,
    ip_address: Option<String>,
    user_agent: Option<String>,
    device_id: Option<Uuid>,
}

#[derive(Deserialize)]
struct LoginRecoveryRequest {
    username: String,
    code: String,
    ip_address: Option<String>,
    user_agent: Option<String>,
}

#[derive(Serialize)]
struct LoginResponse {
    session_token: String,
    user: UserResponse,
}

#[derive(Serialize, Clone)]
struct UserResponse {
    id: Uuid,
    username: String,
    display_name: String,
    email: String,
    profile_picture: Option<String>,
    has_passkeys: bool,
    has_totp: bool,
    recovery_codes_count: usize,
    created_at: String,
}

#[derive(Deserialize)]
struct RegisterPasskeyRequest {
    credential_id: String,
    public_key: Vec<u8>,
    transports: Vec<String>,
    name: String,
}

#[derive(Deserialize)]
struct SetupTOTPRequest {
    code: String,
}

#[derive(Serialize)]
struct TOTPSetupResponse {
    otpauth_url: String,
    secret: String,
}

#[derive(Deserialize)]
struct UpdateProfileRequest {
    display_name: Option<String>,
    profile_picture: Option<String>,
}

#[derive(Deserialize)]
struct UpdateSettingsRequest {
    theme: Option<String>,
    language: Option<String>,
    email_notifications: Option<bool>,
    auto_sync: Option<bool>,
}

#[derive(Deserialize)]
struct CreateDeviceRequest {
    name: String,
    device_type: String,
}

#[derive(Serialize)]
struct ApiError {
    error: String,
}

#[derive(Deserialize)]
struct BookmarkRequest {
    title: String,
    url: String,
    folder: Option<String>,
    position: Option<i32>,
}

#[derive(Deserialize)]
struct HistoryRequest {
    url: String,
    title: String,
}

#[derive(Deserialize)]
struct SavePasswordRequest {
    domain: String,
    username: String,
    encrypted_password: Vec<u8>,
}

#[derive(Deserialize)]
struct SyncTabRequest {
    device_id: Uuid,
    title: String,
    url: String,
    active: bool,
}

#[derive(Deserialize)]
struct UpdateBrowserSettingsRequest {
    homepage: Option<String>,
    search_engine: Option<String>,
    privacy_mode: Option<bool>,
    sync_passwords: Option<bool>,
    sync_history: Option<bool>,
    sync_bookmarks: Option<bool>,
    sync_tabs: Option<bool>,
    sync_settings: Option<bool>,
}

// --- Auth extraction helper ---

fn extract_session_token(headers: &HeaderMap) -> Option<String> {
    headers
        .get("Authorization")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .map(|s| s.to_string())
}

async fn auth_middleware(
    State(state): State<AppState>,
    headers: HeaderMap,
    mut req: axum::extract::Request,
    next: middleware::Next,
) -> Result<impl IntoResponse, (StatusCode, Json<ApiError>)> {
    let token = extract_session_token(&headers)
        .ok_or_else(|| {
            (
                StatusCode::UNAUTHORIZED,
                Json(ApiError {
                    error: "Missing authorization token".to_string(),
                }),
            )
        })?;

    let session = state
        .auth
        .validate_session(&token)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::UNAUTHORIZED,
                Json(ApiError {
                    error: "Invalid or expired session".to_string(),
                }),
            )
        })?;

    let _ = state.auth.touch_session(&session);
    req.extensions_mut().insert(session);
    Ok(next.run(req).await)
}

// --- Route handlers ---

async fn register(
    State(state): State<AppState>,
    Json(req): Json<RegisterRequest>,
) -> Result<Json<RegisterResponse>, (StatusCode, Json<ApiError>)> {
    let user = state
        .auth
        .register_user(&req.username, &req.display_name, &req.email)
        .map_err(|e| {
            (
                StatusCode::CONFLICT,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    let codes = state.auth.generate_recovery_codes();
    let session = state
        .auth
        .create_session(user.id, None, "0.0.0.0", "registration")
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    info!("User registered: {}", user.username);
    Ok(Json(RegisterResponse {
        user_id: user.id,
        session_token: session.token,
        recovery_codes: codes,
    }))
}

async fn login_passkey(
    State(state): State<AppState>,
    Json(req): Json<LoginPasskeyRequest>,
) -> Result<Json<LoginResponse>, (StatusCode, Json<ApiError>)> {
    let user = state
        .store
        .get_user_by_username(&req.username)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    let _credential = user
        .passkey_credentials
        .iter()
        .find(|c| c.id == req.credential_id)
        .ok_or_else(|| {
            (
                StatusCode::UNAUTHORIZED,
                Json(ApiError {
                    error: "Invalid credential".to_string(),
                }),
            )
        })?;

    let session = state
        .auth
        .create_session(
            user.id,
            req.device_id,
            req.ip_address.as_deref().unwrap_or(""),
            req.user_agent.as_deref().unwrap_or(""),
        )
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    let _ = state.auth.record_login(
        user.id,
        req.ip_address.as_deref().unwrap_or(""),
        req.user_agent.as_deref().unwrap_or(""),
        true,
        AuthMethod::Passkey,
    );

    info!("User logged in via passkey: {}", user.username);
    Ok(Json(LoginResponse {
        session_token: session.token,
        user: to_user_response(&user),
    }))
}

async fn login_totp(
    State(state): State<AppState>,
    Json(req): Json<LoginTOTPRequest>,
) -> Result<Json<LoginResponse>, (StatusCode, Json<ApiError>)> {
    let user = state
        .store
        .get_user_by_username(&req.username)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    let valid = AuthManager::verify_totp(&user, &req.code).map_err(|_| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: "TOTP verification failed".to_string(),
            }),
        )
    })?;

    if !valid {
        let _ = state.auth.record_login(
            user.id,
            req.ip_address.as_deref().unwrap_or(""),
            req.user_agent.as_deref().unwrap_or(""),
            false,
            AuthMethod::TOTP,
        );
        return Err((
            StatusCode::UNAUTHORIZED,
            Json(ApiError {
                error: "Invalid TOTP code".to_string(),
            }),
        ));
    }

    let session = state
        .auth
        .create_session(
            user.id,
            req.device_id,
            req.ip_address.as_deref().unwrap_or(""),
            req.user_agent.as_deref().unwrap_or(""),
        )
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    let _ = state.auth.record_login(
        user.id,
        req.ip_address.as_deref().unwrap_or(""),
        req.user_agent.as_deref().unwrap_or(""),
        true,
        AuthMethod::TOTP,
    );

    info!("User logged in via TOTP: {}", user.username);
    Ok(Json(LoginResponse {
        session_token: session.token,
        user: to_user_response(&user),
    }))
}

async fn login_recovery(
    State(state): State<AppState>,
    Json(req): Json<LoginRecoveryRequest>,
) -> Result<Json<LoginResponse>, (StatusCode, Json<ApiError>)> {
    let mut user = state
        .store
        .get_user_by_username(&req.username)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    if !AuthManager::verify_recovery_code(&mut user, &req.code) {
        return Err((
            StatusCode::UNAUTHORIZED,
            Json(ApiError {
                error: "Invalid recovery code".to_string(),
            }),
        ));
    }

    state.store.update_user(&user).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    let session = state
        .auth
        .create_session(
            user.id,
            None,
            req.ip_address.as_deref().unwrap_or(""),
            req.user_agent.as_deref().unwrap_or(""),
        )
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    let _ = state.auth.record_login(
        user.id,
        req.ip_address.as_deref().unwrap_or(""),
        req.user_agent.as_deref().unwrap_or(""),
        true,
        AuthMethod::RecoveryCode,
    );

    info!("User logged in via recovery code: {}", user.username);
    Ok(Json(LoginResponse {
        session_token: session.token,
        user: to_user_response(&user),
    }))
}

async fn get_me(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<UserResponse>, (StatusCode, Json<ApiError>)> {
    let user = state
        .store
        .get_user(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    Ok(Json(to_user_response(&user)))
}

async fn update_profile(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<UpdateProfileRequest>,
) -> Result<Json<UserResponse>, (StatusCode, Json<ApiError>)> {
    let mut user = state
        .store
        .get_user(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    if let Some(name) = req.display_name {
        user.display_name = name;
    }
    if let Some(pic) = req.profile_picture {
        user.profile_picture = Some(pic);
    }
    user.updated_at = Utc::now();

    state.store.update_user(&user).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    Ok(Json(to_user_response(&user)))
}

async fn register_passkey(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<RegisterPasskeyRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let mut user = state
        .store
        .get_user(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    state
        .auth
        .register_passkey(
            &mut user,
            req.credential_id,
            req.public_key,
            req.transports,
            req.name,
        )
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    Ok(Json(serde_json::json!({ "status": "ok" })))
}

async fn setup_totp(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<TOTPSetupResponse>, (StatusCode, Json<ApiError>)> {
    let mut user = state
        .store
        .get_user(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    let otpauth = state.auth.setup_totp(&mut user).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    Ok(Json(TOTPSetupResponse {
        otpauth_url: otpauth.clone(),
        secret: user.totp_secret.clone().unwrap_or_default(),
    }))
}

async fn verify_totp(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<SetupTOTPRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let user = state
        .store
        .get_user(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?
        .ok_or_else(|| {
            (
                StatusCode::NOT_FOUND,
                Json(ApiError {
                    error: "User not found".to_string(),
                }),
            )
        })?;

    let valid = AuthManager::verify_totp(&user, &req.code).map_err(|_| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: "TOTP verification failed".to_string(),
            }),
        )
    })?;

    if !valid {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ApiError {
                error: "Invalid TOTP code".to_string(),
            }),
        ));
    }

    Ok(Json(serde_json::json!({ "status": "ok" })))
}

async fn get_sessions(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<serde_json::Value>>, (StatusCode, Json<ApiError>)> {
    let sessions = state.store.get_user_sessions(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    let result: Vec<serde_json::Value> = sessions
        .into_iter()
        .map(|s| {
            serde_json::json!({
                "id": s.id,
                "device_id": s.device_id,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "is_active": s.is_active,
                "created_at": s.created_at,
                "expires_at": s.expires_at,
                "last_accessed_at": s.last_accessed_at,
            })
        })
        .collect();

    Ok(Json(result))
}

async fn delete_session(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Path(session_id): Path<Uuid>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    // Only allow deleting own sessions
    let target = state.store.get_session(session_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    match target {
        Some(s) if s.user_id == session.user_id => {
            state.auth.invalidate_session(session_id).map_err(|e| {
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(ApiError {
                        error: e.to_string(),
                    }),
                )
            })?;
            Ok(Json(serde_json::json!({ "status": "deleted" })))
        }
        Some(_) => Err((
            StatusCode::FORBIDDEN,
            Json(ApiError {
                error: "Cannot delete another user's session".to_string(),
            }),
        )),
        None => Err((
            StatusCode::NOT_FOUND,
            Json(ApiError {
                error: "Session not found".to_string(),
            }),
        )),
    }
}

async fn get_devices(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<Device>>, (StatusCode, Json<ApiError>)> {
    let devices = state.store.get_user_devices(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(devices))
}

async fn create_device(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<CreateDeviceRequest>,
) -> Result<Json<Device>, (StatusCode, Json<ApiError>)> {
    let device_type = match req.device_type.as_str() {
        "desktop" => DeviceType::Desktop,
        "laptop" => DeviceType::Laptop,
        "phone" => DeviceType::Phone,
        "tablet" => DeviceType::Tablet,
        _ => DeviceType::Unknown,
    };

    let device = state
        .auth
        .register_device(session.user_id, req.name, device_type)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    Ok(Json(device))
}

async fn delete_device(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Path(device_id): Path<Uuid>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let device = state.store.get_device(device_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    match device {
        Some(d) if d.user_id == session.user_id => {
            state.store.delete_device(device_id).map_err(|e| {
                (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    Json(ApiError {
                        error: e.to_string(),
                    }),
                )
            })?;
            Ok(Json(serde_json::json!({ "status": "deleted" })))
        }
        Some(_) => Err((
            StatusCode::FORBIDDEN,
            Json(ApiError {
                error: "Cannot delete another user's device".to_string(),
            }),
        )),
        None => Err((
            StatusCode::NOT_FOUND,
            Json(ApiError {
                error: "Device not found".to_string(),
            }),
        )),
    }
}

async fn get_login_history(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<LoginHistoryEntry>>, (StatusCode, Json<ApiError>)> {
    let history = state
        .store
        .get_login_history(session.user_id, 50)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;
    Ok(Json(history))
}

async fn get_storage_usage(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<StorageUsage>, (StatusCode, Json<ApiError>)> {
    let usage = state.store.get_storage_usage(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(usage))
}

async fn get_settings(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<AccountSettings>, (StatusCode, Json<ApiError>)> {
    let settings = state.store.get_settings(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(settings))
}

async fn update_settings(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<UpdateSettingsRequest>,
) -> Result<Json<AccountSettings>, (StatusCode, Json<ApiError>)> {
    let mut settings = state.store.get_settings(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    if let Some(theme) = req.theme {
        settings.theme = match theme.as_str() {
            "light" => Theme::Light,
            _ => Theme::Dark,
        };
    }
    if let Some(lang) = req.language {
        settings.language = lang;
    }
    if let Some(notif) = req.email_notifications {
        settings.email_notifications = notif;
    }
    if let Some(sync) = req.auto_sync {
        settings.auto_sync = sync;
    }

    state.store.update_settings(&settings).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;

    Ok(Json(settings))
}

// --- Browser sync handlers ---

async fn get_bookmarks(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<Bookmark>>, (StatusCode, Json<ApiError>)> {
    let bookmarks = state.store.get_user_bookmarks(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(bookmarks))
}

async fn add_bookmark(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<BookmarkRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let bookmark = Bookmark {
        id: Uuid::new_v4(),
        user_id: session.user_id,
        title: req.title,
        url: req.url,
        folder: req.folder,
        position: req.position.unwrap_or(0),
        created_at: Utc::now(),
        updated_at: Utc::now(),
    };
    state.store.create_bookmark(&bookmark).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(serde_json::json!({ "id": bookmark.id })))
}

async fn delete_bookmark(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Path(bookmark_id): Path<Uuid>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    state
        .store
        .delete_bookmark(session.user_id, bookmark_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;
    Ok(Json(serde_json::json!({ "status": "deleted" })))
}

async fn get_history(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<HistoryEntry>>, (StatusCode, Json<ApiError>)> {
    let history = state
        .store
        .get_user_history(session.user_id, 200)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;
    Ok(Json(history))
}

async fn add_history(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<HistoryRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let entry = HistoryEntry {
        id: Uuid::new_v4(),
        user_id: session.user_id,
        url: req.url,
        title: req.title,
        visit_count: 1,
        last_visited_at: Utc::now(),
        created_at: Utc::now(),
    };
    state.store.add_history_entry(&entry).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(serde_json::json!({ "id": entry.id })))
}

async fn get_passwords(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<SavedPassword>>, (StatusCode, Json<ApiError>)> {
    let passwords = state.store.get_user_passwords(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(passwords))
}

async fn save_password(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<SavePasswordRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let password = SavedPassword {
        id: Uuid::new_v4(),
        user_id: session.user_id,
        domain: req.domain,
        username: req.username,
        encrypted_password: req.encrypted_password,
        created_at: Utc::now(),
        updated_at: Utc::now(),
    };
    state.store.save_password(&password).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(serde_json::json!({ "id": password.id })))
}

async fn get_tabs(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<Vec<SyncTab>>, (StatusCode, Json<ApiError>)> {
    let tabs = state.store.get_user_tabs(session.user_id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(tabs))
}

async fn sync_tab(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<SyncTabRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    let tab = SyncTab {
        id: Uuid::new_v4(),
        user_id: session.user_id,
        device_id: req.device_id,
        title: req.title,
        url: req.url,
        active: req.active,
        updated_at: Utc::now(),
    };
    state.store.upsert_tab(&tab).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(serde_json::json!({ "id": tab.id })))
}

async fn get_browser_settings(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<BrowserSettings>, (StatusCode, Json<ApiError>)> {
    let settings = state
        .store
        .get_browser_settings(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;
    Ok(Json(settings))
}

async fn update_browser_settings(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
    Json(req): Json<UpdateBrowserSettingsRequest>,
) -> Result<Json<BrowserSettings>, (StatusCode, Json<ApiError>)> {
    let mut settings = state
        .store
        .get_browser_settings(session.user_id)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    if let Some(hp) = req.homepage {
        settings.homepage = Some(hp);
    }
    if let Some(se) = req.search_engine {
        settings.search_engine = se;
    }
    if let Some(pm) = req.privacy_mode {
        settings.privacy_mode = pm;
    }
    if let Some(sp) = req.sync_passwords {
        settings.sync_passwords = sp;
    }
    if let Some(sh) = req.sync_history {
        settings.sync_history = sh;
    }
    if let Some(sb) = req.sync_bookmarks {
        settings.sync_bookmarks = sb;
    }
    if let Some(st) = req.sync_tabs {
        settings.sync_tabs = st;
    }
    if let Some(ss) = req.sync_settings {
        settings.sync_settings = ss;
    }

    state
        .store
        .update_browser_settings(&settings)
        .map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: e.to_string(),
                }),
            )
        })?;

    Ok(Json(settings))
}

async fn logout(
    State(state): State<AppState>,
    Extension(session): Extension<Session>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ApiError>)> {
    state.auth.invalidate_session(session.id).map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ApiError {
                error: e.to_string(),
            }),
        )
    })?;
    Ok(Json(serde_json::json!({ "status": "logged_out" })))
}

// --- Dashboard handler ---

async fn dashboard() -> impl IntoResponse {
    axum::response::Html(include_str!("../frontend/dashboard.html"))
}

// --- Helpers ---

fn to_user_response(user: &User) -> UserResponse {
    UserResponse {
        id: user.id,
        username: user.username.clone(),
        display_name: user.display_name.clone(),
        email: user.email.clone(),
        profile_picture: user.profile_picture.clone(),
        has_passkeys: !user.passkey_credentials.is_empty(),
        has_totp: user.totp_secret.is_some(),
        recovery_codes_count: user.recovery_codes.len(),
        created_at: user.created_at.to_rfc3339(),
    }
}

// --- Main ---

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "ichin_account=trace,tower_http=debug".into()),
        )
        .init();

    let store = AccountStore::new("account_data")?;
    let auth = Arc::new(AuthManager::new(store.clone()));

    let state = AppState { store, auth };

    let public_routes = Router::new()
        .route("/api/auth/register", post(register))
        .route("/api/auth/login/passkey", post(login_passkey))
        .route("/api/auth/login/totp", post(login_totp))
        .route("/api/auth/login/recovery", post(login_recovery));

    let protected_routes = Router::new()
        .route("/api/auth/logout", post(logout))
        .route("/api/account/me", get(get_me))
        .route("/api/account/profile", put(update_profile))
        .route("/api/account/passkeys", post(register_passkey))
        .route("/api/account/totp/setup", get(setup_totp))
        .route("/api/account/totp/verify", post(verify_totp))
        .route("/api/account/sessions", get(get_sessions))
        .route("/api/account/sessions/{id}", delete(delete_session))
        .route("/api/account/devices", get(get_devices).post(create_device))
        .route("/api/account/devices/{id}", delete(delete_device))
        .route("/api/account/login-history", get(get_login_history))
        .route("/api/account/storage", get(get_storage_usage))
        .route("/api/account/settings", get(get_settings).put(update_settings))
        .route("/api/sync/bookmarks", get(get_bookmarks).post(add_bookmark))
        .route("/api/sync/bookmarks/{id}", delete(delete_bookmark))
        .route("/api/sync/history", get(get_history).post(add_history))
        .route("/api/sync/passwords", get(get_passwords).post(save_password))
        .route("/api/sync/tabs", get(get_tabs).post(sync_tab))
        .route("/api/sync/settings", get(get_browser_settings).put(update_browser_settings))
        .route_layer(middleware::from_fn_with_state(
            state.clone(),
            auth_middleware,
        ));

    let app = Router::new()
        .route("/dashboard", get(dashboard))
        .merge(public_routes)
        .merge(protected_routes)
        .layer(CorsLayer::permissive())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8081").await?;
    info!("Ichin Account server listening on http://127.0.0.1:8081");
    axum::serve(listener, app).await?;

    Ok(())
}
