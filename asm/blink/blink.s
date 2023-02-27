.thumb_func
.global main

main:
	ldr r1, =gpioc
	mov r2, #5
	str r2, [r1, #0]

	ldr r1, =gpiod
	mov r2, #48
	str r2, [r1, #0]

	ldr r1, =gpio
	ldr r2, =led
	str r2, [r1, #0x20]
loop:
	str r2, [r1, #0x1c]
	ldr r0, =count
tick:
	sub r0, r0, #1
	cmp r0, #0
	bgt tick
	b loop

.data
.align 4
gpioc:	.word 0x400140cc
gpiod:	.word 0x4001c068
gpio:	.word 0xd0000000
led:	.word 0x2000000
count:	.word 25000
