# manual PWM control over registers
from machine import mem32

# set up PWM function on GPIO
IO_BANK_BASE = 0x40014000
GPIO0_CTRL = IO_BANK_BASE + 0x4
mem32[GPIO0_CTRL] = 0x4

# activate PWM

PWM_TOP = 0x40050000
CH0_CSR = PWM_TOP + 0x0
CH0_DIV = PWM_TOP + 0x4
CH0_CTR = PWM_TOP + 0x8
CH0_CC = PWM_TOP + 0xC
CH0_TOP = PWM_TOP + 0x10

PWM_EN = PWM_TOP + 0xA0

mem32[CH0_CSR] = 0x0
mem32[CH0_DIV] = 125 << 4
mem32[CH0_TOP] = 999
mem32[CH0_CC] = 499
mem32[CH0_CSR] = 0x1
