/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include <stdbool.h>
#include <stdint.h>
/* Clockwise artwork rotation in physical 480x480 panel coordinates. */
typedef struct {
    unsigned rotation,candidate;
    uint64_t last_ms,since_ms;
    float x,y,z;
    bool started,filtered,pending;
} peek_orientation_t;
/* Gravity-down vector in screen axes (+x right,+y down), g; angular speed dps.
 * Samples must be fresh. Invalid/moving/flat input cancels pending evidence. */
void peek_orientation_sample(peek_orientation_t *s,float x,float y,float z,
                             float rate,bool valid,uint64_t now_ms);
/* Inverse artwork transform: physical screen point -> upright canvas point. */
void peek_orientation_point(unsigned rotation,unsigned x,unsigned y,unsigned *lx,unsigned *ly);
void peek_orientation_gaze(unsigned rotation,float x,float y,float *lx,float *ly);
