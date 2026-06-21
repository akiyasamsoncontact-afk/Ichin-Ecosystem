use crate::process::ProcessManager;
use crate::scheduler::Scheduler;
use crate::memory::MemoryManager;
use crate::ipc::IpcManager;
use crate::fs::VirtualFileSystem;
use crate::drivers::DriverManager;
use crate::sandbox::SandboxEngine;
use crate::rollback::RollbackSystem;
use crate::services::ServiceManager;
use crate::syscall::SyscallHandler;

pub struct IchinKernel {
    pub processes: ProcessManager,
    pub scheduler: Scheduler,
    pub memory: MemoryManager,
    pub ipc: IpcManager,
    pub vfs: VirtualFileSystem,
    pub drivers: DriverManager,
    pub sandbox: SandboxEngine,
    pub rollback: RollbackSystem,
    pub services: ServiceManager,
    pub syscalls: SyscallHandler,
    pub ticks: u64,
}

static mut KERNEL_STARTED: bool = false;

impl IchinKernel {
    pub fn new() -> Self {
        IchinKernel {
            processes: ProcessManager::new(),
            scheduler: Scheduler::new(),
            memory: MemoryManager::new(),
            ipc: IpcManager::new(),
            vfs: VirtualFileSystem::new(),
            drivers: DriverManager::new(),
            sandbox: SandboxEngine::new(),
            rollback: RollbackSystem::new(),
            services: ServiceManager::new(),
            syscalls: SyscallHandler::new(),
            ticks: 0,
        }
    }

    pub fn init(&mut self) {
        crate::kprintln!("[ICHIN] Boot stage 1: CPU init complete");
        crate::kprintln!("[ICHIN] Boot stage 2: Memory init");
        self.processes.init();
        self.scheduler.init();
        self.ipc.init();
        self.vfs.init();
        self.drivers.init();
        self.sandbox.init();
        self.rollback.init();
        self.services.init();
        self.syscalls.init();
        crate::kprintln!("[ICHIN] Boot stage 3: All subsystems ready");
        crate::kprintln!("[ICHIN] Boot stage 4: Starting ICHIN services...");
        for id in 1..=8 {
            self.services.start(id);
            crate::kprint!(".");
        }
        crate::kprintln!();
        crate::kprintln!("[ICHIN] Boot stage 5: Kernel ready");
        unsafe { KERNEL_STARTED = true; }
    }

    pub fn tick(&mut self) {
        self.ticks += 1;
        self.scheduler.tick(&self.processes);
        self.processes.cleanup();
        if self.ticks % 100 == 0 {
            self.rollback.take("auto", self.processes.count(), 0);
        }
    }

    pub fn status<'a>(&'a self) -> alloc::string::String {
        alloc::format!(
            "ICHIN Kernel | ticks:{} procs:{} sched_sw:{} idle:{} ipc_msgs:{} vfs_inodes:{} drivers:{} services_ok:{} rollbacks:{} syscalls:{}",
            self.ticks, self.processes.count(), self.scheduler.total_switches, self.scheduler.idle_ticks,
            self.ipc.total_messages, self.vfs.total_inodes(), self.drivers.count(),
            self.services.healthy_count, self.rollback.rollback_count, self.syscalls.total_calls,
        )
    }
}
