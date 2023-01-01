#include <stdio.h>

#include "hardware/gpio.h"
#include "hardware/irq.h"
#include "hardware/sync.h"
#include "hardware/timer.h"
#include "pico/stdlib.h"

// GPIO semaphore - arbitrary as not connected anywhere

#define OUT 18
#define IN 19

// clock

volatile uint32_t t0;
volatile uint32_t dt;

// IRQ handler

void __not_in_flash_func(irq_callback)(uint32_t gpio, uint32_t event) {
  dt = time_us_32() - t0;
  gpio_xor_mask(1 << GPIO_OUT);
}

int main() {
  setup_default_uart();

  gpio_init(OUT);
  gpio_set_dir(OUT, GPIO_OUT);

  gpio_init(IN);
  gpio_set_dir(IN, GPIO_IN);
  gpio_pull_down(IN);

  uint32_t mask = GPIO_IRQ_EDGE_RISE;
  gpio_set_irq_enabled_with_callback(GPIO_IN, mask, true, &irq_callback);

  while (true) {
    t0 = time_us_32();
    gpio_xor_mask(1 << GPIO_OUT);
    sleep_ms(1000);
    printf("%d\n", dt);
  }
}
