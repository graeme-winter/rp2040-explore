# sine wave data source -> generate 100,000 point sine wave buffer
# and then push this out through pio0 at 100kHz -> divider of 
# 1250 etc.

import math
from machine import Pin, mem32, UART
from uctypes import addressof
from rp2 import PIO, StateMachine, asm_pio

# DREQ definitions
DREQ_PIO0_TX0 = 0

# register definitions
PIO0_BASE = 0x50200000
PIO0_CTRL = PIO0_BASE + 0x00
PIO0_FSTAT = PIO0_BASE + 0x04
PIO0_TXF0 = PIO0_BASE + 0x10

# DMA registers
DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x00
CH0_WRITE_ADDR = DMA_BASE + 0x04
CH0_TRANS_COUNT = DMA_BASE + 0x08
CH0_CTRL_TRIG = DMA_BASE + 0x0C
CH0_CTRL = DMA_BASE + 0x1C

CH1_READ_ADDR = DMA_BASE + 0x40
CH1_WRITE_ADDR = DMA_BASE + 0x44
CH1_TRANS_COUNT = DMA_BASE + 0x48
CH1_CTRL_TRIG = DMA_BASE + 0x4C
CH1_CTRL = DMA_BASE + 0x5C

pins = [Pin(j) for j in range(8)]

@asm_pio(
    out_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW),
    out_shiftdir=PIO.SHIFT_RIGHT,
    fifo_join=PIO.JOIN_TX,
    autopull=True,
    pull_thresh=32,
)
def tick():
    wrap_target()
    out(pins, 8)
    wrap()


# set up data: 1kHz sine wave
COUNT = 100_000
data = bytearray(COUNT)

for j in range(100):
    data[j] = int(128 + 127 * math.sin(j * 2 * math.pi * 0.01))
    for k in range(1, 1000):
        data[j + 100 * k] = data[j]

# set up DMA
#        QUIET         DREQ                 CHAIN      READ INCR   4-byte     ENABLE
CTRL0 = (1 << 21) + (DREQ_PIO0_TX0 << 15) + (1 << 11) + (1 << 4) + (2 << 2) + (1 << 0)
CTRL0 = (1 << 21) + (DREQ_PIO0_TX0 << 15) + (0 << 11) + (1 << 4) + (2 << 2) + (1 << 0)
mem32[CH0_READ_ADDR] = addressof(data)
mem32[CH0_WRITE_ADDR] = PIO0_TXF0
mem32[CH0_TRANS_COUNT] = COUNT // 4
mem32[CH0_CTRL] = CTRL0
mem32[CH1_READ_ADDR] = addressof(data)
mem32[CH1_WRITE_ADDR] = PIO0_TXF0
mem32[CH1_TRANS_COUNT] = COUNT // 4
mem32[CH1_CTRL] = CTRL0
