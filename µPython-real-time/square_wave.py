import time

from machine import Pin
import rp2

p0 = Pin(0)

# counter program using side-set to control output
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def square():
    pull()
    wrap_target()
    mov(x, osr).side(1)
    label("high")
    jmp(x_dec, "high")
    mov(x, osr).side(0)
    label("low")
    jmp(x_dec, "low")
    wrap()


# because 50% duty cycle square wave, need frequency to be even
# in here: clock divider of 12.5 is fine
sm = rp2.StateMachine(0, square, freq=10_000_000, sideset_base=p0)

# counts: two fewer than you think:
#
# mov() takes one instruction
# jmp x_dec only jumps when x_dec comes in as zero
sm.put(5 - 2)

sm.active(1)
time.sleep(100)
sm.active(0)

# tidy
p0.off()
