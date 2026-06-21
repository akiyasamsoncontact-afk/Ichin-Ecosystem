use alloc::vec::Vec;
use x86_64::VirtAddr;
use x86_64::structures::paging::{
    FrameAllocator, Mapper, Page, PageTableFlags, PhysFrame, Size4KiB,
};
use spin::Mutex;

const HEAP_SIZE: u64 = 16 * 1024 * 1024;

pub struct MemoryManager {
    heap_start: VirtAddr,
    pages_used: u64,
    pages_total: u64,
}

impl MemoryManager {
    pub fn new() -> Self {
        MemoryManager {
            heap_start: VirtAddr::new(0xFFFF_9000_0000_0000),
            pages_used: 0,
            pages_total: 0,
        }
    }

    pub fn init<A: FrameAllocator<Size4KiB>, M: Mapper<Size4KiB>>(
        &mut self,
        mapper: &mut M,
        allocator: &mut A,
    ) -> Result<(), &'static str> {
        let page_range = {
            let heap_end = self.heap_start + HEAP_SIZE;
            let start_page = Page::containing_address(self.heap_start);
            let end_page = Page::containing_address(heap_end);
            Page::range(start_page, end_page)
        };
        self.pages_total = page_range.clone().count() as u64;

        for page in page_range {
            let frame = allocator.allocate_frame().ok_or("failed to allocate frame")?;
            let flags = PageTableFlags::PRESENT | PageTableFlags::WRITABLE;
            unsafe {
                mapper
                    .map_to(page, frame, flags, allocator)
                    .map_err(|_| "mapping failed")?
                    .flush();
            }
            self.pages_used += 1;
        }
        Ok(())
    }

    pub fn usage(&self) -> (u64, u64) {
        (self.pages_used, self.pages_total)
    }
}

pub static MEMORY_MANAGER: Mutex<Option<MemoryManager>> = Mutex::new(None);

pub fn init_heap() {
    // Heap init happens after paging
}
