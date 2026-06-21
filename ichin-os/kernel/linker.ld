ENTRY(kmain)

PHDRS
{
  text    PT_LOAD    FLAGS((1 << 0) | (1 << 2));
  rodata  PT_LOAD    FLAGS((1 << 2));
  data    PT_LOAD    FLAGS((1 << 1) | (1 << 2));
  dynamic PT_DYNAMIC FLAGS((1 << 1) | (1 << 2));
}

SECTIONS
{
  . = 0xffffffff80000000 + SIZEOF_HEADERS;

  .text : {
    *(.text .text.*)
  } :text

  . = ALIGN(4K);
  .rodata : {
    *(.rodata .rodata.*)
  } :rodata

  . = ALIGN(4K);
  .data : {
    *(.data .data.*)
  } :data

  .dynamic : {
    *(.dynamic)
  } :data :dynamic

  .bss : {
    *(.bss .bss.*)
    *(COMMON)
  } :data

  /DISCARD/ : {
    *(.eh_frame)
    *(.note .note.*)
  }
}
