use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub type UserId = Uuid;
pub type SessionId = Uuid;
pub type DeviceId = Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: UserId,
    pub username: String,
    pub display_name: String,
    pub email: String,
    pub profile_picture: Option<String>,
    pub passkey_credentials: Vec<PasskeyCredential>,
    pub totp_secret: Option<String>,
    pub recovery_codes: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PasskeyCredential {
    pub id: String,
    pub public_key: Vec<u8>,
    pub counter: u32,
    pub transports: Vec<String>,
    pub name: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub id: SessionId,
    pub user_id: UserId,
    pub device_id: Option<DeviceId>,
    pub token: String,
    pub ip_address: String,
    pub user_agent: String,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
    pub last_accessed_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Device {
    pub id: DeviceId,
    pub user_id: UserId,
    pub name: String,
    pub device_type: DeviceType,
    pub last_synced_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DeviceType {
    Desktop,
    Laptop,
    Phone,
    Tablet,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoginHistoryEntry {
    pub id: Uuid,
    pub user_id: UserId,
    pub timestamp: DateTime<Utc>,
    pub ip_address: String,
    pub user_agent: String,
    pub success: bool,
    pub method: AuthMethod,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AuthMethod {
    Passkey,
    TOTP,
    RecoveryCode,
    Password,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AccountSettings {
    pub user_id: UserId,
    pub theme: Theme,
    pub language: String,
    pub email_notifications: bool,
    pub auto_sync: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Theme {
    Dark,
    Light,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageUsage {
    pub user_id: UserId,
    pub total_bytes: u64,
    pub used_bytes: u64,
    pub mail_bytes: u64,
    pub sync_bytes: u64,
}

// Browser sync models

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Bookmark {
    pub id: Uuid,
    pub user_id: UserId,
    pub title: String,
    pub url: String,
    pub folder: Option<String>,
    pub position: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HistoryEntry {
    pub id: Uuid,
    pub user_id: UserId,
    pub url: String,
    pub title: String,
    pub visit_count: i32,
    pub last_visited_at: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SavedPassword {
    pub id: Uuid,
    pub user_id: UserId,
    pub domain: String,
    pub username: String,
    pub encrypted_password: Vec<u8>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SyncTab {
    pub id: Uuid,
    pub user_id: UserId,
    pub device_id: DeviceId,
    pub title: String,
    pub url: String,
    pub active: bool,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrowserSettings {
    pub user_id: UserId,
    pub homepage: Option<String>,
    pub search_engine: String,
    pub privacy_mode: bool,
    pub sync_passwords: bool,
    pub sync_history: bool,
    pub sync_bookmarks: bool,
    pub sync_tabs: bool,
    pub sync_settings: bool,
}
