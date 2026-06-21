use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Site {
    pub id: i64,
    pub domain: String,
    pub name: String,
    pub description: String,
    pub verified: bool,
    pub tags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Page {
    pub id: i64,
    pub site_id: i64,
    pub path: String,
    pub title: String,
    pub content: String,
    pub tags: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct SearchResult {
    pub site: String,
    pub title: String,
    pub path: String,
    pub snippet: String,
    pub verified: bool,
    pub score: i64,
}

#[derive(Debug, Deserialize)]
pub struct SearchQuery {
    pub q: String,
}

#[derive(Debug, Serialize)]
pub struct SearchResponse {
    pub query: String,
    pub results: Vec<SearchResult>,
}
