from machine import Pin
import rp2
import time


# this tells the PIO program we have two output pins
@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
def square():
    mov(osr, isr)
    out(pins, 2)
    mov(x, y)
    label("a")
    jmp(x_dec, "a")
    nop()
    out(pins, 2)
    mov(x, y)
    label("b")
    jmp(x_dec, "b")
    nop()
    out(pins, 2)
    mov(x, y)
    label("c")
    jmp(x_dec, "c")
    nop()
    out(pins, 2)
    mov(x, y)
    label("d")
    jmp(x_dec, "d")


@rp2.asm_pio()
def count_high():
    mov(x, invert(null))
    jmp(x_dec, "wait")
    label("wait")
    wait(1, pin, 0)
    nop()
    label("high")
    jmp(x_dec, "next")
    label("next")
    jmp(pin, "high")
    mov(isr, x)
    push()


p0 = machine.Pin(0, machine.Pin.OUT)
p1 = machine.Pin(1, machine.Pin.OUT)

sm0 = rp2.StateMachine(0, square, out_base=p0)
sm0.put(62_500_000 - 4)
sm0.exec("pull()")
sm0.exec("mov(y, osr)")
sm0.put(0b01111000 << 24)
sm0.exec("pull()")
sm0.exec("mov(isr, osr)")

# very important in_base and jmp_pin point to the same pin
sm1 = rp2.StateMachine(1, count_high, jmp_pin=p1, in_base=p1)

sm1.active(1)
sm0.active(1)

for j in range(100):
    count = sm1.get()
    print("%d ns" % int((0xFFFFFFFF - count) * 16.0))

sm1.active(0)
sm0.active(0)
