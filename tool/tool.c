#include "hardware/dma.h"
#include "hardware/pio.h"
#include "hardware/timer.h"
#include "pico.h"
#include "pico/stdlib.h"
#include <stdio.h>

int main() {
  unsigned int counter = 0;

  stdio_init_all();

  while (true) {
    printf("Counter: %d\n", counter);
    counter++;
    sleep_ms(1000);
  }

  return 0;
}
