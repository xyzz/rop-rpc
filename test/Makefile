test: main.o asm.o
	aarch64-linux-gnu-gcc $^ -o $@

main.c: log.h

%.o: %.c
	aarch64-linux-gnu-gcc -c $^ -o $@

%.o: %.S
	aarch64-linux-gnu-as $^ -o $@

clean:
	-rm -f test *.o
