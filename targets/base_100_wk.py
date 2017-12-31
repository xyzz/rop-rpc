from relocatable import wk_base


class Gadgets100Wk:
    # 0x0000000000001554 : ldp x29, x30, [sp, #0x50] ; ldp x20, x19, [sp, #0x40] ; ldp x22, x21, [sp, #0x30] ; ldp x24, x23, [sp, #0x20] ; ldp x26, x25, [sp, #0x10] ; ldp x28, x27, [sp], #0x60 ; ret
    pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30 = wk_base + 0x1554

    # 0x00000000008f0c94 : mov x0, x23 ; mov x1, x19 ; mov x2, x22 ; mov x3, x21 ; mov x4, x20 ; blr x8
    mov_x0_x23_mov_x1_x19_mov_x2_x22_mov_x3_x21_mov_x4_x20_blr_x8 = wk_base + 0x8f0c94

    # mov x1, x19 ; mov x2, x22 ; mov x3, x21 ; mov x4, x20 ; blr x8
    mov_x1_x19_mov_x2_x22_mov_x3_x21_mov_x4_x20_blr_x8 = wk_base + 0x8f0c98

    # 0x0000000000f6befc : mov x5, x21 ; mov x6, x20 ; mov x7, x19 ; str x27, [sp, #0x10] ; str w28, [sp, #8] ; str x24, [sp] ; blr x8
    mov_x5_x21_mov_x6_x20_mov_x7_x19_trash_stack_blr_x8 = wk_base + 0xf6befc

    # 0x000000000074bb60 : mov x8, x21 ; mov x0, x20 ; mov x1, x19 ; blr x22
    mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22 = wk_base + 0x74bb60

    # 0x000000000071db4c : blr x20 ; ldr w8, [x19, #0x400] ; sub w8, w8, #1 ; str w8, [x19, #0x400] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret
    blr_x20_trash_mem_pop_x20_x19_x29_x30 = wk_base + 0x71db4c

    # 0x00000000000001bc : ret
    ret = wk_base + 0x1bc

    # 0x000000000001e170 : str x0, [x19] ; ldp x29, x30, [sp, #0x10] ; ldr x19, [sp], #0x20 ; ret
    str_x0_x19_pop_x19_0_x29_x30 = wk_base + 0x1e170

    # 0x000000000092ef48 : ldr x0, [x20] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret
    ldr_x0_x20_pop_x20_x19_x29_x30 = wk_base + 0x92ef48

    # 0x0000000000d01bdc : str x19, [x20] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret
    str_x19_x20_pop_x20_x19_x29_x30 = wk_base + 0xd01bdc

    pop_x29_x30 = wk_base + 0x234

class Functions100Wk:
    pass
