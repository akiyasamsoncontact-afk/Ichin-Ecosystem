use std::sync::Arc;

use serde::{Deserialize, Serialize};
use sled::Db;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub id: String,
    pub from_name: String,
    pub from_email: String,
    pub to: Vec<Recipient>,
    pub subject: String,
    pub body: String,
    pub timestamp: i64,
    pub folder: String,
    pub unread: bool,
    pub starred: bool,
    pub attachments: Vec<AttachmentRef>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recipient {
    pub name: String,
    pub email: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttachmentRef {
    pub name: String,
    pub size: String,
    pub hash: Option<String>,
}

pub struct Mailbox {
    db: Arc<Db>,
}

impl Mailbox {
    pub fn open(path: &str) -> Result<Self, anyhow::Error> {
        let db = sled::open(path)?;
        Ok(Self { db: Arc::new(db) })
    }

    pub fn store_message(&self, msg: &Message) -> Result<(), anyhow::Error> {
        let key = format!("msg:{}", msg.id);
        let value = serde_json::to_vec(msg)?;
        self.db.insert(key.as_bytes(), value)?;
        // Also index by folder
        let folder_key = format!("folder:{}:{}", msg.folder, msg.id);
        self.db.insert(folder_key.as_bytes(), msg.id.as_bytes())?;
        self.db.flush()?;
        Ok(())
    }

    pub fn get_message(&self, id: &str) -> Result<Option<Message>, anyhow::Error> {
        let key = format!("msg:{}", id);
        match self.db.get(key.as_bytes())? {
            Some(value) => {
                let msg: Message = serde_json::from_slice(&value)?;
                Ok(Some(msg))
            }
            None => Ok(None),
        }
    }

    pub fn list_folder(&self, folder: &str) -> Result<Vec<Message>, anyhow::Error> {
        let prefix = format!("folder:{}:", folder);
        let mut messages = Vec::new();

        for item in self.db.scan_prefix(prefix.as_bytes()) {
            let (_, value) = item?;
            let msg_id = String::from_utf8_lossy(&value).to_string();
            if let Some(msg) = self.get_message(&msg_id)? {
                messages.push(msg);
            }
        }

        messages.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        Ok(messages)
    }

    pub fn update_folder(&self, id: &str, new_folder: &str) -> Result<(), anyhow::Error> {
        if let Some(mut msg) = self.get_message(id)? {
            // Remove old folder index
            let old_key = format!("folder:{}:{}", msg.folder, id);
            self.db.remove(old_key.as_bytes())?;

            // Update folder
            msg.folder = new_folder.to_string();
            let msg_key = format!("msg:{}", id);
            let value = serde_json::to_vec(&msg)?;
            self.db.insert(msg_key.as_bytes(), value)?;

            // Add new folder index
            let new_key = format!("folder:{}:{}", new_folder, id);
            self.db.insert(new_key.as_bytes(), id.as_bytes())?;
            self.db.flush()?;
        }
        Ok(())
    }

    pub fn mark_read(&self, id: &str, read: bool) -> Result<(), anyhow::Error> {
        if let Some(mut msg) = self.get_message(id)? {
            msg.unread = !read;
            let key = format!("msg:{}", id);
            let value = serde_json::to_vec(&msg)?;
            self.db.insert(key.as_bytes(), value)?;
            self.db.flush()?;
        }
        Ok(())
    }

    pub fn toggle_star(&self, id: &str) -> Result<(), anyhow::Error> {
        if let Some(mut msg) = self.get_message(id)? {
            msg.starred = !msg.starred;
            let key = format!("msg:{}", id);
            let value = serde_json::to_vec(&msg)?;
            self.db.insert(key.as_bytes(), value)?;
            self.db.flush()?;
        }
        Ok(())
    }

    pub fn delete_message(&self, id: &str) -> Result<(), anyhow::Error> {
        if let Some(msg) = self.get_message(id)? {
            let folder_key = format!("folder:{}:{}", msg.folder, id);
            self.db.remove(folder_key.as_bytes())?;
            let msg_key = format!("msg:{}", id);
            self.db.remove(msg_key.as_bytes())?;
            self.db.flush()?;
        }
        Ok(())
    }

    pub fn unread_count(&self, folder: &str) -> Result<usize, anyhow::Error> {
        let msgs = self.list_folder(folder)?;
        Ok(msgs.iter().filter(|m| m.unread).count())
    }
}
