use alloc::collections::BTreeMap;
use alloc::vec::Vec;
use alloc::string::String;

pub enum SandboxLevel { Unrestricted = 0, Low = 1, Medium = 2, High = 3, Maximum = 4 }

pub struct SandboxEngine {
    process_levels: BTreeMap<u64, u8>,
    pub audit_log: Vec<(u64, String, bool)>,
}

impl SandboxEngine {
    pub fn new() -> Self { SandboxEngine { process_levels: BTreeMap::new(), audit_log: Vec::new() } }
    pub fn init(&mut self) {}
    pub fn assign(&mut self, pid: u64, level: u8) { self.process_levels.insert(pid, level.min(4)); }
    pub fn check(&self, pid: u64, _action: &str) -> bool { self.process_levels.get(&pid).copied().unwrap_or(4) < 3 }
    pub fn audit(&mut self, pid: u64, action: String, allowed: bool) { self.audit_log.push((pid, action, allowed)); }
    pub fn policy_count(&self) -> usize { 5 }
}
