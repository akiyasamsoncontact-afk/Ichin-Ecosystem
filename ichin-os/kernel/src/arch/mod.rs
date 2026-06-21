pub mod gdt;
pub mod idt;
pub mod paging;
pub mod serial;

use x86_64::instructions::port::Port;

pub fn init() {
    gdt::init();
    idt::init();
    serial::init();
}

pub fn outb(port: u16, value: u8) {
    unsafe { Port::new(port).write(value); }
}

pub fn inb(port: u16) -> u8 {
    unsafe { Port::new(port).read() }
}

pub fn io_wait() {
    outb(0x80, 0);
}

pub fn hlt_forever() -> ! {
    loop {
        x86_64::instructions::hlt();
    }
}
