import time

from machine import Pin
import rp2

p0 = Pin(0, Pin.OUT)


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


sm = rp2.StateMachine(0, count_high, jmp_pin=p0)

sm.active(1)

# target time for sleeping, ms
delta_ms = 50

for j in range(100):
    p0.on()
    time.sleep_ms(delta_ms)
    p0.off()
    delta = (16 * (0xFFFFFFFF - sm.get())) - delta_ms * 1_000_000
    print(f"∂ = {delta} ns")

sm.active(0)
