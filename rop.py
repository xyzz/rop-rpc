import struct

from relocatable import data_base, main_base, wk_base
from targets.base_rop import Ret


def target_select():
    from targets import target_100_webapplet, target_200_webauth, target_210_shopn, target_210_webapplet
    from config import target

    selector = {
        "100_webapplet": target_100_webapplet,
        "200_webauth": target_200_webauth,
        "210_shopn": target_210_shopn,
        "210_webapplet": target_210_webapplet,
    }
    if target not in selector:
        raise Exception("unknown target {}".format(target))

    return selector[target]


t = target_select()
Rop, G, F, D = t.Rop, t.Gadgets(), t.Functions(), t.Dataptrs()
t = None
