from uctypes import addressof
from machine import UART, Pin, mem32

uart0 = UART(0, baudrate=115200 * 16, tx=Pin(16), rx=Pin(17))

SIZE = 100_000

tx = bytearray(SIZE)

for j in range(SIZE):
    tx[j] = j % 250

UART0_BASE = 0x40034000
UART0_DR = UART0_BASE + 0x0
UART0DMACR = UART0_BASE + 0x48

DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x00
CH0_WRITE_ADDR = DMA_BASE + 0x04
CH0_TRANS_COUNT = DMA_BASE + 0x08
CH0_CTRL_TRIG = DMA_BASE + 0x0C

mem32[UART0DMACR] = 1 << 1

mem32[CH0_READ_ADDR] = addressof(tx)
mem32[CH0_WRITE_ADDR] = UART0_DR
mem32[CH0_TRANS_COUNT] = SIZE
mem32[CH0_CTRL_TRIG] = (1 << 21) + (20 << 15) + (1 << 4) + (1 << 1) + (1 << 0)

BUSY = 1 << 24

while mem32[CH0_CTRL_TRIG] & BUSY:
    continue

print(f"Sent {SIZE} bytes")
