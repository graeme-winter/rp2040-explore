from machine import Pin

led = Pin(25, Pin.OUT)
pin = Pin(0, Pin.OUT)

XOR = 0xD000001C


@micropython.asm_thumb
def blink(r0):
    push({r4, r5, r6, r7})
    align(4)
    mov(r7, pc)
    b(entry)
    align(4)
    data(4, (1 << 25) | 1)  # LED pin
    data(4, 125)  # ticks
    data(4, 10_000_000)  # cycles
    align(2)

    label(entry)  # start of program
    mov(r6, r0)
    ldr(r1, [r7, 8])
    label(tick)
    sub(r1, r1, 1)
    ldr(r0, [r7, 0])
    str(r0, [r6, 0])  # toggle GPIO
    ldr(r0, [r7, 4])
    sub(r0, r0, 2)  # two fewer counts to balance
    label(clock)
    sub(r0, r0, 1)
    cmp(r0, 0)
    bne(clock)
    nop()
    cmp(r1, 0)
    bne(tick)
    pop({r4, r5, r6, r7})


blink(XOR)
