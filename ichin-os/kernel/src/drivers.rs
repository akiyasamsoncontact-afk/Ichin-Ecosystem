use alloc::vec::Vec;
use alloc::string::{String, ToString};

pub enum DeviceClass { Storage, Network, Input, Display, Audio, Serial, Block, Misc }

pub struct Device {
    pub name: String,
    pub class: DeviceClass,
    pub irq: u32,
    pub enabled: bool,
}

pub struct DriverManager {
    pub devices: Vec<Device>,
}

impl DriverManager {
    pub fn new() -> Self { DriverManager { devices: Vec::new() } }
    pub fn init(&mut self) {
        self.probe("ichin-serial", DeviceClass::Serial, 4);
        self.probe("ichin-block", DeviceClass::Block, 14);
        self.probe("ichin-input", DeviceClass::Input, 1);
        self.probe("ichin-display", DeviceClass::Display, 0);
    }
    pub fn probe(&mut self, name: &str, class: DeviceClass, irq: u32) {
        self.devices.push(Device {
            name: name.to_string(), class, irq, enabled: true,
        });
    }
    pub fn count(&self) -> usize { self.devices.len() }
}
