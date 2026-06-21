use x86_64::structures::paging::{
    FrameAllocator, Mapper, Page, PageTable, PhysFrame, Size4KiB,
    OffsetPageTable, page::PageRange,
};
use x86_64::{PhysAddr, VirtAddr};
use linked_list_allocator::LockedHeap;

pub const PAGE_SIZE: u64 = 4096;

pub struct PagingManager {
    pub mapper: OffsetPageTable<'static>,
    pub allocator: BootInfoFrameAllocator,
    pub heap_allocator: LockedHeap,
}

impl PagingManager {
    pub fn new(phys_mem_offset: VirtAddr, memory_map: &'static limine::MemmapResponse) -> Self {
        let level4_table = unsafe {
            let p4 = &mut *(phys_mem_offset.as_mut_ptr::<PageTable>());
            p4
        };
        let mapper = unsafe { OffsetPageTable::new(level4_table, phys_mem_offset) };
        let allocator = BootInfoFrameAllocator::new(memory_map);
        PagingManager {
            mapper,
            allocator,
            heap_allocator: LockedHeap::empty(),
        }
    }

    pub fn init_heap(&mut self, heap_start: VirtAddr, heap_size: u64) {
        let page_range = {
            let heap_end = heap_start + heap_size;
            Page::range(
                Page::containing_address(heap_start),
                Page::containing_address(heap_end),
            )
        };
        for page in page_range {
            let frame = self.allocator.allocate_frame().expect("no frames for heap");
            let flags = x86_64::structures::paging::PageTableFlags::PRESENT
                | x86_64::structures::paging::PageTableFlags::WRITABLE;
            unsafe {
                self.mapper
                    .map_to(page, frame, flags, &mut self.allocator)
                    .expect("heap mapping failed")
                    .flush();
            }
        }
        unsafe {
            self.heap_allocator.lock().init(
                heap_start.as_mut_ptr(),
                heap_size as usize,
            );
        }
    }
}

pub struct BootInfoFrameAllocator {
    memory_map: &'static limine::MemmapResponse,
    next: usize,
}

impl BootInfoFrameAllocator {
    pub fn new(memory_map: &'static limine::MemmapResponse) -> Self {
        BootInfoFrameAllocator { memory_map, next: 0 }
    }
}

unsafe impl FrameAllocator<Size4KiB> for BootInfoFrameAllocator {
    fn allocate_frame(&mut self) -> Option<PhysFrame<Size4KiB>> {
        let entries = self.memory_map.entries();
        let usable = entries.iter().filter(|e| {
            e.ty == limine::MemoryEntryType::Usable
        });
        for entry in usable {
            let base = entry.base;
            let length = entry.length;
            let frame_count = length / PAGE_SIZE;
            if self.next < frame_count as usize {
                let addr = PhysAddr::new(base + (self.next as u64 * PAGE_SIZE));
                self.next += 1;
                return Some(PhysFrame::containing_address(addr));
            }
            self.next -= frame_count as usize;
        }
        None
    }
}
