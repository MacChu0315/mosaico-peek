#define _POSIX_C_SOURCE 200809L
/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_ui.h"
#define GSP_BUNDLE_ENABLE_LEGACY_NAMES 1
#include "bundle_gsp.h"
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#ifdef ESP_PLATFORM
#include "esp_timer.h"
#else
#include <time.h>
#endif
static uint64_t real_us(void){
#ifdef ESP_PLATFORM
    return (uint64_t)esp_timer_get_time();
#else
    struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000+(uint64_t)t.tv_nsec/1000;
#endif
}
static void remember(peek_ui_t *s,esp_gsp_err_t e){if(e!=ESP_GSP_OK)s->error=e;}
static uint16_t heat_color(float c){
    float t=fmaxf(0,fminf(1,(c-20)/20));
    unsigned r=(unsigned)(31*t),g=(unsigned)(63*(1-fabsf(2*t-1))),b=(unsigned)(31*(1-t));
    return (uint16_t)((r<<11)|(g<<5)|b);
}
static void draw(const esp_gsp_canvas_surface_t *surface,void *context)
{
    peek_ui_t *s=context;
    if(surface->pixel_format!=ESP_GSP_CANVAS_PIXEL_RGB565){s->error=ESP_GSP_ERR_NOT_SUPPORTED;return;}
    for(int y=0;y<surface->height;y++){
        uint16_t *line=(uint16_t *)((uint8_t *)surface->pixels+y*surface->stride_bytes);
        for(int x=0;x<surface->width;x++){
            int px=surface->x+x,py=surface->y+y;
            int tx=px/12,ty=py/12;
            line[x]=s->has_frame&&tx>=0&&tx<32&&ty>=0&&ty<24?heat_color(s->displayed.c[ty*32+tx]):0x1082;
            const peek_result_t *r=&s->detector.result;
            if(r->has_target){
                int cx=(int)((r->x+0.5f)*12),cy=(int)((r->y+0.5f)*12);
                if((abs(px-cx)<=1&&abs(py-cy)<=13)||(abs(py-cy)<=1&&abs(px-cx)<=13))line[x]=0xFFFF;
            }
        }
    }
    s->draws++;
}
static void draw_eye(const esp_gsp_canvas_surface_t *surface,void *context)
{
    peek_ui_t *s=context;uint64_t start=real_us();
    if(surface->pixel_format!=ESP_GSP_CANVAS_PIXEL_RGB565 || !s->renderer || !dragon_renderer_draw(s->renderer,surface->pixels,surface->stride_bytes,surface->x,surface->y,surface->width,surface->height)){
        s->error=ESP_GSP_FAIL;return;
    }
    uint64_t elapsed=real_us()-start;s->render_us_total+=elapsed;
    if(elapsed>s->render_us_max)s->render_us_max=elapsed;
    s->draw_pixels+=(uint64_t)surface->width*surface->height;s->draws++;
    if(!s->surface_w_min||surface->width<s->surface_w_min)s->surface_w_min=surface->width;
    if(surface->width>s->surface_w_max)s->surface_w_max=surface->width;
    if(!s->surface_h_min||surface->height<s->surface_h_min)s->surface_h_min=surface->height;
    if(surface->height>s->surface_h_max)s->surface_h_max=surface->height;
}
void peek_ui_time(peek_ui_t *s,uint64_t now)
{
    if(!peek_tick(&s->detector,now)||!dragon_update(&s->dragon,&s->detector.result,now))s->error=ESP_GSP_ERR_INVALID_ARG;
}
esp_gsp_err_t peek_ui_set_view(peek_ui_t *s,bool dragon)
{
    if(dragon&&!s->renderer){
        s->renderer=dragon_renderer_create();if(!s->renderer)return ESP_GSP_ERR_NO_MEM;
        if(!dragon_renderer_prepare(s->renderer,&s->dragon.pose))return ESP_GSP_FAIL;
    }
    if(dragon && !dragon_renderer_set_sample_step(s->renderer,s->sample_step))return ESP_GSP_ERR_INVALID_ARG;
    if(dragon&&!s->dragon_registered){
        esp_gsp_err_t rc=esp_gsp_canvas_set_draw_cb(s->ui,GSP_BIND_EYE,draw_eye,s);
        if(rc!=ESP_GSP_OK)return rc;
        s->dragon_registered=true;
    }
    esp_gsp_err_t rc=gsp_peek_diagnostic_set_visible(s->ui,!dragon);
    if(rc!=ESP_GSP_OK)return rc;
    rc=gsp_peek_eye_layer_set_visible(s->ui,dragon);
    if(rc!=ESP_GSP_OK)return rc;
    s->dragon_view=dragon;return ESP_GSP_OK;
}
void peek_ui_release(peek_ui_t *s){dragon_renderer_destroy(s->renderer);s->renderer=NULL;}
void peek_ui_refresh(peek_ui_t *s,uint64_t now)
{
    peek_ui_time(s,now);
    if(s->error!=ESP_GSP_OK)return;
    if(s->dragon_view){
        uint64_t start=real_us();
        if(!dragon_renderer_prepare(s->renderer,&s->dragon.pose)){s->error=ESP_GSP_FAIL;return;}
        uint64_t elapsed=real_us()-start;s->prepare_us_total+=elapsed;s->prepares++;
        if(elapsed>s->prepare_us_max)s->prepare_us_max=elapsed;
        if(s->dragon_prepared && s->previous_blink==0 && s->dragon.pose.blink==0){
            /* Both open poses differ only in this tested eye/crease union.
             * A blink deforms the whole hood, so those transitions repaint all. */
            remember(s,esp_gsp_canvas_invalidate_dirty(s->ui,GSP_BIND_EYE,(gsp_rect_t){16,80,464,416}));
        }else remember(s,esp_gsp_canvas_invalidate(s->ui,GSP_BIND_EYE));
        s->previous_blink=s->dragon.pose.blink;s->dragon_prepared=true;return;
    }
    const peek_result_t *r=&s->detector.result;char text[160];
    if(r->has_target)snprintf(text,sizeof(text),"%s / TARGET %.1f,%.1f%s",peek_data_name(r->data),r->x,r->y,r->held?" HOLD":"");
    else snprintf(text,sizeof(text),"%s / %s",peek_data_name(r->data),r->data==PEEK_VALID?"NO TARGET":"UNAVAILABLE");
    remember(s,gsp_peek_status_set_text(s->ui,text));
    if(r->has_valid)snprintf(text,sizeof(text),"F %" PRIu64 " | t %" PRIu64 " | last %" PRIu64 " | age %" PRIu64,r->sequence,now,r->last_valid_ms,now-r->last_valid_ms);
    else snprintf(text,sizeof(text),"F %" PRIu64 " | t %" PRIu64 " | last -- | age --",r->sequence,now);
    remember(s,gsp_peek_timing_set_text(s->ui,text));
    remember(s,gsp_peek_source_set_text(s->ui,s->source?s->source:"WAITING"));
    remember(s,gsp_peek_case_label_set_text(s->ui,s->live?"SENSOR":"CASE >"));
    remember(s,gsp_peek_restart_label_set_text(s->ui,s->live?"--":"REPLAY"));
    remember(s,gsp_peek_play_label_set_text(s->ui,s->live?"LIVE":s->paused?"PLAY":"PAUSE"));
    remember(s,esp_gsp_canvas_invalidate(s->ui,GSP_BIND_HEAT));
}
void peek_ui_reset(peek_ui_t *s,const char *source)
{
    peek_reset(&s->detector);dragon_reset(&s->dragon,90640);s->dragon_prepared=false;s->has_frame=false;s->source=source;
}
peek_submit_t peek_ui_submit(peek_ui_t *s,const peek_frame_t *f,uint64_t now)
{
    peek_submit_t rc=peek_submit(&s->detector,f,now);
    if(rc==PEEK_ACCEPTED){s->displayed=*f;s->has_frame=true;}
    if(!dragon_update(&s->dragon,&s->detector.result,now))s->error=ESP_GSP_ERR_INVALID_ARG;
    return rc;
}
static void event(esp_gsp_handle_t ui,const esp_gsp_event_t *e,void *ctx)
{
    (void)ui;peek_ui_t *s=ctx;peek_action_t action;
    if(gsp_peek_event_is_case(e))action=PEEK_ACTION_CASE;
    else if(gsp_peek_event_is_play(e))action=PEEK_ACTION_PLAY;
    else if(gsp_peek_event_is_restart(e))action=PEEK_ACTION_RESTART;
    else return;
    s->actions++;if(s->control)s->control(action,s->context);
}
esp_gsp_err_t peek_ui_init(peek_ui_t *s,esp_gsp_handle_t ui,peek_control_fn control,void *ctx)
{
    memset(s,0,sizeof(*s));s->sample_step=1;s->ui=ui;s->control=control;s->context=ctx;
    if(!peek_init(&s->detector,NULL))return ESP_GSP_ERR_INVALID_ARG;
    peek_ui_reset(s,"WAITING");
    esp_gsp_err_t rc=esp_gsp_canvas_set_draw_cb(ui,GSP_BIND_HEAT,draw,s);
    if(rc!=ESP_GSP_OK){remember(s,rc);return rc;}
    s->canvas_registered=true;
    rc=esp_gsp_on_event(ui,event,s);
    if(rc!=ESP_GSP_OK){remember(s,rc);return rc;}
    s->event_registered=true;
    peek_ui_refresh(s,0);return s->error;
}
esp_gsp_err_t peek_ui_deinit(peek_ui_t *s)
{
    esp_gsp_err_t result=ESP_GSP_OK,rc;
    if(s->event_registered){
        rc=esp_gsp_on_event(s->ui,NULL,NULL);
        if(rc==ESP_GSP_OK)s->event_registered=false;else result=rc;
    }
    if(s->canvas_registered){
        rc=esp_gsp_canvas_stop(s->ui,GSP_BIND_HEAT);
        if(rc==ESP_GSP_OK)s->canvas_registered=false;else result=rc;
    }
    if(s->dragon_registered){
        rc=esp_gsp_canvas_stop(s->ui,GSP_BIND_EYE);
        if(rc==ESP_GSP_OK)s->dragon_registered=false;else result=rc;
    }
    remember(s,result);return result;
}
