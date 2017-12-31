import struct

from rop import F, G, Rop, data_base
from rpc import RPC_RESPONSE_LEN
from util import u64

class FunctionHelper:

    def __init__(self, ch):
        self.ch = ch
        self.funcs = dict()
        for x in dir(F):
            if not x.startswith("__"):
                self.funcs[x] = getattr(F, x)

    def __getattr__(self, name):
        def f(*args, **kwargs):
            return self.call(name, *args, **kwargs)
        return f

    def call(self, func, *args, **kwargs):
        if type(func) in [str, unicode]:
            if func in self.funcs:
                func = self.funcs[func]
            else:
                raise RuntimeError("unknown function {}".format(func))

        return_regs = kwargs.get("regs", False)
        if "regs" in kwargs:
            del kwargs["regs"]

        args = list(args)

        rop = Rop()
        for x, arg in enumerate(args):
            if type(arg) is str:
                args[x] = rop.awrites(arg)

        rop.call(func, *args, **kwargs)

        r0_off = RPC_RESPONSE_LEN - 8
        jmp_buf_off = RPC_RESPONSE_LEN - 0x1000
        # if user asked for return_regs, we use setjmp to retrieve them
        # this is useful for syscalls because they can return values in multiple regs
        if return_regs:
            rop.dump_regs(data_base + jmp_buf_off, and_store_r0=data_base + r0_off)
        else:
            # NB: we store return address as the last qword that switch replies to us, to ensure minimum conflicts with other code
            rop.store_ret(data_base + r0_off)
        
        data = self.ch.execute(rop)
        self.ch.mem = data

        ret = u64(data, r0_off)

        if return_regs:
            regs = {"x0": ret} # this one's special
            for x in range(1, 31):
                regs["x{}".format(x)] = u64(data, jmp_buf_off + 8 * x)

            return regs

        return ret
