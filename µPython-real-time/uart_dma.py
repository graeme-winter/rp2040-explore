from uctypes import addressof
from machine import UART, Pin, mem32
import time

uart0 = UART(0, baudrate=1000000, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=1000000, tx=Pin(8), rx=Pin(9))

# DMA to get the data from the input buffer to the UART watching
# DREQ 20/21/22/23 TX/RX for UART0/1. Input pacing will be to keep
# the FIFO for write to UART full (which in this example is currently
# UART1) and the output pacing will be to act as a preference to a
# busy loop. Only problem is I will need to know how many words
# need to be moved.

# memory wise can easily set aside 100,000 bytes as scratch arrays
# so for this work use 2 x 50,000 byte. Looks like should be able to
# move 14,400 bytes / second at the baud rate above -> should take a
# few seconds to move this data (and thus it is a meaningful example.)

SIZE = 50_000

tx = bytearray(SIZE)
rx = bytearray(SIZE)

for j in range(SIZE):
    tx[j] = j % 250

# UART registers
# UART0 and UART1 registers start at base addresses of 0x40034000
# and 0x40038000 - most of the UART set up is _not_ by messing with
# registers but the DMA / triggering will be.

UART0_BASE = 0x40034000
UART0_DR = UART0_BASE + 0x0
UART0DMACR = UART0_BASE + 0x48

UART1_BASE = 0x40038000
UART1DMACR = UART1_BASE + 0x48
UART1_DR = UART1_BASE + 0x0

# XIP_SSI_BASE = 0x18000000

# set up the DMAs - this will be the first time I have used two DMA
# channels at the same time (something something priority?) - channel
# 0: UART0 -> rx buffer 1: tx buffer -> UART1. Rembering that there
# four register views for each DMA the offset between channel 0, 1
# registers is 0x40.

DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x00
CH0_WRITE_ADDR = DMA_BASE + 0x04
CH0_TRANS_COUNT = DMA_BASE + 0x08
CH0_CTRL_TRIG = DMA_BASE + 0x0C

CH1_READ_ADDR = DMA_BASE + 0x40
CH1_WRITE_ADDR = DMA_BASE + 0x44
CH1_TRANS_COUNT = DMA_BASE + 0x48
CH1_CTRL_TRIG = DMA_BASE + 0x4C

# set up the read back from the UART0 to the rx buffer - SIZE
# words at 8 bit. N.B. this one is incrementing the write.
# INCR_READ is bit 4, WRITE is bit 5. Also probably need to set
# bit 1 to indicate that this is a high priority channel (don't
# know how much that will matter.)

# enable UART0 DMA (RX)
mem32[UART0DMACR] = 1 << 0

mem32[CH0_READ_ADDR] = UART0_DR
mem32[CH0_WRITE_ADDR] = addressof(rx)
mem32[CH0_TRANS_COUNT] = SIZE

# quiet + dreq-uart0-rx + write-incr + enable (byte size default)
mem32[CH0_CTRL_TRIG] = (1 << 21) + (21 << 15) + (1 << 5) + (1 << 1) + (1 << 0)

# enable UART1 DMA (TX)
mem32[UART1DMACR] = 1 << 1

mem32[CH1_READ_ADDR] = addressof(tx)
mem32[CH1_WRITE_ADDR] = UART1_DR
mem32[CH1_TRANS_COUNT] = SIZE

# quiet + dreq-uart0-rx + read-incr + enable (byte size default)
mem32[CH1_CTRL_TRIG] = (1 << 21) + (22 << 15) + (1 << 4) + (1 << 1) + (1 << 0)

BUSY = 1 << 24

while mem32[CH1_CTRL_TRIG] & BUSY:
    continue

while mem32[CH0_CTRL_TRIG] & BUSY:
    continue

for j in range(SIZE):
    assert tx[j] == rx[j]
    assert rx[j] == j % 250
