import numpy
import serial
from matplotlib import pyplot

SIZE = 1_000_000
tty = serial.Serial("/dev/tty.usbmodem14101", 115200 * 16)
bytes = tty.read(SIZE)
tty.close()

x = numpy.array(range(1000))
y = numpy.frombuffer(bytes, dtype=numpy.uint8).astype(numpy.uint32)

y0 = y[:1000]

for k in range(1, 1000):
    y0 += y[k * 1000 : (k + 1) * 1000]

pyplot.plot(x, y0)
pyplot.show()
