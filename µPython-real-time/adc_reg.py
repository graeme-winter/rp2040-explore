from machine import mem32

# prepare the pin (set the function to NULL which is 0b11111, needed for ADC)
IO_BANK_BASE = 0x40014000
GPIO26_CTRL = IO_BANK_BASE + 0xD4
mem32[GPIO26_CTRL] = 0b11111

# configure the ADC inc. FIFO - registers
ADC_BASE = 0x4004C000
ADC_CS = ADC_BASE + 0x0
ADC_RESULT = ADC_BASE + 0x4

# trigger ADC for one read
mem32[ADC_CS] = 0x4 + 0x1

# read value
result = mem32[ADC_RESULT]

# report the value remembering that the range is 12 but not 16
print(result)
