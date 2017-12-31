from util import isint


class Relocatable():

    data = 1
    main = 2
    wk = 3

    def __init__(self, tag, imm):
        self.tag = tag
        self.imm = imm

    def __add__(self, x):
        if not isint(x):
            raise RuntimeError("cannot __add__ a {}".format(x))
        return Relocatable(self.tag, self.imm + x)

    def __sub__(self, x):
        if not isint(x):
            raise RuntimeError("cannot __sub__ a {}".format(x))
        return Relocatable(self.tag, self.imm - x)

    def __repr__(self):
        return "Relocable<tag={}, imm=0x{:x}>".format(self.tag, self.imm)

data_base = Relocatable(Relocatable.data, 0)
main_base = Relocatable(Relocatable.main, 0)
wk_base = Relocatable(Relocatable.wk, 0)
