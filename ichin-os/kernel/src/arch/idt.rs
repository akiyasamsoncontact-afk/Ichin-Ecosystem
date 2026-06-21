use x86_64::structures::idt::{InterruptDescriptorTable, InterruptStackFrame, PageFaultErrorCode};
use spin::Lazy;
use crate::arch::serial;

static IDT: Lazy<InterruptDescriptorTable> = Lazy::new(|| {
    let mut idt = InterruptDescriptorTable::new();
    idt.breakpoint.set_handler_fn(breakpoint_handler);
    idt.page_fault.set_handler_fn(page_fault_handler);
    idt.double_fault.set_handler_fn(double_fault_handler);
    idt.general_protection_fault.set_handler_fn(gpf_handler);
    idt.divide_error.set_handler_fn(divide_error_handler);
    idt.invalid_opcode.set_handler_fn(invalid_opcode_handler);
    idt.stack_segment_fault.set_handler_fn(stack_segment_handler);
    unsafe {
        idt[32].set_handler_fn(timer_handler);
        idt[33].set_handler_fn(keyboard_handler);
    }
    idt
});

pub fn init() {
    IDT.load();
    serial::write(b"IDT installed\n");
}

extern "x86-interrupt" fn breakpoint_handler(frame: InterruptStackFrame) {
    serial::write(b"BREAKPOINT\n");
}

extern "x86-interrupt" fn page_fault_handler(
    frame: InterruptStackFrame,
    error_code: PageFaultErrorCode,
) {
    use x86_64::registers::control::Cr2;
    let addr = Cr2::read();
    serial::write_fmt(format_args!(
        "PAGE FAULT: addr={:?}, error={:?}\n", addr, error_code
    ));
    loop { x86_64::instructions::hlt(); }
}

extern "x86-interrupt" fn double_fault_handler(
    frame: InterruptStackFrame,
    error_code: u64,
) -> ! {
    serial::write(b"DOUBLE FAULT\n");
    loop { x86_64::instructions::hlt(); }
}

extern "x86-interrupt" fn gpf_handler(frame: InterruptStackFrame, error_code: u64) {
    serial::write_fmt(format_args!("GPF: error={}\n", error_code));
}

extern "x86-interrupt" fn divide_error_handler(frame: InterruptStackFrame) {
    serial::write(b"DIVIDE BY ZERO\n");
}

extern "x86-interrupt" fn invalid_opcode_handler(frame: InterruptStackFrame) {
    serial::write(b"INVALID OPCODE\n");
}

extern "x86-interrupt" fn stack_segment_handler(frame: InterruptStackFrame, error_code: u64) {
    serial::write_fmt(format_args!("STACK SEGMENT FAULT: {}\n", error_code));
}

extern "x86-interrupt" fn timer_handler(_frame: InterruptStackFrame) {
    unsafe { crate::KERNEL_TICKS += 1; }
    crate::arch::outb(0x20, 0x20);
}

extern "x86-interrupt" fn keyboard_handler(_frame: InterruptStackFrame) {
    let scancode = crate::arch::inb(0x60);
    crate::arch::outb(0x20, 0x20);
    unsafe { crate::LAST_SCANCODE = scancode; }
}
