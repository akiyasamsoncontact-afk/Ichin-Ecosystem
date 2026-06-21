use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::time::{interval, Duration};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct DaemonConfig {
    name: String,
    enabled: bool,
    interval_secs: u64,
    last_run: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SystemDaemon {
    version: String,
    uptime: DateTime<Utc>,
    tasks: HashMap<String, DaemonConfig>,
    status: String,
}

impl SystemDaemon {
    fn new() -> Self {
        let mut tasks = HashMap::new();
        for (name, interval) in &[
            ("health_check", 30u64),
            ("log_rotation", 300),
            ("temp_cleanup", 600),
            ("sync_check", 60),
            ("backup_check", 3600),
        ] {
            tasks.insert(
                name.to_string(),
                DaemonConfig {
                    name: name.to_string(),
                    enabled: true,
                    interval_secs: *interval,
                    last_run: None,
                },
            );
        }
        SystemDaemon {
            version: "0.1.0".to_string(),
            uptime: Utc::now(),
            tasks,
            status: "running".to_string(),
        }
    }

    fn run_task(&mut self, task_name: &str) -> String {
        if let Some(task) = self.tasks.get_mut(task_name) {
            if !task.enabled {
                return format!("task '{}' is disabled", task_name);
            }
            task.last_run = Some(Utc::now());
            format!("task '{}' executed successfully", task_name)
        } else {
            format!("task '{}' not found", task_name)
        }
    }

    fn list_tasks(&self) -> Vec<&DaemonConfig> {
        self.tasks.values().collect()
    }

    fn toggle_task(&mut self, task_name: &str, enabled: bool) -> bool {
        if let Some(task) = self.tasks.get_mut(task_name) {
            task.enabled = enabled;
            true
        } else {
            false
        }
    }
}

fn parse_route(request: &str) -> (String, String) {
    let lines: Vec<&str> = request.lines().collect();
    if lines.is_empty() {
        return ("GET".to_string(), "/".to_string());
    }
    let parts: Vec<&str> = lines[0].split_whitespace().collect();
    let method = parts.first().unwrap_or(&"GET").to_string();
    let path = parts.get(1).unwrap_or(&"/").to_string();
    (method, path)
}

#[tokio::main]
async fn main() {
    println!("[SYSTEM-DAEMON] ICHIN OS System Daemon starting on port 7010...");

    let daemon = Arc::new(RwLock::new(SystemDaemon::new()));

    let d = daemon.clone();
    tokio::spawn(async move {
        let mut interval = interval(Duration::from_secs(30));
        loop {
            interval.tick().await;
            let mut d = d.write().await;
            for (name, task) in &d.tasks.clone() {
                if task.enabled {
                    if let Some(last) = task.last_run {
                        let elapsed = (Utc::now() - last).num_seconds() as u64;
                        if elapsed >= task.interval_secs {
                            d.run_task(name);
                            println!("[SYSTEM-DAEMON] Ran scheduled task: {}", name);
                        }
                    } else {
                        d.run_task(name);
                        println!("[SYSTEM-DAEMON] Ran initial task: {}", name);
                    }
                }
            }
        }
    });

    let listener = tokio::net::TcpListener::bind("127.0.0.1:7010")
        .await
        .expect("Failed to bind to port 7010");

    loop {
        let (socket, _) = listener.accept().await.unwrap();
        let daemon = daemon.clone();
        tokio::spawn(async move {
            let mut buf = [0; 4096];
            let n = match socket.try_read(&mut buf) {
                Ok(n) => n,
                Err(_) => return,
            };
            let request = String::from_utf8_lossy(&buf[..n]);
            let (method, path) = parse_route(&request);

            let response = match (method.as_str(), path.as_str()) {
                ("GET", "/daemon/status") => {
                    let d = daemon.read().await;
                    format!(
                        r#"{{"version":"{}","uptime":"{}","status":"{}","tasks":{}}}"#,
                        d.version,
                        d.uptime,
                        d.status,
                        d.tasks.len()
                    )
                }
                ("GET", "/daemon/tasks") => {
                    let d = daemon.read().await;
                    let tasks: Vec<String> = d
                        .list_tasks()
                        .iter()
                        .map(|t| {
                            format!(
                                r#"{{"name":"{}","enabled":{},"interval_secs":{},"last_run":{}}}"#,
                                t.name,
                                t.enabled,
                                t.interval_secs,
                                t.last_run
                                    .map(|dt| format!("\"{}\"", dt))
                                    .unwrap_or("null".to_string())
                            )
                        })
                        .collect();
                    format!(r#"{{"tasks":[{}]}}"#, tasks.join(","))
                }
                ("POST", path) if path.starts_with("/daemon/tasks/") && path.ends_with("/run") => {
                    let task_name = path
                        .trim_start_matches("/daemon/tasks/")
                        .trim_end_matches("/run");
                    let mut d = daemon.write().await;
                    let result = d.run_task(task_name);
                    format!(r#"{{"result":"{}"}}"#, result)
                }
                ("POST", path) if path.starts_with("/daemon/tasks/") && path.ends_with("/toggle") => {
                    let task_name = path
                        .trim_start_matches("/daemon/tasks/")
                        .trim_end_matches("/toggle");
                    let mut d = daemon.write().await;
                    let current = d.tasks.get(task_name).map(|t| t.enabled).unwrap_or(false);
                    d.toggle_task(task_name, !current);
                    format!(r#"{{"task":"{}","enabled":{}}}"#, task_name, !current)
                }
                _ => r#"{"error":"not_found"}"#.to_string(),
            };

            let http_response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
                response.len(),
                response
            );
            let _ = socket.try_write(http_response.as_bytes());
        });
    }
}
