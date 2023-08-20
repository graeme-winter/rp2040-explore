# Frequency counter with example signal generator
#
# Counts pulses in on GPIO20 (used as this is GCLKIN) gated for
# 1s based on second PIO program raising LED. Includes GPIO drive
# test program at 1MHz on GPIO0

from machine import Pin
import rp2
import time


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def gate():
    pull()
    mov(x, osr).side(1)
    label("high")
    jmp(x_dec, "high")
    nop().side(0)
    label("halt")
    jmp("halt")


@rp2.asm_pio()
def high():
    mov(x, null)
    label("entry")
    jmp(pin, "start")
    jmp("entry")
    label("start")
    wait(1, pin, 0)
    wait(0, pin, 0)
    jmp(x_dec, "next")
    label("next")
    jmp(pin, "start")
    mov(isr, x)
    push()
    label("halt")
    jmp("halt")


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


p0 = machine.Pin(0, machine.Pin.OUT)
sm0 = rp2.StateMachine(0, square, freq=10_000_000, sideset_base=p0)
sm0.put(5 - 2)
sm0.exec("pull()")

sm0.active(1)

# Pin(gate) and Pin(count)
pg = Pin(25)
pc = Pin(20, Pin.IN)

sm6 = rp2.StateMachine(6, gate, sideset_base=pg)
sm6.put(125_000_000 - 2)

sm7 = rp2.StateMachine(7, high, jmp_pin=pg, in_base=pc)

sm7.active(1)
sm6.active(1)

count = int((0xFFFFFFFF - sm7.get()))

sm6.active(0)
sm7.active(0)

print(f"{count} Hz")
sm0.active(0)
