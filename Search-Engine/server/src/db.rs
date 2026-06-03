use rusqlite::{Connection, Result, params};
use std::sync::Mutex;

use crate::models::{Page, Site};

pub struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        let db = Self { conn: Mutex::new(conn) };
        db.initialize()?;
        Ok(db)
    }

    fn initialize(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                verified INTEGER NOT NULL DEFAULT 0,
                tags TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                FOREIGN KEY (site_id) REFERENCES sites(id),
                UNIQUE(site_id, path)
            );
            CREATE TABLE IF NOT EXISTS index_terms (
                term TEXT NOT NULL,
                page_id INTEGER NOT NULL,
                PRIMARY KEY (term, page_id),
                FOREIGN KEY (page_id) REFERENCES pages(id)
            );"
        )?;
        Ok(())
    }

    pub fn get_sites(&self) -> Result<Vec<Site>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, domain, name, description, verified, tags FROM sites"
        )?;
        let sites = stmt.query_map([], |row| {
            let tags_str: String = row.get(5)?;
            let tags: Vec<String> = serde_json::from_str(&tags_str).unwrap_or_default();
            Ok(Site {
                id: row.get(0)?,
                domain: row.get(1)?,
                name: row.get(2)?,
                description: row.get(3)?,
                verified: row.get::<_, i32>(4)? != 0,
                tags,
            })
        })?.collect::<Result<Vec<_>>>()?;
        Ok(sites)
    }

    pub fn get_pages(&self) -> Result<Vec<Page>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, site_id, path, title, content, tags FROM pages"
        )?;
        let pages = stmt.query_map([], |row| {
            let tags_str: String = row.get(5)?;
            let tags: Vec<String> = serde_json::from_str(&tags_str).unwrap_or_default();
            Ok(Page {
                id: row.get(0)?,
                site_id: row.get(1)?,
                path: row.get(2)?,
                title: row.get(3)?,
                content: row.get(4)?,
                tags,
            })
        })?.collect::<Result<Vec<_>>>()?;
        Ok(pages)
    }

    pub fn add_site(&self, site: &Site) -> Result<i64> {
        let conn = self.conn.lock().unwrap();
        let result = conn.execute(
            "INSERT OR IGNORE INTO sites (domain, name, description, verified, tags) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![
                site.domain,
                site.name,
                site.description,
                site.verified as i32,
                serde_json::to_string(&site.tags).unwrap(),
            ],
        )?;
        if result > 0 {
            Ok(conn.last_insert_rowid())
        } else {
            let id: i64 = conn.query_row(
                "SELECT id FROM sites WHERE domain = ?1",
                params![site.domain],
                |row| row.get(0),
            )?;
            Ok(id)
        }
    }

    pub fn add_page(&self, page: &Page) -> Result<i64> {
        let conn = self.conn.lock().unwrap();
        let result = conn.execute(
            "INSERT OR IGNORE INTO pages (site_id, path, title, content, tags) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![
                page.site_id,
                page.path,
                page.title,
                page.content,
                serde_json::to_string(&page.tags).unwrap(),
            ],
        )?;
        if result > 0 {
            Ok(conn.last_insert_rowid())
        } else {
            let id: i64 = conn.query_row(
                "SELECT id FROM pages WHERE site_id = ?1 AND path = ?2",
                params![page.site_id, page.path],
                |row| row.get(0),
            )?;
            Ok(id)
        }
    }

    pub fn insert_index_entry(&self, term: &str, page_id: i64) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT OR IGNORE INTO index_terms (term, page_id) VALUES (?1, ?2)",
            params![term, page_id],
        )?;
        Ok(())
    }

    pub fn get_page_ids_for_term(&self, term: &str) -> Result<Vec<i64>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT page_id FROM index_terms WHERE term = ?1"
        )?;
        let ids = stmt.query_map(params![term], |row| {
            row.get(0)
        })?.collect::<Result<Vec<_>>>()?;
        Ok(ids)
    }

    pub fn get_page_by_id(&self, id: i64) -> Result<Option<Page>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, site_id, path, title, content, tags FROM pages WHERE id = ?1"
        )?;
        let mut rows = stmt.query(params![id])?;
        if let Some(row) = rows.next()? {
            let tags_str: String = row.get(5)?;
            let tags: Vec<String> = serde_json::from_str(&tags_str).unwrap_or_default();
            Ok(Some(Page {
                id: row.get(0)?,
                site_id: row.get(1)?,
                path: row.get(2)?,
                title: row.get(3)?,
                content: row.get(4)?,
                tags,
            }))
        } else {
            Ok(None)
        }
    }

    pub fn get_site_by_id(&self, id: i64) -> Result<Option<Site>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, domain, name, description, verified, tags FROM sites WHERE id = ?1"
        )?;
        let mut rows = stmt.query(params![id])?;
        if let Some(row) = rows.next()? {
            let tags_str: String = row.get(5)?;
            let tags: Vec<String> = serde_json::from_str(&tags_str).unwrap_or_default();
            Ok(Some(Site {
                id: row.get(0)?,
                domain: row.get(1)?,
                name: row.get(2)?,
                description: row.get(3)?,
                verified: row.get::<_, i32>(4)? != 0,
                tags,
            }))
        } else {
            Ok(None)
        }
    }

    pub fn clear_index(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM index_terms", [])?;
        Ok(())
    }
}
