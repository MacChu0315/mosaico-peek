/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "esp_gsp.h"
#include "peek.h"
#include "dragon.h"
#include "dragon_render.h"
#include "eye_pack.h"
#include "eye_character_pose.h"
#include "peek_input.h"
typedef enum {PEEK_ACTION_CASE,PEEK_ACTION_PLAY,PEEK_ACTION_RESTART} peek_action_t;
typedef void (*peek_control_fn)(peek_action_t action,void *context);
typedef struct {
    esp_gsp_handle_t ui;
    peek_detector_t detector;
    peek_frame_t displayed;
    bool has_frame,paused,live,canvas_registered,event_registered,dragon_registered,dragon_view,dragon_prepared;
    float previous_blink;
    bool orientation_auto;int orientation_error;
    uint64_t orientation_sampled_ms;float orientation_accel[3];
    unsigned orientation; /* clockwise artwork quarter-turn, UI owner only */
    uint16_t rotation_tile[16*16]; /* bounded scratch, no extra framebuffer */
    unsigned sample_step; /* Eye only:1=480 or2=240 unique samples; output480. */
    dragon_t dragon;dragon_renderer_t *renderer;
    peek_input_t input;bool pointer_registered;
    eye_pack_t *eye_pack;unsigned character; /* 0=dragon,1=owl,2=sea,3=mechanical */
    uint64_t draw_pixels,render_us_total,render_us_max,prepare_us_total,prepares,prepare_us_max;
    uint16_t surface_w_min,surface_w_max,surface_h_min,surface_h_max;
    const char *source;
    uint64_t draws,actions;
    esp_gsp_err_t error;
    peek_control_fn control;
    void *context;
} peek_ui_t;
esp_gsp_err_t peek_ui_init(peek_ui_t *state,esp_gsp_handle_t ui,peek_control_fn control,void *context);
esp_gsp_err_t peek_ui_set_orientation(peek_ui_t *state,unsigned rotation);
void peek_ui_reset(peek_ui_t *state,const char *source);
esp_gsp_err_t peek_ui_set_view(peek_ui_t *state,bool dragon);
/* UI owner only. Selection preserves input, role state, mapping and time. */
esp_gsp_err_t peek_ui_set_character(peek_ui_t *state,unsigned character);
/* UI owner only: cycle four artworks, retaining all detector/role/time state. */
esp_gsp_err_t peek_ui_cycle_character(peek_ui_t *state,int delta);
const char *peek_ui_character_name(const peek_ui_t *state);
/* Only call after callbacks are detached and the device flush has succeeded. */
void peek_ui_release(peek_ui_t *state);
void peek_ui_time(peek_ui_t *state,uint64_t now_ms);
void peek_ui_refresh(peek_ui_t *state,uint64_t now_ms);
peek_submit_t peek_ui_submit(peek_ui_t *state,const peek_frame_t *frame,uint64_t now_ms);
/* Stops registrations. External MCU callers must additionally flush before
 * releasing this context. Returns cleanup status independently of prior errors. */
esp_gsp_err_t peek_ui_deinit(peek_ui_t *state);
