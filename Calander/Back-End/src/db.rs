use rusqlite::{params, Connection, Result};
use std::sync::Mutex;
use tracing::info;

use crate::models::Task;

pub struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    pub fn new(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000;")?;
        let db = Database { conn: Mutex::new(conn) };
        db.init_tables()?;
        Ok(db)
    }

    fn init_tables(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                due_date TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'medium',
                status TEXT NOT NULL DEFAULT 'todo',
                tags TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            );"
        )?;
        info!("Database tables initialized");
        Ok(())
    }

    pub fn get_all_tasks(&self) -> Result<Vec<Task>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT id, title, description, due_date, priority, status, tags, created_at FROM tasks ORDER BY created_at DESC"
        )?;
        let tasks = stmt.query_map([], |row| {
            let tags_str: String = row.get(6)?;
            let tags: Vec<String> = serde_json::from_str(&tags_str).unwrap_or_default();
            Ok(Task {
                id: row.get(0)?,
                title: row.get(1)?,
                description: row.get(2)?,
                due_date: row.get(3)?,
                priority: row.get(4)?,
                status: row.get(5)?,
                tags,
                created_at: row.get(7)?,
            })
        })?;
        tasks.collect()
    }

    pub fn create_task(&self, task: &Task) -> Result<()> {
        let conn = self.conn.lock().unwrap();
        let tags_str = serde_json::to_string(&task.tags).unwrap_or_else(|_| "[]".to_string());
        conn.execute(
            "INSERT INTO tasks (id, title, description, due_date, priority, status, tags, created_at) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![task.id, task.title, task.description, task.due_date, task.priority, task.status, tags_str, task.created_at],
        )?;
        Ok(())
    }

    pub fn update_task(&self, id: &str, task: &Task) -> Result<bool> {
        let conn = self.conn.lock().unwrap();
        let tags_str = serde_json::to_string(&task.tags).unwrap_or_else(|_| "[]".to_string());
        let rows = conn.execute(
            "UPDATE tasks SET title=?1, description=?2, due_date=?3, priority=?4, status=?5, tags=?6 WHERE id=?7",
            params![task.title, task.description, task.due_date, task.priority, task.status, tags_str, id],
        )?;
        Ok(rows > 0)
    }

    pub fn delete_task(&self, id: &str) -> Result<bool> {
        let conn = self.conn.lock().unwrap();
        let rows = conn.execute("DELETE FROM tasks WHERE id=?", params![id])?;
        Ok(rows > 0)
    }
}
