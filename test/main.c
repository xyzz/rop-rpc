#include <inttypes.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include "log.h"


void stack_pivot(void *sp);

enum {
	ROP_STACK_BASE = 0x1000000000,
	ROP_STACK_SIZE = 512 * 1024,
	ROP_STACK_OFFSET = 8 * 1024,

	DATA_MEMORY_BASE = 0x0100000000,
	DATA_MEMORY_SIZE = 0x8000,
};

void load_bin(void *base, const char *file, size_t size) {
	int fd = open(file, O_RDONLY);
	if (fd < 0)
		FATAL("failed to open %s for read\n", file);
	void *res = mmap(base, size, PROT_EXEC | PROT_READ, MAP_PRIVATE | MAP_FIXED, fd, 0);
	if (res != base)
		FATAL("failed to mmap, expected %p got %p\n", base, res);
}

void map_mem(void *base, size_t size) {
	void *res = mmap(base, size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_FIXED | MAP_ANONYMOUS, -1, 0);
	if (res != base)
		FATAL("failed to mmap, expected %p got %p\n", base, res);
}

void rop_final(void) {
	fprintf(stderr, "rop_final is called\n");
	fwrite((void*)DATA_MEMORY_BASE, DATA_MEMORY_SIZE, 1, stdout);
	_exit(0);
}

int main(int argc, char *argv[]) {
	fprintf(stderr, "aarch64 rop tester\n");

	if (argc != 4) {
		fprintf(stderr, "usage: ./run.sh main.bin webkit.bin rop.bin\n");
		return -1;
	}

	load_bin((void*)0x0200000000, argv[1], 0x963000);
	load_bin((void*)0x0300000000, argv[2], 0x1816000);

	fprintf(stderr, "using main.bin: %s\n", argv[1]);
	fprintf(stderr, "using webkit bin: %s\n", argv[2]);

	map_mem((void*)DATA_MEMORY_BASE, DATA_MEMORY_SIZE); // we don't need a lot of "data" memory for tests
	map_mem((void*)ROP_STACK_BASE, ROP_STACK_SIZE + ROP_STACK_OFFSET);

	FILE *fin = fopen(argv[3], "rb");
	if (!fin)
		FATAL("failed to open %s for read\n", argv[3]);
	size_t sz = fread((void*)(ROP_STACK_BASE + ROP_STACK_OFFSET), 1, ROP_STACK_SIZE, fin);
	fclose(fin);

	*(void**)(ROP_STACK_BASE + ROP_STACK_OFFSET + sz) = rop_final;

	stack_pivot((void*)(ROP_STACK_BASE + ROP_STACK_OFFSET));

	return 0;
}
