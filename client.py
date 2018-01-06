#!/usr/bin/env python2

from __future__ import print_function
import random
import socket
import pickle
import shlex
import datetime
import struct
import os

from server import ipc_port
from rop import Rop, data_base, main_base, wk_base, F, G, D, Ret
from util import p16, p32, u32, u64, hexdump, perm_to_str, c_str
from functionhelper import FunctionHelper
from rpc import RPC_SCRATCH_SIZE, RPC_RESPONSE_LEN
from ipc import *

class Client():
    def __init__(self):
        self.fh = FunctionHelper(self)
        self.n = 0

    def execute(self, rop):
        """
        Executes a ROP cmd and returns return buffer. Return buffer can be
        accessed in ROP via data_buffer. Note that last 0x100 bytes of return
        buffer can be used for scratch purposes. For example, function helper
        uses them to store return value of a function. As such, you should not
        use them when using function helper.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", ipc_port))
        obj = pickle.dumps(rop)
        s.send(p32(len(obj)))
        s.send(obj)

        data_len = u32(s.recv(4))
        data = s.recv(data_len, socket.MSG_WAITALL)
        s.close()

        return data

    def x(self, addr, length=0x100):
        self.fh.memcpy(data_base, addr, length)
        data = self.mem[0:length]
        print(hexdump(data, start=addr))

    def r(self, addr, length=1):
        self.fh.memcpy(data_base, addr, length)
        data = self.mem[0:length]
        return data

    def r_big(self, addr, length):
        ret = ''
        while length > 0:
            rem = 0x1000 if length >= 0x1000 else length
            ret += self.r(addr, rem)
            addr += rem
            length -= rem
        return ret

    def r32(self, addr):
        return struct.unpack('<I', self.r(addr, 4))[0]

    def r64(self, addr):
        return struct.unpack('<Q', self.r(addr, 8))[0]

    def memset(self, addr, val, size):
        return self.c(F.memset, addr, val, size)

    def w_big(self, addr, data):
        ret = ''
        length = len(data)
        while length > 0:
            rem = 0x800 if length >= 0x800 else length
            self.w(addr, data[:rem])
            data = data[rem:]
            addr += rem
            length -= rem
        return ret

    def w(self, addr, data):
        rop = Rop()
        src = rop.awrite(data)
        rop.call(F.memcpy, addr, src, len(data))
        self.execute(rop)

    def w32(self, addr, value):
        return self.w(addr, struct.pack('<I', value))

    def w64(self, addr, value):
        return self.w(addr, struct.pack('<Q', value))

    def wf(self, addr, fn):
        buf = open(fn, 'rb').read()
        for i in range((len(buf)+0xFF)/0x100):
            self.w(addr + i*0x100, buf[i*0x100 : (i+1)*0x100])

    def c(self, addr, x0=0, x1=0, x2=0, x3=0, x4=0, x5=0, x6=0, regdump=False):
        return self.fh.call(addr, x0, x1, x2, x3, x4, x5, x6, regs=regdump)

    def c_x8(self, addr, x8, regdump=False):
        return self.fh.call(addr, x8=x8, regs=regdump)

    def c_x0_x8(self, addr, x0, x8, regdump=False):
        return self.fh.call(addr, x0, x8=x8, regs=regdump)

    def cv(self, this, off, a0=0, a1=0, a2=0, a3=0, a4=0, a5=0, a6=0):
        vt = self.r64(this)
        fn = self.r64(vt+off)
        return self.c(fn, this, a0, a1, a2, a3, a4, a5, a6)

    def malloc(self, size):
        return self.c(F.malloc, size)

    def calloc(self, num, size):
        return self.c(F.calloc, num, size)

    def realloc(self, ptr, size):
        return self.c(F.realloc, ptr, size)

    def free(self, ptr):
        return self.c(F.free, ptr)

    def alloc_str(self, s):
        s += '\0'
        ptr = self.malloc(len(s))
        self.w(ptr, s)
        return ptr

    def bases(self):
        """ Ok this is done in a kinda roundabout way but whatever """
        rop = Rop()
        rop.write64(data_base, data_base + 0)
        rop.write64(main_base, data_base + 8)
        rop.write64(wk_base, data_base + 0x10)
        data = self.execute(rop)
        buf_base = u64(data, 0) - 0x10000

        print("Static memory: 0x{:x} (You can use it between different calls)".format(buf_base))
        print("Main binary base: 0x{:x}".format(u64(data, 8)))
        print("Webkit base: 0x{:x}".format(u64(data, 0x10)))

    def get_bases(self):
        rop = Rop()
        rop.write64(data_base, data_base + 0)
        rop.write64(main_base, data_base + 8)
        rop.write64(wk_base, data_base + 0x10)
        data = self.execute(rop)
        buf_base = u64(data, 0) - 0x10000
        return [buf_base, u64(data, 8)]

    def _dump_region(self, base, size, filename):
        """ Dump memory area [base, base+size) to filename """
        whole = size
        sent = 0
        with open(filename, "wb") as fout:
            while size > 0:
                chunk = min(size, RPC_RESPONSE_LEN - RPC_SCRATCH_SIZE)
                self.fh.memcpy(data_base, base, chunk)
                data = self.mem[0:chunk]
                size -= chunk
                base += chunk
                sent += chunk

                print("{:.2f}%".format(100.0 * sent / whole))

                fout.write(data)

    def query(self, addr, detail=False):
        regs = self.fh.svcQueryMemory(data_base, data_base + 0x100, addr, regs=True)
        base =  u64(self.mem, 0)
        size =  u64(self.mem, 8)
        state = u32(self.mem, 0x10)
        attr =  u32(self.mem, 0x14)
        perm =  u64(self.mem, 0x18)
        unk1 =  u32(self.mem, 0x1C)
        unk2 =  u32(self.mem, 0x20)
        unk3 =  u32(self.mem, 0x24)
        pageinfo = regs["x1"] & 0xFFFFFFFF

        perm_str = ''
        perm_str += 'R' if (perm & 1) else ' '
        perm_str += 'W' if (perm & 2) else ' '
        perm_str += 'X' if (perm & 4) else ' '

        type_map = {
            0: 'UNMAPPED',
            1: 'IO',
            2: 'STATIC',
            3: 'CODE RO',
            4: 'CODE RW',
            5: 'HEAP',
            6: 'SHAREDMEM',
            7: 'WEIRDMAP',
            8: 'MODULE RO',
            9: 'MODULE RW',
            0xB: 'MAPPED',
            0xC: 'TLS',
            0xD: 'WEIRDSHARED',
            0xE: 'TRANSFERMEM',
            0xF: 'PROCESS',
            0x10: 'RESERVED'
        }

        attr_str = ''
        if attr & 1:
            attr_str += 'MIRORRED '
        if attr & 2:
            attr_str += '!!UNK!! '
        if attr & 4:
            attr_str += 'DEVICEMAPPED '
        if attr & 8:
            attr_str += 'UNCACHED '

        if state != 0:
            print('[%s] 0x%010x-0x%010x size=0x%010x [%s] %s' % (perm_str, base, base+size-1, size, type_map[state], attr_str))
            if unk1 != 0:
                print('  !!Unk1!!:   0x%x' % unk1)
            if unk2 != 0:
                print('  Unk2:   0x%x' % unk2)
            if unk3 != 0:
                print('  !!Unk3!!:   0x%x' % unk3)
            if pageinfo != 0:
                print('  Info:   0x%x' % pageinfo)

        if not detail:
            return base + size

        return [base + size, (perm_str, base, size, type_map[state], attr_str)]

    def q(self, addr):
        return self.query(addr)

    def maps(self, dump=False, host_path=""):
        cur = 0
        while cur < 2 ** 64:
            cur, info = self.query(cur, detail=True)
            if not dump:
                continue
            perm, base, size, ty, attr = info
            if perm[0] != 'R':
                continue
            fn_fmt = "0x{base:016X}-0x{end:016X}_{perm}_{type}.bin"
            filename = fn_fmt.format(base=base, end=base+size-1, perm=perm, type=ty)
            self._dump_region(base, size, os.path.join(host_path, filename))

    def space(self):
        maps = []

        cur = 0
        while cur < 2 ** 64:
            regs = self.fh.svcQueryMemory(data_base, data_base + 0x100, cur, regs=True)
            base = u64(self.mem, 0)
            size = u64(self.mem, 8)
            perm = u64(self.mem, 0x18)
            state = u64(self.mem, 0x10)
            pageinfo = regs["x1"] & 0xFFFFFFFF # or at self.mem + 0x100

            maps.append({
                'base': base,
                'size': size,
                'perm': perm,
                'state': state,
                'pageinfo': pageinfo
            })
            cur += size

        return maps

    def dump_all(self, host_path):
        self.maps(True, host_path)

    def dump_file(self, src, dst):
        """ Download file `src` from switch to `dst` """
        fin = self.fh.fopen(src, "rb")
        if not fin:
            print("failed to open '{}' for dump".format(src))
            return
        print('fopen success')
        fout = open(dst, "wb")
        while True:
            ret = self.fh.fread(data_base, 1, RPC_RESPONSE_LEN - RPC_SCRATCH_SIZE, fin)
            if ret == 0:
                break
            fout.write(self.mem[0:ret])
        self.fh.fclose(fin)
        fout.close()

    def write_file(self, dst, src):
        """ Upload file `dst` to switch from `src` """
        fin = open(src, "rb")
        fout = self.fh.fopen(dst, "wb")
        if not fout:
            print("failed to open '{}' for write".format(dst))
            return
        print('fopen success')
        while True:
            filedata = fin.read(0x1000)
            if len(filedata) == 0:
                break
            self.w_big(mem+0x2000, filedata)
            ret = self.fh.fwrite(mem+0x2000, 1, len(filedata), fout)
            if ret == 0:
                print("File write failed.")
                break
            if ret < len(filedata):
                print("Only 0x%x of 0x%x bytes were written, aborting." % (ret, len(filedata)))
                break
        self.fh.fclose(fout)
        fin.close()

    def list_dir(self, path, recursive=False, dump_files=False, host_path="", prefix=""):
        if dump_files:
            os.mkdir(host_path)
        ret = self.fh.OpenDirectory(data_base, path, 3)
        if ret != 0:
            print("failed to open '{0}', error={1}=0x{1:x}".format(path, ret))
            return
        handle = u64(self.mem, 0)
        while True:
            self.fh.ReadDirectory(data_base, data_base + 0x200, handle, 1)
            ret = u64(self.mem, 0)
            if ret != 1:
                break

            entry = self.mem[0x200:0x200 + 0x310]
            is_file = u32(entry, 0x304) & 1
            name = c_str(entry, 0)
            print("{}{}{}".format(prefix, name, "/" if not is_file else ""))
            fullpath = "{}/{}".format(path, name)
            if dump_files and is_file:
                self.dump_file(fullpath, os.path.join(host_path, name))
            if recursive and not is_file and ('emoji' not in name):
                self.list_dir(fullpath, recursive, dump_files, os.path.join(host_path, name), prefix + "-")
        self.fh.CloseDirectory(handle)

    def dump_dir(self, src_path, dst_path, recursive=True):
        self.list_dir(src_path, recursive, True, dst_path)

    # 0x01
    def svcSetHeapSize(self, out, size):
        return self.c(F.svcSetHeapSize, out, size)
    # 0x02
    def svcSetMemoryPermission(self, addr, size, perm):
        return self.c(F.svcSetMemoryPermission, addr, size, perm)
    # 0x03
    # TODO: recheck second argument.
    # http://switchbrew.org/index.php?title=SVC#svcSetMemoryAttribute
    def svcSetMemoryAttribute(self, addr, end_addr, state0, state1):
        return self.c(F.svcSetMemoryAttribute, addr, end_addr, state0, state1)
    # 0x04
    def svcMapMemory(self, dst, src, size):
        return self.c(F.svcMapMemory, dst, src, size)
    # 0x05
    def svcUnmapMemory(self, dst, src, size):
        return self.c(F.svcUnmapMemory, dst, src, size)
    # 0x06
    # ...
    # 0x08
    def svcCreateThread(self, handle_out, entry, arg, stack_top, thread_prio, processor_id=0xFFFFFFFE):
        return self.c(F.svcCreateThread, handle_out, entry, arg, stack_top, thread_prio, processor_id)
    # 0x09
    def svcStartThread(self, handle):
        return self.c(F.svcStartThread, handle)
    # 0x0A
    def svcExitThread(self):
        return self.c(F.svcExitThread)
    # 0x0B
    # ...
    # 0x10
    def svcGetCurrentProcessorNumber(self):
        return self.c(F.svcGetCurrentProcessorNumber)
    # 0x11
    def svcSignalEvent(self, handle):
        return self.c(F.svcSignalEvent, handle)
    # 0x12
    # 0x13
    def svcMapSharedMemory(self, handle, addr, size, perm):
        return self.c(F.svcMapSharedMemory, handle, addr, size, perm)
    # 0x14
    # 0x15
    def svcCreateTransferMemory(self, handle_out, addr, size, perm):
        return self.c(F.svcCreateTransferMemory, handle_out, addr, size, perm)
    # 0x16
    def svcCloseHandle(self, handle):
        return self.c(F.svcCloseHandle, handle)
    # 0x17
    def svcResetSignal(self, handle):
        return self.c(F.svcResetSignal, handle)
    # 0x18
    def svcWaitSynchronization(self, out_idx, handles_ptr, handles_num, timeout):
        return self.c(F.svcWaitSynchronization, out_idx, handles_ptr, handles_num, timeout)
    # 0x19
    def svcCancelSynchronization(self, handle):
        return self.c(F.svcCancelSynchronization, h)
    # 0x1A
    # ...
    # 0x1D
    def svcSignalProcessWideKey(self, ptr, value):
        return self.c(F.svcSignalProcessWideKey, ptr, value)
    # 0x1E
    # 0x1F
    def svcConnectToNamedPort(self, handle_out, ptr_str):
        return self.c(F.svcConnectToNamedPort, handle_out, ptr_str)
    # 0x20
    # 0x21
    def svcSendSyncRequest(self, handle):
        return self.c(F.svcSendSyncRequest, handle)
    # 0x22
    def svcSendSyncRequestWithUserBuffer(self, cmdbuf, cmdsz, handle):
        return self.c(F.svcSendSyncRequestWithUserBuffer, cmdbuf, cmdsz, handle)
    # 0x23
    # ...
    # 0x25
    def svcGetThreadId(self, out, handle):
        return self.c(F.svcGetThreadId, out, handle)
    # 0x26
    # ...
    # 0x29
    def svcGetInfo(self, out, id0, handle, id1):
        return self.c(F.svcGetInfo, out, id0, handle, id1)
    # 0x2A
    # ...
    # 0x50
    def svcCreateSharedMemory(self, handle_out, size, perm0, perm1):
        return self.c(F.svcCreateSharedMemory, handle_out, size, perm0, perm1)
    # 0x51
    def svcMapTransferMemory(self, handle, addr, size, perm):
        return self.c(F.svcMapTransferMemory, handle, addr, size, perm)
    # 0x52
    def svcUnmapTransferMemory(self, handle, addr, size):
        return self.c(F.svcUnmapTransferMemory, handle, addr, size)
    # 0x53
    # ...
    # 0x7F

    def write_rop(self, rop_addr, rop):
        writer = Rop()
        n = 0
        for i, x in enumerate([0] + rop.rop):
            writer.write64(x, rop_addr + 8 * i)

            n+=1
            if n == 16:
                self.execute(writer)
                writer = Rop()
                n = 0

        if n != 0:
            self.execute(writer)

    ## Service playground
    def srv_cmd0(self, unk_zero):
        # srv::Initialize
        obj = self.r64(D.srv_objptr)
        return self.cv(obj, 0x20, unk_zero)
    def srv_cmd1(self, handle_out, name):
        # srv::GetService
        return self.c(F.srv_GetServiceHandle, handle_out, name)
    def srv_cmd2(self, handle_out, name_maybe, max_sessions_maybe, unk_bool):
        # srv::RegisterService
        obj = self.r64(D.srv_objptr)
        return self.cv(obj, 0x30, handle_out, name_maybe, max_sessions_maybe, unk_bool)
    def srv_cmd3(self, name_maybe):
        # srv::UnregisterService
        obj = self.r64(D.srv_objptr)
        return self.cv(obj, 0x38, name_maybe)

    def srv_new(self):
        old = self.r32(self.r64(D.srv_objptr)+12)
        self.svcCloseHandle(old)

        self.w(mem+8, 'sm:\0')
        if self.svcConnectToNamedPort(mem, mem+8) != 0:
            print('[-] svcConnectToNamedPort failed')
            return
        srv_handle = c.r32(mem)
        print('[+] Handle', srv_handle)
        self.w32(self.r64(D.srv_objptr)+12, srv_handle)
        print('[+] OK')

    def srv_bruteforce(self, start=''):
        def test(fout, a,b='\0',c='\0',d='\0',e='\0',f='\0',g='\0',h='\0'):
            name_s = (a+b+c+d+e+f+g+h)
            print('testing %s' % name_s)
            name = ord(a) | ord(b)<<8 | ord(c)<<16 | ord(d)<<24 | ord(e)<<32 | ord(f)<<40 | ord(g)<<48 | ord(h)<<56
            ret = self.srv_cmd3(name)
            if ret != 3605:
                print(ret, name_s)
                fout.write("%s\n" % (name_s))
                fout.flush()

        fout = open("bruteforced_services", "a")

        n = 0
        i = 0
        alpha = '\0abcdefghijklmnopqrstuvwxyz:' #ABCDEFGHIJKLMNOPQRSTUVWXYZ
        for s in start:
            n += alpha.index(s) * (len(alpha)**i)
            i+=1
        while True:
            test(fout,
                 's', 'p', 'l', ':',
                alpha[n%len(alpha)],
                alpha[(n/len(alpha))%len(alpha)],
                alpha[n/(len(alpha)**2)%len(alpha)],
                alpha[n/(len(alpha)**3)%len(alpha)]
            )
            n+=1
        fout.close()

    def srv_guess(self, name):
        ret = c.srv_cmd3(int(name[::-1].encode('hex'), 16))
        if ret == 3605:
            return '[*] NOT FOUND'
        print(ret)
        return '[*] !!! FOUND !!! :D'

    def cmd(self, h, _id,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF, f=0xFFFFFFFFFFFFFFFF, fast=False):
        cmd = IpcCmd(_id)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        cmd.add_raw_64(f)
        return cmd.execute(mem+0x1000, self, h, fast)

    def cmd_buf6(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_2(buf, size)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf46(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_40_4_2(buf, size)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_pid_buf46(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.send_pid()
        cmd.add_40_4_2(buf, size)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf86(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_80_4_2(buf, size)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf5(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_1(buf, size)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf5_buf5_raw5(self, h, _id, buf, size, buf2, size2,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_1(buf, size)
        cmd.add_4_1(buf2, size2)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf9(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_8_1(buf, size)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf6_buf6(self, h, _id, buf, size, buf2, size2,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_2(buf, size)
        cmd.add_4_2(buf2, size2)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf5_buf6_buf6(self, h, _id, buf, size, buf2, size2, buf3, size3,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_1(buf, size)
        cmd.add_4_2(buf2, size2)
        cmd.add_4_2(buf3, size3)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf5_buf6(self, h, _id, buf, size, buf2, size2,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_1(buf, size)
        cmd.add_4_2(buf2, size2)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf5_buf6_raw5(self, h, _id, buf, size, buf2, size2,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_4_1(buf, size)
        cmd.add_4_2(buf2, size2)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_bufa_buf9_raw5(self, h, _id, buf, size, buf2, size2,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        cmd.add_8_1(buf2, size2)
        cmd.add_8_2(buf, size)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_buf9_buf9_buf5(self, h, _id, buf, size, buf2, size2, buf3, size3,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        cmd.add_8_1(buf, size)
        cmd.add_8_1(buf2, size2)
        cmd.add_4_1(buf3, size3)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_bufa_buf9_raw4_raw32(self, h, _id, buf, size, buf2, size2,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF, f=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        cmd.add_raw_32(f)
        cmd.add_raw_32(f)
        cmd.add_raw_32(f)
        cmd.add_raw_32(f)
        cmd.add_raw_32(f)
        cmd.add_8_2(buf, size)
        cmd.add_8_1(buf2, size2)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_bufa_raw5(self, h, _id, buf, size,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        #cmd.add_raw_64(c)
        #cmd.add_raw_64(d)
        #cmd.add_raw_64(e)
        cmd.add_8_2(buf, size)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_handle(self, h, _id, handle,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF, f=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_handle(handle)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        cmd.add_raw_64(f)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_pid_handle(self, h, _id, handle,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF, f=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.send_pid()
        cmd.add_handle(handle)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        cmd.add_raw_64(e)
        cmd.add_raw_64(f)
        return cmd.execute(mem+0x1000, self, h)

    def cmd_pid(self, h, _id,
            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.send_pid()
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
        return cmd.execute(mem+0x1000, self, h)


if __name__ == "__main__":
    import code
    print('== Switch RPC Client ==')
    print('')
    c = Client()
    __bases = c.get_bases()
    mem = __bases[0]
    bin = __bases[1]
    main = bin + 0x6000
    code.interact('', local=locals())
