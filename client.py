#!/usr/bin/env python2

import socket
import pickle
import shlex
import datetime
import os

from server import ipc_port
from functionhelper import FunctionHelper
from rpc import RPC_SCRATCH_SIZE, RPC_RESPONSE_LEN

class Client():
    def __init__(self):
        self.fh = FunctionHelper(self)

    def execute(self, rop):
        """
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

        self.fh.memcpy(data_base, addr, length)
        data = self.mem[0:length]
        print hexdump(data, start=addr)

        return self.c(F.memset, addr, val, size)
    def w(self, addr, data):
        rop = Rop()
        src = rop.awrite(data)
        rop.call(F.memcpy, addr, src, len(data))
        self.execute(rop)

        return self.c(F.malloc, size)
        """ Ok this is done in a kinda roundabout way but whatever """
        rop = Rop()
        rop.write64(data_base, data_base + 0)
        rop.write64(main_base, data_base + 8)
        rop.write64(wk_base, data_base + 0x10)
        data = self.execute(rop)
        buf_base = u64(data, 0) - 0x10000

        print "Static memory: 0x{:x} (You can use it between different calls)".format(buf_base)
        print "Main binary base: 0x{:x}".format(u64(data, 8))
        print "Webkit base: 0x{:x}".format(u64(data, 0x10))

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

                print "{:.2f}%".format(100.0 * sent / whole)

                fout.write(data)

            print '[%s] 0x%010x-0x%010x size=0x%010x [%s] %s' % (perm_str, base, base+size-1, size, type_map[state], attr_str)

        cur = 0
        while cur < 2 ** 64:


    def dump_file(self, src, dst):
        """ Download file `src` from switch to `dst` """
        fin = self.fh.fopen(src, "rb")
        if not fin:
            print "failed to open '{}' for dump".format(src)
            return
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
            print "failed to open '{}' for write".format(dst)
            return
        print 'fopen success'
        while True:
            filedata = fin.read(0x1000)
            if len(filedata) == 0:
                break
            self.w_big(mem+0x2000, filedata)
            ret = self.fh.fwrite(mem+0x2000, 1, len(filedata), fout)
            if ret == 0:
                print "File write failed."
                break
            if ret < len(filedata):
                print "Only 0x%x of 0x%x bytes were written, aborting." % (ret, len(filedata))
                break
        self.fh.fclose(fout)
        fin.close()

    def list_dir(self, path, recursive=False, dump_files=False, host_path="", prefix=""):
        if dump_files:
            os.mkdir(host_path)
        ret = self.fh.OpenDirectory(data_base, path, 3)
        if ret != 0:
            print "failed to open '{0}', error={1}=0x{1:x}".format(path, ret)
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
            print "{}{}{}".format(prefix, name, "/" if not is_file else "")
            fullpath = "{}/{}".format(path, name)
            if dump_files and is_file:
                self.dump_file(fullpath, os.path.join(host_path, name))
                self.list_dir(fullpath, recursive, dump_files, os.path.join(host_path, name), prefix + "-")
        self.fh.CloseDirectory(handle)

    def dump_dir(self, src_path, dst_path, recursive=True):
        self.list_dir(src_path, recursive, True, dst_path)

        return self.c(F.svcSetHeapSize, out, size)
        return self.c(F.svcCloseHandle, handle)
        return self.c(F.svcClearEvent, handle)
    def svcMirrorStack(self, dst, src, size):
        return self.c(F.svcMirrorStack, dst, src, size)
    def svcUnmirrorStack(self, dst, src, size):
        return self.c(F.svcUnmirrorStack, dst, src, size)
        return self.c(F.svcProtectMemory, addr, size, perm)
        return self.c(F.svcCreateMemoryMirror, handle_out, addr, size, perm)
        return self.c(F.svcCreateMemoryBlock, handle_out, size, perm0, perm1)
        return self.c(F.svcMapMemoryMirror, handle, addr, size, perm)
        return self.c(F.svcUnmapMemoryMirror, handle, addr, size)
    def svcSendSyncRequestByBuf(self, cmdbuf, cmdsz, handle):
        return self.c(F.svcSendSyncRequestByBuf, cmdbuf, cmdsz, handle)
    def svcGetInfo(self, out, id0, handle, id1):
        return self.c(F.svcGetInfo, out, id0, handle, id1)
        return self.c(F.svcGetThreadId, out, handle)
        return self.c(F.svcSendSyncRequest, handle)
        return self.c(F.svcMapMemoryBlock, handle, addr, size, perm)
        return self.c(F.svc3, addr, end_addr, state0, state1)
        return self.c(F.svc19, h)
        return self.c(F.svc11, handle)
        return self.c(F.svc1D, ptr, value)
        return self.c(F.svcConnectToPort, handle_out, ptr_str)
        return self.c(F.svcCreateThread, handle_out, entry, arg, stack_top, thread_prio, processor_id)
        return self.c(F.svcStartThread, handle)
        return self.c(F.svcExitThread)
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

            a=0xFFFFFFFFFFFFFFFF, b=0xFFFFFFFFFFFFFFFF,
            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF,
            e=0xFFFFFFFFFFFFFFFF):
        cmd = IpcCmd(_id)
        cmd.add_raw_64(a)
        cmd.add_raw_64(b)
        cmd.add_raw_64(c)
        cmd.add_raw_64(d)
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

            c=0xFFFFFFFFFFFFFFFF, d=0xFFFFFFFFFFFFFFFF):
        cmd.add_raw_64(d)
if __name__ == "__main__":
    main = bin + 0x6000
