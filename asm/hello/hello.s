.thumb_func
.global main

main:
    mov r7, #0
    bl stdio_init_all
loop:
    ldr r0, =hello
    add r7, #1
    mov r1, r7
    bl printf
    b loop

.data
.align 4
hello: .asciz "Hello, world! %d\n"

