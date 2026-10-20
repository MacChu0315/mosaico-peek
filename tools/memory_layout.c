/* Compile-only: use the target ABI to size the actual device structures.
 * GSP/FreeRTOS function signatures come from Host test stubs; no code is run. */
#include "../projects/peek/main/device_thermal.c"
#include "../src/dragon_render.c"
const uint32_t peek_memory_layout[] __attribute__((used,section(".rodata.peek_layout")))={
    sizeof(peek_detector_t),sizeof(peek_frame_t),sizeof(dragon_t),sizeof(peek_ui_t),sizeof(capture_t),sizeof(*app),sizeof(dragon_renderer_t)
};
