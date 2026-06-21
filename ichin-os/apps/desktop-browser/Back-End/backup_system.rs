use std::fs;
use std::path::Path;
use std::time::{SystemTime, Duration};
use tokio::time::interval;
use tracing::{info, warn, error};

/// Automated backup system for Ichin databases
pub struct BackupSystem {
    db_path: String,
    backup_dir: String,
    backup_interval_hours: u64,
    max_backups: usize,
}

impl BackupSystem {
    pub fn new(db_path: String, backup_dir: String, backup_interval_hours: u64, max_backups: usize) -> Self {
        Self {
            db_path,
            backup_dir,
            backup_interval_hours,
            max_backups,
        }
    }

    /// Start the automated backup system
    pub async fn start(&self) {
        // Create backup directory if it doesn't exist
        if let Err(e) = fs::create_dir_all(&self.backup_dir) {
            error!("Failed to create backup directory: {}", e);
            return;
        }

        // Run initial backup
        if let Err(e) = self.perform_backup() {
            error!("Initial backup failed: {}", e);
        }

        // Set up periodic backup
        let mut interval = interval(Duration::from_hours(self.backup_interval_hours));
        loop {
            interval.tick().await;
            if let Err(e) = self.perform_backup() {
                error!("Scheduled backup failed: {}", e);
            }
        }
    }

    /// Perform a backup operation
    fn perform_backup(&self) -> Result<(), std::io::Error> {
        let timestamp = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)?
            .as_secs();
        
        let backup_file = format!("{}/ichin_backup_{}.db", self.backup_dir, timestamp);
        
        // Copy the database file
        fs::copy(&self.db_path, &backup_file)?;
        
        info!("Database backup created: {}", backup_file);
        
        // Clean up old backups
        self.cleanup_old_backups()?;
        
        Ok(())
    }

    /// Remove old backups exceeding the maximum count
    fn cleanup_old_backups(&self) -> Result<(), std::io::Error> {
        let mut backups: Vec<(std::path::PathBuf, u64)> = fs::read_dir(&self.backup_dir)?
            .filter_map(|entry| {
                let entry = entry.ok()?;
                let path = entry.path();
                if path.extension().and_then(|s| s.to_str()) == Some("db") {
                    // Extract timestamp from filename
                    if let Some(file_name) = path.file_name().and_then(|s| s.to_str()) {
                        if let Some(underscore_idx) = file_name.rfind('_') {
                            if let Some(dot_idx) = file_name.rfind('.') {
                                if underscore_idx + 1 < dot_idx {
                                    if let Ok(timestamp) = &file_name[underscore_idx+1..dot_idx].parse::<u64>() {
                                        return Some((path, *timestamp));
                                    }
                                }
                            }
                        }
                    }
                }
                None
            })
            .collect();

        // Sort by timestamp (newest first)
        backups.sort_by(|a, b| b.1.cmp(&a.1));

        // Remove excess backups
        if backups.len() > self.max_backups {
            for (path, _) in backups.iter().skip(self.max_backups) {
                if let Err(e) = fs::remove_file(path) {
                    warn!("Failed to remove old backup {}: {}", path.display(), e);
                } else {
                    info!("Removed old backup: {}", path.display());
                }
            }
        }

        Ok(())
    }

    /// Restore database from a backup file
    pub fn restore_from_backup(&self, backup_timestamp: u64) -> Result<(), std::io::Error> {
        let backup_file = format!("{}/ichin_backup_{}.db", self.backup_dir, backup_timestamp);
        
        if !Path::new(&backup_file).exists() {
            return Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                format!("Backup file not found: {}", backup_file),
            ));
        }
        
        // Copy backup to main database location
        fs::copy(&backup_file, &self.db_path)?;
        
        info!("Database restored from backup: {}", backup_file);
        
        Ok(())
    }

    /// List available backups
    pub fn list_backups(&self) -> Result<Vec<u64>, std::io::Error> {
        let mut backups = Vec::new();
        
        for entry in fs::read_dir(&self.backup_dir)? {
            let entry = entry?;
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("db") {
                if let Some(file_name) = path.file_name().and_then(|s| s.to_str()) {
                    if let Some(underscore_idx) = file_name.rfind('_') {
                        if let Some(dot_idx) = file_name.rfind('.') {
                            if underscore_idx + 1 < dot_idx {
                                if let Ok(timestamp) = &file_name[underscore_idx+1..dot_idx].parse::<u64>() {
                                    backups.push(*timestamp);
                                }
                            }
                        }
                    }
                }
            }
        }
        
        backups.sort();
        backups.dedup();
        
        Ok(backups)
    }
}