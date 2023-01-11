from machine import Pin
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
PIO0_RXF1 = PIO0_BASE + 0x24

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
scratch = bytearray(10240)
ptr = addressof(scratch)
# set up DMA from PIO ISR
# trigger DMA on DREQ from PIO (1 word depth trigger)
# read bytes for as long as needed (should be multiple of 4)

tick = StateMachine(0, saw, freq=12500, sideset_base=pins[0], out_base=pins[1])

# this is reading eight pins not 6 bit I think that doesn't matter as all pins
# are wired for input
bits = StateMachine(1, eight_bits_in, freq=12500, in_base=pins[0])

# activate
PIO0_CTRL = 0x3

# wait for DMA completion
