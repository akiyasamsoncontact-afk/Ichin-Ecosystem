use alloc::collections::VecDeque;
use alloc::string::{String, ToString};

pub struct Snapshot {
    pub id: u64,
    pub label: String,
    pub process_count: usize,
    pub memory_used: u64,
}

pub struct RollbackSystem {
    snapshots: VecDeque<Snapshot>,
    next_id: u64,
    pub rollback_count: u64,
}

impl RollbackSystem {
    pub fn new() -> Self { RollbackSystem { snapshots: VecDeque::new(), next_id: 1, rollback_count: 0 } }
    pub fn init(&mut self) {
        self.snapshots.push_back(Snapshot { id: 0, label: "initial".into(), process_count: 0, memory_used: 0 });
    }
    pub fn take(&mut self, label: &str, pc: usize, mem: u64) -> u64 {
        let id = self.next_id; self.next_id += 1;
        self.snapshots.push_back(Snapshot { id, label: label.to_string(), process_count: pc, memory_used: mem });
        if self.snapshots.len() > 50 { self.snapshots.pop_front(); }
        id
    }
    pub fn rollback_to(&mut self, id: u64) -> Option<&Snapshot> {
        let pos = self.snapshots.iter().position(|s| s.id == id)?;
        self.snapshots.truncate(pos + 1);
        self.rollback_count += 1;
        self.snapshots.back()
    }
    pub fn list(&self) -> Vec<&Snapshot> { self.snapshots.iter().rev().collect() }
    pub fn count(&self) -> usize { self.snapshots.len() }
}
