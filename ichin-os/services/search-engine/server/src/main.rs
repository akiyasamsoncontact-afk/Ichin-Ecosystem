mod db;
mod index;
mod models;
mod search;

use std::sync::{Arc, Mutex};

use axum::{
    extract::Query,
    http::Method,
    routing::get,
    Json, Router,
};
use tower_http::cors::{Any, CorsLayer};
use tracing::info;

use models::{Page, SearchQuery, SearchResponse, Site};
use search::SearchEngine;

async fn handle_search(
    state: axum::extract::State<Arc<Mutex<SearchEngine>>>,
    Query(params): Query<SearchQuery>,
) -> Json<SearchResponse> {
    let engine = state.lock().unwrap();
    let results = engine.search(&params.q);

    Json(SearchResponse {
        query: params.q,
        results,
    })
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "search_engine=info".into()),
        )
        .init();

    let db = db::Database::new("search.db").expect("Failed to open database");

    let mut engine = SearchEngine::new(db);

    // Load any existing data from the database
    let _ = engine.load();

    // Seed data
    let docs_site_id = engine.add_site(Site {
        id: 0,
        domain: "docs.ichin".to_string(),
        name: "Ichin Documentation".to_string(),
        description: "Official documentation for the Ichin ecosystem".to_string(),
        verified: true,
        tags: vec!["docs".into(), "official".into(), "reference".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: docs_site_id,
        path: "/home".to_string(),
        title: "Welcome to Ichin".to_string(),
        content: "Ichin is a structured, permissioned ecosystem for registered websites. \
                   All sites are registered through GurtDNS and GurtCA. \
                   This is the central documentation hub.".to_string(),
        tags: vec!["welcome".into(), "introduction".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: docs_site_id,
        path: "/registry".to_string(),
        title: "Domain Registry Guide".to_string(),
        content: "Learn how to register your domain with GurtDNS and obtain certificates \
                   from GurtCA. Every site in Ichin must be registered before it can be accessed.".to_string(),
        tags: vec!["registry".into(), "dns".into(), "certificate".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: docs_site_id,
        path: "/search".to_string(),
        title: "Search Engine Overview".to_string(),
        content: "The Ichin search engine allows you to find registered sites and pages \
                   using keyword search. Results are ranked by title, tag, and content relevance.".to_string(),
        tags: vec!["search".into(), "ranking".into()],
    });

    let tools_site_id = engine.add_site(Site {
        id: 0,
        domain: "tools.ichin".to_string(),
        name: "Ichin Tools".to_string(),
        description: "Developer tools and utilities for the Ichin network".to_string(),
        verified: true,
        tags: vec!["tools".into(), "developer".into(), "utilities".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: tools_site_id,
        path: "/home".to_string(),
        title: "Developer Tools".to_string(),
        content: "A collection of tools for Ichin developers including API clients, \
                   testing utilities, and deployment helpers.".to_string(),
        tags: vec!["developer".into(), "tools".into(), "api".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: tools_site_id,
        path: "/dns-lookup".to_string(),
        title: "GurtDNS Lookup Tool".to_string(),
        content: "Look up any registered .ichin domain to see its DNS records, \
                   verification status, and associated metadata.".to_string(),
        tags: vec!["dns".into(), "lookup".into(), "network".into()],
    });

    let blog_site_id = engine.add_site(Site {
        id: 0,
        domain: "blog.ichin".to_string(),
        name: "Ichin Blog".to_string(),
        description: "Community blog about Ichin development and ecosystem updates".to_string(),
        verified: false,
        tags: vec!["blog".into(), "community".into(), "updates".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: blog_site_id,
        path: "/home".to_string(),
        title: "Welcome to the Ichin Blog".to_string(),
        content: "Stay up to date with the latest Ichin ecosystem news, \
                   developer stories, and platform announcements.".to_string(),
        tags: vec!["blog".into(), "news".into(), "updates".into()],
    });

    engine.add_page(Page {
        id: 0,
        site_id: blog_site_id,
        path: "/gurtca-update".to_string(),
        title: "GurtCA Certificate Changes".to_string(),
        content: "Important updates regarding GurtCA certificate issuance. \
                   All certificates now require domain ownership verification \
                   through GurtDNS before issuance.".to_string(),
        tags: vec!["gurtca".into(), "certificate".into(), "security".into()],
    });

    engine.persist_index();

    let search_engine = Arc::new(Mutex::new(engine));

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any);

    let app = Router::new()
        .route("/health", get(|| async { Json(serde_json::json!({"status": "ok"})) }))
        .route("/search", get(handle_search))
        .layer(cors)
        .with_state(search_engine);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001")
        .await
        .expect("Failed to bind to port 3001");

    info!("Search engine running on http://0.0.0.0:3001");
    axum::serve(listener, app).await.expect("Server error");
}
