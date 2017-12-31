.global stack_pivot

stack_pivot:
	mov sp, x0
	ldp x29, x30, [sp], #0x10
	ret
