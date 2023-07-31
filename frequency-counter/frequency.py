# Usage: connect a jumper lead from GPIO0 to GPIO20 i.e.
# pin 1 to pin 26

from machine import mem32, Pin
import rp2


# register bases
CLOCKS_BASE = 0x40008000
IO_BANK0_BASE = 0x40014000

# standard square wave PIO program, counts down from content of
# OSR, with overhead of 2 => set the register as 2 fewer counts
# than wanted for high / low i.e. full period is 2 x (this + 2)
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


# output 1MHz square wave - to get that need to set high / low to
# 50 counts - 2 => 48 counts and set PIO frequency to 100 MHz
p0 = machine.Pin(0, machine.Pin.OUT)
sm0 = rp2.StateMachine(0, square, freq=100_000_000, sideset_base=p0)
sm0.put(50 - 2)
sm0.exec("pull()")

# square wave on
sm0.active(1)


# set GPIO20 to mode 8 i.e. frequency counter in, zero
mem32[IO_BANK0_BASE | 0xA4] = 0x8

# set up frequency counter - CLK_REG is 6MHz I believe
mem32[CLOCKS_BASE | 0x80] = 6000
mem32[CLOCKS_BASE | 0x8C] = 4
mem32[CLOCKS_BASE | 0x90] = 10

# read frequency from IN0
mem32[CLOCKS_BASE | 0x94] = 0x6

while mem32[CLOCKS_BASE | 0x98] & (1 << 8):
    pass

nn = mem32[CLOCKS_BASE | 0x9C]
khz = nn >> 4
frc = nn & 0xF
print(f"{khz + frc / 16:.1f} kHz")

# disable square output
sm0.active(0)
