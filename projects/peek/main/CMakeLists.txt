idf_component_register(
    SRCS "main.c" "device_thermal.c" "../../../src/peek.c" "../../../src/peek_ui.c" "board_display.c"
    INCLUDE_DIRS "." "../../../src"
    REQUIRES esp_iris esp-mosaico-bsp esp_mosaico_app_recovery
        mosaico_module_thermal mosaico_module_mgr esp_mosaico_gsp_bundle esp_mosaico_gsp_iris freertos nvs_flash
    PRIV_REQUIRES esp_timer esp-gsp esp_display_present esp_lcd)
include("${MOSAICO_UTILS_ROOT}/mosaico-tools/cmake/gsp_bundle.cmake")
mosaico_gsp_add_ui_bundle(${COMPONENT_LIB} "../ui/main.json")
target_compile_options(${COMPONENT_LIB} PRIVATE -Wall -Wextra -Werror -ffp-contract=off)
