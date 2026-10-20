/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_ui.h"
#define GSP_BUNDLE_ENABLE_LEGACY_NAMES 1
#include "bundle_gsp.h"
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
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
void peek_ui_refresh(peek_ui_t *s,uint64_t now)
{
    if(!peek_tick(&s->detector,now)){s->error=ESP_GSP_ERR_INVALID_ARG;return;}
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
    peek_reset(&s->detector);s->has_frame=false;s->source=source;
}
peek_submit_t peek_ui_submit(peek_ui_t *s,const peek_frame_t *f,uint64_t now)
{
    peek_submit_t rc=peek_submit(&s->detector,f,now);
    if(rc==PEEK_ACCEPTED){s->displayed=*f;s->has_frame=true;}
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
    memset(s,0,sizeof(*s));s->ui=ui;s->control=control;s->context=ctx;
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
    remember(s,result);return result;
}
