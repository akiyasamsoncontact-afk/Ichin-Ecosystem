use axum::{
    response::Html,
    routing::get,
    Router,
};
use std::net::SocketAddr;
use tracing::info;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "ichin_backend=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    let app = Router::new()
        .route("/health", get(|| async { Html("<h1>Ichin Backend is healthy!</h1>") }))
        .fallback(|| async { Html(include_str!("../../Front-End/index.html").to_string()) });

    let addr = SocketAddr::from(([127, 0, 0, 1], 3003));
    info!("Ichin Backend listening on http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
