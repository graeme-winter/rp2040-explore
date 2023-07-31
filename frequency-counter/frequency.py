from machine import mem32, Pin
import rp2

p0 = machine.Pin(0, machine.Pin.OUT)


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


# output 1MHz square wave
sm0 = rp2.StateMachine(0, square, freq=100_000_000, sideset_base=p0)
sm0.put(50 - 2)
sm0.exec("pull()")

sm0.active(1)

CLOCKS_BASE = 0x40008000
IO_BANK0_BASE = 0x40014000

clk = machine.Pin(20, Pin.IN)

# overwrite function
mem32[IO_BANK0_BASE | 0xA4] = 0x8

mem32[CLOCKS_BASE | 0x80] = 6000
mem32[CLOCKS_BASE | 0x8C] = 4
mem32[CLOCKS_BASE | 0x90] = 10

mem32[CLOCKS_BASE | 0x94] = 0x6

while mem32[CLOCKS_BASE | 0x98] & (1 << 8):
    pass

nn = mem32[CLOCKS_BASE | 0x9C]
khz = nn >> 4
frc = nn & 0xF
print(f"{khz + frc / 16:.1f} kHz")

sm0.active(0)
