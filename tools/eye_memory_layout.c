/* Compile only with the actual ESP32-S31 command/headers. */
#include "../src/eye_pack.c"
#include "peek_ui.h"
const uint32_t eye_memory_layout[] __attribute__((used,section(".rodata.eye_budget")))={
    sizeof(eye_pack_t),sizeof(tinfl_decompressor),FRAME_BYTES,EYE_BYTES+2*LAYER_BYTES,
    sizeof(peek_ui_t),sizeof(eye_themes),EYE_DEPTH_BYTES
};
