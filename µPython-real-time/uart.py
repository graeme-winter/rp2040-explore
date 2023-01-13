from machine import UART, Pin
import time

uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

tx = bytearray(range(256))

uart1.write(tx)

rx = uart0.read()

for j in range(256):
    assert tx[j] == rx[j]
