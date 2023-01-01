#include <stdio.h>

#include "hardware/gpio.h"
#include "hardware/irq.h"
#include "hardware/sync.h"
#include "hardware/timer.h"
#include "pico/stdlib.h"

#include "count.pio.h"

// GPIO semaphore - arbitrary as not connected anywhere

#define OUT 18
#define IN 19

// clock

volatile uint32_t t0;
volatile uint32_t dt;

// IRQ handler

void __not_in_flash_func(irq_callback)(uint32_t gpio, uint32_t event) {
  dt = time_us_32() - t0;
  gpio_xor_mask(1 << OUT);
}

int main() {
  setup_default_uart();

  gpio_init(OUT);
  gpio_set_dir(OUT, GPIO_OUT);

  gpio_init(IN);
  gpio_set_dir(IN, GPIO_IN);
  gpio_pull_down(IN);

  uint32_t mask = GPIO_IRQ_EDGE_RISE;
  gpio_set_irq_enabled_with_callback(IN, mask, true, &irq_callback);

  uint32_t offset = pio_add_program(pio0, &count_program);
  count_program_init(pio0, 0, offset_0, IN);
  pio_sm_set_enabled(pio0, 0, true);

  while (true) {
    t0 = time_us_32();
    gpio_xor_mask(1 << OUT);
    sleep_ms(1000);
    uint32_t count = 0xfffffffe - pio_sm_get_blocking(pio0, 0);
    printf("%d %d\n", dt, count);
  }
}
