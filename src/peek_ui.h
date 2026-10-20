/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "esp_gsp.h"
#include "peek.h"
typedef enum {PEEK_ACTION_CASE,PEEK_ACTION_PLAY,PEEK_ACTION_RESTART} peek_action_t;
typedef void (*peek_control_fn)(peek_action_t action,void *context);
typedef struct {
    esp_gsp_handle_t ui;
    peek_detector_t detector;
    peek_frame_t displayed;
    bool has_frame,paused,live,canvas_registered,event_registered;
    const char *source;
    uint64_t draws,actions;
    esp_gsp_err_t error;
    peek_control_fn control;
    void *context;
} peek_ui_t;
esp_gsp_err_t peek_ui_init(peek_ui_t *state,esp_gsp_handle_t ui,peek_control_fn control,void *context);
void peek_ui_reset(peek_ui_t *state,const char *source);
void peek_ui_refresh(peek_ui_t *state,uint64_t now_ms);
peek_submit_t peek_ui_submit(peek_ui_t *state,const peek_frame_t *frame,uint64_t now_ms);
/* Stops registrations. External MCU callers must additionally flush before
 * releasing this context. Returns cleanup status independently of prior errors. */
esp_gsp_err_t peek_ui_deinit(peek_ui_t *state);
