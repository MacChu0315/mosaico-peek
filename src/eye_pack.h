/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "dragon_pose.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct eye_pack eye_pack_t;
/* Three retained themes, ordered night_owl, deep_sea, mechanical. Only call
 * select/prepare on the UI owner; draw reads prepared data, never samples/time.
 * Gaze uses existing bounded +/-0.78, +/-0.58 pose after physical mapping.
 * Full-resolution bilinear sphere rotation (+/-120px horizontal, +/-80px
 * vertical center travel on pure axes); lid is [0,1] weighted premultiplied
 * RGBA, then source-over black/eye/lid/frame; RGB565 rounded only at output. */
eye_pack_t *eye_pack_create(void);
void eye_pack_destroy(eye_pack_t *r);
bool eye_pack_select(eye_pack_t *r,unsigned theme);
bool eye_pack_prepare(eye_pack_t *r,const dragon_pose_t *p);
bool eye_pack_draw(const eye_pack_t *r,void *pixels,size_t stride,int x,int y,int w,int h);
size_t eye_pack_heap_bytes(void);
size_t eye_pack_asset_bytes(void);
const char *eye_pack_name(unsigned theme);
