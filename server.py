#!/usr/bin/env python2

from __future__ import print_function
from sys import argv
import threading

from webserver import webserver
from sockserver import sockserver
from ipcserver import ipcserver
from rpc import Rpc

webserver_port = 6969
socket_port = 6970
ipc_port = 6971


def main():
    if len(argv) != 2:
        print("usage: ./server.py MY_IP_AS_VISIBLE_FROM_SWITCH")
        return -1
    host = argv[1]

    print("!! ipc is extremely insecure but it's only listening on 127.0.0.1 !!")

    print("running webserver on http://{}:{}/".format(host, webserver_port))
    print("running sockserver on {}:{}".format(host, socket_port))
    print("running ipc server on 127.0.0.1:{}".format(ipc_port))

    rpc = Rpc(host, socket_port)

    t = threading.Thread(target=sockserver, kwargs=dict(host=host, port=socket_port, rpc=rpc))
    t.daemon = True
    t.start()

    t2 = threading.Thread(target=webserver, kwargs=dict(host=host, port=webserver_port, rpc=rpc))
    t2.daemon = True
    t2.start()

    ipcserver(ipc_port, rpc)



if __name__ == "__main__":
    main()
