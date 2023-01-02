cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

include(pico_sdk_import.cmake)

project(irq C CXX ASM)

pico_sdk_init()

add_executable(irq irq.c)

pico_generate_pio_header(irq ${CMAKE_CURRENT_LIST_DIR}/count.pio)

pico_set_program_name(irq "irq")
pico_set_program_version(irq "0.1")

pico_enable_stdio_uart(irq 1)
pico_enable_stdio_usb(irq 0)

target_link_libraries(irq pico_stdlib hardware_pio)

pico_add_extra_outputs(irq)

