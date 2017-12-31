from relocatable import main_base


class Gadgets210Shopn:
    pop_x20_x19_x29_x30 = main_base + 0xa540
    str_x19_x20_pop_x20_x19_x29_x30 = main_base + 0x120f4
    str_x0_x19_pop_x21_0_x20_x19_x29_x30 = main_base + 0x114930
    ldr_x0_x19_pop_x21_0_x20_x19_x29_x30 = main_base + 0xa0f4

    # these are really from rtld but i don't care to fix it atm
    ret = main_base + 0x268
    infloop = main_base + 0xf4
    pop_x29_x30 = main_base + 0x1770


class Functions210Shopn:
    malloc = main_base+0x6338

    setjmp = main_base + 0x43a66c
    longjmp = main_base + 0x43a5dc
    get_errno = main_base + 0x3b4780
    socket = main_base + 0x3b46c0
    connect = main_base + 0x3b46a4
    send = main_base + 0x3b4694
    recv = main_base + 0x3b468c

    memset = main_base+0x4411c0

    svcQueryMemory = main_base + 0x3c2e04

    svcSetHeapSize = main_base+0x3c2dcc
    svcCloseHandle = main_base+0x3c2edc
    svcClearEvent = main_base+0x3c2ee4
    svcMirrorStack = main_base+0x3c2df4
    svcUnmirrorStack = main_base+0x3c2dfc
    svcProtectMemory = main_base+0x3c2de4
    svcCreateMemoryMirror = main_base+0x3c2ec4
    svcCreateMemoryBlock = main_base+0x3c2f9c
    svcMapMemoryMirror = main_base+0x3c2fb4
    svcUnmapMemoryMirror = main_base+0x3c2fbc
    svcSendSyncRequestByBuf = main_base+0x3c2f4c
    svcGetInfo = main_base+0x3c2f84
    svcGetThreadId = main_base+0x3c2f54
    svcSendSyncRequest = main_base+0x3c2f44
    svcMapMemoryBlock = main_base+0x3c2eb4
    svc3 = main_base+0x3c2dec
    svc19 = main_base+0x3c2f04
    svc11 = main_base+0x3c2ea4
    svc1D = main_base+0x3c2f24
    svcConnectToPort = main_base+0x3c2f2c
    svcCreateThread = main_base+0x3c2e24
    svcStartThread = main_base+0x3c2e3c
    svcExitThread = main_base+0x3c2e44
    svcWaitEvents = main_base+0x3c2eec
    svcGetCurrentProcessorNumber = main_base+0x3c2e9c

    OpenDirectory = main_base + 0x2349B8 + 0x6000
    ReadDirectory = main_base + 0x2339D8 + 0x6000
    CloseDirectory = main_base + 0x23394C + 0x6000
    fopen = main_base + 0x43ED74 + 0x6000
    fread = main_base + 0x4399D4 + 0x6000
    fclose = main_base +  0x439490 + 0x6000

    open_sysdata = main_base+0x2405a8
    open_sysdata_wrap = main_base + 0x2374ec + 0x6000
    mount_title = main_base+0xd7ba0
    test_sysdata = main_base + 0x23a6c0 + 0x6000
    mount_content_type5 = main_base+0x39e83c
    mount_content_type4 = main_base+0x39e7dc
    mount_content = main_base+0x5a6d8c
    CreateFileSystemAdaptor_obj = main_base+0x247fe4
    AddMountPoint = main_base+0x24045c

    ScopedPtr_Reset = main_base+0x8104
    Buffer_Reset = main_base+0xf143c

    NvOsDrvOpen = main_base + 0x1a5ae8 + 0x6000
    NvOsDrvClose = main_base + 0x1a5ba4 + 0x6000
    NvOsDrvIoctl = main_base + 0x1a5c34 + 0x6000

    srv_GetServiceHandle = main_base + 0x3b3f04

    lm_createobj = main_base+0x26d5c8
    lm_cmd0 = main_base+0x26d7dc
    nsam_getobjptr = main_base+0x39ea60
    plu_getsingleton = main_base+0x3aa874
    mm_init = main_base+0x5a7ba4

    NvOsDrvObj__Open = main_base+0x1a9368
    nv_createservobj = main_base+0x1a904c
    nv_cmd3_somefunc = main_base+0x3a6a70


class Dataptrs210Shopn:
    srv_objptr = main_base + 0x92ee70
    fs_panic_flag = main_base+0x87a708
    fsp_objptr = main_base+0x906d20
    hid_objptr = main_base+0x910350
    accu_objptr = main_base+0x8f9668
    plu_sharedmem_ptr = main_base+0x926cb0
    ro_objptr = main_base+0x95c658
    mm_objptr = main_base+0x95c668
    nif_objptr = main_base+0x91e320
    nv_objptr = main_base+0x8f4be8
