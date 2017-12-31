from relocatable import wk_base


class Gadgets100Wk:
    # 0x0000000000001554 : ldp x29, x30, [sp, #0x50] ; ldp x20, x19, [sp, #0x40] ; ldp x22, x21, [sp, #0x30] ; ldp x24, x23, [sp, #0x20] ; ldp x26, x25, [sp, #0x10] ; ldp x28, x27, [sp], #0x60 ; ret

    # 0x00000000008f0c94 : mov x0, x23 ; mov x1, x19 ; mov x2, x22 ; mov x3, x21 ; mov x4, x20 ; blr x8

    # mov x1, x19 ; mov x2, x22 ; mov x3, x21 ; mov x4, x20 ; blr x8

    # 0x0000000000f6befc : mov x5, x21 ; mov x6, x20 ; mov x7, x19 ; str x27, [sp, #0x10] ; str w28, [sp, #8] ; str x24, [sp] ; blr x8

    # 0x000000000074bb60 : mov x8, x21 ; mov x0, x20 ; mov x1, x19 ; blr x22

    # 0x000000000071db4c : blr x20 ; ldr w8, [x19, #0x400] ; sub w8, w8, #1 ; str w8, [x19, #0x400] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret

    # 0x00000000000001bc : ret

    # 0x000000000001e170 : str x0, [x19] ; ldp x29, x30, [sp, #0x10] ; ldr x19, [sp], #0x20 ; ret

    # 0x000000000092ef48 : ldr x0, [x20] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret

    # 0x0000000000d01bdc : str x19, [x20] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret


class Functions100Wk:
    pass
