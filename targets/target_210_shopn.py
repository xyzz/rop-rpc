from targets.base_210_wk import Gadgets210Wk, Functions210Wk
from targets.base_210_shopn import Gadgets210Shopn, Functions210Shopn, Dataptrs210Shopn
from targets import target_200_webauth


class Gadgets(Gadgets210Wk, Gadgets210Shopn):
    pass


class Functions(Functions210Wk, Functions210Shopn):
    pass


class Dataptrs(Dataptrs210Shopn):
    pass


class Rop(target_200_webauth.Rop):
    G = Gadgets()
    F = Functions()
    D = Dataptrs()
