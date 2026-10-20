/* SPDX-License-Identifier: Apache-2.0 */
#define _POSIX_C_SOURCE 200809L
#include "gsp_sim_bridge.h"
#include "peek_ui.h"
#include "replay.h"
#include <errno.h>
#include <inttypes.h>
#include <stdlib.h>
#include <signal.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <time.h>
static struct {
    peek_ui_t view;peek_replay_t replay;void *timer;
    uint64_t logical_ms,wall_ms,ack;
    uint64_t tick_calls,tick_us_total,tick_work_us_total,publish_us_total,tick_us_max;
    uint64_t interval_count,interval_us_total,interval_us_max,last_tick_start_us,last_completed_us;
    uint64_t interval_bins[8];
    unsigned case_index;int fd;
    const char *data_dir,*run_dir;
    char label[80],status[512],temporary[512],socket_path[108];
} app={.fd=-1};
static const char *cases[]={"empty","motion","multi","gaps","recorded","aging","dragon","idle"};
#define CASE_COUNT (sizeof(cases)/sizeof(cases[0]))
static uint64_t real_us(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000+(uint64_t)t.tv_nsec/1000;}
static void publish(void)
{
    FILE *f=fopen(app.temporary,"w");if(!f){perror("status");app.view.error=ESP_GSP_FAIL;return;}
    fprintf(f,"{\"case\":\"%s\",\"paused\":%s,\"ack\":%" PRIu64 ",\"draws\":%" PRIu64 ",\"actions\":%" PRIu64 ",\"error\":%d,\"eof\":%s,\"result\":",cases[app.case_index],app.view.paused?"true":"false",app.ack,app.view.draws,app.view.actions,app.view.error,app.replay.eof?"true":"false");
    peek_write_result(f,&app.view.detector);
    const dragon_t *c=&app.view.dragon;
    fprintf(f,",\"view\":\"%s\",\"role\":{\"mode\":\"%s\",\"phase_ms\":%" PRIu64 ",\"observations\":%" PRIu64 ",\"notices\":%" PRIu64 ",\"blinks\":%" PRIu64 ",\"observation_held\":%s,\"stationary\":%s,\"speed_px_s\":%.5f,\"next_blink_ms\":%" PRIu64 ",\"pose\":{\"gaze_x\":%.9g,\"gaze_y\":%.9g,\"blink\":%.9g,\"squint\":%.9g,\"pupil_width\":%.9g,\"tension\":%.9g}},\"render\":{\"pixels\":%" PRIu64 ",\"draw_us_total\":%" PRIu64 ",\"draw_us_max\":%" PRIu64 ",\"prepare_us_total\":%" PRIu64 ",\"prepares\":%" PRIu64 ",\"renderer_heap_bytes\":%zu,\"assets_bytes\":%zu}",
        app.view.dragon_view?"dragon":"diagnostic",dragon_mode_name(c->mode),c->phase_ms,c->observations,c->notices,c->blinks,c->observation_held?"true":"false",c->stationary?"true":"false",c->speed_px_s,c->next_blink_ms,c->pose.gaze_x,c->pose.gaze_y,c->pose.blink,c->pose.squint,c->pose.pupil_width,c->pose.tension,app.view.draw_pixels,app.view.render_us_total,app.view.render_us_max,app.view.prepare_us_total,app.view.prepares,dragon_renderer_heap_bytes(),dragon_renderer_asset_bytes());
    fprintf(f,",\"host_timing\":{\"target_timer_ms\":33,\"completed_callbacks\":%" PRIu64 ",\"callback_us_total\":%" PRIu64 ",\"work_us_total\":%" PRIu64 ",\"publish_us_total\":%" PRIu64 ",\"callback_us_max_session\":%" PRIu64 ",\"interval_count\":%" PRIu64 ",\"interval_us_total\":%" PRIu64 ",\"interval_us_max_session\":%" PRIu64 ",\"completed_until_us\":%" PRIu64 ",\"published_us\":%" PRIu64 ",\"interval_bins_le_us\":[10000,20000,35000,50000,75000,100000,200000,18446744073709551615],\"interval_bins\":[",
        app.tick_calls,app.tick_us_total,app.tick_work_us_total,app.publish_us_total,app.tick_us_max,app.interval_count,app.interval_us_total,app.interval_us_max,app.last_completed_us,real_us());
    for(unsigned i=0;i<8;i++)fprintf(f,"%s%" PRIu64,i?",":"",app.interval_bins[i]);
    fprintf(f,"]},\"surface\":{\"width_min\":%u,\"width_max\":%u,\"height_min\":%u,\"height_max\":%u,\"prepare_us_max_session\":%" PRIu64 "}}\n",app.view.surface_w_min,app.view.surface_w_max,app.view.surface_h_min,app.view.surface_h_max,app.view.prepare_us_max);
    bool failed=ferror(f);if(fclose(f)!=0)failed=true;
    if(failed||rename(app.temporary,app.status)!=0){perror("publish");app.view.error=ESP_GSP_FAIL;}
}
static bool pump(uint64_t until)
{
    while(app.replay.ready&&app.replay.due_ms<=until){
        if(app.replay.sample)(void)peek_ui_submit(&app.view,&app.replay.frame,app.replay.due_ms);
        else {peek_ui_time(&app.view,app.replay.due_ms);if(app.view.error!=ESP_GSP_OK)return false;}
        if(!peek_replay_next(&app.replay)){fprintf(stderr,"replay error: %s\n",app.replay.error);return false;}
    }
    app.logical_ms=until;peek_ui_refresh(&app.view,until);return true;
}
static bool load_case(void)
{
    char path[512];int n=snprintf(path,sizeof(path),"%s/%s.peek",app.data_dir,cases[app.case_index]);
    if(n<0||n>=(int)sizeof(path))return false;
    peek_replay_close(&app.replay);
    if(!peek_replay_open(&app.replay,path)){fprintf(stderr,"%s\n",app.replay.error);return false;}
    snprintf(app.label,sizeof(app.label),"%s / %s",app.case_index==4?"RECORDED (sparse)":"SYNTHETIC",cases[app.case_index]);
    peek_ui_reset(&app.view,app.label);app.logical_ms=0;app.wall_ms=gsp_sim_bridge_time_ms();
    return pump(0);
}
static void control(peek_action_t action,void *ctx)
{
    (void)ctx;
    if(action==PEEK_ACTION_CASE){app.case_index=(app.case_index+1)%CASE_COUNT;app.view.paused=true;if(!load_case())app.view.error=ESP_GSP_FAIL;}
    else if(action==PEEK_ACTION_RESTART){if(!load_case())app.view.error=ESP_GSP_FAIL;}
    else {app.view.paused=!app.view.paused;app.wall_ms=gsp_sim_bridge_time_ms();}
    peek_ui_refresh(&app.view,app.logical_ms);publish();
    fprintf(stderr,"PEEK action=%d case=%s paused=%d logical=%" PRIu64 "\n",action,cases[app.case_index],app.view.paused,app.logical_ms);
}
static void tick(esp_gsp_handle_t ui,void *ctx)
{
    (void)ui;(void)ctx;
    uint64_t started=real_us(),interval=app.last_tick_start_us?started-app.last_tick_start_us:0;
    app.last_tick_start_us=started;
    uint64_t wall=gsp_sim_bridge_time_ms();
    if(!app.view.paused){
        if(!pump(app.logical_ms+wall-app.wall_ms))app.view.error=ESP_GSP_FAIL;
        if(app.replay.eof)app.view.paused=true;
    }
    app.wall_ms=wall;
    char msg[128];ssize_t n;
    while((n=recv(app.fd,msg,sizeof(msg)-1,MSG_DONTWAIT))>0){
        msg[n]=0;unsigned long long id,delta;char verb[20];unsigned index;
        if(sscanf(msg,"%llu %19s",&id,verb)!=2)continue;
        bool accepted=true;
        if(!strcmp(verb,"case")&&sscanf(msg,"%llu %19s %u",&id,verb,&index)==3&&index<CASE_COUNT){app.case_index=(index+CASE_COUNT-1)%CASE_COUNT;control(PEEK_ACTION_CASE,NULL);}
        else if(!strcmp(verb,"replay"))control(PEEK_ACTION_RESTART,NULL);
        else if(!strcmp(verb,"pause")){app.view.paused=true;peek_ui_refresh(&app.view,app.logical_ms);}
        else if(!strcmp(verb,"play")){app.view.paused=false;app.wall_ms=wall;peek_ui_refresh(&app.view,app.logical_ms);}
        else if(!strcmp(verb,"advance")&&sscanf(msg,"%llu %19s %llu",&id,verb,&delta)==3&&delta<=600000){app.view.paused=true;if(!pump(app.logical_ms+(uint64_t)delta))app.view.error=ESP_GSP_FAIL;}
        else if(!strcmp(verb,"step")){app.view.paused=true;if(app.replay.ready&&!pump(app.replay.due_ms))app.view.error=ESP_GSP_FAIL;}
        else if(!strcmp(verb,"view")){
            char which[20];
            if(sscanf(msg,"%llu %19s %19s",&id,verb,which)!=3 || (strcmp(which,"dragon")&&strcmp(which,"diagnostic")))accepted=false;
            else {esp_gsp_err_t rc=peek_ui_set_view(&app.view,!strcmp(which,"dragon"));if(rc!=ESP_GSP_OK)app.view.error=rc;peek_ui_refresh(&app.view,app.logical_ms);}
        }
        else if(!strcmp(verb,"draw")){peek_ui_refresh(&app.view,app.logical_ms);}
        else if(!strcmp(verb,"quit")){app.view.paused=true;raise(SIGTERM);}
        else accepted=false;
        if(!accepted)app.view.error=ESP_GSP_ERR_INVALID_ARG;
        app.ack=id;
        fprintf(stderr,"PEEK command=%s accepted=%d ",verb,accepted);peek_write_result(stderr,&app.view.detector);fputc('\n',stderr);
    }
    if(n<0&&errno!=EAGAIN&&errno!=EWOULDBLOCK)app.view.error=ESP_GSP_FAIL;
    uint64_t before_publish=real_us();publish();uint64_t finished=real_us();
    app.tick_calls++;app.tick_work_us_total+=before_publish-started;app.publish_us_total+=finished-before_publish;
    app.tick_us_total+=finished-started;if(finished-started>app.tick_us_max)app.tick_us_max=finished-started;
    app.last_completed_us=finished;
    if(interval){
        app.interval_count++;app.interval_us_total+=interval;if(interval>app.interval_us_max)app.interval_us_max=interval;
        const uint64_t bounds[]={10000,20000,35000,50000,75000,100000,200000,UINT64_MAX};
        unsigned bin=0;while(bin<7&&interval>bounds[bin])bin++;app.interval_bins[bin]++;
    }
}
esp_gsp_err_t gsp_bridge_app_init(esp_gsp_handle_t ui)
{
    app.data_dir=getenv("PEEK_DATA_DIR");app.run_dir=getenv("PEEK_RUN_DIR");
    if(!app.data_dir||!app.run_dir)return ESP_GSP_ERR_INVALID_ARG;
    if(snprintf(app.socket_path,sizeof(app.socket_path),"%s/control.sock",app.run_dir)>=(int)sizeof(app.socket_path))return ESP_GSP_ERR_INVALID_ARG;
    snprintf(app.status,sizeof(app.status),"%s/status.json",app.run_dir);snprintf(app.temporary,sizeof(app.temporary),"%s/status.tmp",app.run_dir);
    app.fd=socket(AF_UNIX,SOCK_DGRAM,0);if(app.fd<0)return ESP_GSP_FAIL;
    struct sockaddr_un addr={.sun_family=AF_UNIX};strcpy(addr.sun_path,app.socket_path);
    if(bind(app.fd,(struct sockaddr *)&addr,sizeof(addr))!=0){perror("bind");close(app.fd);app.fd=-1;return ESP_GSP_FAIL;}
    esp_gsp_err_t rc=peek_ui_init(&app.view,ui,control,NULL);if(rc!=ESP_GSP_OK)return rc;
    const char *view=getenv("PEEK_VIEW");bool dragon=!view||strcmp(view,"diagnostic");
    rc=peek_ui_set_view(&app.view,dragon);if(rc!=ESP_GSP_OK)return rc;
    app.view.paused=true;app.case_index=dragon?6:1;if(!load_case())return ESP_GSP_FAIL;
    app.timer=esp_gsp_timer_create(ui,33,tick,NULL);if(!app.timer)return ESP_GSP_ERR_NO_MEM;
    publish();fprintf(stderr,"PEEK ready native C; case=%s view=%s paused\n",cases[app.case_index],dragon?"dragon":"diagnostic");return app.view.error;
}
void gsp_bridge_app_deinit(esp_gsp_handle_t ui)
{
    if(app.timer){esp_gsp_err_t rc=esp_gsp_timer_delete(ui,app.timer);if(rc!=ESP_GSP_OK)fprintf(stderr,"timer delete=%d\n",rc);}
    peek_ui_deinit(&app.view);peek_ui_release(&app.view);peek_replay_close(&app.replay);
    if(app.fd>=0){close(app.fd);unlink(app.socket_path);}
    fprintf(stderr,"PEEK stopped draws=%" PRIu64 " actions=%" PRIu64 " error=%d\n",app.view.draws,app.view.actions,app.view.error);
}
