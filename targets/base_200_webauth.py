from relocatable import main_base


class Gadgets200Webauth:
    pop_x20_x19_x29_x30 = main_base + 0x117c8 # ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret
    str_x19_x20_pop_x20_x19_x29_x30 = main_base + 0x117c4 # str x19, [x20] ; ldp x29, x30, [sp, #0x10] ; ldp x20, x19, [sp], #0x20 ; ret
    #pop_x29_x30 = main_base + 0x1db934 # ldp x29, x30, [sp], #0x10 ; ret
    str_x0_x19_pop_x21_0_x20_x19_x29_x30 = main_base + 0x11380c # str x0, [x19] ; ldp x29, x30, [sp, #0x20] ; ldp x20, x19, [sp, #0x10] ; ldr x21, [sp], #0x30 ; ret
    ldr_x0_x19_pop_x21_0_x20_x19_x29_x30 = main_base + 0x9eac # ldr x0, [x19] ; ldp x29, x30, [sp, #0x20] ; ldp x20, x19, [sp, #0x10] ; ldr x21, [sp], #0x30 ; ret

    # these are really from rtld but i don't care to fix it atm
    ret = main_base + 0x268
    infloop = main_base + 0xf4
    pop_x29_x30 = main_base + 0x1770


class Functions200Webauth:
    malloc = main_base+0x6338

    setjmp = main_base + 0x4396b0
    longjmp = main_base + 0x439620
    get_errno = main_base + 0x3b38f0
    socket = main_base + 0x3b3840
    connect = main_base + 0x3b382c
    send = main_base + 0x3b3824
    recv = main_base + 0x3b3820

    memset = main_base+0x440200

    svcSetHeapSize = main_base+0x3c1e10
    svcSetMemoryPermission = main_base+0x3c1e28
    svcSetMemoryAttribute = main_base+0x3c1e30
    svcMapMemory = main_base+0x3c1e38
    svcUnmapMemory = main_base+0x3c1e40

    svcQueryMemory = main_base + 0x3c1e48

    svcCreateThread = main_base+0x3c1e68
    svcStartThread = main_base+0x3c1e80
    svcExitThread = main_base+0x3c1e88
    svcGetCurrentProcessorNumber = main_base+0x3c1ee0
    svcSignalEvent = main_base+0x3c1ee8
    svcMapSharedMemory = main_base+0x3c1ef8
    svcCreateTransferMemory = main_base+0x3c1f08
    svcCloseHandle = main_base+0x3c1f20
    svcResetSignal = main_base+0x3c1f28
    svcWaitSynchronization = main_base+0x3c1f30
    svcCancelSynchronization = main_base+0x3c1f48
    svcSignalProcessWideKey = main_base+0x3c1f68
    svcConnectToNamedPort = main_base+0x3c1f70
    svcSendSyncRequest = main_base+0x3c1f88
    svcSendSyncRequestWithUserBuffer = main_base+0x3c1f90
    svcGetThreadId = main_base+0x3c1f98
    svcGetInfo = main_base+0x3c1fc8
    svcCreateSharedMemory = main_base+0x3c1fe0
    svcMapTransferMemory = main_base+0x3c1ff8
    svcUnmapTransferMemory = main_base+0x3c2000

    # from https://github.com/reswitched/PegaSwitch/blob/master/exploit/sploitcore.js
    OpenDirectory = main_base + 0x233894 + 0x6000  # int OpenDirectory(_QWORD *handle, char *path, unsigned int flags)
    ReadDirectory = main_base + 0x2328B4 + 0x6000  # int ReadDirectory(_QWORD *sDirInfo, _QWORD *out, _QWORD *handle, __int64 size)
    CloseDirectory = main_base + 0x232828 + 0x6000 # int CloseDirectory(_QWORD *handle)
    fopen = main_base + 0x43DDB4 + 0x6000
    fread = main_base + 0x438A14 + 0x6000
    fclose = main_base + 0x4384D0 + 0x6000

    open_sysdata = main_base+0x23f484
    open_sysdata_wrap = main_base + 0x2363c8 + 0x6000
    mount_title = main_base+0xd6ba4
    test_sysdata = main_base + 0x23959c + 0x6000
    mount_content_type5 = main_base+0x39d974
    mount_content_type4 = main_base+0x39d914
    mount_content = main_base+0x5a5dcc
    CreateFileSystemAdaptor_obj = main_base+0x246ec0
    AddMountPoint = main_base+0x23f338

    ScopedPtr_Reset = main_base+0x808c
    Buffer_Reset = main_base+0xf0440

    NvOsDrvOpen = main_base + 0x1a49c4 + 0x6000
    NvOsDrvClose = main_base + 0x1a4a80 + 0x6000
    NvOsDrvIoctl = main_base + 0x1a4b10 + 0x6000

    srv_GetServiceHandle = main_base + 0x3b2f48

    lm_createobj = main_base+0x26c700
    lm_cmd0 = main_base+0x26c914
    nsam_getobjptr = main_base+0x39db98
    plu_getsingleton = main_base+0x3a98b8
    mm_init = main_base+0x5a6be4

    NvOsDrvObj__Open = main_base+0x1a8244
    nv_createservobj = main_base+0x1a7f28
    nv_cmd3_somefunc = main_base+0x3a5ab4


class Dataptrs200Webauth:
    srv_objptr = main_base + 0x92dd70
    fs_panic_flag = main_base+0x879708
    fsp_objptr = main_base+0x905c20
    hid_objptr = main_base+0x90f250
    accu_objptr = main_base+0x8f85e8
    plu_sharedmem_ptr = main_base+0x925bb0
    ro_objptr = main_base+0x95b558
    mm_objptr = main_base+0x95b568
    nif_objptr = main_base+0x91d220
    nv_objptr = main_base+0x8f3b68
    vi_objptr = main_base+0x8B04D8

    webapplet_titleid = 0x010000000000100A
