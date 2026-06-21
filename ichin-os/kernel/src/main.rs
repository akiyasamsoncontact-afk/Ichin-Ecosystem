#![no_std]
#![no_main]
#![feature(alloc_error_handler)]
#![feature(abi_x86_interrupt)]

extern crate alloc;

mod arch;
mod memory;
mod process;
mod scheduler;
mod ipc;
mod fs;
mod drivers;
mod sandbox;
mod rollback;
mod services;
mod syscall;
mod kernel;

use core::panic::PanicInfo;
use limine::{BaseRevision, MemmapRequest, FramebufferRequest};
use kernel::IchinKernel;
use spin::Mutex;
use arch::serial;

static BASE_REVISION: BaseRevision = BaseRevision::new();
static MEMMAP: MemmapRequest = MemmapRequest::new();
static FRAMEBUFFER: FramebufferRequest = FramebufferRequest::new();

pub static KERNEL_TICKS: core::sync::atomic::AtomicU64 = core::sync::atomic::AtomicU64::new(0);
pub static LAST_SCANCODE: core::sync::atomic::AtomicU8 = core::sync::atomic::AtomicU8::new(0);

static KERNEL: Mutex<Option<IchinKernel>> = Mutex::new(None);

#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    serial::write(b"KERNEL PANIC: ");
    serial::write_fmt(format_args!("{}", info));
    loop { x86_64::instructions::hlt(); }
}

#[alloc_error_handler]
fn alloc_error(layout: &core::alloc::Layout) -> ! {
    serial::write(b"ALLOC ERROR: ");
    serial::write_fmt(format_args!("{:?}", layout));
    loop { x86_64::instructions::hlt(); }
}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    serial::init();
    serial::write(b"\n=== ICHIN OS Kernel v0.1 ===\n");

    // Validate limine protocol
    if !BASE_REVISION.is_supported() {
        serial::write(b"ERROR: Limine protocol not supported\n");
        loop { x86_64::instructions::hlt(); }
    }

    // Enable interrupts and init CPU
    arch::gdt::init();
    arch::idt::init();
    x86_64::instructions::interrupts::enable();
    serial::write(b"GDT/IDT installed, interrupts enabled\n");

    // Initialize kernel subsystems
    let mut kernel = IchinKernel::new();
    kernel.init();

    // Main kernel loop
    loop {
        for _ in 0..10000 {
            x86_64::instructions::hlt();
        }
        kernel.tick();

        // Status every ~1000 ticks
        if kernel.ticks % 1000 == 0 {
            let s = kernel.status();
            serial::write(s.as_bytes());
            serial::write(b"\n");
        }
    }
}
