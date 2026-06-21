use alloc::collections::BTreeMap;
use alloc::string::{String, ToString};
use alloc::vec::Vec;

pub struct Inode {
    pub id: u64,
    pub name: String,
    pub is_dir: bool,
    pub size: u64,
    pub children: Vec<u64>,
    pub data: Vec<u8>,
}

pub struct VirtualFileSystem {
    inodes: BTreeMap<u64, Inode>,
    next_id: u64,
    root: u64,
}

impl VirtualFileSystem {
    pub fn new() -> Self {
        VirtualFileSystem { inodes: BTreeMap::new(), next_id: 1, root: 0 }
    }
    pub fn init(&mut self) {
        self.inodes.insert(0, Inode {
            id: 0, name: String::new(), is_dir: true, size: 0, children: Vec::new(), data: Vec::new(),
        });
        self.root = 0;
        self.mkdir("/dev", 0);
        self.mkdir("/proc", 0);
        self.mkdir("/sys", 0);
        self.mkdir("/tmp", 0);
        self.mkdir("/home", 0);
    }
    fn resolve(&self, path: &str) -> Option<u64> {
        if path == "/" { return Some(self.root); }
        let trimmed = path.trim_start_matches('/').trim_end_matches('/');
        if trimmed.is_empty() { return Some(self.root); }
        let parts: Vec<&str> = trimmed.split('/').collect();
        let mut current = self.root;
        for part in parts {
            let inode = self.inodes.get(&current)?;
            if !inode.is_dir { return None; }
            current = inode.children.iter().find_map(|&cid| {
                self.inodes.get(&cid).and_then(|c| if c.name == part { Some(cid) } else { None })
            })?;
        }
        Some(current)
    }
    pub fn mkdir(&mut self, path: &str, _uid: u32) -> Result<u64, ()> {
        let parent = path.rsplit_once('/').map(|(p, _)| p).unwrap_or("/");
        let name = path.rsplit_once('/').map(|(_, n)| n).unwrap_or(path);
        let parent_id = self.resolve(parent).ok_or(())?;
        let id = self.next_id; self.next_id += 1;
        self.inodes.insert(id, Inode { id, name: name.to_string(), is_dir: true, size: 0, children: Vec::new(), data: Vec::new() });
        self.inodes.get_mut(&parent_id).unwrap().children.push(id);
        Ok(id)
    }
    pub fn create(&mut self, path: &str) -> Result<u64, ()> {
        let parent = path.rsplit_once('/').map(|(p, _)| p).unwrap_or("/");
        let name = path.rsplit_once('/').map(|(_, n)| n).unwrap_or(path);
        let parent_id = self.resolve(parent).ok_or(())?;
        let id = self.next_id; self.next_id += 1;
        self.inodes.insert(id, Inode { id, name: name.to_string(), is_dir: false, size: 0, children: Vec::new(), data: Vec::new() });
        self.inodes.get_mut(&parent_id).unwrap().children.push(id);
        Ok(id)
    }
    pub fn write(&mut self, path: &str, data: Vec<u8>) -> Result<(), ()> {
        let id = self.resolve(path).ok_or(())?;
        self.inodes.get_mut(&id).map(|n| { n.data = data; n.size = n.data.len() as u64; }).ok_or(())
    }
    pub fn read(&self, path: &str) -> Result<Vec<u8>, ()> {
        let id = self.resolve(path).ok_or(())?;
        self.inodes.get(&id).map(|n| n.data.clone()).ok_or(())
    }
    pub fn ls(&self, path: &str) -> Result<Vec<String>, ()> {
        let id = self.resolve(path).ok_or(())?;
        let inode = self.inodes.get(&id).ok_or(())?;
        if !inode.is_dir { return Err(()); }
        Ok(inode.children.iter().filter_map(|cid| self.inodes.get(cid).map(|c| c.name.clone())).collect())
    }
    pub fn total_inodes(&self) -> usize { self.inodes.len() }
}
