#include "hardware/adc.h"
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

// ADC configuration
#define ADC0 26

// data buffer
#define SIZE 100000
unsigned char data[SIZE];

int main() {
  unsigned int counter = 0;

  char buffer[80];

  stdio_init_all();

  gpio_set_function(UART_TX, GPIO_FUNC_UART);
  gpio_set_function(UART_RX, GPIO_FUNC_UART);

  // UART configuration
  uart_init(uart0, 115200);
  int baud = uart_set_baudrate(uart0, 115200);
  uart_set_hw_flow(uart0, false, false);
  uart_set_format(uart0, 8, 1, UART_PARITY_NONE);

  // ADC configuration N.B. shifting to just keep 8 MSB
  adc_init();
  adc_gpio_init(ADC0);
  adc_select_input(0);
  adc_fifo_setup(true, true, 1, false, true);
  adc_set_clkdiv(0);

  // ADC DMA configuration
  unsigned int adc_dma;
  dma_channel_config adc_dmac;
  adc_dma = dma_claim_unused_channel(true);
  adc_dmac = dma_channel_get_default_config(adc_dma);
  channel_config_set_transfer_data_size(&adc_dmac, DMA_SIZE_8);
  channel_config_set_dreq(&adc_dmac, DREQ_ADC);
  channel_config_set_read_increment(&adc_dmac, false);
  channel_config_set_write_increment(&adc_dmac, true);
  while (true) {
    printf("Reading from stdin\n");
    scanf("%79s", buffer);
    printf("Read %s\n", buffer);
    dma_channel_configure(adc_dma, &adc_dmac, (volatile void *)&data,
                          (const volatile void *)&(adc_hw->fifo), SIZE, false);

    // kick everything off - draininng FIFO first
    adc_fifo_drain();
    dma_channel_start(adc_dma);
    adc_run(true);
    dma_channel_wait_for_finish_blocking(adc_dma);
    adc_run(false);

    printf("Sending %d bytes to UART @ %d\n", SIZE, baud);
    uart_write_blocking(uart0, data, SIZE);
    printf("Done\n");
    counter++;
  }

  return 0;
}
