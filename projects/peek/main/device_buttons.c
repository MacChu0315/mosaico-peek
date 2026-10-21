/* SPDX-License-Identifier: Apache-2.0 */
#include "device_buttons.h"
#include "bsp/button.h"
#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
static button_handle_t buttons[BSP_BUTTON_NUM];
static atomic_uint pending;
static bool started;
static void clicked(void *handle,void *context){
    (void)handle;(void)context;
    atomic_fetch_add_explicit(&pending,1,memory_order_relaxed);
}
uint32_t device_buttons_take_presses(void){return atomic_exchange_explicit(&pending,0,memory_order_relaxed);}
esp_err_t device_buttons_start(void){
    if(started)return ESP_ERR_INVALID_STATE;
    /* A failed cleanup retains ownership; do not allocate over that handle. */
    for(unsigned i=0;i<BSP_BUTTON_NUM;i++)if(buttons[i])return ESP_ERR_INVALID_STATE;
    int count=0;atomic_store_explicit(&pending,0,memory_order_relaxed);
    esp_err_t rc=bsp_iot_button_create(buttons,&count,BSP_BUTTON_NUM);
    if(rc==ESP_OK && (count!=BSP_BUTTON_NUM || !buttons[BSP_BUTTON_AI]))rc=ESP_ERR_INVALID_STATE;
    if(rc==ESP_OK)rc=iot_button_register_cb(buttons[BSP_BUTTON_AI],BUTTON_SINGLE_CLICK,NULL,clicked,NULL);
    if(rc==ESP_OK){started=true;return ESP_OK;}
    for(unsigned i=0;i<BSP_BUTTON_NUM;i++)if(buttons[i]){
        esp_err_t cleanup=iot_button_delete(buttons[i]);
        if(cleanup==ESP_OK)buttons[i]=NULL;else rc=cleanup;
    }
    return rc;
}
