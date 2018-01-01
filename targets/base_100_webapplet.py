from relocatable import main_base


class Gadgets100Webapplet:
    pass


class Functions100Webapplet:
    malloc = main_base+0x6338

    setjmp = main_base + 0x45f398
    longjmp = main_base + 0x45f308
    socket = main_base + 0x3c6cbc
    connect = main_base + 0x3c6ca0
    send = main_base + 0x3c6c90
    recv = main_base + 0x3c6c88

    memset = main_base+0x465edc
    memcpy = main_base+0x46f324

    svcQueryMemory = main_base + 0x3dab2c
    svcCloseHandle = main_base + 0x3dabfc
    svcConnectToNamedPort = main_base + 0x3dac4c
    svcSendSyncRequest = main_base + 0x3dac64
    svcSendSyncRequestWithUserBuffer = main_base+0x3dac6c

    srv_GetServiceHandle = main_base + 0x3c60c4

class Dataptrs100Webapplet:
    srv_objptr = main_base + 0x92a420
    fsp_objptr = main_base + 0x902140

    webapplet_titleid = 0x0100000000001011
