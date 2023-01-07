from machine import mem32
from uctypes import addressof
from array import array

COUNT = 1024

target = array("H", [0 for j in range(COUNT)])
source = array("H", [0xFFFF])

print(addressof(target), addressof(source))

# DMA registers
DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x0
CH0_WRITE_ADDR = DMA_BASE + 0x4
CH0_TRANS_COUNT = DMA_BASE + 0x8
CH0_CTRL_TRIG = DMA_BASE + 0xC

QUIET = 0x1 << 21
DREQ = 0x3F << 15
WRITE_INCR = 0x1 << 5
DATA_SIZE = 0x1 << 2
ENABLE = 1

mem32[CH0_READ_ADDR] = addressof(source)
mem32[CH0_WRITE_ADDR] = addressof(target)
mem32[CH0_TRANS_COUNT] = COUNT
mem32[CH0_CTRL_TRIG] = QUIET + DREQ + WRITE_INCR + DATA_SIZE + ENABLE

BUSY = 0x1 << 24

while mem32[CH0_CTRL_TRIG] & BUSY:
    continue

for t in target:
    print(t)
