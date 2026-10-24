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
 * vertical center travel on pure axes). Organic R2 selects independent nearest9 membrane and outer-lid layers at
 * (0,128), with no gaze-dependent rim correction. Full480 detail is retained.
 * Mechanical C selects nearest shutter of9, composites HDR RGB in texture
 * space before rotation, then overlays the fixed mount. RGB565 rounds at output. */
eye_pack_t *eye_pack_create(void);
void eye_pack_destroy(eye_pack_t *r);
bool eye_pack_select(eye_pack_t *r,unsigned theme);
bool eye_pack_prepare(eye_pack_t *r,const dragon_pose_t *p);
/* Organic R2 modes: independently selected nearest9 screen overlays. The
 * UI supplies shared-source presentation phases; this API owns no clock. */
bool eye_pack_prepare_layers(eye_pack_t *r,const dragon_pose_t *p,float membrane,float lid);
bool eye_pack_draw(const eye_pack_t *r,void *pixels,size_t stride,int x,int y,int w,int h);
size_t eye_pack_heap_bytes(void);
size_t eye_pack_asset_bytes(void);
const char *eye_pack_name(unsigned theme);
