from relocatable import main_base


class Gadgets210Webapplet:
    pop_x20_x19_x29_x30 = main_base + 0xa6fc
    str_x19_x20_pop_x20_x19_x29_x30 = main_base + 0x12134
    str_x0_x19_pop_x21_0_x20_x19_x29_x30 = main_base + 0x1147a4
    ldr_x0_x19_pop_x21_0_x20_x19_x29_x30 = main_base + 0xa2b0

    # these are really from rtld but i don't care to fix it atm
    ret = main_base + 0x268
    infloop = main_base + 0xf4
    pop_x29_x30 = main_base + 0x1770


class Functions210Webapplet:
    malloc = main_base+0x6338

    setjmp = main_base + 0x43a4fc
    longjmp = main_base + 0x43a46c
    get_errno = main_base + 0x3b45f4
    socket = main_base + 0x3b4534
    connect = main_base + 0x3b4518
    send = main_base + 0x3b4508
    recv = main_base + 0x3b4500

    memset = main_base+0x441040

    svcQueryMemory = main_base + 0x3c2c78

    svcSetHeapSize = main_base+0x3c2c40
    svcCloseHandle = main_base+0x3c2d50
    svcClearEvent = main_base+0x3c2d58
    svcMirrorStack = main_base+0x3c2c68
    svcUnmirrorStack = main_base+0x3c2c70
    svcProtectMemory = main_base+0x3c2c58
    svcCreateMemoryMirror = main_base+0x3c2d38
    svcCreateMemoryBlock = main_base+0x3c2e10
    svcMapMemoryMirror = main_base+0x3c2e28
    svcUnmapMemoryMirror = main_base+0x3c2e30
    svcSendSyncRequestByBuf = main_base+0x3c2dc0
    svcGetInfo = main_base+0x3c2df8
    svcGetThreadId = main_base+0x3c2dc8
    svcSendSyncRequest = main_base+0x3c2db8
    svcMapMemoryBlock = main_base+0x3c2d28
    svc3 = main_base+0x3c2c60
    svc19 = main_base+0x3c2d78
    svc11 = main_base+0x3c2d18
    svc1D = main_base+0x3c2d98
    svcConnectToPort = main_base+0x3c2da0
    svcCreateThread = main_base+0x3c2c98
    svcStartThread = main_base+0x3c2cb0
    svcExitThread = main_base+0x3c2cb8
    svcWaitEvents = main_base+0x3c2d60
    svcGetCurrentProcessorNumber = main_base+0x3c2d10

    OpenDirectory = main_base + 0x23482C + 0x6000
    ReadDirectory = main_base + 0x23384C + 0x6000
    CloseDirectory = main_base + 0x2337C0 + 0x6000
    fopen = main_base + 0x43EBF4 + 0x6000
    fread = main_base + 0x439854 + 0x6000
    fclose = main_base +  0x439310 + 0x6000

    open_sysdata = main_base+0x24041c
    open_sysdata_wrap = main_base + 0x237360 + 0x6000
    mount_title = main_base+0xd7a14
    test_sysdata = main_base + 0x23a534 + 0x6000
    mount_content_type5 = main_base+0x39e6b0
    mount_content_type4 = main_base+0x39e650
    mount_content = main_base+0x5a6c0c
    CreateFileSystemAdaptor_obj = main_base+0x247e58
    AddMountPoint = main_base+0x2402d0

    ScopedPtr_Reset = main_base+0x82c0
    Buffer_Reset = main_base+0xf12b0

    NvOsDrvOpen = main_base + 0x1a595c + 0x6000
    NvOsDrvClose = main_base + 0x1a5a18 + 0x6000
    NvOsDrvIoctl = main_base + 0x1a5aa8 + 0x6000

    srv_GetServiceHandle = main_base + 0x3b3d78

    lm_createobj = main_base+0x26d43c
    lm_cmd0 = main_base+0x26d650
    nsam_getobjptr = main_base+0x39e8d4
    plu_getsingleton = main_base+0x3aa6e8
    mm_init = main_base+0x5a7a24

    NvOsDrvObj__Open = main_base+0x1a91dc
    nv_createservobj = main_base+0x1a8ec0
    nv_cmd3_somefunc = main_base+0x3a68e4


class Dataptrs210Webapplet:
    srv_objptr = main_base + 0x92ed70
    fs_panic_flag = main_base+0x87a708
    fsp_objptr = main_base+0x906c20
    hid_objptr = main_base+0x910250
    accu_objptr = main_base+0x8f95e8
    plu_sharedmem_ptr = main_base+0x926bb0
    ro_objptr = main_base+0x95c558
    mm_objptr = main_base+0x95c568
    nif_objptr = main_base+0x91e220
    nv_objptr = main_base+0x8f4b68

    webapplet_titleid = 0x010000000000100A
