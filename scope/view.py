import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy
import serial

tty = serial.Serial("/dev/tty.usbmodem14101", 115200 * 8)

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)

x = numpy.array(range(2000))
y = numpy.array([0 for j in range(2000)], dtype=numpy.uint8)


def update(i):
    global y
    y = numpy.roll(y, -500)
    bytes = tty.read(500)
    y[-500:] = numpy.frombuffer(bytes, dtype=numpy.uint8)
    ax1.clear()
    ax1.plot(x, y)


ani = animation.FuncAnimation(fig, update, interval=100)
plt.show()
