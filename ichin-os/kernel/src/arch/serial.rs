use spin::Mutex;
use core::fmt;

static SERIAL: Mutex<Option<uart_16550::SerialPort>> = Mutex::new(None);

pub fn init() {
    let mut serial_port = unsafe { uart_16550::SerialPort::new(0x3F8) };
    serial_port.init();
    *SERIAL.lock() = Some(serial_port);
}

pub fn write(data: &[u8]) {
    if let Some(ref mut port) = *SERIAL.lock() {
        for &byte in data {
            port.send(byte);
        }
    }
}

pub fn write_str(s: &str) {
    write(s.as_bytes());
}

pub fn write_fmt(args: fmt::Arguments) {
    use core::fmt::Write;
    if let Some(ref mut port) = *SERIAL.lock() {
        let _ = port.write_fmt(args);
    }
}

impl fmt::Write for uart_16550::SerialPort {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        for byte in s.bytes() {
            self.send(byte);
        }
        Ok(())
    }
}

#[macro_export]
macro_rules! kprint {
    ($($arg:tt)*) => ($crate::arch::serial::write_fmt(format_args!($($arg)*)));
}

#[macro_export]
macro_rules! kprintln {
    () => ($crate::kprint!("\n"));
    ($($arg:tt)*) => ($crate::kprint!("{}\n", format_args!($($arg)*)));
}
