import numpy
import serial
from matplotlib import pyplot

tty = serial.Serial("/dev/tty.usbmodem14101", 115200 * 16)

SIZE = 100_000

bytes = tty.read(SIZE)
data = numpy.frombuffer(bytes, dtype=numpy.uint8).astype(numpy.uint32)

tty.close()

x = numpy.array(range(1000))
y = data.astype(numpy.uint8)

y0 = y[1000:2000]
y1 = y[-2000:-1000]

pyplot.plot(x, y0)
pyplot.plot(x, y1)
pyplot.show()
