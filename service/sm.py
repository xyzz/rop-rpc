from __future__ import print_function
from service import Service
from rop import Rop, data_base, main_base, wk_base, F, G, D, Ret
from ipc import *

class SM(Service):
    #def initialize(self, unk_zero):
    #    # srv::Initialize
    #    obj = self.client.r64(D.srv_objptr)
    #    return self.client.cv(obj, 0x20, unk_zero)

    def get_service(self, name):
        # srv::GetService
        out = self.client.malloc(8)
        if out == 0:
            print('[-] malloc failed')
            return
        ret = self.client.c(F.srv_GetServiceHandle, out, name)
        if ret != 0:
            print('[-] sm:GetService failed (0x%X)' % ret)
            self.client.free(out)
            return
        handle = self.client.r32(out)
        print('[+] Handle', handle)
        self.client.free(out)
        return handle

    def _name2u64(self, name):
        if len(name) > 8:
            raise Exception('wrong name')
        buf = self.client.calloc(1, 8)
        if buf == 0:
            raise Exception('malloc failed')
        self.client.w(buf, name)
        out = self.client.r64(buf)
        self.client.free(buf)
        return out

    def register_service(self, name, max_sessions=1000):
        # srv::RegisterService
        try:
            name_u64 = self._name2u64(name)
        except Exception as e:
            print('[-]', e.message)
            return

        cmd = IpcCmd(2)
        cmd.add_raw_64(name_u64)
        # just use 0x20 for is_light
        # copied from pegaswitch
        cmd.add_raw_32(0x20)
        cmd.add_raw_32(max_sessions)
        cmd.add_raw_64(0xFFFFFFFFFFFFFFFF)
        cmd.add_raw_64(0xFFFFFFFFFFFFFFFF)
        cmd.add_raw_64(0xFFFFFFFFFFFFFFFF)
        cmd.add_raw_64(0xFFFFFFFFFFFFFFFF)

        try:
            ret = cmd.execute(self.membase + 0x1000, self.client, self.handle)
        except Exception as e:
            print('[-]', e.message)
            return
        if ret.get('rc') != 0:
            print('[-] sm:RegisterService failed (0x%X)' % ret.get('rc'))
            return
        handle = ret.get('handles')[0]
        print('[+] Handle', handle)
        return handle

    def unregister_service(self, name):
        # srv::UnregisterService
        try:
            name_u64 = self._name2u64(name)
        except Exception as e:
            print('[-]', e.message)
            return
        ret = self.client.cmd(self.handle, 3, name_u64).get('rc')
        if ret != 0:
            print('[-] sm:UnregisterService failed (0x%X)' % ret)
        return ret
