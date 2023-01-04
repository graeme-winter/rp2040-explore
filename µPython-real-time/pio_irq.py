import time

from machine import Pin
import rp2

p0 = Pin(0)
p25 = Pin(25, Pin.OUT)

# counter program using side-set to control output
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def square():
    wrap_target()
    mov(x, osr).side(1)
    irq(0)
    label("high")
    jmp(x_dec, "high")
    mov(x, osr).side(0)
    irq(0)
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


# program to side-set the LED based on PIO irq
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def wait_irq():
    wrap_target()
    wait(1, irq, 0).side(1)
    irq(clear, 0)
    wait(1, irq, 0).side(0)
    irq(clear, 0)
    wrap()


sm0 = rp2.StateMachine(0, square, sideset_base=p0)
sm1 = rp2.StateMachine(1, count_high, jmp_pin=p0)
sm2 = rp2.StateMachine(2, wait_irq, sideset_base=p25)

# half a second - so should report 500,000,000 ns once things warm up
sm0.put(62500000 - 3)
sm0.exec("pull()")

sm2.active(1)
sm1.active(1)
sm0.active(1)

for j in range(10):
    high = 0xFFFFFFFF - sm1.get()
    print(f"{high * 16e-9:.3f} s / {2 * high} ticks")

sm0.active(0)
sm1.active(0)
sm2.active(0)


# tidy
p0.off()
p25.off()
