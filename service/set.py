from __future__ import print_function
from service import Service
from rop import Rop, data_base, main_base, wk_base, F, G, D, Ret
from ipc import *

class Sys(Service):
    def get_mii_author_id(self):
        try:
            out = self.client.cmd(self.handle, 90)
        except Exception as e:
            print('[-] set:sys:GetMiiAuthorId failed')
            print('[-] ', e.message)
            return
        ids = struct.unpack('>QQ', out['data'])
        ret = (ids[0] << 64) | ids[1]
        return '%X' % ret
