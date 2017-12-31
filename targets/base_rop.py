from relocatable import data_base, Relocatable
from util import isint, u64
import struct


Ret = object()


class BaseRop:
    _call_funcs = dict()

    def __init__(self):
        self.rop = []
        self.amem_off = data_base + 0x4000
        self.scratch = self.alloc(0x10) # scratch mem - stored X0

    def call(self, func, *args, **kwargs):
        """ Generic call function that will do argument matching and execute a proper call* handler """
        # Generate argument signature
        sig = ""
        for arg in args:
            if isint(arg) or isinstance(arg, Relocatable):
                sig += "v"
            elif arg is Ret:
                sig += "r"
            else:
                raise RuntimeError("unsupported function argument: {}".format(arg))
        for match, f in self._call_funcs.items():
            if match.startswith(sig):
                return f(self, func, *args, **kwargs)
        raise RuntimeError("didn't match sig: {} for args: {}".format(sig, args))

    def alloc(self, sz):
        ret = self.amem_off
        self.amem_off += sz
        while self.amem_off.imm % 8 != 0:
            self.amem_off += 1
        return ret

    def awrite(self, data):
        """ automem write: "allocate" memory in data section and write into it """
        while len(data) % 8 != 0:
            data += "\x00"
        mem = self.alloc(len(data))
        for x in range(len(data) / 8):
            self.write64(u64(data, 8 * x), mem + 8 * x)
        return mem

    def awrites(self, s):
        """ same as above but for strings """
        return self.awrite(s + "\x00")


    # Ropchain generation functions
    def generate_binary(self, relocs):
        """ Generate a ROP chain with relocs applied """
        output = [0] # NB: PC is *second* pointer in output
        for qword in self.rop:
            if isint(qword):
                output.append(qword)
            elif isinstance(qword, Relocatable):
                output.append(qword.imm + relocs[qword.tag])
            else:
                raise RuntimeError("unknown qword: {}".format(qword))
        return "".join(struct.pack("<Q", x) for x in output)

    def js_array(self, arr):
        return "[" + (",".join("0x{:x}".format(x) for x in arr)) + "]"

    def generate_js(self):
        """
            Generates JS code: ropchain and relocs arrays
            Note: For JS we generate arrays where each item is 4 bytes, because JS cannot work with 8 bytes.
            As such you need to work on qword-level in JS. (see exploit.js)
        """
        rop_chain = []
        rop_relocs = []

        rop = [0] + self.rop[:] # NB: PC is *second* pointer in output

        for qword in rop:
            if isint(qword):
                reloc = 0
            elif isinstance(qword, Relocatable):
                reloc = qword.tag
                qword = qword.imm
            else:
                raise RuntimeError("unknown qword: {}".format(qword))
            rop_chain.append(qword & 0xFFFFFFFF) # lo
            rop_chain.append(qword >> 32) # hi
            rop_relocs.append(reloc)
            rop_relocs.append(0)

        js = "rop_chain = {};\nrop_relocs = {};\n".format(self.js_array(rop_chain), self.js_array(rop_relocs))
        return js

    def size(self):
        return 8 * len(self.rop)
