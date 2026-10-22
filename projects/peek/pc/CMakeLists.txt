cmake_minimum_required(VERSION 3.20)
project(peek_backend LANGUAGES C)
set(CMAKE_C_STANDARD 11)
if(NOT ESP_GSP_COMPONENT_DIR)
    set(ESP_GSP_COMPONENT_DIR "$ENV{ESP_GSP_COMPONENT_DIR}")
endif()
include("../../../cmake/dragon_assets.cmake")
include("../../../cmake/eye_pack.cmake")
find_package(ZLIB REQUIRED)
add_subdirectory("${ESP_GSP_COMPONENT_DIR}/tools/sim_bridge" sim_bridge)
gsp_add_backend(peek_backend
    SOURCES ../../../src/peek_orientation.c ../../../src/peek_input.c ../../../src/eye_pack.c ../../../src/dragon.c ../../../src/dragon_render.c ../../../src/peek.c ../../../src/replay.c ../../../src/peek_ui.c platform_pc.c
    INCLUDE_DIRECTORIES ../../../src "${PEEK_GENERATED_DIR}" "${PEEK_EYE_GENERATED_DIR}"
    SCENES ../ui/main.json)
target_compile_options(peek_backend PRIVATE -Wall -Wextra -Werror -ffp-contract=off)
target_link_libraries(peek_backend PRIVATE m ZLIB::ZLIB)

add_dependencies(peek_backend peek_dragon_assets peek_eye_assets)
