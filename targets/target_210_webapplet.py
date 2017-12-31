from targets.base_210_wk import Gadgets210Wk, Functions210Wk
from targets.base_210_webapplet import Gadgets210Webapplet, Functions210Webapplet, Dataptrs210Webapplet
from targets import target_200_webauth


class Gadgets(Gadgets210Wk, Gadgets210Webapplet):
    pass


class Functions(Functions210Wk, Functions210Webapplet):
    pass


class Dataptrs(Dataptrs210Webapplet):
    pass


class Rop(target_200_webauth.Rop):
    G = Gadgets()
    F = Functions()
    D = Dataptrs()
