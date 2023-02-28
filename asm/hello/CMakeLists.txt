cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(hello C CXX ASM)

pico_sdk_init()

add_executable(hello hello.s)

pico_set_program_name(hello "hello")
pico_set_program_version(hello "0.1")

pico_enable_stdio_uart(hello 1)
pico_enable_stdio_usb(hello 0)

target_link_libraries(hello pico_stdlib)

pico_add_extra_outputs(hello)

