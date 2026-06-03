use rusqlite::{params, Connection, Result};
use std::sync::{Arc, Mutex};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Workspace {
    pub id: String,
    pub name: String,
    pub color: String,
    pub icon: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tab {
    pub id: String,
    pub title: String,
    pub url: String,
    pub favicon: Option<String>,
    pub pinned: bool,
    pub workspace_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Favorite {
    pub id: String,
    pub title: String,
    pub url: String,
    pub icon: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub workspaces: Vec<Workspace>,
    pub tabs: Vec<Tab>,
    pub active_workspace: Option<String>,
    pub active_tab: Option<String>,
}

pub struct Database {
    connection: Mutex<Connection>,
}

impl Database {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        let db = Database {
            connection: Mutex::new(conn),
        };
        db.init()?;
        Ok(db)
    }

    fn init(&self) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                color TEXT NOT NULL,
                icon TEXT NOT NULL
            )",
            [],
        )?;
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tabs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                favicon TEXT,
                pinned BOOLEAN NOT NULL DEFAULT 0,
                workspace_id TEXT NOT NULL,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )",
            [],
        )?;
        conn.execute(
            "CREATE TABLE IF NOT EXISTS favorites (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                icon TEXT NOT NULL
            )",
            [],
        )?;
        conn.execute(
            "CREATE TABLE IF NOT EXISTS session (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                active_workspace_id TEXT,
                active_tab_id TEXT
            )",
            [],
        )?;

        // Initialize default data if empty
        let workspace_count: i64 = conn.query_row("SELECT COUNT(*) FROM workspaces", [], |row| row.get(0))?;
        if workspace_count == 0 {
            Self::initialize_defaults(&conn)?;
        }

        Ok(())
    }

    fn initialize_defaults(conn: &Connection) -> Result<()> {
        let workspaces = vec![
            Workspace {
                id: "work".to_string(),
                name: "Work".to_string(),
                color: "#3b82f6".to_string(),
                icon: "briefcase".to_string(),
            },
            Workspace {
                id: "personal".to_string(),
                name: "Personal".to_string(),
                color: "#22c55e".to_string(),
                icon: "home".to_string(),
            },
            Workspace {
                id: "research".to_string(),
                name: "Research".to_string(),
                color: "#8b5cf6".to_string(),
                icon: "book-open".to_string(),
            },
            Workspace {
                id: "social".to_string(),
                name: "Social".to_string(),
                color: "#ec4899".to_string(),
                icon: "users".to_string(),
            },
        ];

        for ws in &workspaces {
            conn.execute(
                "INSERT INTO workspaces (id, name, color, icon) VALUES (?1, ?2, ?3, ?4)",
                params![ws.id, ws.name, ws.color, ws.icon],
            )?;
        }

        let tabs = vec![
            Tab {
                id: "1".to_string(),
                title: "GitHub".to_string(),
                url: "https://github.com".to_string(),
                favicon: Some("icon-github".to_string()),
                pinned: true,
                workspace_id: "work".to_string(),
            },
            Tab {
                id: "2".to_string(),
                title: "Notion".to_string(),
                url: "https://notion.so".to_string(),
                favicon: Some("icon-file-text".to_string()),
                pinned: true,
                workspace_id: "work".to_string(),
            },
            Tab {
                id: "3".to_string(),
                title: "Linear".to_string(),
                url: "https://linear.app".to_string(),
                favicon: Some("icon-layers".to_string()),
                pinned: false,
                workspace_id: "work".to_string(),
            },
            Tab {
                id: "4".to_string(),
                title: "Figma".to_string(),
                url: "https://figma.com".to_string(),
                favicon: Some("icon-pen-tool".to_string()),
                pinned: false,
                workspace_id: "personal".to_string(),
            },
            Tab {
                id: "5".to_string(),
                title: "Vercel".to_string(),
                url: "https://vercel.com".to_string(),
                favicon: Some("icon-triangle".to_string()),
                pinned: false,
                workspace_id: "work".to_string(),
            },
        ];

        for tab in &tabs {
            conn.execute(
                "INSERT INTO tabs (id, title, url, favicon, pinned, workspace_id) VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
                params![tab.id, tab.title, tab.url, tab.favicon, tab.pinned as i32, tab.workspace_id],
            )?;
        }

        let favorites = vec![
            Favorite {
                id: "f1".to_string(),
                title: "Stack Overflow".to_string(),
                url: "https://stackoverflow.com".to_string(),
                icon: "icon-code".to_string(),
            },
            Favorite {
                id: "f2".to_string(),
                title: "MDN Web Docs".to_string(),
                url: "https://developer.mozilla.org".to_string(),
                icon: "icon-book".to_string(),
            },
            Favorite {
                id: "f3".to_string(),
                title: "Twitter".to_string(),
                url: "https://twitter.com".to_string(),
                icon: "icon-at-sign".to_string(),
            },
        ];

        for fav in &favorites {
            conn.execute(
                "INSERT INTO favorites (id, title, url, icon) VALUES (?1, ?2, ?3, ?4)",
                params![fav.id, fav.title, fav.url, fav.icon],
            )?;
        }

        // Initialize session
        conn.execute(
            "INSERT OR IGNORE INTO session (id) VALUES (1)",
            [],
        )?;

        Ok(())
    }

    pub fn get_session(&self) -> Result<Session> {
        let conn = self.connection.lock().unwrap();
        let workspaces = Self::get_workspaces(&conn)?;
        let tabs = Self::get_tabs(&conn)?;
        let (active_workspace_id, active_tab_id) = Self::get_active_ids(&conn)?;

        Ok(Session {
            workspaces,
            tabs,
            active_workspace: active_workspace_id,
            active_tab: active_tab_id,
        })
    }

    fn get_workspaces(conn: &Connection) -> Result<Vec<Workspace>> {
        let mut stmt = conn.prepare("SELECT id, name, color, icon FROM workspaces")?;
        let workspace_iter = stmt.query_map([], |row| {
            Ok(Workspace {
                id: row.get(0)?,
                name: row.get(1)?,
                color: row.get(2)?,
                icon: row.get(3)?,
            })
        })?;
        let mut workspaces = Vec::new();
        for workspace in workspace_iter {
            workspaces.push(workspace?);
        }
        Ok(workspaces)
    }

    fn get_tabs(conn: &Connection) -> Result<Vec<Tab>> {
        let mut stmt = conn.prepare("SELECT id, title, url, favicon, pinned, workspace_id FROM tabs")?;
        let tab_iter = stmt.query_map([], |row| {
            Ok(Tab {
                id: row.get(0)?,
                title: row.get(1)?,
                url: row.get(2)?,
                favicon: row.get(3)?,
                pinned: row.get(4)? != 0,
                workspace_id: row.get(5)?,
            })
        })?;
        let mut tabs = Vec::new();
        for tab in tab_iter {
            tabs.push(tab?);
        }
        Ok(tabs)
    }

    fn get_active_ids(conn: &Connection) -> Result<(Option<String>, Option<String>)> {
        let mut stmt = conn.prepare("SELECT active_workspace_id, active_tab_id FROM session WHERE id = 1")?;
        let mut rows = stmt.query([])?;
        if let Some(row) = rows.next()? {
            let active_workspace_id: Option<String> = row.get(0)?;
            let active_tab_id: Option<String> = row.get(1)?;
            Ok((active_workspace_id, active_tab_id))
        } else {
            Ok((None, None))
        }
    }

    pub fn save_session_state(&self, active_workspace_id: Option<&str>, active_tab_id: Option<&str>) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "UPDATE session SET active_workspace_id = ?1, active_tab_id = ?2 WHERE id = 1",
            params![active_workspace_id, active_tab_id],
        )?;
        Ok(())
    }

    pub fn get_workspaces(&self) -> Result<Vec<Workspace>> {
        let conn = self.connection.lock().unwrap();
        Self::get_workspaces(&conn)
    }

    pub fn create_workspace(&self, workspace: Workspace) -> Result<Workspace> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "INSERT INTO workspaces (id, name, color, icon) VALUES (?1, ?2, ?3, ?4)",
            params![workspace.id, workspace.name, workspace.color, workspace.icon],
        )?;
        Ok(workspace)
    }

    pub fn update_workspace(&self, id: &str, workspace: Workspace) -> Result<Workspace> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "UPDATE workspaces SET name = ?1, color = ?2, icon = ?3 WHERE id = ?4",
            params![workspace.name, workspace.color, workspace.icon, id],
        )?;
        Ok(workspace)
    }

    pub fn delete_workspace(&self, id: &str) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        conn.execute("DELETE FROM workspaces WHERE id = ?1", params![id])?;
        conn.execute("DELETE FROM tabs WHERE workspace_id = ?1", params![id])?;
        Ok(())
    }

    pub fn get_tabs_by_workspace(&self, workspace_id: &str) -> Result<Vec<Tab>> {
        let conn = self.connection.lock().unwrap();
        let mut stmt = conn.prepare("SELECT id, title, url, favicon, pinned, workspace_id FROM tabs WHERE workspace_id = ?1")?;
        let tab_iter = stmt.query_map([workspace_id], |row| {
            Ok(Tab {
                id: row.get(0)?,
                title: row.get(1)?,
                url: row.get(2)?,
                favicon: row.get(3)?,
                pinned: row.get(4)? != 0,
                workspace_id: row.get(5)?,
            })
        })?;
        let mut tabs = Vec::new();
        for tab in tab_iter {
            tabs.push(tab?);
        }
        Ok(tabs)
    }

    pub fn get_tabs(&self) -> Result<Vec<Tab>> {
        let conn = self.connection.lock().unwrap();
        Self::get_tabs(&conn)
    }

    pub fn create_tab(&self, tab: Tab) -> Result<Tab> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "INSERT INTO tabs (id, title, url, favicon, pinned, workspace_id) VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
            params![tab.id, tab.title, tab.url, tab.favicon, tab.pinned as i32, tab.workspace_id],
        )?;
        Ok(tab)
    }

    pub fn update_tab(&self, id: &str, tab: Tab) -> Result<Tab> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "UPDATE tabs SET title = ?1, url = ?2, favicon = ?3, pinned = ?4, workspace_id = ?5 WHERE id = ?6",
            params![tab.title, tab.url, tab.favicon, tab.pinned as i32, tab.workspace_id, id],
        )?;
        Ok(tab)
    }

    pub fn delete_tab(&self, id: &str) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        conn.execute("DELETE FROM tabs WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn reorder_tabs(&self, tab_ids: Vec<String>) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        let tx = conn.transaction()?;
        for (position, tab_id) in tab_ids.iter().enumerate() {
            tx.execute(
                "UPDATE tabs SET pinned = CASE WHEN ?1 < 2 THEN 1 ELSE 0 END WHERE id = ?2",
                params![position as i32, tab_id],
            )?;
        }
        tx.commit()?;
        Ok(())
    }

    pub fn get_favorites(&self) -> Result<Vec<Favorite>> {
        let conn = self.connection.lock().unwrap();
        let mut stmt = conn.prepare("SELECT id, title, url, icon FROM favorites")?;
        let favorite_iter = stmt.query_map([], |row| {
            Ok(Favorite {
                id: row.get(0)?,
                title: row.get(1)?,
                url: row.get(2)?,
                icon: row.get(3)?,
            })
        })?;
        let mut favorites = Vec::new();
        for favorite in favorite_iter {
            favorites.push(favorite?);
        }
        Ok(favorites)
    }

    pub fn create_favorite(&self, favorite: Favorite) -> Result<Favorite> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "INSERT INTO favorites (id, title, url, icon) VALUES (?1, ?2, ?3, ?4)",
            params![favorite.id, favorite.title, favorite.url, favorite.icon],
        )?;
        Ok(favorite)
    }

    pub fn delete_favorite(&self, id: &str) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        conn.execute("DELETE FROM favorites WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn get_history(&self, limit: u32) -> Result<Vec<HistoryItem>> {
        let conn = self.connection.lock().unwrap();
        let mut stmt = conn.prepare("SELECT id, title, url, timestamp FROM history ORDER BY timestamp DESC LIMIT ?1")?;
        let history_iter = stmt.query_map([limit], |row| {
            Ok(HistoryItem {
                id: row.get(0)?,
                title: row.get(1)?,
                url: row.get(2)?,
                timestamp: row.get(3)?,
            })
        })?;
        let mut history = Vec::new();
        for item in history_iter {
            history.push(item?);
        }
        Ok(history)
    }

    pub fn add_history(&self, history: HistoryItem) -> Result<HistoryItem> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "INSERT INTO history (id, title, url, timestamp) VALUES (?1, ?2, ?3, ?4)",
            params![history.id, history.title, history.url, history.timestamp],
        )?;
        Ok(history)
    }

    pub fn delete_history(&self, id: &str) -> Result<()> {
        let conn = self.connection.lock().unwrap();
        conn.execute("DELETE FROM history WHERE id = ?1", params![id])?;
        Ok(())
    }

    pub fn get_user_profile(&self) -> Result<UserProfile> {
        let conn = self.connection.lock().unwrap();
        let mut stmt = conn.prepare("SELECT id, name, email, avatar FROM user_profile WHERE id = 1")?;
        let mut rows = stmt.query([])?;
        if let Some(row) = rows.next()? {
            Ok(UserProfile {
                id: row.get(0)?,
                name: row.get(1)?,
                email: row.get(2)?,
                avatar: row.get(3)?,
            })
        } else {
            // Create default profile if none exists
            let default_profile = UserProfile {
                id: 1,
                name: "Ichin User".to_string(),
                email: "user@ichin.browser".to_string(),
                avatar: Some("icon-user".to_string()),
            };
            conn.execute(
                "INSERT INTO user_profile (id, name, email, avatar) VALUES (?1, ?2, ?3, ?4)",
                params![default_profile.id, default_profile.name, default_profile.email, default_profile.avatar],
            )?;
            Ok(default_profile)
        }
    }

    pub fn update_user_profile(&self, profile: UserProfile) -> Result<UserProfile> {
        let conn = self.connection.lock().unwrap();
        conn.execute(
            "UPDATE user_profile SET name = ?1, email = ?2, avatar = ?3 WHERE id = ?4",
            params![profile.name, profile.email, profile.avatar, profile.id],
        )?;
        Ok(profile)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HistoryItem {
    pub id: String,
    pub title: String,
    pub url: String,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserProfile {
    pub id: i32,
    pub name: String,
    pub email: String,
    pub avatar: Option<String>,
}