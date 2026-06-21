use axum::{
    extract::State,
    http::header,
    response::{Html, IntoResponse, Response},
    routing::get,
    Router,
};
use std::net::SocketAddr;
use std::sync::Arc;
use tower::ServiceBuilder;
use tower_http::set_header::SetResponseHeaderLayer;
use tower_http::trace::TraceLayer;
use tracing::{info, Level};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use crate::backup_system::BackupSystem;
use crate::db::Database;
use crate::routes::{favorites, history, tabs, user, workspaces};

mod backup_system;
mod db;
mod routes;

#[derive(Clone)]
struct AppState {
    db: Database,
    backup_system: BackupSystem,
}

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| "ichin_backend=debug,tower_http=debug".into()))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Initialize database
    let db_path = "./ichin.db";
    let db = Database::new(db_path).expect("Failed to initialize database");

    // Initialize backup system
    let backup_dir = "./backups";
    let backup_system = BackupSystem::new(
        db_path.to_string(),
        backup_dir.to_string(),
        24, // Backup every 24 hours
        7,  // Keep 7 backups
    );

    // Start backup system in background
    let backup_system_clone = backup_system.clone();
    tokio::spawn(async move {
        backup_system_clone.start().await;
    });

    // Shared state
    let state = Arc::new(AppState { db, backup_system });

    // Build routes
    let app = Router::new()
        // Health check endpoint
        .route("/health", get(health_check))
        // API routes
        .route("/api/workspaces", get(workspaces::list_workspaces).post(workspaces::create_workspace))
        .route("/api/workspaces/:id", get(workspaces::get_workspace).put(workspaces::update_workspace).delete(workspaces::delete_workspace))
        .route("/api/tabs", get(tabs::list_tabs).post(tabs::create_tab))
        .route("/api/tabs/:id", get(tabs::get_tab).put(tabs::update_tab).delete(tabs::delete_tab))
        .route("/api/favorites", get(favorites::list_favorites).post(favorites::create_favorite))
        .route("/api/favorites/:id", get(favorites::get_favorite).delete(favorites::delete_favorite))
        .route("/api/history", get(history::list_history).post(history::add_history))
        .route("/api/user", get(user::get_profile).put(user::update_profile))
        // Serve frontend
        .fallback(frontend_handler)
        // Apply middleware
        .layer(
            ServiceBuilder::new()
                .layer(SetResponseHeaderLayer::if_not_present(
                    header::CONTENT_SECURITY_POLICY,
                    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'",
                ))
                .layer(SetResponseHeaderLayer::if_not_present(
                    header::X_FRAME_OPTIONS,
                    "DENY",
                ))
                .layer(SetResponseHeaderLayer::if_not_present(
                    header::X_CONTENT_TYPE_OPTIONS,
                    "nosniff",
                ))
                .layer(SetResponseHeaderLayer::if_not_present(
                    header::REFERRER_POLICY,
                    "strict-origin-when-cross-origin",
                ))
                .layer(TraceLayer::new_for_http())
                .layer(axum::middleware::from_fn_with_state(
                    state.clone(),
                    crate::routes::csrf_protection,
                ))
        )
        .with_state(state);

    // Run server
    let addr = SocketAddr::from(([127, 0, 0, 1], 3001));
    info!("Ichin Backend listening on http://{}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn health_check() -> impl IntoResponse {
    Html("<h1>Ichin Backend is healthy!</h1>")
}

async fn frontend_handler() -> impl IntoResponse {
    // Serve the frontend index.html
    Html(include_str!("../../Front-End/index.html").to_string())
}