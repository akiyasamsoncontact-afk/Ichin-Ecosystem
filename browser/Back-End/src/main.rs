use axum::{
    response::{Html, IntoResponse},
    routing::get,
    Router,
};
use std::net::SocketAddr;
use tracing::{info, Level};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| "ichin_backend=debug".into()))
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Build routes
    let app = Router::new()
        // Health check endpoint
        .route("/health", get(|| async { Html("<h1>Ichin Backend is healthy!</h1>") }))
        // Serve frontend
        .fallback(|| async { Html(include_str!("../../Front-End/index.html").to_string()) });

    // Run server
    let addr = SocketAddr::from(([127, 0, 0, 1], 3001));
    info!("Ichin Backend listening on http://{}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}