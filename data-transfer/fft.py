import numpy
import serial
from matplotlib import pyplot

tty = serial.Serial("/dev/tty.usbmodem14101", 115200 * 16)
SIZE = 100_000_000
bytes = tty.read(SIZE)
tty.close()
x = numpy.array(range(SIZE))
y = numpy.frombuffer(bytes, dtype=numpy.uint8).astype(numpy.float32)
y -= numpy.mean(y)
fft = numpy.abs(numpy.fft.rfft(y))
freq = numpy.fft.rfftfreq(y.size, d=1e-5)
pyplot.plot(freq, fft)
pyplot.yscale("log")
pyplot.show()
