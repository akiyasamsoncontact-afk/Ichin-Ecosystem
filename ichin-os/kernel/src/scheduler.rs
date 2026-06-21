use alloc::collections::VecDeque;
use crate::process::{ProcessManager, Priority};

pub struct Scheduler {
    queues: [VecDeque<u64>; 6],
    current_pid: Option<u64>,
    pub total_switches: u64,
    pub idle_ticks: u64,
    pub time_slice: u64,
}

impl Scheduler {
    pub fn new() -> Self {
        Scheduler {
            queues: Default::default(),
            current_pid: None,
            total_switches: 0,
            idle_ticks: 0,
            time_slice: 50,
        }
    }
    pub fn init(&mut self) {}
    pub fn enqueue(&mut self, pid: u64, priority: &Priority) {
        self.queues[priority.value() as usize].push_back(pid);
    }
    pub fn dequeue(&mut self, pid: u64) {
        for q in &mut self.queues { q.retain(|&p| p != pid); }
    }
    pub fn tick(&mut self, procs: &ProcessManager) {
        for level in 0..6 {
            while let Some(pid) = self.queues[level].pop_front() {
                if let Some(proc_arc) = procs.get(pid) {
                    let mut proc = proc_arc.lock();
                    if proc.is_alive() && proc.state == crate::process::ProcessState::Ready {
                        proc.state = crate::process::ProcessState::Running;
                        proc.cpu_time += 1;
                        self.current_pid = Some(pid);
                        self.total_switches += 1;
                        return;
                    }
                }
            }
        }
        self.idle_ticks += 1;
        self.current_pid = None;
    }
    pub fn boost(&mut self, pid: u64) {
        for l in 0..6 {
            if let Some(pos) = self.queues[l].iter().position(|&p| p == pid) {
                let p = self.queues[l].remove(pos).unwrap();
                self.queues[(l as isize - 1).max(0) as usize].push_front(p);
                break;
            }
        }
    }
    pub fn throttle(&mut self, pid: u64) {
        for l in 0..6 {
            if let Some(pos) = self.queues[l].iter().position(|&p| p == pid) {
                let p = self.queues[l].remove(pos).unwrap();
                self.queues[(l + 1).min(5)].push_back(p);
                break;
            }
        }
    }
}
