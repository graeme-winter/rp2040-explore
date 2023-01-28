from machine import Pin, mem32, UART
from uctypes import addressof
import time

# UART stuff
uart0 = UART(0, baudrate=115200 * 16, tx=Pin(16), rx=Pin(17))

UART0_BASE = 0x40034000
UART0_DR = UART0_BASE + 0x0
UART0DMACR = UART0_BASE + 0x48

# enable UART0 DMA (TX)
mem32[UART0DMACR] = 1 << 1

# set up ADC channel

# zero-out the pin (set the function to NULL, needed for ADC)
IO_BANK_BASE = 0x40014000
GPIO26_CTRL = IO_BANK_BASE + 0xD4
mem32[GPIO26_CTRL] = 0b11111

# ADC inc. FIFO - registers
ADC_BASE = 0x4004C000
ADC_CS = ADC_BASE + 0x0
ADC_RESULT = ADC_BASE + 0x4
ADC_FCS = ADC_BASE + 0x8
ADC_FIFO = ADC_BASE + 0xC
ADC_DIV = ADC_BASE + 0x10


# DMA registers
DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x0
CH0_WRITE_ADDR = DMA_BASE + 0x4
CH0_TRANS_COUNT = DMA_BASE + 0x8
CH0_CTRL_TRIG = DMA_BASE + 0xC

# control register: see table 124 in data sheet - follow ADC DREQ,
# increment write pointer, data size 2 bytes (N.B. will be 12 bit
# not 16 like usual ADC with read_u16())
#
# DREQ 36 / 0x24 for ADC for CTRL.DREQ_SEL
QUIET = 0x1 << 21
DREQ_ADC = 0x24 << 15
DATA_SIZE = 0x0 << 2
ENABLE = 0x1

mem32[CH0_READ_ADDR] = ADC_FIFO
mem32[CH0_WRITE_ADDR] = UART0_DR
mem32[CH0_TRANS_COUNT] = 100000
mem32[CH0_CTRL_TRIG] = QUIET + DREQ_ADC + DATA_SIZE + ENABLE

# drain FIFO before we start
while (mem32[ADC_FCS] >> 16) & 0xF:
    _ = mem32[ADC_FIFO]

# ADC_FIFO configuration - set threshold, clear, enable DREQ and enable FIFO
THRESH = 0x1 << 24
CLEAR = (0x1 << 11) + (0x1 << 10)
DREQ_EN = 0x1 << 3
SHIFT = 0x1 << 1
FIFO_EN = 0x1
mem32[ADC_FCS] = THRESH + CLEAR + DREQ_EN + SHIFT + FIFO_EN

# 100000 samples / second
mem32[ADC_DIV] = 479 << 8

# ADC configuration - since using channel 0 only just enable and start many
t0 = time.ticks_us()
mem32[ADC_CS] = 0x8 + 0x1

BUSY = 0x1 << 24

while mem32[CH0_CTRL_TRIG] & BUSY:
    continue
t1 = time.ticks_us()

mem32[ADC_CS] = 0x0
print(f"100000 samples transferred in {1e-6 * (t1 - t0):.2f}s")
