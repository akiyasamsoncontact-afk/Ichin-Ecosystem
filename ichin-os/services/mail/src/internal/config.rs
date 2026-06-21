use std::path::PathBuf;

#[derive(Debug, Clone)]
pub struct Config {
    pub server_name: String,
    pub listen_addr: String,
    pub tls_cert_path: String,
    pub tls_key_path: String,
    pub db_path: PathBuf,
    pub storage_path: PathBuf,
    pub gateway_listen_addr: String,
    pub max_message_size: u64,
    pub rate_limit_per_min: u32,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            server_name: "mail.ichin.local".to_string(),
            listen_addr: "0.0.0.0:443".to_string(),
            tls_cert_path: "/etc/ichin/cert.pem".to_string(),
            tls_key_path: "/etc/ichin/key.pem".to_string(),
            db_path: PathBuf::from("/var/lib/ichin/db"),
            storage_path: PathBuf::from("/var/lib/ichin/storage"),
            gateway_listen_addr: "0.0.0.0:25".to_string(),
            max_message_size: 10 * 1024 * 1024,
            rate_limit_per_min: 60,
        }
    }
}

impl Config {
    pub fn from_env() -> Self {
        Self {
            server_name: std::env::var("ICHIN_SERVER_NAME")
                .unwrap_or_else(|_| "mail.ichin.local".to_string()),
            listen_addr: std::env::var("ICHIN_LISTEN_ADDR")
                .unwrap_or_else(|_| "0.0.0.0:443".to_string()),
            tls_cert_path: std::env::var("ICHIN_TLS_CERT")
                .unwrap_or_else(|_| "/etc/ichin/cert.pem".to_string()),
            tls_key_path: std::env::var("ICHIN_TLS_KEY")
                .unwrap_or_else(|_| "/etc/ichin/key.pem".to_string()),
            db_path: PathBuf::from(
                std::env::var("ICHIN_DB_PATH")
                    .unwrap_or_else(|_| "/var/lib/ichin/db".to_string()),
            ),
            storage_path: PathBuf::from(
                std::env::var("ICHIN_STORAGE_PATH")
                    .unwrap_or_else(|_| "/var/lib/ichin/storage".to_string()),
            ),
            gateway_listen_addr: std::env::var("ICHIN_GATEWAY_ADDR")
                .unwrap_or_else(|_| "0.0.0.0:25".to_string()),
            max_message_size: 10 * 1024 * 1024,
            rate_limit_per_min: 60,
        }
    }
}
