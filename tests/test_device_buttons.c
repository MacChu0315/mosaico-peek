/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <pthread.h>
#include <stdio.h>
#include "../projects/peek/main/device_buttons.c"
static bool fail_create,fail_register,fail_delete;
static unsigned deletes;
static button_cb_t callback;
esp_err_t bsp_iot_button_create(button_handle_t *b,int *count,int capacity){
    assert(capacity==BSP_BUTTON_NUM);b[BSP_BUTTON_AI]=(void *)1;*count=BSP_BUTTON_NUM;
    return fail_create?ESP_FAIL:ESP_OK;
}
esp_err_t iot_button_register_cb(button_handle_t b,button_event_t event,void *args,button_cb_t cb,void *context){
    assert(b==(void *)1 && event==BUTTON_SINGLE_CLICK && !args && !context);
    callback=cb;return fail_register?ESP_FAIL:ESP_OK;
}
esp_err_t iot_button_delete(button_handle_t b){assert(b==(void *)1);deletes++;return fail_delete?ESP_FAIL:ESP_OK;}
static void reset(void){buttons[0]=NULL;started=false;fail_create=fail_register=fail_delete=false;deletes=0;callback=NULL;atomic_store(&pending,0);}
static void *presses(void *p){(void)p;for(unsigned i=0;i<10000;i++)callback((void *)1,NULL);return NULL;}
int main(void){
    reset();fail_create=true;assert(device_buttons_start()!=ESP_OK && !buttons[0] && deletes==1);
    reset();fail_register=true;assert(device_buttons_start()!=ESP_OK && !buttons[0] && deletes==1);
    reset();fail_register=fail_delete=true;assert(device_buttons_start()!=ESP_OK && buttons[0]);
    assert(device_buttons_start()==ESP_ERR_INVALID_STATE); /* retained handle cannot be overwritten */
    reset();assert(device_buttons_start()==ESP_OK && callback);
    assert(device_buttons_start()==ESP_ERR_INVALID_STATE);
    callback((void *)1,NULL);callback((void *)1,NULL);
    assert(device_buttons_take_presses()==2 && device_buttons_take_presses()==0);
    pthread_t thread;assert(!pthread_create(&thread,NULL,presses,NULL));unsigned total=0;
    for(unsigned i=0;i<10000;i++)total+=device_buttons_take_presses();
    assert(!pthread_join(thread,NULL));total+=device_buttons_take_presses();assert(total==10000);
    puts("PASS BSP AI SINGLE_CLICK binding, partial init cleanup and lossless concurrent count handoff");
}
