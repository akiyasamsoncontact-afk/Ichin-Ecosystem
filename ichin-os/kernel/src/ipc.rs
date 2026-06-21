use alloc::collections::{BTreeMap, VecDeque};
use alloc::vec::Vec;

pub type ChannelId = u64;

#[derive(Clone)]
pub struct Message {
    pub sender: u64,
    pub receiver: u64,
    pub channel: ChannelId,
    pub data: Vec<u8>,
}

#[derive(Clone)]
pub struct Channel {
    pub id: ChannelId,
    pub owner: u64,
    pub subscribers: Vec<u64>,
    pub queue: VecDeque<Message>,
}

pub struct IpcManager {
    channels: BTreeMap<ChannelId, Channel>,
    next_id: ChannelId,
    pub total_messages: u64,
}

impl IpcManager {
    pub fn new() -> Self {
        IpcManager { channels: BTreeMap::new(), next_id: 1, total_messages: 0 }
    }
    pub fn init(&mut self) {
        self.create_channel(0, u64::MAX);
    }
    pub fn create_channel(&mut self, id_hint: ChannelId, owner: u64) -> ChannelId {
        let id = if id_hint != 0 { id_hint } else { self.next_id };
        self.next_id = self.next_id.max(id + 1);
        self.channels.insert(id, Channel {
            id, owner, subscribers: Vec::new(), queue: VecDeque::new(),
        });
        id
    }
    pub fn subscribe(&mut self, channel: ChannelId, pid: u64) -> bool {
        self.channels.get_mut(&channel).map(|c| { c.subscribers.push(pid); true }).unwrap_or(false)
    }
    pub fn send(&mut self, sender: u64, receiver: u64, channel: ChannelId, data: Vec<u8>) -> bool {
        self.channels.get_mut(&channel).map(|c| {
            c.queue.push_back(Message { sender, receiver, channel, data });
            self.total_messages += 1;
            true
        }).unwrap_or(false)
    }
    pub fn recv(&mut self, pid: u64) -> Option<Message> {
        for (_, ch) in &mut self.channels {
            if let Some(pos) = ch.queue.iter().position(|m| m.receiver == pid || m.receiver == u64::MAX) {
                return ch.queue.remove(pos);
            }
        }
        None
    }
    pub fn broadcast(&mut self, sender: u64, channel: ChannelId, data: Vec<u8>) -> usize {
        self.channels.get_mut(&channel).map(|c| {
            let count = c.subscribers.len();
            for &sub in &c.subscribers.clone() {
                c.queue.push_back(Message { sender, receiver: sub, channel, data: data.clone() });
            }
            self.total_messages += count as u64;
            count
        }).unwrap_or(0)
    }
    pub fn pending(&self, pid: u64) -> usize {
        self.channels.values().flat_map(|c| &c.queue)
            .filter(|m| m.receiver == pid || m.receiver == u64::MAX).count()
    }
    pub fn channel_count(&self) -> usize { self.channels.len() }
}
