# sine wave data source -> generate 100,000 point sine wave buffer
# and then push this out through pio0 at 100kHz -> divider of
# 1250 etc.

import math
from machine import Pin, mem32, UART
from uctypes import addressof
from rp2 import PIO, StateMachine, asm_pio
import _thread

# DREQ definitions
DREQ_PIO0_TX0 = const(0)

# register definitions
PIO0_BASE = const(0x50200000)
PIO0_CTRL = const(PIO0_BASE + 0x00)
PIO0_FSTAT = const(PIO0_BASE + 0x04)
PIO0_TXF0 = const(PIO0_BASE + 0x10)

# DMA registers
DMA_BASE = const(0x50000000)
CH0_READ_ADDR = const(DMA_BASE + 0x00)
CH0_WRITE_ADDR = const(DMA_BASE + 0x04)
CH0_TRANS_COUNT = const(DMA_BASE + 0x08)
CH0_CTRL_TRIG = const(DMA_BASE + 0x0C)
CH0_CTRL = const(DMA_BASE + 0x10)

CH1_READ_ADDR = const(DMA_BASE + 0x40)
CH1_WRITE_ADDR = const(DMA_BASE + 0x44)
CH1_TRANS_COUNT = const(DMA_BASE + 0x48)
CH1_CTRL_TRIG = const(DMA_BASE + 0x4C)
CH1_CTRL = const(DMA_BASE + 0x50)

MULTI_CHAN_TRIGGER = const(DMA_BASE + 0x430)

pins = [Pin(j) for j in range(8)]
led = Pin(25, Pin.OUT)


@asm_pio(
    out_init=(
        PIO.OUT_LOW,
        PIO.OUT_LOW,
        PIO.OUT_LOW,
        PIO.OUT_LOW,
        PIO.OUT_LOW,
        PIO.OUT_LOW,
        PIO.OUT_LOW,
        PIO.OUT_LOW,
    ),
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
COUNT = const(125_000)
data = bytearray(COUNT)

for j in range(1250):
    data[j] = int(128 + 127 * math.sin(0.0008 * 2 * math.pi * j))
    for k in range(1, 100):
        data[j + 1250 * k] = data[j]

# FIXME run DMA in a second thread so the main thread could be used to
# update the data array (say)

# set up DMA
#        QUIET         DREQ                 CHAIN      READ INCR   4-byte     ENABLE
CTRL0 = (1 << 21) + (DREQ_PIO0_TX0 << 15) + (1 << 11) + (1 << 4) + (2 << 2) + (3 << 0)
CTRL1 = (1 << 21) + (DREQ_PIO0_TX0 << 15) + (0 << 11) + (1 << 4) + (2 << 2) + (3 << 0)

mem32[CH0_READ_ADDR] = addressof(data)
mem32[CH0_WRITE_ADDR] = PIO0_TXF0
mem32[CH0_TRANS_COUNT] = COUNT // 4
mem32[CH0_CTRL] = CTRL0

mem32[CH1_READ_ADDR] = addressof(data)
mem32[CH1_WRITE_ADDR] = PIO0_TXF0
mem32[CH1_TRANS_COUNT] = COUNT // 4
mem32[CH1_CTRL] = CTRL1

# set up PIO
sm0 = StateMachine(0, tick, freq=1_250_000, out_base=pins[0])

COUNT4 = const(COUNT // 4)
PTR = addressof(data)

BUSY = 1 << 24


@micropython.viper
def go():
    # trigger DMA0 and PIO
    mem32[MULTI_CHAN_TRIGGER] = 1
    mem32[PIO0_CTRL] = 1

    while True:
        while mem32[CH0_CTRL_TRIG] & BUSY:
            continue
        mem32[CH0_READ_ADDR] = PTR
        mem32[CH0_WRITE_ADDR] = PIO0_TXF0
        mem32[CH0_CTRL] = CTRL0
        mem32[CH0_TRANS_COUNT] = COUNT4
        while mem32[CH1_CTRL_TRIG] & BUSY:
            continue
        mem32[CH1_READ_ADDR] = PTR
        mem32[CH1_WRITE_ADDR] = PIO0_TXF0
        mem32[CH1_CTRL] = CTRL1
        mem32[CH1_TRANS_COUNT] = COUNT4


_thread.start_new_thread(go, ())
