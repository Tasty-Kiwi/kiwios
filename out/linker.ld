ENTRY(_start)

SECTIONS
{
  /* Start loading the kernel at 2MB */
  . = 2M;

  /* Code section: multiboot header and .text */
  .text : ALIGN(4K)
  {
    KEEP(*(.multiboot))   /* Multiboot header must not be stripped */
    *(.text .text.*)
  }

  /* Read-only data */
  .rodata : ALIGN(4K)
  {
    *(.rodata .rodata.*)
  }

  /* Initialized data */
  .data : ALIGN(4K)
  {
    *(.data .data.*)
  }

  /* Uninitialized data (BSS and COMMON) */
  .bss : ALIGN(4K)
  {
    *(.bss .bss.*)
    *(COMMON)
  }

  /* Optional: discard unwanted sections */
  /DISCARD/ :
  {
    *(.comment)
    *(.note*)
    *(.eh_frame)
  }
}
