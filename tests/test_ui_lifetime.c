/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_ui.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "bundle_gsp.h"
static peek_ui_t view;
static bool fail_canvas,fail_event,fail_stop,fail_unregister,fail_text;
static unsigned stops,unregisters;
static esp_gsp_canvas_draw_cb_t eye_draw;
static esp_gsp_pointer_observer_cb_t pointer_callback;
static bool fail_pointer,fail_pointer_stop;
esp_gsp_err_t esp_gsp_set_pointer_observer(esp_gsp_handle_t ui,esp_gsp_pointer_observer_cb_t cb,void *ctx){
    (void)ui;(void)ctx;if((cb&&fail_pointer)||(!cb&&fail_pointer_stop))return ESP_GSP_FAIL;
    pointer_callback=cb;return ESP_GSP_OK;
}
esp_gsp_err_t mock_text(esp_gsp_handle_t ui,const char *text){(void)ui;(void)text;return fail_text?ESP_GSP_FAIL:ESP_GSP_OK;}
esp_gsp_err_t esp_gsp_canvas_set_draw_cb(esp_gsp_handle_t ui,uint16_t bind,esp_gsp_canvas_draw_cb_t cb,void *ctx){(void)ui;if(bind==GSP_BIND_EYE)eye_draw=cb;assert(ctx==&view);return fail_canvas?ESP_GSP_FAIL:ESP_GSP_OK;}
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
    /* Rotation must preserve every artwork pixel and source-owned state. */
    reset();assert(peek_ui_init(&view,(void *)1,NULL,NULL)==ESP_GSP_OK);
    uint16_t *reference=malloc(480*480*2),*output=malloc(480*480*2);assert(reference&&output);
    for(unsigned step=1;step<=2;step++)for(unsigned character=0;character<4;character++)for(unsigned q=0;q<360;q+=90){
        view.sample_step=step;
        assert(peek_ui_set_orientation(&view,0)==ESP_GSP_OK);
        assert(peek_ui_set_character(&view,character)==ESP_GSP_OK);
        view.dragon.pose=(dragon_pose_t){.39f,.145f,.2f,.69f,.072f,.16f};
        view.dragon.target_active=true;
        view.dragon.now_ms=6090;view.dragon.next_blink_ms=6020;
        assert(peek_tick(&view.detector,6090)); /* Keep the synthetic source clock coherent for later pointer refresh. */
        before=view.dragon;detector=view.detector;
        dragon_pose_t upright=view.dragon.pose;
        if(q==90){upright.gaze_x=.195f;upright.gaze_y=-.29f;}
        if(q==180){upright.gaze_x=-.39f;upright.gaze_y=-.145f;}
        if(q==270){upright.gaze_x=-.195f;upright.gaze_y=.29f;}
        eye_layers_t layers=eye_character_layers(character,&view.dragon);
        assert(character==2?eye_pack_prepare_layers(view.eye_pack,&upright,layers.membrane,layers.lid):character?eye_pack_prepare(view.eye_pack,&upright):dragon_renderer_prepare(view.renderer,&upright));
        assert(character?eye_pack_draw(view.eye_pack,reference,960,0,0,480,480):dragon_renderer_draw(view.renderer,reference,960,0,0,480,480));
        /* set_view prepares current pose; orientation prepares its inverse gaze. */
        assert(peek_ui_set_view(&view,true)==ESP_GSP_OK);
        assert(peek_ui_set_orientation(&view,q)==ESP_GSP_OK);
        assert(!memcmp(&before,&view.dragon,sizeof(before))&&!memcmp(&detector,&view.detector,sizeof(detector)));
        memset(output,0,480*480*2);
        /* Non-square, offset strips exercise GSP canvas stride and partial tiles. */
        for(unsigned y=0;y<480;y+=17){
            esp_gsp_canvas_surface_t surface={.pixels=output+y*480,.stride_bytes=960,.x=0,.y=y,.width=480,.height=y+17>480?480-y:17,.pixel_format=ESP_GSP_CANVAS_PIXEL_RGB565};
            eye_draw(&surface,&view);assert(view.error==ESP_GSP_OK);
        }
        for(unsigned y=0;y<480;y++)for(unsigned x=0;x<480;x++){
            unsigned a=x,b=y;
            if(q==90){a=y;b=479-x;}if(q==180){a=479-x;b=479-y;}if(q==270){a=479-y;b=x;}
            assert(output[y*480+x]==reference[b*480+a]);
        }
    }
    /* A role transition with unchanged source gaze must never move the pupil.
     * This catches changing gaze coordinate frames at IDLE/NOTICE/LEAVE edges. */
    assert(peek_ui_set_orientation(&view,180)==ESP_GSP_OK);
    for(unsigned c=0;c<4;c++){
        assert(peek_ui_set_character(&view,c)==ESP_GSP_OK);
        view.dragon.pose=(dragon_pose_t){-.32f,-.045f,0,.69f,.072f,.16f};
        view.dragon.mode=DRAGON_IDLE;view.dragon.target_active=false;
        assert(peek_ui_set_view(&view,true)==ESP_GSP_OK);
        esp_gsp_canvas_surface_t frame={.pixels=reference,.stride_bytes=960,.width=480,.height=480,.pixel_format=ESP_GSP_CANVAS_PIXEL_RGB565};
        eye_draw(&frame,&view);
        view.dragon.mode=DRAGON_NOTICE;view.dragon.target_active=true;
        assert(peek_ui_set_view(&view,true)==ESP_GSP_OK);frame.pixels=output;eye_draw(&frame,&view);
        assert(!memcmp(reference,output,480*480*2));
        view.dragon.mode=DRAGON_LEAVE;view.dragon.target_active=false;
        assert(peek_ui_set_view(&view,true)==ESP_GSP_OK);frame.pixels=reference;eye_draw(&frame,&view);
        view.dragon.mode=DRAGON_IDLE;
        assert(peek_ui_set_view(&view,true)==ESP_GSP_OK);frame.pixels=output;eye_draw(&frame,&view);
        assert(!memcmp(reference,output,480*480*2));
    }
    assert(peek_ui_set_orientation(&view,45)==ESP_GSP_ERR_INVALID_ARG);
    assert(peek_ui_set_orientation(&view,90)==ESP_GSP_OK);
    assert(peek_ui_set_character(&view,0)==ESP_GSP_OK);
    pointer_callback(view.ui,279,300,true,&view);pointer_callback(view.ui,279,100,false,&view);
    assert(view.character==1); /* physical upward swipe is upright left at90 */
    pointer_callback(view.ui,200,200,true,&view);
    assert(peek_ui_set_orientation(&view,180)==ESP_GSP_OK);
    pointer_callback(view.ui,200,200,false,&view);assert(view.character==1);
    free(reference);free(output);assert(peek_ui_deinit(&view)==ESP_GSP_OK);peek_ui_release(&view);
    puts("PASS actual UI: partial registration, teardown errors retain ownership, retry detaches");
}
