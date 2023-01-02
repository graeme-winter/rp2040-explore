#include <stdio.h>

#include "hardware/gpio.h"
#include "hardware/irq.h"
#include "hardware/sync.h"
#include "hardware/timer.h"
#include "pico/stdlib.h"

#include "count.pio.h"

// GPIO semaphores - wired together

#define PIO 17
#define OUT 18
#define IN 19

// IRQ handler

void __not_in_flash_func(irq_callback)(void) {
  gpio_xor_mask(1 << OUT);
  gpio_acknowledge_irq(IN, IO_IRQ_BANK0);
}

int main() {
  setup_default_uart();

  gpio_init(OUT);
  gpio_set_dir(OUT, GPIO_OUT);

  gpio_init(IN);
  gpio_set_dir(IN, GPIO_IN);
  gpio_pull_down(IN);

  uint32_t mask = GPIO_IRQ_EDGE_RISE;
  irq_set_exclusive_handler(IO_IRQ_BANK0, irq_callback);
  gpio_set_irq_enabled(IN, mask, true);
  irq_set_enabled(IO_IRQ_BANK0, true);

  uint32_t offset = pio_add_program(pio0, &count_program);
  count_program_init(pio0, 0, offset, PIO);
  pio_sm_set_enabled(pio0, 0, true);

  while (true) {
    gpio_xor_mask(1 << OUT);
    sleep_ms(50);
    uint32_t count = 0xffffffff - pio_sm_get_blocking(pio0, 0);
    printf("%d cycles\n", 5 * count);
  }
}
