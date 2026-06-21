use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};
use std::sync::atomic::{AtomicU32, Ordering as AtomicOrdering};
use std::sync::Arc;

use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::routing::{delete, get, patch, post};
use axum::{Json, Router};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use tokio::sync::RwLock;
use tracing::info;
use uuid::Uuid;

use sysinfo::{System, SystemExt};

// ============================================================
// Data Models
// ============================================================

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum ProcessStatus {
    Running,
    Suspended,
    Terminated,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    Anomaly,
    Threat,
    Violation,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum SnapshotStatus {
    Active,
    RolledBack,
    Failed,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum SecurityMode {
    Passive,
    Active,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Process {
    pub id: Uuid,
    pub name: String,
    pub pid: u32,
    pub status: ProcessStatus,
    pub priority: u8,
    pub cpu_usage: f64,
    pub memory_usage: u64,
    pub sandbox_level: u8,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceLimits {
    pub max_memory_mb: u64,
    pub max_cpu_percent: f64,
    pub max_processes: u32,
    pub allowed_network: bool,
    pub allowed_filesystem: bool,
}

impl Default for ResourceLimits {
    fn default() -> Self {
        ResourceLimits {
            max_memory_mb: 512,
            max_cpu_percent: 50.0,
            max_processes: 5,
            allowed_network: false,
            allowed_filesystem: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Sandbox {
    pub id: Uuid,
    pub level: u8,
    pub process_ids: Vec<Uuid>,
    pub permissions: Vec<String>,
    pub resource_limits: ResourceLimits,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityEvent {
    pub id: Uuid,
    pub event_type: EventType,
    pub process_id: Option<Uuid>,
    pub severity: Severity,
    pub description: String,
    pub detected_at: DateTime<Utc>,
    pub action_taken: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Snapshot {
    pub id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub description: String,
    pub services_included: Vec<String>,
    pub size: u64,
    pub status: SnapshotStatus,
    pub processes: HashMap<Uuid, Process>,
    pub sandboxes: HashMap<Uuid, Sandbox>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEntry {
    pub id: Uuid,
    pub timestamp: DateTime<Utc>,
    pub process_id: Option<Uuid>,
    pub action: String,
    pub permission_used: String,
    pub impact_score: f64,
    pub rollback_available: bool,
}

// Request DTOs

#[derive(Debug, Deserialize)]
pub struct CreateProcessRequest {
    pub name: String,
    pub priority: u8,
    pub sandbox_level: u8,
}

#[derive(Debug, Deserialize)]
pub struct CreateSandboxRequest {
    pub level: u8,
    pub permissions: Vec<String>,
    #[serde(default)]
    pub resource_limits: Option<ResourceLimits>,
}

#[derive(Debug, Deserialize)]
pub struct ChangePriorityRequest {
    pub priority: u8,
}

#[derive(Debug, Deserialize)]
pub struct CreateSnapshotRequest {
    pub description: String,
    #[serde(default)]
    pub services_included: Option<Vec<String>>,
}

#[derive(Debug, Deserialize)]
pub struct CreateAuditEntryRequest {
    pub process_id: Option<Uuid>,
    pub action: String,
    pub permission_used: String,
    pub impact_score: f64,
    pub rollback_available: bool,
}

#[derive(Debug, Deserialize)]
pub struct ThreatResponseRequest {
    pub action: String,
}

// Response DTOs

#[derive(Debug, Serialize)]
pub struct HealthResponse {
    pub status: String,
    pub service: String,
    pub version: String,
    pub timestamp: String,
    pub uptime_seconds: u64,
}

#[derive(Debug, Serialize)]
pub struct SchedulerStatusResponse {
    pub queue: Vec<ScheduledProcessInfo>,
    pub total_cpu_allocated: f64,
    pub total_memory_allocated: u64,
    pub system_cpu_usage: f64,
    pub system_memory_usage: f64,
    pub system_total_memory: u64,
    pub mode: String,
    pub focus_mode: bool,
}

#[derive(Debug, Serialize)]
pub struct ScheduledProcessInfo {
    pub process_id: Uuid,
    pub name: String,
    pub priority: u8,
    pub cpu_allocated: f64,
    pub memory_allocated: u64,
}

#[derive(Debug, Serialize)]
pub struct ScanResult {
    pub events_generated: usize,
    pub threats_detected: usize,
    pub scan_duration_ms: u64,
    pub summary: String,
}

#[derive(Debug, Serialize)]
pub struct ErrorResponse {
    pub error: String,
}

// ============================================================
// Scheduled Process for Priority Queue
// ============================================================

#[derive(Debug, Clone)]
pub struct ScheduledProcess {
    pub process_id: Uuid,
    pub priority: u8,
    pub cpu_allocated: f64,
    pub memory_allocated: u64,
    pub name: String,
}

impl Eq for ScheduledProcess {}

impl PartialEq for ScheduledProcess {
    fn eq(&self, other: &Self) -> bool {
        self.process_id == other.process_id
    }
}

impl PartialOrd for ScheduledProcess {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for ScheduledProcess {
    fn cmp(&self, other: &Self) -> Ordering {
        other
            .priority
            .cmp(&self.priority)
            .then_with(|| self.cpu_allocated.partial_cmp(&other.cpu_allocated).unwrap_or(Ordering::Equal))
    }
}

// ============================================================
// App State
// ============================================================

pub struct AppState {
    pub processes: HashMap<Uuid, Process>,
    pub sandboxes: HashMap<Uuid, Sandbox>,
    pub security_events: Vec<SecurityEvent>,
    pub active_threats: Vec<SecurityEvent>,
    pub snapshots: Vec<Snapshot>,
    pub audit_log: Vec<AuditEntry>,
    pub scheduler_queue: BinaryHeap<ScheduledProcess>,
    pub next_process_num: AtomicU32,
    pub security_mode: SecurityMode,
    pub focus_mode: bool,
    pub start_time: DateTime<Utc>,
}

impl AppState {
    pub fn new() -> Self {
        AppState {
            processes: HashMap::new(),
            sandboxes: HashMap::new(),
            security_events: Vec::with_capacity(1000),
            active_threats: Vec::new(),
            snapshots: Vec::new(),
            audit_log: Vec::with_capacity(10000),
            scheduler_queue: BinaryHeap::new(),
            next_process_num: AtomicU32::new(1),
            security_mode: SecurityMode::Passive,
            focus_mode: false,
            start_time: Utc::now(),
        }
    }

    pub fn allocate_pid(&self) -> u32 {
        self.next_process_num.fetch_add(1, AtomicOrdering::SeqCst)
    }

    pub fn rebuild_scheduler_queue(&mut self) {
        let mut new_heap = BinaryHeap::new();
        for process in self.processes.values() {
            if process.status == ProcessStatus::Running || process.status == ProcessStatus::Suspended {
                new_heap.push(ScheduledProcess {
                    process_id: process.id,
                    priority: process.priority,
                    cpu_allocated: 100.0 / (process.priority as f64),
                    memory_allocated: process.memory_usage,
                    name: process.name.clone(),
                });
            }
        }
        self.scheduler_queue = new_heap;
    }

    pub fn add_audit_entry(
        &mut self,
        process_id: Option<Uuid>,
        action: String,
        permission_used: String,
        impact_score: f64,
        rollback_available: bool,
    ) {
        let entry = AuditEntry {
            id: Uuid::new_v4(),
            timestamp: Utc::now(),
            process_id,
            action,
            permission_used,
            impact_score,
            rollback_available,
        };
        self.audit_log.push(entry);
    }

    pub fn add_security_event(
        &mut self,
        event_type: EventType,
        process_id: Option<Uuid>,
        severity: Severity,
        description: String,
        action_taken: String,
        is_threat: bool,
    ) -> Uuid {
        let event = SecurityEvent {
            id: Uuid::new_v4(),
            event_type,
            process_id,
            severity,
            description,
            detected_at: Utc::now(),
            action_taken,
        };
        let id = event.id;
        if is_threat {
            self.active_threats.push(event.clone());
        }
        self.security_events.push(event);
        id
    }
}

// ============================================================
// Security Detector Background Task
// ============================================================

async fn security_detector_loop(state: Arc<RwLock<AppState>>) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(45));
    loop {
        interval.tick().await;
        let mut state_lock = state.write().await;

        if state_lock.security_mode == SecurityMode::Passive && fastrand::u32(0..100) > 15 {
            continue;
        }

        let process_count = state_lock.processes.len();
        if process_count == 0 {
            continue;
        }

        let process_ids: Vec<Uuid> = state_lock.processes.keys().copied().collect();
        let target_id = process_ids[fastrand::usize(0..process_ids.len())];

        let anomaly_score = fastrand::u32(0..100);
        if anomaly_score > 92 {
            let event_type = if anomaly_score > 98 {
                EventType::Critical
            } else if anomaly_score > 95 {
                EventType::Threat
            } else {
                EventType::Anomaly
            };

            let severity = match event_type {
                EventType::Critical => Severity::Critical,
                EventType::Threat => Severity::High,
                EventType::Violation => Severity::Medium,
                EventType::Anomaly => Severity::Low,
            };

            let description = match event_type {
                EventType::Critical => {
                    format!("Critical anomaly detected in process {}: unauthorized memory access attempt", target_id)
                }
                EventType::Threat => {
                    format!("Suspicious system call pattern detected from process {}", target_id)
                }
                EventType::Violation => {
                    format!("Sandbox permission violation by process {}", target_id)
                }
                EventType::Anomaly => {
                    format!("Unusual behavior pattern in process {}: high CPU usage spike", target_id)
                }
            };

            let action = if state_lock.security_mode == SecurityMode::Critical {
                let proc = state_lock.processes.get_mut(&target_id);
                if let Some(p) = proc {
                    p.status = ProcessStatus::Terminated;
                }
                "Process terminated, rollback initiated".to_string()
            } else if state_lock.security_mode == SecurityMode::Active {
                let proc = state_lock.processes.get_mut(&target_id);
                if let Some(p) = proc {
                    p.status = ProcessStatus::Suspended;
                }
                "Process suspended, isolation engaged".to_string()
            } else {
                "Event logged, continuing monitoring".to_string()
            };

            state_lock.add_security_event(
                event_type,
                Some(target_id),
                severity,
                description,
                action.clone(),
                anomaly_score > 95,
            );

            state_lock.add_audit_entry(
                Some(target_id),
                "security_detection".to_string(),
                "system.security.detect".to_string(),
                anomaly_score as f64 / 100.0,
                true,
            );

            info!(
                "Security detector: {} (severity={:?}, action={})",
                description, severity, action
            );
        }
    }
}

// ============================================================
// Handlers
// ============================================================

// --- Health ---

async fn health_handler(State(state): State<Arc<RwLock<AppState>>>) -> Json<HealthResponse> {
    let state_lock = state.read().await;
    let uptime = Utc::now() - state_lock.start_time;
    Json(HealthResponse {
        status: "healthy".to_string(),
        service: "ichin-security-core".to_string(),
        version: "0.1.0".to_string(),
        timestamp: Utc::now().to_rfc3339(),
        uptime_seconds: uptime.num_seconds() as u64,
    })
}

// --- Process Handlers ---

async fn list_processes(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<Vec<Process>> {
    let state_lock = state.read().await;
    let mut processes: Vec<Process> = state_lock.processes.values().cloned().collect();
    processes.sort_by_key(|p| p.priority);
    Json(processes)
}

async fn create_process(
    State(state): State<Arc<RwLock<AppState>>>,
    Json(req): Json<CreateProcessRequest>,
) -> impl IntoResponse {
    if req.priority < 1 || req.priority > 6 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ErrorResponse {
                error: "Priority must be between 1 and 6".to_string(),
            }),
        )
            .into_response();
    }
    if req.sandbox_level < 1 || req.sandbox_level > 4 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ErrorResponse {
                error: "Sandbox level must be between 1 and 4".to_string(),
            }),
        )
            .into_response();
    }

    let mut state_lock = state.write().await;

    let process = Process {
        id: Uuid::new_v4(),
        name: req.name,
        pid: state_lock.allocate_pid(),
        status: ProcessStatus::Running,
        priority: req.priority,
        cpu_usage: 0.0,
        memory_usage: 0,
        sandbox_level: req.sandbox_level,
        created_at: Utc::now(),
    };

    state_lock.processes.insert(process.id, process.clone());
    state_lock.rebuild_scheduler_queue();

    state_lock.add_audit_entry(
        Some(process.id),
        "create_process".to_string(),
        "system.process.create".to_string(),
        0.3,
        true,
    );

    info!("Process created: {} (id={}, priority={})", process.name, process.id, process.priority);
    (StatusCode::CREATED, Json(process)).into_response()
}

async fn terminate_process(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;
    match state_lock.processes.get_mut(&id) {
        Some(proc) => {
            proc.status = ProcessStatus::Terminated;
            state_lock.rebuild_scheduler_queue();

            state_lock.add_audit_entry(
                Some(id),
                "terminate_process".to_string(),
                "system.process.terminate".to_string(),
                0.5,
                true,
            );

            info!("Process terminated: {} (id={})", proc.name, id);
            (StatusCode::OK, Json(proc.clone())).into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Process {} not found", id),
            }),
        )
            .into_response(),
    }
}

async fn change_priority(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
    Json(req): Json<ChangePriorityRequest>,
) -> impl IntoResponse {
    if req.priority < 1 || req.priority > 6 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ErrorResponse {
                error: "Priority must be between 1 and 6".to_string(),
            }),
        )
            .into_response();
    }

    let mut state_lock = state.write().await;
    match state_lock.processes.get_mut(&id) {
        Some(proc) => {
            let old_priority = proc.priority;
            proc.priority = req.priority;
            state_lock.rebuild_scheduler_queue();

            state_lock.add_audit_entry(
                Some(id),
                "change_priority".to_string(),
                "system.process.priority".to_string(),
                (req.priority as f64 - old_priority as f64).abs() * 0.1,
                true,
            );

            info!(
                "Process priority changed: id={}, from {} to {}",
                id, old_priority, req.priority
            );
            (StatusCode::OK, Json(proc.clone())).into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Process {} not found", id),
            }),
        )
            .into_response(),
    }
}

async fn suspend_process(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;
    match state_lock.processes.get_mut(&id) {
        Some(proc) => {
            if proc.status != ProcessStatus::Running {
                return (
                    StatusCode::CONFLICT,
                    Json(ErrorResponse {
                        error: format!("Process {} is not running", id),
                    }),
                )
                    .into_response();
            }
            proc.status = ProcessStatus::Suspended;
            state_lock.rebuild_scheduler_queue();

            state_lock.add_audit_entry(
                Some(id),
                "suspend_process".to_string(),
                "system.process.suspend".to_string(),
                0.2,
                true,
            );

            info!("Process suspended: {} (id={})", proc.name, id);
            (StatusCode::OK, Json(proc.clone())).into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Process {} not found", id),
            }),
        )
            .into_response(),
    }
}

async fn resume_process(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;
    match state_lock.processes.get_mut(&id) {
        Some(proc) => {
            if proc.status != ProcessStatus::Suspended {
                return (
                    StatusCode::CONFLICT,
                    Json(ErrorResponse {
                        error: format!("Process {} is not suspended", id),
                    }),
                )
                    .into_response();
            }
            proc.status = ProcessStatus::Running;
            state_lock.rebuild_scheduler_queue();

            state_lock.add_audit_entry(
                Some(id),
                "resume_process".to_string(),
                "system.process.resume".to_string(),
                0.1,
                true,
            );

            info!("Process resumed: {} (id={})", proc.name, id);
            (StatusCode::OK, Json(proc.clone())).into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Process {} not found", id),
            }),
        )
            .into_response(),
    }
}

// --- Sandbox Handlers ---

async fn list_sandboxes(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<Vec<Sandbox>> {
    let state_lock = state.read().await;
    let mut sandboxes: Vec<Sandbox> = state_lock.sandboxes.values().cloned().collect();
    sandboxes.sort_by_key(|s| s.level);
    Json(sandboxes)
}

async fn create_sandbox(
    State(state): State<Arc<RwLock<AppState>>>,
    Json(req): Json<CreateSandboxRequest>,
) -> impl IntoResponse {
    if req.level < 1 || req.level > 4 {
        return (
            StatusCode::BAD_REQUEST,
            Json(ErrorResponse {
                error: "Sandbox level must be between 1 and 4".to_string(),
            }),
        )
            .into_response();
    }

    let mut state_lock = state.write().await;

    let resource_limits = match req.level {
        1 => ResourceLimits {
            max_memory_mb: 1024,
            max_cpu_percent: 90.0,
            max_processes: 10,
            allowed_network: false,
            allowed_filesystem: false,
        },
        2 => ResourceLimits {
            max_memory_mb: 2048,
            max_cpu_percent: 70.0,
            max_processes: 20,
            allowed_network: true,
            allowed_filesystem: false,
        },
        3 => ResourceLimits {
            max_memory_mb: 4096,
            max_cpu_percent: 50.0,
            max_processes: 30,
            allowed_network: true,
            allowed_filesystem: true,
        },
        4 => ResourceLimits {
            max_memory_mb: 1024,
            max_cpu_percent: 25.0,
            max_processes: 10,
            allowed_network: true,
            allowed_filesystem: false,
        },
        _ => ResourceLimits::default(),
    };

    let sandbox = Sandbox {
        id: Uuid::new_v4(),
        level: req.level,
        process_ids: Vec::new(),
        permissions: req.permissions,
        resource_limits: req.resource_limits.unwrap_or(resource_limits),
    };

    state_lock.sandboxes.insert(sandbox.id, sandbox.clone());

    state_lock.add_audit_entry(
        None,
        "create_sandbox".to_string(),
        "system.sandbox.create".to_string(),
        0.4,
        true,
    );

    info!(
        "Sandbox created: id={}, level={}",
        sandbox.id, sandbox.level
    );
    (StatusCode::CREATED, Json(sandbox)).into_response()
}

async fn get_sandbox(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let state_lock = state.read().await;
    match state_lock.sandboxes.get(&id) {
        Some(sb) => (StatusCode::OK, Json(sb.clone())).into_response(),
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Sandbox {} not found", id),
            }),
        )
            .into_response(),
    }
}

async fn destroy_sandbox(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;
    match state_lock.sandboxes.remove(&id) {
        Some(sb) => {
            for proc_id in &sb.process_ids {
                if let Some(proc) = state_lock.processes.get_mut(proc_id) {
                    proc.status = ProcessStatus::Terminated;
                }
            }
            state_lock.rebuild_scheduler_queue();

            state_lock.add_audit_entry(
                None,
                "destroy_sandbox".to_string(),
                "system.sandbox.destroy".to_string(),
                0.6,
                false,
            );

            info!("Sandbox destroyed: id={}, level={}", id, sb.level);
            (StatusCode::OK, Json(sb)).into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Sandbox {} not found", id),
            }),
        )
            .into_response(),
    }
}

// --- Security Handlers ---

async fn get_security_events(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<Vec<SecurityEvent>> {
    let state_lock = state.read().await;
    let mut events = state_lock.security_events.clone();
    events.reverse();
    Json(events)
}

async fn list_active_threats(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<Vec<SecurityEvent>> {
    let state_lock = state.read().await;
    Json(state_lock.active_threats.clone())
}

async fn trigger_security_scan(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<ScanResult> {
    let start = std::time::Instant::now();
    let mut state_lock = state.write().await;

    let mut events_generated = 0;
    let mut threats_detected = 0;

    for process in state_lock.processes.values() {
        let anomaly_score = fastrand::u32(0..100);
        if anomaly_score > 85 {
            let event_type = if anomaly_score > 97 {
                EventType::Critical
            } else if anomaly_score > 93 {
                EventType::Threat
            } else if anomaly_score > 88 {
                EventType::Violation
            } else {
                EventType::Anomaly
            };

            let severity = match event_type {
                EventType::Critical => Severity::Critical,
                EventType::Threat => Severity::High,
                EventType::Violation => Severity::Medium,
                EventType::Anomaly => Severity::Low,
            };

            let description = format!(
                "[Scan] {} detected in process {} (score: {})",
                match event_type {
                    EventType::Anomaly => "Behavioral anomaly",
                    EventType::Threat => "Security threat",
                    EventType::Violation => "Permission violation",
                    EventType::Critical => "Critical security breach",
                },
                process.name,
                anomaly_score
            );

            let is_threat = event_type == EventType::Threat || event_type == EventType::Critical;

            if is_threat {
                threats_detected += 1;
            }

            state_lock.add_security_event(
                event_type,
                Some(process.id),
                severity,
                description,
                "Scan initiated - logged for review".to_string(),
                is_threat,
            );
            events_generated += 1;

            if event_type == EventType::Critical {
                state_lock.add_audit_entry(
                    Some(process.id),
                    "security_scan_critical".to_string(),
                    "system.security.scan".to_string(),
                    0.9,
                    true,
                );
            }
        }
    }

    let elapsed = start.elapsed().as_millis() as u64;

    info!(
        "Security scan complete: {} events, {} threats in {}ms",
        events_generated, threats_detected, elapsed
    );

    Json(ScanResult {
        events_generated,
        threats_detected,
        scan_duration_ms: elapsed,
        summary: format!(
            "Scan completed. {} anomalies detected, {} threats among them.",
            events_generated, threats_detected
        ),
    })
}

async fn respond_to_threat(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
    Json(req): Json<ThreatResponseRequest>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;

    let threat_index = state_lock.active_threats.iter().position(|t| t.id == id);
    match threat_index {
        Some(idx) => {
            let threat = &state_lock.active_threats[idx];
            let process_id = threat.process_id;

            let action_taken = match req.action.as_str() {
                "isolate" => {
                    if let Some(pid) = process_id {
                        if let Some(proc) = state_lock.processes.get_mut(&pid) {
                            proc.status = ProcessStatus::Suspended;
                        }
                    }
                    "Process isolated and suspended"
                }
                "terminate" => {
                    if let Some(pid) = process_id {
                        if let Some(proc) = state_lock.processes.get_mut(&pid) {
                            proc.status = ProcessStatus::Terminated;
                        }
                    }
                    "Process terminated"
                }
                "rollback" => {
                    if let Some(pid) = process_id {
                        if let Some(proc) = state_lock.processes.get_mut(&pid) {
                            proc.status = ProcessStatus::Suspended;
                        }
                    }
                    "Process suspended, system rollback recommended"
                }
                _ => {
                    return (
                        StatusCode::BAD_REQUEST,
                        Json(ErrorResponse {
                            error: "Invalid action. Use: isolate, terminate, or rollback".to_string(),
                        }),
                    )
                        .into_response();
                }
            };

            state_lock.active_threats.remove(idx);

            state_lock.add_security_event(
                EventType::Critical,
                process_id,
                Severity::High,
                format!("Threat response: {} for threat {}", action_taken, id),
                action_taken.to_string(),
                false,
            );

            state_lock.add_audit_entry(
                process_id,
                "respond_to_threat".to_string(),
                "system.security.respond".to_string(),
                0.8,
                true,
            );

            state_lock.rebuild_scheduler_queue();

            info!("Threat {} responded with action: {}", id, req.action);
            (
                StatusCode::OK,
                Json(serde_json::json!({
                    "threat_id": id.to_string(),
                    "action_taken": action_taken,
                })),
            )
                .into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Threat {} not found", id),
            }),
        )
            .into_response(),
    }
}

// --- Scheduler Handlers ---

async fn get_scheduler_status(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<SchedulerStatusResponse> {
    let state_lock = state.read().await;

    let mut sys = System::new_all();
    sys.refresh_cpu();
    sys.refresh_memory();

    let mut sorted: Vec<ScheduledProcess> = state_lock
        .scheduler_queue
        .clone()
        .into_sorted_vec();
    sorted.reverse();

    let queue: Vec<ScheduledProcessInfo> = sorted
        .into_iter()
        .map(|sp| ScheduledProcessInfo {
            process_id: sp.process_id,
            name: sp.name,
            priority: sp.priority,
            cpu_allocated: sp.cpu_allocated,
            memory_allocated: sp.memory_allocated,
        })
        .collect();

    let total_cpu: f64 = queue.iter().map(|p| p.cpu_allocated).sum();
    let total_mem: u64 = queue.iter().map(|p| p.memory_allocated).sum();

    Json(SchedulerStatusResponse {
        queue,
        total_cpu_allocated: total_cpu.min(100.0),
        total_memory_allocated: total_mem,
        system_cpu_usage: sys.global_cpu_info().cpu_usage() as f64,
        system_memory_usage: sys.used_memory() as f64,
        system_total_memory: sys.total_memory(),
        mode: format!("{:?}", state_lock.security_mode),
        focus_mode: state_lock.focus_mode,
    })
}

async fn trigger_scheduler_optimize(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<SchedulerStatusResponse> {
    let mut state_lock = state.write().await;

    let running_count = state_lock
        .processes
        .values()
        .filter(|p| p.status == ProcessStatus::Running)
        .count() as f64;

    if running_count > 0.0 {
        let base_cpu_per_process = 100.0 / running_count;
        let mut heap = BinaryHeap::new();

        for process in state_lock.processes.values() {
            if process.status == ProcessStatus::Running || process.status == ProcessStatus::Suspended {
                let cpu = if process.status == ProcessStatus::Suspended {
                    0.0
                } else {
                    base_cpu_per_process * (7.0 - process.priority as f64) / 6.0
                };

                heap.push(ScheduledProcess {
                    process_id: process.id,
                    priority: process.priority,
                    cpu_allocated: cpu,
                    memory_allocated: (process.priority as u64).saturating_mul(256),
                    name: process.name.clone(),
                });
            }
        }
        state_lock.scheduler_queue = heap;
    }

    state_lock.add_audit_entry(
        None,
        "scheduler_optimize".to_string(),
        "system.scheduler.optimize".to_string(),
        0.2,
        true,
    );

    info!("Scheduler optimization complete");
    drop(state_lock);
    get_scheduler_status(State(state)).await
}

// --- Snapshot Handlers ---

async fn list_snapshots(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<Vec<Snapshot>> {
    let state_lock = state.read().await;
    let mut snapshots = state_lock.snapshots.clone();
    snapshots.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
    Json(snapshots)
}

async fn create_snapshot(
    State(state): State<Arc<RwLock<AppState>>>,
    Json(req): Json<CreateSnapshotRequest>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;

    let services = req.services_included.unwrap_or_else(|| {
        vec![
            "security-core".to_string(),
            "orchestrator".to_string(),
            "memory-engine".to_string(),
            "app-runtime".to_string(),
            "agents".to_string(),
        ]
    });

    let snapshot_data = serde_json::to_value(&state_lock.processes).unwrap_or_default();
    let snapshot_size = snapshot_data.to_string().len() as u64;

    let snapshot = Snapshot {
        id: Uuid::new_v4(),
        timestamp: Utc::now(),
        description: req.description,
        services_included: services,
        size: snapshot_size,
        status: SnapshotStatus::Active,
        processes: state_lock.processes.clone(),
        sandboxes: state_lock.sandboxes.clone(),
    };

    state_lock.snapshots.push(snapshot.clone());

    state_lock.add_audit_entry(
        None,
        "create_snapshot".to_string(),
        "system.snapshot.create".to_string(),
        0.3,
        true,
    );

    info!("Snapshot created: id={}, desc={}", snapshot.id, snapshot.description);
    (StatusCode::CREATED, Json(snapshot)).into_response()
}

async fn rollback_snapshot(
    State(state): State<Arc<RwLock<AppState>>>,
    Path(id): Path<Uuid>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;

    let snapshot_idx = state_lock.snapshots.iter().position(|s| s.id == id);
    match snapshot_idx {
        Some(idx) => {
            let snapshot = state_lock.snapshots[idx].clone();

            if snapshot.status != SnapshotStatus::Active {
                return (
                    StatusCode::CONFLICT,
                    Json(ErrorResponse {
                        error: format!("Snapshot {} is not active (status: {:?})", id, snapshot.status),
                    }),
                )
                    .into_response();
            }

            state_lock.processes = snapshot.processes.clone();
            state_lock.sandboxes = snapshot.sandboxes.clone();
            state_lock.rebuild_scheduler_queue();

            state_lock.snapshots[idx].status = SnapshotStatus::RolledBack;

            state_lock.add_audit_entry(
                None,
                "rollback_snapshot".to_string(),
                "system.snapshot.rollback".to_string(),
                0.7,
                true,
            );

            info!("Rolled back to snapshot: id={}, desc={}", id, snapshot.description);
            (
                StatusCode::OK,
                Json(serde_json::json!({
                    "message": "Rollback completed successfully",
                    "snapshot_id": id.to_string(),
                    "processes_restored": snapshot.processes.len(),
                    "sandboxes_restored": snapshot.sandboxes.len(),
                })),
            )
                .into_response()
        }
        None => (
            StatusCode::NOT_FOUND,
            Json(ErrorResponse {
                error: format!("Snapshot {} not found", id),
            }),
        )
            .into_response(),
    }
}

// --- Audit Handlers ---

async fn get_audit_log(
    State(state): State<Arc<RwLock<AppState>>>,
) -> Json<Vec<AuditEntry>> {
    let state_lock = state.read().await;
    let mut log = state_lock.audit_log.clone();
    log.reverse();
    Json(log)
}

async fn create_audit_entry(
    State(state): State<Arc<RwLock<AppState>>>,
    Json(req): Json<CreateAuditEntryRequest>,
) -> impl IntoResponse {
    let mut state_lock = state.write().await;

    let entry = AuditEntry {
        id: Uuid::new_v4(),
        timestamp: Utc::now(),
        process_id: req.process_id,
        action: req.action,
        permission_used: req.permission_used,
        impact_score: req.impact_score,
        rollback_available: req.rollback_available,
    };

    state_lock.audit_log.push(entry.clone());

    info!(
        "Audit entry created: action={}, permission={}",
        entry.action, entry.permission_used
    );
    (StatusCode::CREATED, Json(entry)).into_response()
}

// ============================================================
// Main
// ============================================================

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "ichin_security_core=info,tower_http=info".into()),
        )
        .init();

    info!("Initializing ICHIN OS Security Core (Service 7)...");

    let state = Arc::new(RwLock::new(AppState::new()));

    let detector_state = state.clone();
    tokio::spawn(async move {
        security_detector_loop(detector_state).await;
    });

    let cors = tower_http::cors::CorsLayer::new()
        .allow_origin(tower_http::cors::Any)
        .allow_methods(tower_http::cors::Any)
        .allow_headers(tower_http::cors::Any);

    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/processes", get(list_processes).post(create_process))
        .route("/processes/:id", delete(terminate_process))
        .route("/processes/:id/priority", patch(change_priority))
        .route("/processes/:id/suspend", patch(suspend_process))
        .route("/processes/:id/resume", patch(resume_process))
        .route("/sandboxes", get(list_sandboxes).post(create_sandbox))
        .route("/sandboxes/:id", get(get_sandbox).delete(destroy_sandbox))
        .route("/security/events", get(get_security_events))
        .route("/security/scan", post(trigger_security_scan))
        .route("/security/threats", get(list_active_threats))
        .route("/security/threats/:id/respond", post(respond_to_threat))
        .route("/scheduler/status", get(get_scheduler_status))
        .route("/scheduler/optimize", post(trigger_scheduler_optimize))
        .route("/snapshots", get(list_snapshots).post(create_snapshot))
        .route("/snapshots/:id/rollback", post(rollback_snapshot))
        .route("/audit", get(get_audit_log).post(create_audit_entry))
        .layer(cors)
        .with_state(state);

    let addr = "0.0.0.0:8017";
    info!("ICHIN Security Core listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
