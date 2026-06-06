use std::sync::Arc;

use anyhow::{Context, Result};
use sled::Db;
use tracing::info;
use uuid::Uuid;

use crate::models::*;

#[derive(Clone)]
pub struct AccountStore {
    db: Arc<Db>,
}

impl AccountStore {
    pub fn new(path: &str) -> Result<Self> {
        let db = sled::open(path).context("Failed to open sled database")?;
        info!("Account store opened at {}", path);
        Ok(Self { db: Arc::new(db) })
    }

    // --- Users ---

    pub fn create_user(&self, user: &User) -> Result<()> {
        let key = format!("user:{}", user.id);
        let value = serde_json::to_vec(user)?;
        self.db.insert(key.as_bytes(), value)?;

        let username_key = format!("username:{}", user.username);
        self.db.insert(username_key.as_bytes(), user.id.to_string().as_bytes())?;

        let email_key = format!("email:{}", user.email);
        self.db.insert(email_key.as_bytes(), user.id.to_string().as_bytes())?;

        Ok(())
    }

    pub fn get_user(&self, user_id: UserId) -> Result<Option<User>> {
        let key = format!("user:{}", user_id);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => Ok(Some(serde_json::from_slice(&bytes)?)),
            None => Ok(None),
        }
    }

    pub fn get_user_by_username(&self, username: &str) -> Result<Option<User>> {
        let username_key = format!("username:{}", username);
        match self.db.get(username_key.as_bytes())? {
            Some(bytes) => {
                let id_str = String::from_utf8(bytes.to_vec())?;
                let id = UserId::parse_str(&id_str)?;
                self.get_user(id)
            }
            None => Ok(None),
        }
    }

    pub fn get_user_by_email(&self, email: &str) -> Result<Option<User>> {
        let email_key = format!("email:{}", email);
        match self.db.get(email_key.as_bytes())? {
            Some(bytes) => {
                let id_str = String::from_utf8(bytes.to_vec())?;
                let id = UserId::parse_str(&id_str)?;
                self.get_user(id)
            }
            None => Ok(None),
        }
    }

    pub fn update_user(&self, user: &User) -> Result<()> {
        let key = format!("user:{}", user.id);
        let value = serde_json::to_vec(user)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    // --- Sessions ---

    pub fn create_session(&self, session: &Session) -> Result<()> {
        let key = format!("session:{}", session.id);
        let value = serde_json::to_vec(session)?;
        self.db.insert(key.as_bytes(), value)?;

        let token_key = format!("token:{}", session.token);
        self.db.insert(token_key.as_bytes(), session.id.to_string().as_bytes())?;

        let user_sessions_key = format!("user_sessions:{}", session.user_id);
        let mut sessions: Vec<SessionId> = self
            .db
            .get(user_sessions_key.as_bytes())?
            .map(|b| serde_json::from_slice(&b).unwrap_or_default())
            .unwrap_or_default();
        sessions.push(session.id);
        self.db
            .insert(user_sessions_key.as_bytes(), serde_json::to_vec(&sessions)?)?;

        Ok(())
    }

    pub fn get_session(&self, session_id: SessionId) -> Result<Option<Session>> {
        let key = format!("session:{}", session_id);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => Ok(Some(serde_json::from_slice(&bytes)?)),
            None => Ok(None),
        }
    }

    pub fn get_session_by_token(&self, token: &str) -> Result<Option<Session>> {
        let token_key = format!("token:{}", token);
        match self.db.get(token_key.as_bytes())? {
            Some(bytes) => {
                let id_str = String::from_utf8(bytes.to_vec())?;
                let id = SessionId::parse_str(&id_str)?;
                self.get_session(id)
            }
            None => Ok(None),
        }
    }

    pub fn get_user_sessions(&self, user_id: UserId) -> Result<Vec<Session>> {
        let key = format!("user_sessions:{}", user_id);
        let session_ids: Vec<SessionId> = self
            .db
            .get(key.as_bytes())?
            .map(|b| serde_json::from_slice(&b).unwrap_or_default())
            .unwrap_or_default();
        let mut sessions = Vec::new();
        for id in session_ids {
            if let Some(s) = self.get_session(id)? {
                sessions.push(s);
            }
        }
        Ok(sessions)
    }

    pub fn update_session(&self, session: &Session) -> Result<()> {
        let key = format!("session:{}", session.id);
        let value = serde_json::to_vec(session)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn delete_session(&self, session_id: SessionId) -> Result<()> {
        let session = self.get_session(session_id)?;
        if let Some(s) = session {
            let token_key = format!("token:{}", s.token);
            self.db.remove(token_key.as_bytes())?;
        }
        let key = format!("session:{}", session_id);
        self.db.remove(key.as_bytes())?;
        Ok(())
    }

    // --- Devices ---

    pub fn create_device(&self, device: &Device) -> Result<()> {
        let key = format!("device:{}", device.id);
        let value = serde_json::to_vec(device)?;
        self.db.insert(key.as_bytes(), value)?;

        let user_devices_key = format!("user_devices:{}", device.user_id);
        let mut devices: Vec<DeviceId> = self
            .db
            .get(user_devices_key.as_bytes())?
            .map(|b| serde_json::from_slice(&b).unwrap_or_default())
            .unwrap_or_default();
        devices.push(device.id);
        self.db
            .insert(user_devices_key.as_bytes(), serde_json::to_vec(&devices)?)?;

        Ok(())
    }

    pub fn get_device(&self, device_id: DeviceId) -> Result<Option<Device>> {
        let key = format!("device:{}", device_id);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => Ok(Some(serde_json::from_slice(&bytes)?)),
            None => Ok(None),
        }
    }

    pub fn get_user_devices(&self, user_id: UserId) -> Result<Vec<Device>> {
        let key = format!("user_devices:{}", user_id);
        let device_ids: Vec<DeviceId> = self
            .db
            .get(key.as_bytes())?
            .map(|b| serde_json::from_slice(&b).unwrap_or_default())
            .unwrap_or_default();
        let mut devices = Vec::new();
        for id in device_ids {
            if let Some(d) = self.get_device(id)? {
                devices.push(d);
            }
        }
        Ok(devices)
    }

    pub fn update_device(&self, device: &Device) -> Result<()> {
        let key = format!("device:{}", device.id);
        let value = serde_json::to_vec(device)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn delete_device(&self, device_id: DeviceId) -> Result<()> {
        let device = self.get_device(device_id)?;
        if let Some(d) = device {
            let user_devices_key = format!("user_devices:{}", d.user_id);
            let mut devices: Vec<DeviceId> = self
                .db
                .get(user_devices_key.as_bytes())?
                .map(|b| serde_json::from_slice(&b).unwrap_or_default())
                .unwrap_or_default();
            devices.retain(|id| *id != device_id);
            self.db
                .insert(user_devices_key.as_bytes(), serde_json::to_vec(&devices)?)?;
        }
        let key = format!("device:{}", device_id);
        self.db.remove(key.as_bytes())?;
        Ok(())
    }

    // --- Login History ---

    pub fn add_login_history(&self, entry: &LoginHistoryEntry) -> Result<()> {
        let key = format!("login:{}:{}", entry.user_id, entry.id);
        let value = serde_json::to_vec(entry)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn get_login_history(&self, user_id: UserId, limit: usize) -> Result<Vec<LoginHistoryEntry>> {
        let prefix = format!("login:{}:", user_id);
        let mut entries: Vec<LoginHistoryEntry> = self
            .db
            .scan_prefix(prefix.as_bytes())
            .filter_map(|r| r.ok())
            .filter_map(|(_, v)| serde_json::from_slice::<LoginHistoryEntry>(&v).ok())
            .collect();
        entries.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        entries.truncate(limit);
        Ok(entries)
    }

    // --- Storage Usage ---

    pub fn get_storage_usage(&self, user_id: UserId) -> Result<StorageUsage> {
        let key = format!("storage:{}", user_id);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => Ok(serde_json::from_slice(&bytes)?),
            None => Ok(StorageUsage {
                user_id,
                total_bytes: 1_073_741_824, // 1 GB default
                used_bytes: 0,
                mail_bytes: 0,
                sync_bytes: 0,
            }),
        }
    }

    pub fn update_storage_usage(&self, usage: &StorageUsage) -> Result<()> {
        let key = format!("storage:{}", usage.user_id);
        let value = serde_json::to_vec(usage)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    // --- Account Settings ---

    pub fn get_settings(&self, user_id: UserId) -> Result<AccountSettings> {
        let key = format!("settings:{}", user_id);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => Ok(serde_json::from_slice(&bytes)?),
            None => Ok(AccountSettings {
                user_id,
                theme: Theme::Dark,
                language: "en".to_string(),
                email_notifications: true,
                auto_sync: true,
            }),
        }
    }

    pub fn update_settings(&self, settings: &AccountSettings) -> Result<()> {
        let key = format!("settings:{}", settings.user_id);
        let value = serde_json::to_vec(settings)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    // --- Browser Sync: Bookmarks ---

    pub fn create_bookmark(&self, bookmark: &Bookmark) -> Result<()> {
        let key = format!("bookmark:{}:{}", bookmark.user_id, bookmark.id);
        let value = serde_json::to_vec(bookmark)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn get_user_bookmarks(&self, user_id: UserId) -> Result<Vec<Bookmark>> {
        let prefix = format!("bookmark:{}:", user_id);
        Ok(self
            .db
            .scan_prefix(prefix.as_bytes())
            .filter_map(|r| r.ok())
            .filter_map(|(_, v)| serde_json::from_slice::<Bookmark>(&v).ok())
            .collect())
    }

    pub fn delete_bookmark(&self, user_id: UserId, bookmark_id: Uuid) -> Result<()> {
        let key = format!("bookmark:{}:{}", user_id, bookmark_id);
        self.db.remove(key.as_bytes())?;
        Ok(())
    }

    // --- Browser Sync: History ---

    pub fn add_history_entry(&self, entry: &HistoryEntry) -> Result<()> {
        let key = format!("history:{}:{}", entry.user_id, entry.id);
        let value = serde_json::to_vec(entry)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn get_user_history(&self, user_id: UserId, limit: usize) -> Result<Vec<HistoryEntry>> {
        let prefix = format!("history:{}:", user_id);
        let mut entries: Vec<HistoryEntry> = self
            .db
            .scan_prefix(prefix.as_bytes())
            .filter_map(|r| r.ok())
            .filter_map(|(_, v)| serde_json::from_slice::<HistoryEntry>(&v).ok())
            .collect();
        entries.sort_by(|a, b| b.last_visited_at.cmp(&a.last_visited_at));
        entries.truncate(limit);
        Ok(entries)
    }

    // --- Browser Sync: Saved Passwords ---

    pub fn save_password(&self, password: &SavedPassword) -> Result<()> {
        let key = format!("password:{}:{}", password.user_id, password.id);
        let value = serde_json::to_vec(password)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn get_user_passwords(&self, user_id: UserId) -> Result<Vec<SavedPassword>> {
        let prefix = format!("password:{}:", user_id);
        Ok(self
            .db
            .scan_prefix(prefix.as_bytes())
            .filter_map(|r| r.ok())
            .filter_map(|(_, v)| serde_json::from_slice::<SavedPassword>(&v).ok())
            .collect())
    }

    // --- Browser Sync: Tabs ---

    pub fn upsert_tab(&self, tab: &SyncTab) -> Result<()> {
        let key = format!("tab:{}:{}", tab.user_id, tab.id);
        let value = serde_json::to_vec(tab)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    pub fn get_user_tabs(&self, user_id: UserId) -> Result<Vec<SyncTab>> {
        let prefix = format!("tab:{}:", user_id);
        Ok(self
            .db
            .scan_prefix(prefix.as_bytes())
            .filter_map(|r| r.ok())
            .filter_map(|(_, v)| serde_json::from_slice::<SyncTab>(&v).ok())
            .collect())
    }

    // --- Browser Settings ---

    pub fn get_browser_settings(&self, user_id: UserId) -> Result<BrowserSettings> {
        let key = format!("browser_settings:{}", user_id);
        match self.db.get(key.as_bytes())? {
            Some(bytes) => Ok(serde_json::from_slice(&bytes)?),
            None => Ok(BrowserSettings {
                user_id,
                homepage: None,
                search_engine: "ichin".to_string(),
                privacy_mode: false,
                sync_passwords: true,
                sync_history: true,
                sync_bookmarks: true,
                sync_tabs: true,
                sync_settings: true,
            }),
        }
    }

    pub fn update_browser_settings(&self, settings: &BrowserSettings) -> Result<()> {
        let key = format!("browser_settings:{}", settings.user_id);
        let value = serde_json::to_vec(settings)?;
        self.db.insert(key.as_bytes(), value)?;
        Ok(())
    }

    // --- Username availability ---

    pub fn is_username_available(&self, username: &str) -> Result<bool> {
        let key = format!("username:{}", username);
        Ok(self.db.get(key.as_bytes())?.is_none())
    }

    pub fn is_email_available(&self, email: &str) -> Result<bool> {
        let key = format!("email:{}", email);
        Ok(self.db.get(key.as_bytes())?.is_none())
    }
}
