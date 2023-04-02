#include "hardware/dma.h"
#include "hardware/pio.h"
#include "hardware/timer.h"
#include "hardware/uart.h"
#include "pico.h"
#include "pico/stdlib.h"
#include <stdio.h>
#include <string.h>

// UART configuration
// connect uart0 at "defaults" i.e. 115200 / 8 / 1 / N

#define UART_TX 0
#define UART_RX 1

int main() {
  unsigned int counter = 0;

  char buffer[80];

  stdio_init_all();
  uart_init(uart0, 115200);

  gpio_set_function(UART_TX, GPIO_FUNC_UART);
  gpio_set_function(UART_RX, GPIO_FUNC_UART);

  // UART configuration
  int baud = uart_set_baudrate(uart0, 115200);
  uart_set_hw_flow(uart0, false, false);
  uart_set_format(uart0, 8, 1, UART_PARITY_NONE);

  while (true) {
    printf("To USB: %d\n", counter);
    printf("  sending to UART @ %d\n", baud);
    sprintf(buffer, "To UART: %d\r\n", counter);
    uart_write_blocking(uart0, buffer, strlen(buffer));
    counter++;
    sleep_ms(1000);
  }

  return 0;
}
