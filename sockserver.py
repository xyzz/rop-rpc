from __future__ import print_function
import socket

from util import u64
from rpc import RPC_ROP_LEN, RPC_RESPONSE_LEN, RPC_DYNAMIC_MEM_OFF

def sockserver(host, port, rpc):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(10)

    c, addr = s.accept()
    print(c, addr)
    setup_buf = c.recv(0x1000, socket.MSG_WAITALL)

    data_base = u64(setup_buf, 0)
    main_base = u64(setup_buf, 8)
    wk_base = u64(setup_buf, 0x10)
    sockfd = u64(setup_buf, 0x100)
    print("got data of len 0x{:x}".format(len(setup_buf)))
    print("data: 0x{:x} main: 0x{:x} wk: 0x{:x} sockfd: {}".format(data_base, main_base, wk_base, sockfd))

    # NOTE: in this first payload, data_base is at +0x8000
    # See rpc.py for the buf layout
    buf = data_base - 0x8000
    rpc.set_args(sockfd, buf)
    relocs = {1: buf + RPC_DYNAMIC_MEM_OFF, 2: main_base, 3: wk_base} # 1 = data_base = dynamic mem

    print("--- setup complete ---")
    print("you can run ./client.py now")

    while True:
        rop = rpc.next_payload()
        binary = rop.generate_binary(relocs)
        print("Sending rop len = 0x{:x}".format(len(binary)))
        binary += "\x00" * (RPC_ROP_LEN - len(binary))

        ret = c.send(binary)

        print("Sent 0x{:x}".format(ret))

        data = c.recv(RPC_RESPONSE_LEN, socket.MSG_WAITALL)

        rpc.res_q.put(data)

        # print "Got data: {} len 0x{:x}".format(data, len(data))
        print("Got data len 0x{:x}".format(len(data)))
