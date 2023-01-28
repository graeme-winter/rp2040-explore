import numpy
import serial
from matplotlib import pyplot

tty = serial.Serial("/dev/tty.usbmodem14101", 115200 * 16)

bytes = tty.read(1000000)
data = numpy.frombuffer(bytes, dtype=numpy.uint8).astype(numpy.uint32)
print(numpy.sum(data))
tty.close()

pyplot.plot(data)
pyplot.show()
