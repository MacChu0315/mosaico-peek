/* SPDX-License-Identifier: Apache-2.0 */
#include "peek.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

peek_config_t peek_default_config(void)
{
    return (peek_config_t){3.0f,2.0f,5.0f,0.5f,6,300,3,2,750,300,500};
}
bool peek_init(peek_detector_t *d,const peek_config_t *config)
{
    if(!d)return false;
    peek_config_t c=config?*config:peek_default_config();
    if(!isfinite(c.enter_delta_c)||!isfinite(c.keep_delta_c)||!isfinite(c.max_distance)||
       !isfinite(c.smoothing)||c.keep_delta_c<=0||c.enter_delta_c<c.keep_delta_c||
       c.max_distance<=0||c.smoothing<=0||c.smoothing>1||!c.min_area||
       c.max_area<c.min_area||c.max_area>768||!c.acquire_frames||!c.release_frames||
       !c.continuity_ms||c.hold_ms<c.continuity_ms||c.stale_ms<=c.hold_ms)return false;
    memset(d,0,sizeof(*d));d->config=c;d->result.x=d->result.y=-1;return true;
}
static void clear_track(peek_detector_t *d)
{
    d->tracking=false;d->hits=d->misses=0;
    d->result.has_target=d->result.held=false;
    d->result.x=d->result.y=-1;d->result.area=0;
}
void peek_reset(peek_detector_t *d)
{
    peek_config_t c=d->config;(void)peek_init(d,&c);clear_track(d);
}
bool peek_tick(peek_detector_t *d,uint64_t now)
{
    if(!d || (d->clock_started && now<d->now_ms))return false;
    d->clock_started=true;d->now_ms=now;
    if(d->result.has_valid && now-d->result.last_valid_ms>=d->config.stale_ms){
        d->result.data=PEEK_STALE;clear_track(d);
    } else if(d->tracking && now-d->result.last_seen_ms>=d->config.hold_ms)clear_track(d);
    return true;
}
static int compare_float(const void *a,const void *b)
{
    float x=*(const float *)a,y=*(const float *)b;return (x>y)-(x<y);
}
typedef struct {float x,y,score;unsigned area;} region_t;
static float distance(float x,float y,float bx,float by)
{
    return (x-bx)*(x-bx)+(y-by)*(y-by);
}
static peek_submit_t invalid(peek_detector_t *d)
{
    clear_track(d);d->result.data=PEEK_INVALID;return PEEK_REJECTED;
}
bool peek_fault(peek_detector_t *d,uint64_t now)
{
    if(!peek_tick(d,now))return false;
    invalid(d);return true;
}
peek_submit_t peek_submit(peek_detector_t *d,const peek_frame_t *f,uint64_t now)
{
    if(!d||!f||!peek_tick(d,now))return PEEK_REJECTED;
    if(d->has_input && f->sequence<=d->last_input_sequence)return PEEK_DUPLICATE;
    if(f->captured_ms>now || (d->has_input && f->captured_ms<=d->last_input_ms))return invalid(d);
    d->has_input=true;d->last_input_sequence=f->sequence;d->last_input_ms=f->captured_ms;
    d->result.sequence=f->sequence;
    if(!f->complete)return invalid(d);
    for(unsigned i=0;i<768;i++){
        if(!f->valid[i]||!isfinite(f->c[i])||f->c[i]<-40||f->c[i]>300)return invalid(d);
        d->sorted[i]=f->c[i];
    }
    if(now-f->captured_ms>=d->config.stale_ms){clear_track(d);d->result.data=PEEK_STALE;return PEEK_REJECTED;}
    if(d->result.has_valid && f->captured_ms-d->result.last_valid_ms>d->config.continuity_ms){
        d->hits=0;
        if(f->captured_ms-d->result.last_seen_ms>=d->config.hold_ms)clear_track(d);
    }
    qsort(d->sorted,768,sizeof(float),compare_float);
    float bg=(d->sorted[383]+d->sorted[384])*0.5f;
    d->result.background_c=bg;d->result.data=PEEK_VALID;d->result.has_valid=true;
    d->result.last_valid_ms=f->captured_ms;d->result.accepted_samples++;
    memset(d->visited,0,sizeof(d->visited));
    region_t best={0},near={0};float nearest=INFINITY;
    unsigned candidates=0;
    /* Hysteresis lowers the connected-region threshold only during tracking.
     * Distant replacement candidates must still meet the entry contrast. */
    float threshold=d->tracking?d->config.keep_delta_c:d->config.enter_delta_c;
    for(unsigned start=0;start<768;start++){
        if(d->visited[start] || f->c[start]-bg<threshold)continue;
        unsigned head=0,tail=0;d->queue[tail++]=(uint16_t)start;d->visited[start]=1;
        float sx=0,sy=0,weight=0;unsigned area=0;
        while(head<tail){
            unsigned p=d->queue[head++];int x=p%32,y=p/32;
            float w=f->c[p]-bg;sx+=x*w;sy+=y*w;weight+=w;area++;
            int adjacent[4]={x>0?(int)p-1:-1,x<31?(int)p+1:-1,y>0?(int)p-32:-1,y<23?(int)p+32:-1};
            for(int n=0;n<4;n++){
                int k=adjacent[n];
                if(k>=0 && !d->visited[k] && f->c[k]-bg>=threshold){
                    d->visited[k]=1;d->queue[tail++]=(uint16_t)k;
                }
            }
        }
        if(area<d->config.min_area||area>d->config.max_area)continue;
        region_t r={sx/weight,sy/weight,weight,area};candidates++;
        float dist=distance(r.x,r.y,d->result.x,d->result.y);
        if(d->tracking && dist<=d->config.max_distance*d->config.max_distance && dist<nearest){near=r;nearest=dist;}
        if(weight/area>=d->config.enter_delta_c && r.score>best.score)best=r;
    }
    d->result.candidates=candidates;
    if(d->tracking){
        if(near.area){
            d->result.x+=d->config.smoothing*(near.x-d->result.x);
            d->result.y+=d->config.smoothing*(near.y-d->result.y);
            d->result.area=near.area;d->misses=0;d->result.held=false;
            d->result.last_seen_ms=f->captured_ms;return PEEK_ACCEPTED;
        }
        d->result.held=true;
        if(++d->misses<d->config.release_frames)return PEEK_ACCEPTED;
        clear_track(d);
    }
    if(!best.area){d->hits=0;return PEEK_ACCEPTED;}
    if(!d->hits || distance(best.x,best.y,d->pending_x,d->pending_y)>d->config.max_distance*d->config.max_distance)d->hits=0;
    d->pending_x=best.x;d->pending_y=best.y;
    if(++d->hits>=d->config.acquire_frames){
        d->tracking=d->result.has_target=true;d->result.held=false;
        d->result.x=best.x;d->result.y=best.y;d->result.area=best.area;
        d->result.last_seen_ms=f->captured_ms;d->hits=0;
    }
    return PEEK_ACCEPTED;
}
const char *peek_data_name(peek_data_t data)
{
    static const char *names[]={"WAITING","VALID","INVALID","STALE"};
    return data<=PEEK_STALE?names[data]:"UNKNOWN";
}
