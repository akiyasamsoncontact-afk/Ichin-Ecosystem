use std::collections::HashMap;

use crate::db::Database;
use crate::models::Page;

pub struct InvertedIndex {
    pub map: HashMap<String, Vec<i64>>,
}

impl InvertedIndex {
    pub fn new() -> Self {
        Self { map: HashMap::new() }
    }

    pub fn tokenize(text: &str) -> Vec<String> {
        text.to_lowercase()
            .split(|c: char| !c.is_alphanumeric())
            .filter(|s| !s.is_empty())
            .map(String::from)
            .collect()
    }

    pub fn add_page(&mut self, page: &Page) {
        let terms: Vec<String> = Self::tokenize(&page.title)
            .into_iter()
            .chain(Self::tokenize(&page.content))
            .chain(page.tags.iter().flat_map(|t| Self::tokenize(t)))
            .collect();

        for term in terms {
            self.map.entry(term).or_default().push(page.id);
        }
    }

    pub fn search_term(&self, term: &str) -> Vec<i64> {
        let term = term.to_lowercase();
        self.map.get(&term).cloned().unwrap_or_default()
    }

    pub fn persist(&self, db: &Database) {
        let _ = db.clear_index();
        for (term, page_ids) in &self.map {
            for &page_id in page_ids {
                let _ = db.insert_index_entry(term, page_id);
            }
        }
    }
}
