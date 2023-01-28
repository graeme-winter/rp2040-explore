from machine import UART, Pin
import _thread
import time

uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
uart1 = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

tx = bytearray(1000)

for j in range(1000):
    tx[j] = j % 250

rx = bytearray(1000)

nn = 0


def reader(buffer):
    global nn
    nn = None
    while nn is None:
        nn = uart0.readinto(buffer)
    print("Done reading:", nn)


_thread.start_new_thread(reader, (rx,))
nw = uart1.write(tx)
print("Done writing:", nw)

time.sleep(0.1)

assert nn == 1000

for j in range(1000):
    assert tx[j] == rx[j]
