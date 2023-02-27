.thumb_func
.global main

main:
	ldr r1, =gpioc
	mov r2, #5
	str r2, [r1, #0]

	ldr r1, =gpiox	
	ldr r2, =led
loop:
	str r2, [r1, #0]
	ldr r0, =count
tick:
	sub r0, r0, #1
	cmp r0, #0
	bgt tick
	b loop

.data
.align 4
gpioc:	.word 0x40014068
gpiox:	.word 0xd000001c
led:	.word 0x2000000
count:	.word 25000000
