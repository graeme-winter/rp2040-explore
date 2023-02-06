import machine
import time

# constants
SIO_BASE = const(0xD0000000)
GPIO_OUT = const(SIO_BASE + 0x10)
GPIO_OUT_XOR = const(SIO_BASE + 0x1C)

led = machine.Pin(25, machine.Pin.OUT)
out = machine.Pin(0, machine.Pin.OUT)


def dumb():
    for j in range(20):
        led.toggle()
        time.sleep(0.5)


def sio():
    for j in range(20):
        machine.mem32[GPIO_OUT_XOR] = 1 << 25
        time.sleep(0.5)


@micropython.asm_thumb
def asm(r0, r1, r2):
    # save the XOUT address
    mov(r7, r0)

    # save the number of cycles to count to
    mov(r6, r1)

    # save the number of repeats
    mov(r5, r2)

    # set up r4 with bit I want - 1 << 25 for LED
    mov(r4, 0x1)
    # mov(r2, 25)
    # lsl(r4, r2)

    # start of cycle loop
    label(cycle)

    # switch on
    str(r4, [r7, 0])
    mov(r2, r6)
    label(on)
    sub(r2, r2, 1)
    cmp(r2, 0)
    bne(on)

    # 3 no-ops because 3 to jmp below?
    nop()
    nop()
    nop()
    nop()

    # switch off
    str(r4, [r7, 0])
    mov(r2, r6)
    label(off)
    sub(r2, r2, 1)
    cmp(r2, 0)
    bne(off)

    sub(r5, r5, 1)
    cmp(r5, 0)
    bne(cycle)


led.on()
asm(GPIO_OUT_XOR, 10, 50_000_000)
led.off()
