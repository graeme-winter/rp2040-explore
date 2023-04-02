cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(PICO_SDK_PATH "/Users/graeme/C/pico-sdk")

set(PICO_BOARD pico CACHE STRING "Board type")

include(pico_sdk_import.cmake)

project(tool C CXX ASM)

pico_sdk_init()

add_executable(tool tool.c )

pico_set_program_name(tool "tool")
pico_set_program_version(tool "0.0")

pico_enable_stdio_uart(tool 0)
pico_enable_stdio_usb(tool 1)

target_link_libraries(tool pico_stdlib hardware_dma hardware_pio hardware_timer)

target_include_directories(tool PRIVATE ${CMAKE_CURRENT_LIST_DIR})

pico_add_extra_outputs(tool)

