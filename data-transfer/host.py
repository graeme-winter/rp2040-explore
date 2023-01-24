import numpy
import serial

tty = serial.Serial("/dev/tty.usbmodem14101", 115200 * 16)

SIZE = 200_000

bytes = tty.read(SIZE)
data = numpy.frombuffer(bytes, dtype=numpy.uint8).astype(numpy.uint32)
print(numpy.sum(data))
