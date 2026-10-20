/* Only the generated binding API surface is stubbed; actual UI logic is compiled. */
#pragma once
#include "esp_gsp.h"
#define GSP_BIND_HEAT 1
esp_gsp_err_t mock_text(esp_gsp_handle_t,const char *);
#define gsp_peek_status_set_text mock_text
#define gsp_peek_timing_set_text mock_text
#define gsp_peek_source_set_text mock_text
#define gsp_peek_case_label_set_text mock_text
#define gsp_peek_restart_label_set_text mock_text
#define gsp_peek_play_label_set_text mock_text
static inline bool gsp_peek_event_is_case(const esp_gsp_event_t *e){return e->code==1;}
static inline bool gsp_peek_event_is_play(const esp_gsp_event_t *e){return e->code==2;}
static inline bool gsp_peek_event_is_restart(const esp_gsp_event_t *e){return e->code==3;}
