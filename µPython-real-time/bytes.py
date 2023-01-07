from uctypes import addressof
from machine import mem16, mem32
from array import array

scratch = array("H", [0xFFFF for _ in range(1024)])

address = addressof(scratch)

for j in range(0, 2048, 2):
    mem16[address + j] = j // 2

for s in scratch:
    print(s)
