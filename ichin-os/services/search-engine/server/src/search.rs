use std::collections::HashMap;

use crate::db::Database;
use crate::index::InvertedIndex;
use crate::models::{Page, SearchResult, Site};

pub struct SearchEngine {
    pub db: Database,
    pub index: InvertedIndex,
    sites: HashMap<i64, Site>,
    pages: HashMap<i64, Page>,
}

impl SearchEngine {
    pub fn new(db: Database) -> Self {
        Self {
            db,
            index: InvertedIndex::new(),
            sites: HashMap::new(),
            pages: HashMap::new(),
        }
    }

    pub fn load(&mut self) {
        let sites = self.db.get_sites().expect("Failed to load sites");
        let pages = self.db.get_pages().expect("Failed to load pages");

        for site in &sites {
            self.sites.insert(site.id, site.clone());
        }

        for page in &pages {
            self.pages.insert(page.id, page.clone());
            self.index.add_page(page);
        }

        self.index.persist(&self.db);
    }

    pub fn add_site(&mut self, site: Site) -> i64 {
        let id = self.db.add_site(&site).expect("Failed to add site");
        let mut site = site;
        site.id = id;
        self.sites.insert(id, site);
        id
    }

    pub fn add_page(&mut self, page: Page) -> i64 {
        let id = self.db.add_page(&page).expect("Failed to add page");
        let mut page = page;
        page.id = id;
        self.index.add_page(&page);
        self.pages.insert(id, page);
        id
    }

    pub fn persist_index(&self) {
        self.index.persist(&self.db);
    }

    pub fn search(&self, query: &str) -> Vec<SearchResult> {
        let query_lower = query.to_lowercase();
        let query_terms: Vec<String> = InvertedIndex::tokenize(query);

        // Collect candidate page IDs from inverted index
        let mut candidate_page_ids: Vec<i64> = Vec::new();
        for term in &query_terms {
            let ids = self.index.search_term(term);
            for id in ids {
                if !candidate_page_ids.contains(&id) {
                    candidate_page_ids.push(id);
                }
            }
        }

        // If no index matches, fall back to scanning all pages
        if candidate_page_ids.is_empty() {
            candidate_page_ids = self.pages.keys().copied().collect();
        }

        let mut results: Vec<SearchResult> = Vec::new();

        for &page_id in &candidate_page_ids {
            let page = match self.pages.get(&page_id) {
                Some(p) => p,
                None => continue,
            };
            let site = match self.sites.get(&page.site_id) {
                Some(s) => s,
                None => continue,
            };

            let mut score: i64 = 0;

            let title_lower = page.title.to_lowercase();
            let content_lower = page.content.to_lowercase();
            let site_name_lower = site.name.to_lowercase();
            let page_tags_lower: Vec<String> =
                page.tags.iter().map(|t| t.to_lowercase()).collect();
            let site_tags_lower: Vec<String> =
                site.tags.iter().map(|t| t.to_lowercase()).collect();

            // title match = +5
            if title_lower.contains(&query_lower)
                || query_terms.iter().any(|t| title_lower.contains(t))
            {
                score += 5;
            }

            // tag match = +4 (page tags + site tags)
            for t in &query_terms {
                if page_tags_lower.contains(t) || site_tags_lower.contains(t) {
                    score += 4;
                }
            }

            // site name match = +3
            if site_name_lower.contains(&query_lower)
                || query_terms.iter().any(|t| site_name_lower.contains(t))
            {
                score += 3;
            }

            // content match = +1
            if content_lower.contains(&query_lower)
                || query_terms.iter().any(|t| content_lower.contains(t))
            {
                score += 1;
            }

            // verified bonus = +3
            if site.verified {
                score += 3;
            }

            if score > 0 {
                let snippet = if page.content.len() > 150 {
                    format!("{}...", &page.content[..150])
                } else {
                    page.content.clone()
                };

                results.push(SearchResult {
                    site: site.domain.clone(),
                    title: page.title.clone(),
                    path: page.path.clone(),
                    snippet,
                    verified: site.verified,
                    score,
                });
            }
        }

        results.sort_by(|a, b| b.score.cmp(&a.score));
        results.truncate(20);

        results
    }
}
