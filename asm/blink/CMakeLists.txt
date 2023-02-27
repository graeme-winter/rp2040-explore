cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(blink C CXX ASM)

pico_sdk_init()

add_executable(blink blink.s)

pico_set_program_name(blink "blink")
pico_set_program_version(blink "0.1")

pico_enable_stdio_uart(blink 1)
pico_enable_stdio_usb(blink 0)

target_link_libraries(blink pico_stdlib)

pico_add_extra_outputs(blink)

