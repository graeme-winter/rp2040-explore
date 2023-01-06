from machine import mem32
import time

# set up GPIO25 (the LED) by hand and switch it on and off by
# poking values into registers - see datasheet 2.19.6.1

led = 25

# have to set the pin to SIO mode in the control register
mem32[0x40014000 | 0xCC] = 0x5

# pad drive mode - 12mA
mem32[0x4001C000 | 0x68] = 0x3 << 4

# enable output
mem32[0xD0000000 | 0x20] = 0x1 << led


def on():
    # set the right bit as on
    mem32[0xD0000000 | 0x14] = 0x1 << led


def off():
    # set the right bit as clear
    mem32[0xD0000000 | 0x18] = 0x1 << led


for j in range(10):
    on()
    time.sleep(1)
    off()
    time.sleep(1)
