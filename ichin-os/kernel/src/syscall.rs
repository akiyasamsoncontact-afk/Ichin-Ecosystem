use alloc::collections::BTreeMap;
use crate::arch::serial;
use crate::process::{ProcessManager, Priority};

pub enum Syscall {
    Exit = 1, GetPid = 8, Kill = 9, SchedYield = 16, GetTime = 15,
    IpcSend = 12, IpcRecv = 13, Shutdown = 17,
}

pub struct SyscallHandler {
    pub total_calls: u64,
}

impl SyscallHandler {
    pub fn new() -> Self { SyscallHandler { total_calls: 0 } }
    pub fn init(&mut self) {}
    pub fn handle(&mut self, number: u64, args: &[u64; 6], pid: u64) -> i64 {
        self.total_calls += 1;
        match number {
            1 => { serial::write(b"sys_exit\n"); 0 }
            8 => pid as i64,
            15 => core::time::Duration::ZERO.as_millis() as i64,
            16 => 0,
            17 => 0,
            _ => { serial::write_fmt(format_args!("unknown syscall {}\n", number)); -1 }
        }
    }
}
