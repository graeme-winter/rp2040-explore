from machine import Pin, mem32
import rp2


PIO0_BASE = 0x50200000
PIO1_BASE = 0x50300000


# advance one or more PIO SMs on PIO block pointed at by r0 masked by r1
# call with e.g. advance(PIO1_BASE, 0x3) to advance SM 4, 5 by one tick
@micropython.asm_thumb
def advance(r0, r1):
    mov(r2, 0x0)
    str(r1, [r0, 0])
    str(r2, [r0, 0])
    mov(r0, 0)


@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def incr():
    wrap_target()
    pull()
    mov(x, osr)
    label("start")
    set(pins, 1)[1]
    set(pins, 3)[1]
    set(pins, 2)[1]
    set(pins, 0)
    jmp(x_dec, "start")
    mov(isr, invert(x))
    push()
    wrap()


@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def decr():
    wrap_target()
    pull()
    mov(x, osr)
    label("start")
    set(pins, 2)[1]
    set(pins, 3)[1]
    set(pins, 1)[1]
    set(pins, 0)
    jmp(x_dec, "start")
    mov(isr, invert(x))
    push()
    wrap()


# PIO1 blocks for signal generation

pins = [Pin(j, Pin.OUT) for j in range(4)]

sm4 = rp2.StateMachine(4, incr, freq=8_000_000, set_base=pins[0])
sm5 = rp2.StateMachine(5, decr, freq=8_000_000, set_base=pins[0])


@micropython.native
def updown(n, m):
    for j in range(n):
        sm4.put((m // 4) - 1)
        sm4.active(1)
        sm4.get()
        sm4.active(0)
        sm5.put((m // 4) - 1)
        sm5.active(1)
        sm5.get()
        sm5.active(0)


@micropython.native
def up(m):
    sm4.put((m // 4) - 1)
    sm4.active(1)
    sm4.get()
    sm4.active(0)


@micropython.native
def down(m):
    sm5.put((m // 4) - 1)
    sm5.active(1)
    sm5.get()
    sm5.active(0)


up(1000)
down(1000)
