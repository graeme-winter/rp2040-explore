@micropython.viper
def byteswap(a: uint) -> uint:
    return (
        ((uint(0xFF000000) & a) >> 24)
        | ((uint(0x00FF0000) & a) >> 8)
        | ((uint(0x0000FF00) & a) << 8)
        | ((uint(0x000000FF) & a) << 24)
    )


@micropython.asm_thumb
def byteswap_asm(r0):
    # const for masking
    mov(r6, 0xFF)

    # save input
    mov(r7, r0)

    # byte 3
    mov(r1, r7)
    mov(r5, 24)
    lsr(r1, r5)
    and_(r1, r6)
    mov(r0, r1)

    # byte 2
    mov(r1, r7)
    mov(r5, 16)
    lsr(r1, r5)
    and_(r1, r6)
    mov(r5, 8)
    lsl(r1, r5)
    orr(r0, r1)

    # byte 1
    mov(r1, r7)
    mov(r5, 8)
    lsr(r1, r5)
    and_(r1, r6)
    mov(r5, 16)
    lsl(r1, r5)
    orr(r0, r1)

    # byte 0
    mov(r1, r7)
    and_(r1, r6)
    mov(r5, 24)
    lsl(r1, r5)
    orr(r0, r1)


x = 0x11223344
print(hex(x), hex(byteswap(x)), hex(byteswap_asm(x)))
