import socket
import pickle

from util import u32, p32


def ipcserver(port, rpc):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(10)

    while True:
        c, addr = s.accept()

        # protocol is 
        # - request: u32 size, serialized rop obj
        # - response: u32 size, binary rpc response
        # the rop obj can contain any ropchain. common rpc stuff is appended to the end by us

        sz = u32(c.recv(4))
        obj = c.recv(sz, socket.MSG_WAITALL)

        rop = pickle.loads(obj)

        data = rpc.exec_rop(rop)

        c.send(p32(len(data)))
        c.send(data)

        c.close()
