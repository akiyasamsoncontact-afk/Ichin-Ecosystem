use axum::{
    extract::{Path, State},
    http::StatusCode,
    response::{IntoResponse, Json},
    routing::{get, post},
    Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;
use tower_http::cors::CorsLayer;
use tower_http::trace::TraceLayer;
use tracing::{error, info, warn};
use uuid::Uuid;

// ─── Data Models ─────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum AppType {
    Native,
    Web,
    External,
}

impl std::fmt::Display for AppType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AppType::Native => write!(f, "native"),
            AppType::Web => write!(f, "web"),
            AppType::External => write!(f, "external"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum PermissionType {
    AiAccess,
    MemoryRead,
    FileAccess,
    NetworkAccess,
    WorkspaceIntegration,
    CalendarAccess,
    NotificationsAccess,
}

impl std::fmt::Display for PermissionType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            PermissionType::AiAccess => write!(f, "ai_access"),
            PermissionType::MemoryRead => write!(f, "memory_read"),
            PermissionType::FileAccess => write!(f, "file_access"),
            PermissionType::NetworkAccess => write!(f, "network_access"),
            PermissionType::WorkspaceIntegration => write!(f, "workspace_integration"),
            PermissionType::CalendarAccess => write!(f, "calendar_access"),
            PermissionType::NotificationsAccess => write!(f, "notifications_access"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Permission {
    #[serde(rename = "type")]
    pub perm_type: PermissionType,
    pub granted: bool,
    pub user_approved: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppManifest {
    pub name: String,
    pub version: String,
    pub app_type: AppType,
    pub permissions: Vec<Permission>,
    pub ai_compatibility: String,
    pub workspace_integration: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum AppState {
    Installed,
    Running,
    Suspended,
    Terminated,
}

impl std::fmt::Display for AppState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AppState::Installed => write!(f, "installed"),
            AppState::Running => write!(f, "running"),
            AppState::Suspended => write!(f, "suspended"),
            AppState::Terminated => write!(f, "terminated"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceUsage {
    pub cpu_percent: f64,
    pub memory_mb: f64,
    pub uptime_seconds: u64,
}

impl Default for ResourceUsage {
    fn default() -> Self {
        Self {
            cpu_percent: 0.0,
            memory_mb: 0.0,
            uptime_seconds: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppInstance {
    pub id: String,
    pub manifest: AppManifest,
    pub state: AppState,
    pub sandbox_id: String,
    pub resource_usage: ResourceUsage,
    pub installed_at: DateTime<Utc>,
    pub last_state_change: DateTime<Utc>,
    pub user_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppStoreEntry {
    pub id: String,
    pub name: String,
    pub description: String,
    pub category: String,
    pub rating: f64,
    pub downloads: u64,
    pub ai_tested: bool,
    pub version: String,
    pub app_type: AppType,
    pub permissions: Vec<PermissionType>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiSimulationResult {
    pub simulation_id: String,
    pub app_name: String,
    pub behavior_score: f64,
    pub security_issues: Vec<String>,
    pub resource_profile: String,
    pub ai_compatibility_score: f64,
    pub recommended: bool,
}

// ─── Request / Response Types ─────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize)]
pub struct InstallRequest {
    pub manifest: AppManifest,
    pub user_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PermissionUpdateRequest {
    pub permissions: Vec<Permission>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PublishRequest {
    pub name: String,
    pub description: String,
    pub category: String,
    pub manifest: AppManifest,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimulateRequest {
    pub manifest: AppManifest,
    pub test_duration_seconds: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T: Serialize> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

impl<T: Serialize> ApiResponse<T> {
    pub fn ok(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    pub fn err(msg: impl Into<String>) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(msg.into()),
        }
    }
}

// ─── Application State ────────────────────────────────────────────────────────

#[derive(Debug)]
pub struct AppStateInner {
    pub apps: HashMap<String, AppInstance>,
    pub store: HashMap<String, AppStoreEntry>,
    pub simulations: Vec<AiSimulationResult>,
    pub docs_cache: String,
}

pub type SharedState = Arc<Mutex<AppStateInner>>;

fn new_state() -> SharedState {
    let mut store = HashMap::new();
    store.insert(
        "store-default-1".to_string(),
        AppStoreEntry {
            id: "store-default-1".to_string(),
            name: "ICHIN Assistant".to_string(),
            description: "AI-powered personal assistant with full Ichin OS integration".to_string(),
            category: "AI Agents".to_string(),
            rating: 4.8,
            downloads: 15420,
            ai_tested: true,
            version: "2.1.0".to_string(),
            app_type: AppType::Native,
            permissions: vec![
                PermissionType::AiAccess,
                PermissionType::MemoryRead,
                PermissionType::WorkspaceIntegration,
                PermissionType::NotificationsAccess,
            ],
        },
    );
    store.insert(
        "store-default-2".to_string(),
        AppStoreEntry {
            id: "store-default-2".to_string(),
            name: "CodeForge".to_string(),
            description: "Multi-language code editor with AI pair programming".to_string(),
            category: "Coding Tools".to_string(),
            rating: 4.6,
            downloads: 8930,
            ai_tested: true,
            version: "1.8.3".to_string(),
            app_type: AppType::Native,
            permissions: vec![
                PermissionType::FileAccess,
                PermissionType::AiAccess,
                PermissionType::WorkspaceIntegration,
            ],
        },
    );
    store.insert(
        "store-default-3".to_string(),
        AppStoreEntry {
            id: "store-default-3".to_string(),
            name: "StudyPal".to_string(),
            description: "AI study companion with flash cards and spaced repetition".to_string(),
            category: "Study Tools".to_string(),
            rating: 4.3,
            downloads: 12500,
            ai_tested: true,
            version: "3.0.1".to_string(),
            app_type: AppType::Web,
            permissions: vec![
                PermissionType::AiAccess,
                PermissionType::CalendarAccess,
                PermissionType::NotificationsAccess,
            ],
        },
    );
    store.insert(
        "store-default-4".to_string(),
        AppStoreEntry {
            id: "store-default-4".to_string(),
            name: "TerminalX".to_string(),
            description: "Advanced terminal emulator with Linux compatibility".to_string(),
            category: "System Extensions".to_string(),
            rating: 4.1,
            downloads: 6700,
            ai_tested: false,
            version: "0.9.5".to_string(),
            app_type: AppType::External,
            permissions: vec![PermissionType::FileAccess, PermissionType::NetworkAccess],
        },
    );

    let docs = r#"# ICHIN OS Developer Platform

## Overview
The ICHIN OS Developer Platform enables building, testing, and distributing applications for the Ichin ecosystem.

## SDKs
- **TypeScript SDK**: `npm install @ichin-os/sdk`
- **Python SDK**: `pip install ichin-os-sdk`
- **Rust SDK**: `cargo add ichin-os-sdk`

## App Types
1. **Native Ichin Apps** — Full AI/memory/workspace integration
2. **Web Apps (Wrapped)** — Sandbox container with limited system access
3. **External Apps** — Linux/Windows/Android via compatibility layers

## Permissions
| Permission | Description | Sensitive |
|---|---|---|
| AI_ACCESS | Use Ichin AI system | No |
| MEMORY_READ | Read user memory | Yes |
| FILE_ACCESS | File system access | Yes |
| NETWORK_ACCESS | Internet usage | No |
| WORKSPACE_INTEGRATION | UI embedding | No |
| CALENDAR_ACCESS | Calendar access | No |
| NOTIFICATIONS_ACCESS | Send notifications | No |

## App Lifecycle
Install → Initialize → Run → Suspend → Terminate

## AI Simulation
Use the `/developer/simulate` endpoint to test your app behavior inside a simulated OS environment before publishing.
"#
    .to_string();

    Arc::new(Mutex::new(AppStateInner {
        apps: HashMap::new(),
        store,
        simulations: Vec::new(),
        docs_cache: docs,
    }))
}

// ─── Handlers ─────────────────────────────────────────────────────────────────

async fn health() -> impl IntoResponse {
    Json(serde_json::json!({
        "service": "ichin-os-app-runtime",
        "version": "0.1.0",
        "status": "healthy",
        "layers": [
            "App Runtime Layer",
            "Permission & Sandbox Layer",
            "API Gateway Layer",
            "App Store & Distribution Layer",
            "Developer Platform Layer"
        ],
        "timestamp": Utc::now().to_rfc3339()
    }))
}

async fn install_app(
    State(state): State<SharedState>,
    Json(req): Json<InstallRequest>,
) -> impl IntoResponse {
    let manifest = req.manifest;
    let user_id = req.user_id.unwrap_or_else(|| "default-user".to_string());

    let app_id = Uuid::new_v4().to_string();
    let sandbox_id = format!("sandbox-{}", &app_id[..8]);

    let sensitive: std::collections::HashSet<PermissionType> = [
        PermissionType::MemoryRead,
        PermissionType::FileAccess,
    ]
    .into();

    let mut processed_permissions = Vec::new();
    for perm in &manifest.permissions {
        let is_sensitive = sensitive.contains(&perm.perm_type);
        processed_permissions.push(Permission {
            perm_type: perm.perm_type.clone(),
            granted: true,
            user_approved: if is_sensitive { false } else { true },
        });
    }

    let app_instance = AppInstance {
        id: app_id.clone(),
        manifest: AppManifest {
            name: manifest.name.clone(),
            version: manifest.version.clone(),
            app_type: manifest.app_type.clone(),
            permissions: processed_permissions,
            ai_compatibility: manifest.ai_compatibility.clone(),
            workspace_integration: manifest.workspace_integration.clone(),
            description: manifest.description.clone(),
        },
        state: AppState::Installed,
        sandbox_id,
        resource_usage: ResourceUsage::default(),
        installed_at: Utc::now(),
        last_state_change: Utc::now(),
        user_id,
    };

    let mut guard = state.lock().await;
    guard.apps.insert(app_id.clone(), app_instance.clone());

    info!(app_id = %app_id, name = %app_instance.manifest.name, "App installed");

    Json(ApiResponse::ok(app_instance))
}

async fn run_app(
    State(state): State<SharedState>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    let mut guard = state.lock().await;

    match guard.apps.get_mut(&id) {
        Some(app) => {
            if app.state == AppState::Running {
                return (
                    StatusCode::CONFLICT,
                    Json(ApiResponse::<()>::err("App is already running")),
                );
            }

            let pending_sensitive = app
                .manifest
                .permissions
                .iter()
                .any(|p| !p.user_approved);

            if pending_sensitive {
                return (
                    StatusCode::FORBIDDEN,
                    Json(ApiResponse::<()>::err(
                        "Sensitive permissions not yet approved by user",
                    )),
                );
            }

            app.state = AppState::Running;
            app.last_state_change = Utc::now();
            app.resource_usage = ResourceUsage {
                cpu_percent: rand::random::<f64>() * 30.0 + 5.0,
                memory_mb: rand::random::<f64>() * 200.0 + 50.0,
                uptime_seconds: 0,
            };

            info!(app_id = %id, name = %app.manifest.name, "App started");

            (
                StatusCode::OK,
                Json(ApiResponse::ok(app.clone())),
            )
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ApiResponse::<()>::err(format!("App {} not found", id))),
        ),
    }
}

async fn suspend_app(
    State(state): State<SharedState>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    let mut guard = state.lock().await;

    match guard.apps.get_mut(&id) {
        Some(app) => {
            if app.state != AppState::Running {
                return (
                    StatusCode::CONFLICT,
                    Json(ApiResponse::<()>::err("App is not currently running")),
                );
            }

            app.state = AppState::Suspended;
            app.last_state_change = Utc::now();
            app.resource_usage.cpu_percent = 0.5;
            app.resource_usage.memory_mb = 10.0;

            info!(app_id = %id, name = %app.manifest.name, "App suspended");

            (
                StatusCode::OK,
                Json(ApiResponse::ok(app.clone())),
            )
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ApiResponse::<()>::err(format!("App {} not found", id))),
        ),
    }
}

async fn terminate_app(
    State(state): State<SharedState>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    let mut guard = state.lock().await;

    match guard.apps.get_mut(&id) {
        Some(app) => {
            app.state = AppState::Terminated;
            app.last_state_change = Utc::now();
            app.resource_usage = ResourceUsage::default();

            info!(app_id = %id, name = %app.manifest.name, "App terminated");

            (
                StatusCode::OK,
                Json(ApiResponse::ok(app.clone())),
            )
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ApiResponse::<()>::err(format!("App {} not found", id))),
        ),
    }
}

async fn list_apps(State(state): State<SharedState>) -> impl IntoResponse {
    let guard = state.lock().await;
    let apps: Vec<&AppInstance> = guard.apps.values().collect();
    Json(ApiResponse::ok(apps))
}

async fn get_app(
    State(state): State<SharedState>,
    Path(id): Path<String>,
) -> impl IntoResponse {
    let guard = state.lock().await;

    match guard.apps.get(&id) {
        Some(app) => (
            StatusCode::OK,
            Json(ApiResponse::ok(app.clone())),
        ),
        None => (
            StatusCode::NOT_FOUND,
            Json(ApiResponse::<()>::err(format!("App {} not found", id))),
        ),
    }
}

async fn update_permissions(
    State(state): State<SharedState>,
    Path(id): Path<String>,
    Json(req): Json<PermissionUpdateRequest>,
) -> impl IntoResponse {
    let mut guard = state.lock().await;

    match guard.apps.get_mut(&id) {
        Some(app) => {
            let sensitive: std::collections::HashSet<PermissionType> = [
                PermissionType::MemoryRead,
                PermissionType::FileAccess,
            ]
            .into();

            for update_perm in &req.permissions {
                if let Some(existing) = app
                    .manifest
                    .permissions
                    .iter_mut()
                    .find(|p| p.perm_type == update_perm.perm_type)
                {
                    let is_sensitive = sensitive.contains(&update_perm.perm_type);
                    existing.granted = update_perm.granted;
                    if update_perm.user_approved && is_sensitive {
                        existing.user_approved = true;
                    } else if !is_sensitive {
                        existing.user_approved = update_perm.user_approved || update_perm.granted;
                    }
                }
            }

            info!(app_id = %id, "Permissions updated");

            (
                StatusCode::OK,
                Json(ApiResponse::ok(app.manifest.permissions.clone())),
            )
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ApiResponse::<()>::err(format!("App {} not found", id))),
        ),
    }
}

async fn list_store(State(state): State<SharedState>) -> impl IntoResponse {
    let guard = state.lock().await;
    let entries: Vec<&AppStoreEntry> = guard.store.values().collect();
    Json(ApiResponse::ok(entries))
}

async fn publish_app(
    State(state): State<SharedState>,
    Json(req): Json<PublishRequest>,
) -> impl IntoResponse {
    let entry_id = Uuid::new_v4().to_string();

    let permissions: Vec<PermissionType> = req
        .manifest
        .permissions
        .iter()
        .map(|p| p.perm_type.clone())
        .collect();

    let ai_tested = rand::random::<f64>() > 0.3;

    let entry = AppStoreEntry {
        id: entry_id.clone(),
        name: req.name,
        description: req.description,
        category: req.category,
        rating: 0.0,
        downloads: 0,
        ai_tested,
        version: req.manifest.version.clone(),
        app_type: req.manifest.app_type,
        permissions,
    };

    let mut guard = state.lock().await;
    guard.store.insert(entry_id.clone(), entry.clone());

    info!(store_id = %entry_id, name = %entry.name, "App published to store");

    Json(ApiResponse::ok(entry))
}

async fn api_gateway_ai() -> impl IntoResponse {
    Json(serde_json::json!({
        "service": "AI API Gateway",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api-gateway/ai/query", "method": "POST", "description": "Query the AI system"},
            {"path": "/api-gateway/ai/agent", "method": "POST", "description": "Request agent assistance"},
            {"path": "/api-gateway/ai/summarize", "method": "POST", "description": "Generate summaries"},
            {"path": "/api-gateway/ai/reason", "method": "POST", "description": "Run reasoning"}
        ],
        "note": "All API calls pass through Orchestrator Service — no direct system bypass allowed.",
        "status": "operational"
    }))
}

async fn api_gateway_memory() -> impl IntoResponse {
    Json(serde_json::json!({
        "service": "Memory API Gateway",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api-gateway/memory/read", "method": "POST", "description": "Read allowed memory slices"},
            {"path": "/api-gateway/memory/store", "method": "POST", "description": "Store structured data"},
            {"path": "/api-gateway/memory/search", "method": "POST", "description": "Retrieve semantic context"}
        ],
        "note": "Restricted — only memory slices the app has permission to access are returned.",
        "status": "operational"
    }))
}

async fn api_gateway_calendar() -> impl IntoResponse {
    Json(serde_json::json!({
        "service": "Calendar API Gateway",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api-gateway/calendar/create", "method": "POST", "description": "Create calendar event"},
            {"path": "/api-gateway/calendar/modify", "method": "PUT", "description": "Modify existing event"},
            {"path": "/api-gateway/calendar/conflicts", "method": "POST", "description": "Detect scheduling conflicts"}
        ],
        "status": "operational"
    }))
}

async fn api_gateway_files() -> impl IntoResponse {
    Json(serde_json::json!({
        "service": "File API Gateway",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api-gateway/files/read", "method": "POST", "description": "Read files inside sandbox"},
            {"path": "/api-gateway/files/write", "method": "POST", "description": "Write files inside sandbox"},
            {"path": "/api-gateway/files/tag", "method": "POST", "description": "Metadata tagging"},
            {"path": "/api-gateway/files/index", "method": "POST", "description": "AI file indexing"}
        ],
        "note": "File operations restricted to sandbox directory.",
        "status": "operational"
    }))
}

async fn api_gateway_notifications() -> impl IntoResponse {
    Json(serde_json::json!({
        "service": "Notification API Gateway (Orb)",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api-gateway/notifications/trigger", "method": "POST", "description": "Trigger AI orb event"},
            {"path": "/api-gateway/notifications/attention", "method": "POST", "description": "Request attention window"}
        ],
        "status": "operational"
    }))
}

async fn developer_docs(State(state): State<SharedState>) -> impl IntoResponse {
    let guard = state.lock().await;
    Json(serde_json::json!({
        "documentation": guard.docs_cache,
        "sdk_quickstart": {
            "typescript": "npm install @ichin-os/sdk",
            "python": "pip install ichin-os-sdk",
            "rust": "cargo add ichin-os-sdk"
        },
        "app_categories": [
            "Productivity",
            "Study Tools",
            "Coding Tools",
            "AI Agents",
            "Learning Modules",
            "System Extensions"
        ],
        "app_types": ["native", "web", "external"],
        "lifecycle": ["install", "initialize", "run", "suspend", "terminate"]
    }))
}

async fn developer_simulate(
    State(state): State<SharedState>,
    Json(req): Json<SimulateRequest>,
) -> impl IntoResponse {
    let sim_id = Uuid::new_v4().to_string();
    let app_name = req.manifest.name.clone();
    let test_duration = req.test_duration_seconds.unwrap_or(30);

    let behavior_score = rand::random::<f64>() * 0.4 + 0.6;
    let security_issues: Vec<String> = if behavior_score < 0.7 {
        vec!["Excessive memory access patterns detected".to_string()]
    } else {
        vec![]
    };
    let ai_compatibility_score = match req.manifest.app_type {
        AppType::Native => rand::random::<f64>() * 0.2 + 0.8,
        AppType::Web => rand::random::<f64>() * 0.3 + 0.6,
        AppType::External => rand::random::<f64>() * 0.4 + 0.3,
    };
    let resource_profile = if behavior_score > 0.8 {
        "low"
    } else {
        "moderate"
    }
    .to_string();

    let result = AiSimulationResult {
        simulation_id: sim_id.clone(),
        app_name: app_name.clone(),
        behavior_score,
        security_issues,
        resource_profile,
        ai_compatibility_score,
        recommended: behavior_score > 0.7 && ai_compatibility_score > 0.6,
    };

    {
        let mut guard = state.lock().await;
        guard.simulations.push(result.clone());
    }

    info!(
        sim_id = %sim_id,
        app_name = %app_name,
        duration_secs = %test_duration,
        recommended = %result.recommended,
        "AI simulation completed"
    );

    Json(ApiResponse::ok(result))
}

// ─── Server Setup ─────────────────────────────────────────────────────────────

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "ichin_os_app_runtime=info,tower_http=info".into()),
        )
        .init();

    let state = new_state();

    let app = Router::new()
        .route("/health", get(health))
        .route("/apps/install", post(install_app))
        .route("/apps/{id}/run", post(run_app))
        .route("/apps/{id}/suspend", post(suspend_app))
        .route("/apps/{id}/terminate", post(terminate_app))
        .route("/apps", get(list_apps))
        .route("/apps/{id}", get(get_app))
        .route("/apps/{id}/permissions", post(update_permissions))
        .route("/store", get(list_store))
        .route("/store/publish", post(publish_app))
        .route("/api-gateway/ai", get(api_gateway_ai))
        .route("/api-gateway/memory", get(api_gateway_memory))
        .route("/api-gateway/calendar", get(api_gateway_calendar))
        .route("/api-gateway/files", get(api_gateway_files))
        .route("/api-gateway/notifications", get(api_gateway_notifications))
        .route("/developer/docs", get(developer_docs))
        .route("/developer/simulate", post(developer_simulate))
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(state);

    let addr = "0.0.0.0:8015";
    info!("ICHIN OS App Runtime starting on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr)
        .await
        .expect("Failed to bind to address");

    axum::serve(listener, app)
        .await
        .expect("Server failed");
}
