#!/bin/bash

qemu-aarch64-static -g 6886 -L $LINARO/aarch64-linux-gnu/libc ./test $@ &
aarch64-linux-gnu-gdb -ex "file test" -ex "set sysroot $LINARO/aarch64-linux-gnu/libc" -ex "target remote localhost:6886"
