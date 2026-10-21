/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_ui.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static peek_ui_t view;
static bool fail_canvas,fail_event,fail_stop,fail_unregister,fail_text;
static unsigned stops,unregisters;
static esp_gsp_pointer_observer_cb_t pointer_callback;
static bool fail_pointer,fail_pointer_stop;
esp_gsp_err_t esp_gsp_set_pointer_observer(esp_gsp_handle_t ui,esp_gsp_pointer_observer_cb_t cb,void *ctx){
    (void)ui;(void)ctx;if((cb&&fail_pointer)||(!cb&&fail_pointer_stop))return ESP_GSP_FAIL;
    pointer_callback=cb;return ESP_GSP_OK;
}
esp_gsp_err_t mock_text(esp_gsp_handle_t ui,const char *text){(void)ui;(void)text;return fail_text?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_set_draw_cb(esp_gsp_handle_t ui,uint16_t bind,esp_gsp_canvas_draw_cb_t cb,void *ctx){(void)ui;(void)bind;(void)cb;assert(ctx==&view);return fail_canvas?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_invalidate(esp_gsp_handle_t ui,uint16_t bind){(void)ui;(void)bind;return ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_stop(esp_gsp_handle_t ui,uint16_t bind){(void)ui;(void)bind;stops++;return fail_stop?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_on_event(esp_gsp_handle_t ui,esp_gsp_event_cb_t cb,void *ctx){(void)ui;(void)ctx;if(!cb){unregisters++;return fail_unregister?ESP_GSP_FAIL:ESP_GSP_OK;}return fail_event?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t mock_visible(esp_gsp_handle_t ui,bool visible){(void)ui;(void)visible;return ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_invalidate_dirty(esp_gsp_handle_t ui,uint16_t bind,gsp_rect_t rect){(void)rect;return esp_gsp_canvas_invalidate(ui,bind);}
static void reset(void){fail_canvas=fail_event=fail_stop=fail_unregister=fail_text=false;stops=unregisters=0;fail_pointer=fail_pointer_stop=false;}
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
    reset();assert(peek_ui_init(&view,(void *)1,NULL,NULL)==ESP_GSP_OK);
    fail_canvas=true;assert(peek_ui_set_view(&view,true)!=ESP_GSP_OK);
    assert(view.renderer && !view.dragon_registered);
    assert(peek_ui_deinit(&view)==ESP_GSP_OK);peek_ui_release(&view);assert(!view.renderer);
    reset();assert(peek_ui_init(&view,(void *)1,NULL,NULL)==ESP_GSP_OK);
    assert(peek_ui_set_view(&view,true)==ESP_GSP_OK && view.dragon_registered && view.renderer);
    fail_stop=true;assert(peek_ui_deinit(&view)!=ESP_GSP_OK);
    assert(view.dragon_registered && view.renderer);
    fail_stop=false;assert(peek_ui_deinit(&view)==ESP_GSP_OK && !view.dragon_registered);
    peek_ui_release(&view);assert(!view.renderer);
    reset();assert(peek_ui_init(&view,(void *)1,NULL,NULL)==ESP_GSP_OK);
    view.dragon.mapping.flip_x=true;view.dragon.mapping.flip_y=true;
    peek_ui_time(&view,12000);dragon_t before=view.dragon;peek_detector_t detector=view.detector;
    for(unsigned pass=0;pass<2;pass++)for(unsigned c=0;c<4;c++){
        assert(peek_ui_set_character(&view,c)==ESP_GSP_OK);
        peek_ui_refresh(&view,12000);
        assert(!memcmp(&before,&view.dragon,sizeof(before)));
        assert(!memcmp(&detector,&view.detector,sizeof(detector)));
        assert(peek_ui_set_view(&view,false)==ESP_GSP_OK);
        assert(peek_ui_set_character(&view,c)==ESP_GSP_OK);
    }
    assert(peek_ui_set_character(&view,4)==ESP_GSP_ERR_INVALID_ARG && view.character==3);
    assert(peek_ui_deinit(&view)==ESP_GSP_OK);peek_ui_release(&view);assert(!view.eye_pack && !view.renderer);
    reset();fail_pointer=true;assert(peek_ui_init(&view,(void *)1,NULL,NULL)!=ESP_GSP_OK);
    assert(!view.pointer_registered && view.event_registered);assert(peek_ui_deinit(&view)==ESP_GSP_OK);
    reset();assert(peek_ui_init(&view,(void *)1,NULL,NULL)==ESP_GSP_OK);assert(pointer_callback);
    assert(peek_ui_set_character(&view,0)==ESP_GSP_OK);
    before=view.dragon;detector=view.detector;
    pointer_callback(view.ui,300,200,true,&view);pointer_callback(view.ui,100,200,true,&view);
    assert(view.character==0);pointer_callback(view.ui,100,200,false,&view);assert(view.character==1);
    pointer_callback(view.ui,100,200,false,&view);assert(view.character==1);
    assert(!memcmp(&before,&view.dragon,sizeof(before)) && !memcmp(&detector,&view.detector,sizeof(detector)));
    pointer_callback(view.ui,200,200,true,&view);assert(peek_ui_set_character(&view,3)==ESP_GSP_OK);
    pointer_callback(view.ui,200,200,false,&view);assert(view.character==3);
    assert(peek_ui_cycle_character(&view,1)==ESP_GSP_OK && view.character==0);
    assert(peek_ui_cycle_character(&view,-1)==ESP_GSP_OK && view.character==3);
    fail_pointer_stop=true;assert(peek_ui_deinit(&view)!=ESP_GSP_OK && view.pointer_registered);
    fail_pointer_stop=false;assert(peek_ui_deinit(&view)==ESP_GSP_OK && !view.pointer_registered);
    peek_ui_release(&view);
    puts("PASS actual UI: partial registration, teardown errors retain ownership, retry detaches");
}
