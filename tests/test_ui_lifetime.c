/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_ui.h"
#include <assert.h>
#include <stdio.h>
static peek_ui_t view;
static bool fail_canvas,fail_event,fail_stop,fail_unregister,fail_text;
static unsigned stops,unregisters;
esp_gsp_err_t mock_text(esp_gsp_handle_t ui,const char *text){(void)ui;(void)text;return fail_text?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_set_draw_cb(esp_gsp_handle_t ui,uint16_t bind,esp_gsp_canvas_draw_cb_t cb,void *ctx){(void)ui;(void)bind;(void)cb;assert(ctx==&view);return fail_canvas?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_invalidate(esp_gsp_handle_t ui,uint16_t bind){(void)ui;(void)bind;return ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_stop(esp_gsp_handle_t ui,uint16_t bind){(void)ui;(void)bind;stops++;return fail_stop?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_on_event(esp_gsp_handle_t ui,esp_gsp_event_cb_t cb,void *ctx){(void)ui;(void)ctx;if(!cb){unregisters++;return fail_unregister?ESP_GSP_FAIL:ESP_GSP_OK;}return fail_event?ESP_GSP_FAIL:ESP_GSP_OK;}
static void reset(void){fail_canvas=fail_event=fail_stop=fail_unregister=fail_text=false;stops=unregisters=0;}
int main(void){
    reset();fail_canvas=true;assert(peek_ui_init(&view,(void *)1,NULL,NULL)!=ESP_GSP_OK);
    assert(peek_ui_deinit(&view)==ESP_GSP_OK && !stops && !unregisters);
    reset();fail_event=true;assert(peek_ui_init(&view,(void *)1,NULL,NULL)!=ESP_GSP_OK);
    assert(view.canvas_registered && !view.event_registered);
    assert(peek_ui_deinit(&view)==ESP_GSP_OK && stops==1 && !unregisters);
    reset();fail_text=true;assert(peek_ui_init(&view,(void *)1,NULL,NULL)!=ESP_GSP_OK);
    assert(peek_ui_deinit(&view)==ESP_GSP_OK && stops==1 && unregisters==1);
    assert(!view.canvas_registered && !view.event_registered);
    reset();assert(peek_ui_init(&view,(void *)1,NULL,NULL)==ESP_GSP_OK);
    fail_stop=fail_unregister=true;assert(peek_ui_deinit(&view)!=ESP_GSP_OK);
    assert(view.canvas_registered && view.event_registered);
    fail_stop=fail_unregister=false;assert(peek_ui_deinit(&view)==ESP_GSP_OK);
    assert(!view.canvas_registered && !view.event_registered && stops==2 && unregisters==2);
    puts("PASS actual UI: partial registration, teardown errors retain ownership, retry detaches");
}
