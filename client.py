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

    def w(self, addr, data):
        rop = Rop()
        src = rop.awrite(data)
        rop.call(F.memcpy, addr, src, len(data))
        self.execute(rop)

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

if __name__ == "__main__":
    main = bin + 0x6000
