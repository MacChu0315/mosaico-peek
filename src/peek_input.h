/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include <stdbool.h>
#include <stdint.h>
typedef struct {
    bool down,blocked;
    int32_t start_x,start_y,max_dx,max_dy;
    uint64_t started_ms;
} peek_input_t;
/* Physical/UI coordinates:480 square, +x right,+y down; monotonic wall ms.
 * Return+1(next) for a tap/left swipe,-1(previous) for a right swipe, else0.
 * Only release emits. Tap <=600ms and maximum excursion<=16px per axis;
 * swipe >=48px horizontally with |dx|>=2*|dy|. Everything else cancels. */
int peek_input_update(peek_input_t *s,int32_t x,int32_t y,bool pressed,bool enabled,uint64_t now_ms);
/* Preserve down state so a stale release cannot start another gesture. */
void peek_input_cancel(peek_input_t *s);
