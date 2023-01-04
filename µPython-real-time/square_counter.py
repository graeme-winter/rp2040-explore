import time

from machine import Pin
import rp2

p0 = Pin(0)

# counter program using side-set to control output
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def square():
    wrap_target()
    mov(x, osr).side(1)
    label("high")
    jmp(x_dec, "high")
    mov(x, osr).side(0)
    label("low")
    jmp(x_dec, "low")
    wrap()


# counter for how many ticks we are high
@rp2.asm_pio()
def count_high():
    mov(x, invert(null))
    wait(1, pin, 0)
    label("high")
    jmp(x_dec, "next")
    label("next")
    jmp(pin, "high")
    mov(isr, x)
    push()


sm0 = rp2.StateMachine(0, square, sideset_base=p0)
sm1 = rp2.StateMachine(1, count_high, jmp_pin=p0)

# half a second - so should report 500,000,000ns
sm0.put(62500000 - 2)
sm0.exec("pull()")

# start the reader first as we are waiting on high
sm1.active(1)
sm0.active(1)

for j in range(10):
    high = 16 * (0xFFFFFFFF - sm1.get())
    print(high)

sm0.active(0)
sm1.active(0)

# tidy
p0.off()
