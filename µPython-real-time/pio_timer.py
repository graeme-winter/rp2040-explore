from machine import Pin, PWM
import rp2

# deterministic source for 500µs pulses (reliably reproduced on 'scope)
p0 = Pin(0, Pin.OUT)

pwm = PWM(p0)
pwm.freq(100)
pwm.duty_ns(500000)


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

for j in range(100):
    delta = 0xFFFFFFFF - sm.get()
    print(f"{delta} counts / {delta*16} ns")

sm.active(0)
