from uctypes import addressof
from machine import mem32, Pin, PWM
from array import array
import rp2
import math
import time
import random

# set up clock signal
pin = Pin(0, Pin.OUT)
pwm = PWM(pin)
pwm.freq(1000)
pwm.duty_u16(0x4000)

scratch = array("I", [0x0, 0x0])
address = addressof(scratch)

# DREQ definitions
DREQ_PIO0_RX0 = 4 << 15
DREQ_PIO0_RX1 = 5 << 15

# register definitions
PIO0_BASE = 0x50200000
PIO0_CTRL = PIO0_BASE + 0x00
PIO0_FSTAT = PIO0_BASE + 0x04
PIO0_RXF0 = PIO0_BASE + 0x20
PIO0_RXF1 = PIO0_BASE + 0x24

# DMA registers
DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x0
CH0_WRITE_ADDR = DMA_BASE + 0x4
CH0_TRANS_COUNT = DMA_BASE + 0x8
CH0_CTRL_TRIG = DMA_BASE + 0xC

CH1_READ_ADDR = DMA_BASE + 0x40
CH1_WRITE_ADDR = DMA_BASE + 0x44
CH1_TRANS_COUNT = DMA_BASE + 0x48
CH1_CTRL_TRIG = DMA_BASE + 0x4C

QUIET = 0x1 << 21
DATA_SIZE = 0x2 << 2
ENABLE = 0x1

mem32[CH0_READ_ADDR] = PIO0_RXF0
mem32[CH0_WRITE_ADDR] = address
mem32[CH0_TRANS_COUNT] = 4000
mem32[CH0_CTRL_TRIG] = QUIET + DREQ_PIO0_RX0 + DATA_SIZE + ENABLE

mem32[CH1_READ_ADDR] = PIO0_RXF1
mem32[CH1_WRITE_ADDR] = address + 4
mem32[CH1_TRANS_COUNT] = 4000
mem32[CH1_CTRL_TRIG] = QUIET + DREQ_PIO0_RX1 + DATA_SIZE + ENABLE


@rp2.asm_pio()
def count_high():
    mov(x, invert(null))
    jmp(x_dec, "wait")
    label("wait")
    wait(1, pin, 0)
    nop()
    label("high")
    jmp(x_dec, "next")
    label("next")
    jmp(pin, "high")
    mov(isr, x)
    push()


@rp2.asm_pio()
def count_low():
    mov(x, invert(null))
    jmp(x_dec, "wait")
    label("wait")
    wait(0, pin, 0)
    label("next")
    jmp(pin, "out")
    jmp(x_dec, "next")
    label("out")
    mov(isr, x)
    push()


sm0 = rp2.StateMachine(0, count_low, jmp_pin=pin, in_base=pin)
sm1 = rp2.StateMachine(1, count_high, jmp_pin=pin, in_base=pin)

BUSY = 0x1 << 24

mem32[PIO0_CTRL] = 0x3

while (mem32[CH0_CTRL_TRIG] & BUSY) or (mem32[CH1_CTRL_TRIG] & BUSY):
    time.sleep(0.1)
    low = int((0xFFFFFFFF - scratch[0]) * 16.0)
    high = int((0xFFFFFFFF - scratch[1]) * 16.0)
    print("%d %d %d" % (low, high, low + high))
    continue

mem32[PIO0_CTRL] = 0x0
