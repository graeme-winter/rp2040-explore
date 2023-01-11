from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

# use pin0 as sideset, 1...5 as "data"
pins = [Pin(j) for j in range(6)]


@asm_pio(
    sideset_init=PIO.OUT_LOW,
    out_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW),
    out_shiftdir=PIO.SHIFT_RIGHT,
)
def saw():
    wrap_target()
    set(x, 31)
    label("tick")
    mov(osr, x)
    out(pins, 5).side(1)
    nop()
    nop().side(0)
    jmp(x_dec, "tick")
    wrap()


sm = StateMachine(0, saw, freq=12500, sideset_base=pins[0], out_base=pins[1])
sm.active(1)
