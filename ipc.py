from __future__ import print_function
import struct

class IpcCmd:
    def __init__(self, cmdid, debug=False):
        self.cmdid = cmdid
        self.debug = debug
        self.x = []
        self.a = []
        self.b = []
        self.c = []
        self.handles = []
        self.x_ctr = 0
        self.pid = False
        self.type = 4

        self.raw = ''
        self.add_raw_64(0x49434653)
        self.add_raw_64(cmdid)

        self.recv_handles = []

    def add_raw_64(self, val):
        self.raw += struct.pack('<Q', val)
    def add_raw_32(self, val):
        self.raw += struct.pack('<I', val)
    def add_handle(self, h):
        self.handles.append(h)
    def send_pid(self):
        self.pid = True

    def _add_ab(self, buf, size, flags, type):
        flags |= ((buf >> 32) & 0xF) << 28;
        flags |= ((buf >> 36) & 0x7) << 2;
        low_size = size & 0xFFFFFFFF
        low_addr = buf & 0xFFFFFFFF
        if type == 'a':
            self.a.append(struct.pack('<III', low_size, low_addr, flags))
        else:
            self.b.append(struct.pack('<III', low_size, low_addr, flags))

    def _add_x(self, buf, size):
        flags = self.x_ctr | (((buf >> 32) & 0xF) << 12) | (size << 16)
        flags |= (((buf >> 36) & 0x7) << 6)
        self.x_ctr += 1
        self.x.append(struct.pack('<II', flags, buf & 0xFFFFFFFF))

    def _add_c(self, buf, size): # Must be called after all other add_raw* calls.
        self.add_raw_32(size & 0xFFFF)
        flags = (((buf >> 32) & 0xFFFF)) | (size << 16)
        #word0 = 0x5 #size
        self.c.append(struct.pack('<II', buf & 0xFFFFFFFF, flags)) #originally III

    def add_4_1(self, buf, size):
        return self._add_ab(buf, size, 0, 'a')
    def add_40_4_1(self, buf, size):
        return self._add_ab(buf, size, 1, 'a')
    def add_80_4_1(self, buf, size):
        return self._add_ab(buf, size, 3, 'a')
    def add_4_2(self, buf, size):
        return self._add_ab(buf, size, 0, 'b')
    def add_40_4_2(self, buf, size):
        return self._add_ab(buf, size, 1, 'b')
    def add_80_4_2(self, buf, size):
        return self._add_ab(buf, size, 3, 'b')

    def add_8_1(self, buf, size):
        return self._add_x(buf, size)

    def add_8_2(self, buf, size):
        return self._add_c(buf, size)

    def set_type(self, t):
        self.type = t

    def _construct(self):
        header_flags = self.type

        # 0, 1, 2 seems to be doing nothing
        # 3 is kernel highway
        # 5 is control
        header_flags |= len(self.x) << 16
        header_flags |= len(self.a) << 20
        header_flags |= len(self.b) << 24

        c_bufs = ''.join(self.c)

        size = len(self.a)*3 + len(self.b)*3 + len(self.x)*2
        size += 2 + len(self.raw)/4
        #print len(self.raw)

        if (len(self.handles) > 0) or self.pid:
            size += 1
            size += len(self.handles)
            size += 2 if self.pid else 0
            size |= (1<<31)

        if (len(self.c) > 0):
            size |= 0x3 << 10
            #c_bufs = '\x00'*0x4 + c_bufs #0xc

        header = ''
        header += struct.pack('<I', header_flags)
        header += struct.pack('<I', size)

        if (len(self.handles) > 0) or self.pid:
            extra = 1 if self.pid else 0
            extra |= len(self.handles) << 1

            header += struct.pack('<I', extra)

            if self.pid:
                header += struct.pack('<II', 0, 0)

            for h in self.handles:
                header += struct.pack('<I', h)

        x_bufs = ''.join(self.x)
        a_bufs = ''.join(self.a)
        b_bufs = ''.join(self.b)
        header += x_bufs + a_bufs + b_bufs

        header += '\x00' * ((16-(len(header)%16)) % 16)

        return header + self.raw + c_bufs

    def _dump_response(self, c, cmdbuf):
        cmd1 = c.r32(cmdbuf+4)

        size = 4 * (cmd1 & 0x3FF) + 8
        if cmd1 & 0x80000000:
            size += 4
            handle_desc = c.r32(cmdbuf+8)

            if handle_desc & 1:
                size += 8

            size += (((handle_desc >> 1) & 0xF) + ((handle_desc >> 5) & 0xF)) * 4

        cmd = c.r(cmdbuf, size)

        self._debug_print('__ Raw: _____')
        c.x(cmdbuf, size, self._debug_print)

        self.pid = None

        if cmd1 & 0x80000000:
            handle_desc = c.r32(cmdbuf+8)
            start = 0

            if handle_desc & 1:
                self.pid = c.r32(cmdbuf+12)
                start = 2

            num_handles_copy = (handle_desc >> 1) & 0xF
            num_handles_move = (handle_desc >> 5) & 0xF
            num_handles = num_handles_copy+num_handles_move

            self._debug_print('__ Handles: ___')
            for i in range(start, num_handles_copy + start):
                handle = c.r32(cmdbuf+12+i*4)
                self._debug_print('  [Copied] Handle 0x%x' % handle)
                self.recv_handles.append(handle)
            for i in range(num_handles_copy + start, num_handles + start):
                handle = c.r32(cmdbuf+12+i*4)
                self._debug_print('  [Moved] Handle 0x%x' % handle)
                self.recv_handles.append(handle)

        pos = cmd.find('SFCO')
        ret = None

        if pos != -1:
            ret = cmd[pos+8 : pos+8+4]
            self._debug_print('__ Return ___')
            if len(ret) > 0:
                ret = struct.unpack('<I', ret)[0]
                self._debug_print('0x%x' % ret)
            else:
                self._debug_print('(void)')
        self.recv_ret = ret

        self.recv_raw = cmd[pos:]
        recv_data_len = 4 * (cmd1 & 0x3FF) - 0x10
        self.recv_data = cmd[pos+16:pos+recv_data_len]

    def execute(self, cmdbuf, c, h, fast=False):
        c.w(cmdbuf, self._construct())
        #self._dump_response(c, cmdbuf)
        #c.x(cmdbuf, 0x100)

        rc = c.svcSendSyncRequestWithUserBuffer(cmdbuf, 0x1000, h)
        if rc != 0:
            c.svcCloseHandle(h)
            raise Exception("Failed: %x" % rc)

        if not fast:
            self._dump_response(c, cmdbuf)
            return {
                "rc": self.recv_ret,
                "handles": self.recv_handles,
                "pid": self.pid,
                "raw": self.recv_raw,
                "data": self.recv_data,
            }

    def _debug_print(self, *args):
        if self.debug:
            print(*args)
