#ifndef DRAGON_RENDER_H
#define DRAGON_RENDER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "dragon_pose.h"

typedef struct dragon_renderer dragon_renderer_t;

/* One owner prepares a frame before the renderer starts drawing its regions.
 * Serialize prepare/destroy against draw; all regions of a repaint must use
 * the same prepared generation. Draw allocates nothing and mutates no state. */
dragon_renderer_t *dragon_renderer_create(void);
/* Serialize with prepare/draw.1 preserves original pixel output;2 samples at
 * (x|1,y|1) and replicates globally aligned2x2 cells into480x480 output. */
bool dragon_renderer_set_sample_step(dragon_renderer_t *renderer,unsigned step);
void dragon_renderer_destroy(dragon_renderer_t *renderer);
bool dragon_renderer_prepare(dragon_renderer_t *renderer,
                             const dragon_pose_t *pose);
/* pixels starts at the requested region, not the origin of the whole frame.
 * Stride is in bytes. All coordinates are local to the 480 x 480 Canvas.
 * Draw reads prepared state only and initializes every requested pixel.
 * RGB565 values are native uint16_t words, not a byte-swapped wire stream. */
bool dragon_renderer_draw(const dragon_renderer_t *renderer, uint16_t *pixels,
                          size_t stride_bytes, unsigned x, unsigned y,
                          unsigned width, unsigned height);
/* True only for a fully prepared reusable240 geometry generation. */
bool dragon_renderer_geometry_cached(const dragon_renderer_t *renderer);
/* Workspace plus immutable fixed-pixel cache and prepared geometry cache per instance, excluding allocator
 * bookkeeping. The device cache uses explicit PSRAM; creation fails if absent. */
size_t dragon_renderer_heap_bytes(void);
/* Includes indexed textures, RGB565 palettes, and immutable numeric tables. */
size_t dragon_renderer_asset_bytes(void);

#endif
