include("../../../cmake/dragon_assets.cmake")
idf_component_register(
    SRCS "device_status.c" "../../../src/dragon.c" "../../../src/dragon_render.c" "main.c" "device_thermal.c" "../../../src/peek.c" "../../../src/peek_ui.c" "board_display.c"
    INCLUDE_DIRS "." "../../../src" "${PEEK_GENERATED_DIR}"
    REQUIRES esp_iris esp-mosaico-bsp esp_mosaico_app_recovery
        mosaico_module_thermal mosaico_module_mgr esp_mosaico_gsp_bundle esp_mosaico_gsp_iris freertos nvs_flash
    PRIV_REQUIRES esp_timer esp-gsp esp_display_present esp_lcd)
include("${MOSAICO_UTILS_ROOT}/mosaico-tools/cmake/gsp_bundle.cmake")
mosaico_gsp_add_ui_bundle(${COMPONENT_LIB} "../ui/main.json")
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -ffp-contract=off)

add_dependencies(${COMPONENT_LIB} peek_dragon_assets)

execute_process(COMMAND git rev-parse HEAD WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../../.." OUTPUT_VARIABLE PEEK_SOURCE_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
file(WRITE "${CMAKE_BINARY_DIR}/peek_build_revision.h" "#define PEEK_SOURCE_REVISION \"${PEEK_SOURCE_REVISION}\"\n")
target_include_directories(${COMPONENT_LIB} PRIVATE "${CMAKE_BINARY_DIR}")
