use alloc::collections::BTreeMap;
use alloc::string::{String, ToString};

pub struct Service {
    pub id: u8,
    pub name: String,
    pub port: u16,
    pub running: bool,
    pub healthy: bool,
}

pub struct ServiceManager {
    services: BTreeMap<u8, Service>,
    pub healthy_count: u8,
}

impl ServiceManager {
    pub fn new() -> Self {
        let mut services = BTreeMap::new();
        for (id, name, port) in [
            (1, "orchestrator", 8011u16), (2, "agents", 8012), (3, "memory-engine", 8013),
            (4, "ui-system", 8014), (5, "app-runtime", 8015), (6, "ai-studio", 8016),
            (7, "security-core", 8017), (8, "system-daemon", 7010),
        ] {
            services.insert(id, Service { id, name: name.to_string(), port, running: false, healthy: false });
        }
        ServiceManager { services, healthy_count: 0 }
    }
    pub fn init(&mut self) {}
    pub fn start(&mut self, id: u8) -> bool {
        self.services.get_mut(&id).map(|s| { s.running = true; s.healthy = true; self.healthy_count += 1; true }).unwrap_or(false)
    }
    pub fn stop(&mut self, id: u8) -> bool {
        self.services.get_mut(&id).map(|s| { s.running = false; s.healthy = false; self.healthy_count -= 1; true }).unwrap_or(false)
    }
    pub fn status(&self) -> alloc::vec::Vec<(u8, String, bool)> {
        self.services.values().map(|s| (s.id, s.name.clone(), s.healthy)).collect()
    }
}
