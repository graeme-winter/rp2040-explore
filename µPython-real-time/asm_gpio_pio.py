import machine
import time
import rp2
import _thread
from uctypes import addressof
import array

# constants
SIO_BASE = const(0xD0000000)
GPIO_OUT = const(SIO_BASE + 0x10)
GPIO_OUT_XOR = const(SIO_BASE + 0x1C)

# DMA
DREQ_PIO0_RX0 = 4

# register definitions
PIO0_BASE = 0x50200000
PIO0_CTRL = PIO0_BASE + 0x0
PIO0_FSTAT = PIO0_BASE + 0x4
PIO0_RXF0 = PIO0_BASE + 0x20

# DMA registers
DMA_BASE = 0x50000000
CH0_READ_ADDR = DMA_BASE + 0x0
CH0_WRITE_ADDR = DMA_BASE + 0x4
CH0_TRANS_COUNT = DMA_BASE + 0x8
CH0_CTRL_TRIG = DMA_BASE + 0xC

# configure GPIO
led = machine.Pin(25, machine.Pin.OUT)
out_pin = machine.Pin(0, machine.Pin.OUT)
out_pin.off()


def dumb():
    for j in range(20):
        led.toggle()
        time.sleep(0.5)


def sio():
    for j in range(20):
        machine.mem32[GPIO_OUT_XOR] = 1 << 25
        time.sleep(0.5)


# set up DMA
COUNT = 100
buffer = array.array("I", [0 for j in range(COUNT)])

# set up DMA from PIO ISR
QUIET = 0x1 << 21
DREQ = DREQ_PIO0_RX0 << 15
WRITE_INCR = 0x1 << 5
DATA_SIZE = 0x2 << 2
ENABLE = 0x1

# clear FIFO
while not (machine.mem32[PIO0_FSTAT] & (1 << 9)):
    _ = machine.mem32[PIO0_RXF0]

machine.mem32[CH0_READ_ADDR] = PIO0_RXF0
machine.mem32[CH0_WRITE_ADDR] = addressof(buffer)
machine.mem32[CH0_TRANS_COUNT] = COUNT

# wait(1, pin, 0) instruction takes 1 tick -> remove this from count
# and add a nop() to make it up to two ticks we are losing as that
# is what 1 lower count means
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


sm = rp2.StateMachine(0, count_high, jmp_pin=out_pin)


def count(sm, n, out_pin):
    for j in range(n):
        n = sm.get()
        print("%d ns" % int((0xFFFFFFFF - n) * 16.0))


@micropython.asm_thumb
def asm(r0, r1, r2):
    # save the OUT_XOR address
    mov(r7, r0)

    # save the number of cycles to count to
    mov(r6, r1)
    sub(r6, r6, 1)

    # 10% duty cycle
    mov(r3, 9)
    mul(r3, r1)
    sub(r3, r3, 1)

    # save the number of repeats
    mov(r5, r2)

    # set up r4 with bit I want - 1 << 25 for LED + GPIO0
    mov(r4, 1)
    mov(r2, 25)
    lsl(r4, r2)
    add(r4, r4, 1)

    # start of cycle loop
    label(cycle)

    # switch on
    str(r4, [r7, 0])
    mov(r2, r6)
    label(on)
    sub(r2, r2, 1)
    cmp(r2, 0)
    nop()
    bne(on)

    # 4 nops to pad on to 5 extra cycles
    nop()
    nop()
    nop()
    nop()

    # switch off
    str(r4, [r7, 0])
    mov(r2, r3)
    label(off)
    sub(r2, r2, 1)
    cmp(r2, 0)
    nop()
    bne(off)

    sub(r5, r5, 1)
    cmp(r5, 0)
    bne(cycle)


machine.mem32[CH0_CTRL_TRIG] = QUIET + DREQ + WRITE_INCR + DATA_SIZE + ENABLE
sm.active(1)
asm(GPIO_OUT_XOR, 25, COUNT)

# wait for DMA completion
BUSY = 0x1 << 24

while machine.mem32[CH0_CTRL_TRIG] & BUSY:
    continue

sm.active(0)

for j in range(COUNT):
    print("%d ns" % int((0xFFFFFFFF - buffer[j]) * 16.0))
