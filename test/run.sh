#!/bin/bash

qemu-aarch64-static -L $LINARO/aarch64-linux-gnu/libc ./test $@
