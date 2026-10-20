/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "peek.h"
#include "dragon.h"
/* Single acquisition-task owner. Whole immutable snapshots cross the display
 * mailbox, so a slow render cannot discard samples before detection. */
typedef struct {
    peek_detector_t detector;
    dragon_t dragon;
    peek_frame_t displayed;
    bool has_frame;
} peek_live_t;
bool peek_live_init(peek_live_t *live);
bool peek_live_event(peek_live_t *live,const peek_frame_t *frame,bool fault,uint64_t now_ms);
