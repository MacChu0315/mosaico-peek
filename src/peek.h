/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include <stdbool.h>
#include <stdint.h>
#define PEEK_W 32
#define PEEK_H 24
#define PEEK_PIXELS (PEEK_W * PEEK_H)

/* Celsius, row-major [y*32+x]. Origin top left; x right, y down.
 * Adapters own physical mounting rotation. Times are injected monotonic ms
 * from one epoch. Restarting an epoch requires peek_reset(). */
typedef struct {
    uint64_t sequence, captured_ms;
    bool complete;
    float c[PEEK_PIXELS];
    uint8_t valid[PEEK_PIXELS];
} peek_frame_t;
typedef enum { PEEK_WAITING, PEEK_VALID, PEEK_INVALID, PEEK_STALE } peek_data_t;
typedef enum { PEEK_ACCEPTED, PEEK_DUPLICATE, PEEK_REJECTED } peek_submit_t;
typedef struct {
    float enter_delta_c, keep_delta_c, max_distance, smoothing;
    unsigned min_area, max_area, acquire_frames, release_frames;
    uint64_t stale_ms, continuity_ms, hold_ms;
} peek_config_t;
typedef struct {
    peek_data_t data;
    bool has_target, held, has_valid;
    float x, y, background_c;
    unsigned area, candidates;
    uint64_t sequence, last_valid_ms, last_seen_ms, accepted_samples;
} peek_result_t;
/* Single owner. Scratch space lives here, not on the MCU task stack. */
typedef struct {
    peek_config_t config;
    peek_result_t result;
    uint64_t now_ms, last_input_sequence, last_input_ms;
    bool has_input, clock_started, tracking;
    unsigned hits, misses;
    float pending_x, pending_y;
    float sorted[PEEK_PIXELS];
    uint16_t queue[PEEK_PIXELS];
    uint8_t visited[PEEK_PIXELS];
} peek_detector_t;
peek_config_t peek_default_config(void);
bool peek_init(peek_detector_t *d, const peek_config_t *config);
void peek_reset(peek_detector_t *d);
peek_submit_t peek_submit(peek_detector_t *d, const peek_frame_t *frame, uint64_t now_ms);
/* False on clock rollback; state is unchanged. Never counts a sample. */
bool peek_tick(peek_detector_t *d, uint64_t now_ms);
/* Acquisition failure is an event, never a new sensor sample or sequence. */
bool peek_fault(peek_detector_t *d, uint64_t now_ms);
const char *peek_data_name(peek_data_t data);
