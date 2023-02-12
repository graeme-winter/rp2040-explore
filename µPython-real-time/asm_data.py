from machine import Pin
import time

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
    data(4, 10)  # ticks
    data(4, 100_000_000)  # total cycles
    align(2)

    label(entry)  # start of program
    mov(r6, r0)
    ldr(r1, [r7, 8])
    label(tick)
    sub(r1, r1, 1)
    ldr(r0, [r7, 0])
    str(r0, [r6, 0])  # toggle GPIO
    ldr(r0, [r7, 4])
    label(clock)
    sub(r0, r0, 1)
    cmp(r0, 0)
    bne(clock)
    nop()
    nop()
    cmp(r1, 0)
    bne(tick)
    pop({r4, r5, r6, r7})


t0 = time.ticks_us()
blink(XOR)
t1 = time.ticks_us()
print(t1 - t0)
