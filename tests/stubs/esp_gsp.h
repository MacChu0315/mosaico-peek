#pragma once
#include <stdint.h>
#include "esp_err.h"
typedef void *esp_gsp_handle_t;
typedef int esp_gsp_err_t;
#define ESP_GSP_OK ESP_OK
#define ESP_GSP_FAIL ESP_FAIL
#define ESP_GSP_ERR_NO_MEM ESP_ERR_NO_MEM
#define ESP_GSP_ERR_INVALID_ARG ESP_ERR_INVALID_ARG
typedef void (*esp_gsp_timer_cb_t)(esp_gsp_handle_t,void *);
void *esp_gsp_timer_create(esp_gsp_handle_t ui,uint32_t period,esp_gsp_timer_cb_t cb,void *ctx);
esp_gsp_err_t esp_gsp_timer_delete(esp_gsp_handle_t ui,void *timer);
esp_gsp_err_t esp_gsp_flush(esp_gsp_handle_t ui,uint32_t timeout);
#include <stdbool.h>
#include <stddef.h>
#define ESP_GSP_ERR_NOT_SUPPORTED 5
#define ESP_GSP_CANVAS_PIXEL_RGB565 0
typedef struct {void *pixels;size_t stride_bytes;uint16_t x,y,width,height;uint8_t pixel_format;} esp_gsp_canvas_surface_t;
typedef struct {int code;} esp_gsp_event_t;
typedef void (*esp_gsp_canvas_draw_cb_t)(const esp_gsp_canvas_surface_t *,void *);
typedef void (*esp_gsp_event_cb_t)(esp_gsp_handle_t,const esp_gsp_event_t *,void *);
esp_gsp_err_t esp_gsp_canvas_set_draw_cb(esp_gsp_handle_t,uint16_t,esp_gsp_canvas_draw_cb_t,void *);
esp_gsp_err_t esp_gsp_canvas_invalidate(esp_gsp_handle_t,uint16_t);
esp_gsp_err_t esp_gsp_canvas_stop(esp_gsp_handle_t,uint16_t);
esp_gsp_err_t esp_gsp_on_event(esp_gsp_handle_t,esp_gsp_event_cb_t,void *);

typedef struct {int16_t x1,y1,x2,y2;} gsp_rect_t;
esp_gsp_err_t esp_gsp_canvas_invalidate_dirty(esp_gsp_handle_t,uint16_t,gsp_rect_t);

typedef void (*esp_gsp_pointer_observer_cb_t)(esp_gsp_handle_t,int32_t,int32_t,bool,void *);
esp_gsp_err_t esp_gsp_set_pointer_observer(esp_gsp_handle_t,esp_gsp_pointer_observer_cb_t,void *);
