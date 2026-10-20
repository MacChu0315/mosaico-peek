cmake_minimum_required(VERSION 3.20)
project(peek_backend LANGUAGES C)
set(CMAKE_C_STANDARD 11)
if(NOT ESP_GSP_COMPONENT_DIR)
    set(ESP_GSP_COMPONENT_DIR "$ENV{ESP_GSP_COMPONENT_DIR}")
endif()
add_subdirectory("${ESP_GSP_COMPONENT_DIR}/tools/sim_bridge" sim_bridge)
gsp_add_backend(peek_backend
    SOURCES ../../../src/peek.c ../../../src/replay.c ../../../src/peek_ui.c platform_pc.c
    INCLUDE_DIRECTORIES ../../../src
    SCENES ../ui/main.json)
target_compile_options(peek_backend PRIVATE -Wall -Wextra -Werror -ffp-contract=off)
target_link_libraries(peek_backend PRIVATE m)
