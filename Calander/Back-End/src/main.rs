mod db;
mod handlers;
mod models;

use std::net::SocketAddr;
use std::sync::Arc;

use axum::{
    http::Method,
    routing::{get, put},
    Router,
};
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing::info;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;

use db::Database;

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "calentask_backend=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let db = Arc::new(Database::new("calentask.db").expect("Failed to open database"));
    info!("CalenTask database initialized");

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
        .allow_headers(Any);

    let api_routes = Router::new()
        .route("/api/tasks", get(handlers::get_tasks).post(handlers::create_task))
        .route("/api/tasks/:id", put(handlers::update_task).delete(handlers::delete_task))
        .layer(cors.clone())
        .with_state(db);

    let health_routes = Router::new()
        .route("/health", get(|| async { axum::Json(serde_json::json!({"status": "ok"})) }));

    let app = Router::new()
        .merge(health_routes)
        .nest("", api_routes)
        .layer(TraceLayer::new_for_http());

    let addr = SocketAddr::from(([127, 0, 0, 1], 3002));
    info!("CalenTask backend listening on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
