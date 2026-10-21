#pragma once
#include "esp_err.h"
typedef void *button_handle_t;
typedef enum {BSP_BUTTON_AI=0,BSP_BUTTON_NUM} bsp_button_t;
typedef enum {BUTTON_SINGLE_CLICK=3} button_event_t;
typedef void (*button_cb_t)(void *,void *);
esp_err_t bsp_iot_button_create(button_handle_t *,int *,int);
esp_err_t iot_button_register_cb(button_handle_t,button_event_t,void *,button_cb_t,void *);
esp_err_t iot_button_delete(button_handle_t);
