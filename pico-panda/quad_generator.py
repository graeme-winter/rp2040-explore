from machine import Pin
import rp2


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

pins = [machine.Pin(j, machine.Pin.OUT) for j in range(4)]

sm4 = rp2.StateMachine(4, incr, freq=12_500_000, set_base=pins[0])
sm5 = rp2.StateMachine(5, decr, freq=12_500_000, set_base=pins[0])


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
def down(m):
    sm5.put((m // 4) - 1)
    sm5.active(1)
    sm5.get()
    sm5.active(0)


down(1_000)
updown(10, 1_002_000)
