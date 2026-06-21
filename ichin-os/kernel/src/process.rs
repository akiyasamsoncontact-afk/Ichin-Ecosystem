use alloc::collections::BTreeMap;
use alloc::string::{String, ToString};
use alloc::sync::Arc;
use alloc::vec::Vec;
use spin::Mutex;
use core::sync::atomic::{AtomicU64, Ordering};

pub type Pid = u64;
static NEXT_PID: AtomicU64 = AtomicU64::new(1);

#[derive(Debug, Clone, PartialEq)]
pub enum ProcessState {
    Ready,
    Running,
    Blocked(BlockReason),
    Suspended,
    Terminated,
    Zombie,
}

#[derive(Debug, Clone, PartialEq)]
pub enum BlockReason {
    WaitingIpc,
    WaitingIo,
    Sleeping(u64),
}

#[derive(Debug, Clone, PartialEq)]
pub enum Priority {
    RealTime = 0,
    High = 1,
    Normal = 2,
    Low = 3,
    Idle = 4,
    Background = 5,
}

impl Priority {
    pub fn value(&self) -> u8 {
        match self {
            Priority::RealTime => 0,
            Priority::High => 1,
            Priority::Normal => 2,
            Priority::Low => 3,
            Priority::Idle => 4,
            Priority::Background => 5,
        }
    }
    pub fn from_u8(v: u8) -> Self {
        match v { 0 => Priority::RealTime, 1 => Priority::High, 2 => Priority::Normal, 3 => Priority::Low, 4 => Priority::Idle, _ => Priority::Background }
    }
}

#[derive(Debug, Clone)]
pub struct Process {
    pub pid: Pid,
    pub parent_pid: Option<Pid>,
    pub name: String,
    pub state: ProcessState,
    pub priority: Priority,
    pub cpu_time: u64,
    pub sandbox_level: u8,
    pub focus_level: u8,
    pub children: Vec<Pid>,
    pub rsp: u64,
    pub cr3: u64,
}

impl Process {
    pub fn new(name: &str, priority: Priority, sandbox_level: u8) -> Self {
        let pid = NEXT_PID.fetch_add(1, Ordering::SeqCst);
        Process {
            pid,
            parent_pid: None,
            name: name.to_string(),
            state: ProcessState::Ready,
            priority,
            cpu_time: 0,
            sandbox_level,
            focus_level: 0,
            children: Vec::new(),
            rsp: 0,
            cr3: 0,
        }
    }
    pub fn is_alive(&self) -> bool {
        !matches!(self.state, ProcessState::Terminated | ProcessState::Zombie)
    }
    pub fn block(&mut self, reason: BlockReason) { self.state = ProcessState::Blocked(reason); }
    pub fn unblock(&mut self) { self.state = ProcessState::Ready; }
}

pub struct ProcessManager {
    processes: BTreeMap<Pid, Arc<Mutex<Process>>>,
    count: usize,
}

impl ProcessManager {
    pub fn new() -> Self { ProcessManager { processes: BTreeMap::new(), count: 0 } }
    pub fn init(&mut self) {
        let idle = Process::new("idle", Priority::Idle, 0);
        self.spawn(idle);
    }
    pub fn spawn(&mut self, process: Process) -> Pid {
        let pid = process.pid;
        self.processes.insert(pid, Arc::new(Mutex::new(process)));
        self.count += 1;
        pid
    }
    pub fn get(&self, pid: Pid) -> Option<Arc<Mutex<Process>>> {
        self.processes.get(&pid).cloned()
    }
    pub fn kill(&mut self, pid: Pid) -> bool {
        self.processes.get(&pid).map(|p| { p.lock().state = ProcessState::Terminated; true }).unwrap_or(false)
    }
    pub fn cleanup(&mut self) {
        let dead: Vec<Pid> = self.processes.iter()
            .filter(|(_, p)| matches!(p.lock().state, ProcessState::Zombie))
            .map(|(pid, _)| *pid).collect();
        for pid in dead { self.processes.remove(&pid); self.count -= 1; }
    }
    pub fn count(&self) -> usize { self.count }
    pub fn list(&self) -> Vec<(Pid, String, String, u64)> {
        self.processes.iter().map(|(pid, p)| {
            let proc = p.lock();
            (*pid, proc.name.clone(), format!("{:?}", proc.state), proc.cpu_time)
        }).collect()
    }
}
