from machine import Pin, mem32
from rp2 import PIO, StateMachine, asm_pio
from uctypes import addressof

# state maachine allocation (both on PIO0)
# machine 0 -> signal generator
# machine 1 -> signal reader

# useful DREQ definitions
DREQ_PIO0_RX1 = 22

# register definitions
PIO0_BASE = 0x50200000
PIO0_CTRL = PIO0_BASE + 0x0
PIO0_FSTAT = PIO0_BASE + 0x4
PIO0_RXF1 = PIO0_BASE + 0x24

# DMA registers
DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x0
CH0_WRITE_ADDR = DMA_BASE + 0x4
CH0_TRANS_COUNT = DMA_BASE + 0x8
CH0_CTRL_TRIG = DMA_BASE + 0xC

# use pin0 as sideset, 1...5 as "data"
pins = [Pin(j) for j in range(6)]


@asm_pio(
    sideset_init=PIO.OUT_LOW,
    out_init=(PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW, PIO.OUT_LOW),
    out_shiftdir=PIO.SHIFT_RIGHT,
)
def saw():
    wrap_target()
    set(x, 31)
    label("tick")
    mov(osr, x)
    out(pins, 5).side(1)
    nop()
    nop().side(0)
    jmp(x_dec, "tick")
    wrap()


# auto-push / push on 32 bits to FIFO / join FIFOs
@asm_pio(autopush=True, push_thresh=32, fifo_join=PIO.JOIN_RX)
def eight_bits_in():
    wrap_target()
    in_(pins, 8)
    wrap()


# set up scratch array to copy results to
COUNT = 256
scratch = bytearray(COUNT)

# set up DMA from PIO ISR
QUIET = 0x1 << 21
DREQ = DREQ_PIO0_RX1
WRITE_INCR = 0x1 << 5
DATA_SIZE = 0x0
ENABLE = 0x1

# clear FIFO
while mem32[PIO0_FSTAT] & (1 << 9):
    _ = mem32[PIO0_RXF1]

mem32[CH0_READ_ADDR] = PIO0_RXF1
mem32[CH0_WRITE_ADDR] = addressof(scratch)
mem32[CH0_TRANS_COUNT] = COUNT
mem32[CH0_CTRL_TRIG] = QUIET + DREQ + WRITE_INCR + DATA_SIZE + ENABLE

# trigger DMA on DREQ from PIO (1 word depth trigger)
# read bytes for as long as needed (should be multiple of 4)
tick = StateMachine(0, saw, freq=12500, sideset_base=pins[0], out_base=pins[1])

# this is reading eight pins not 6 bit I think that doesn't matter as all pins
# are wired for input
bits = StateMachine(1, eight_bits_in, freq=12500, in_base=pins[0])

# activate
PIO0_CTRL = 0x3

# wait for DMA completion
BUSY = 0x1 << 24

while mem32[CH0_CTRL_TRIG] & BUSY:
    continue

# stop
PIO0_CTRL = 0

for j in range(COUNT):
    print(scratch[j])