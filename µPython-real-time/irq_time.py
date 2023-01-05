from machine import Pin
import rp2


p0 = Pin(0, Pin.OUT)
p0.irq(lambda pin: pin.off(), Pin.IRQ_RISING)
p0.off()

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


sm1 = rp2.StateMachine(1, count_high, jmp_pin=p0)

sm1.active(1)

for j in range(10):
    p0.on()
    high = 0xFFFFFFFF - sm1.get()
    print(f"{2 * high} cycles")

sm1.active(0)


# tidy
p0.off()
