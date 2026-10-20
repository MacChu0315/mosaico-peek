/* SPDX-License-Identifier: Apache-2.0 */
#include "dragon.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static peek_detector_t d;
static peek_frame_t f;
static dragon_t c;
static void frame(unsigned k){
    f=(peek_frame_t){.sequence=k+1,.captured_ms=k*125,.complete=true};
    for(unsigned i=0;i<768;i++){f.c[i]=22;f.valid[i]=1;}
    int x=k<16?(int)k:16;
    if(k<88 && k!=42)for(int y=8;y<12;y++)for(int j=x;j<x+4;j++)f.c[y*32+j]=30;
    if(k>=96 && k<104)f.complete=false;
}
static unsigned run(unsigned hz,dragon_mode_t *states){
    assert(peek_init(&d,NULL));dragon_reset(&c,90640);unsigned sample=0,decisions=0;
    for(unsigned tick=0;tick<=hz*16;tick++){
        uint64_t now=(uint64_t)tick*1000/hz;
        while(sample<=128 && (uint64_t)sample*125<=now){
            frame(sample);assert(peek_submit(&d,&f,f.captured_ms)!=PEEK_DUPLICATE);
            assert(dragon_update(&c,&d.result,f.captured_ms));
            states[decisions++]=c.mode;sample++;
        }
        assert(peek_tick(&d,now));assert(dragon_update(&c,&d.result,now));
        assert(isfinite(c.pose.gaze_x)&&fabsf(c.pose.gaze_x)<=1);
        if(now>=5250 && now<5375){assert(c.observation_held);assert(!c.stationary);assert(c.mode!=DRAGON_HOLD);}
        if(now>=7000 && now<10000)assert(c.mode==DRAGON_HOLD && c.stationary);
    }
    return decisions;
}
int main(void){
    dragon_mode_t a[200],b[200],e[200];unsigned n=run(30,a);assert(run(60,b)==n);assert(run(120,e)==n);
    assert(!memcmp(a,b,n*sizeof(*a))&&!memcmp(a,e,n*sizeof(*a)));
    dragon_mapping_t mapping={0};float x,y;
    assert(dragon_map(&mapping,15.5f,11.5f,&x,&y)&&fabsf(x)<.0001f&&fabsf(y)<.0001f);
    assert(dragon_map(&mapping,31,23,&x,&y)&&x>0&&y>0);
    mapping.flip_x=true;assert(dragon_map(&mapping,31,23,&x,&y)&&x<0&&y>0);
    mapping.rotation=90;assert(dragon_map(&mapping,0,0,&x,&y));
    dragon_reset(&c,90640);peek_result_t r={.data=PEEK_VALID,.has_valid=true,.has_target=true,.x=10,.y=10,.last_valid_ms=0,.last_seen_ms=0,.accepted_samples=1};
    assert(dragon_update(&c,&r,0));assert(c.mode==DRAGON_NOTICE&&c.notices==1);
    for(unsigned i=0;i<100;i++){assert(dragon_update(&c,&r,0));}
    assert(c.observations==1&&c.notices==1);
    r.data=PEEK_STALE;r.has_target=false;r.x=r.y=-1;assert(dragon_update(&c,&r,100));assert(c.mode==DRAGON_LEAVE);
    float oldx=c.pose.gaze_x,oldv=c.vx;r.data=PEEK_VALID;r.has_target=true;r.x=20;r.y=10;r.last_valid_ms=r.last_seen_ms=100;r.accepted_samples++;
    assert(dragon_update(&c,&r,100));assert(c.mode==DRAGON_NOTICE&&c.notices==2&&c.pose.gaze_x==oldx&&c.vx==oldv);
    assert(!dragon_update(&c,&r,99));
    dragon_reset(&c,90640);r=(peek_result_t){.data=PEEK_WAITING};assert(dragon_update(&c,&r,6160));assert(c.pose.blink==1);
    dragon_t replay=c;dragon_reset(&c,90640);assert(dragon_update(&c,&r,6160));assert(!memcmp(&c,&replay,sizeof(c)));
    dragon_reset(&c,1);r=(peek_result_t){.data=PEEK_VALID,.has_valid=true,.has_target=true,.x=15.5f,.y=11.5f};
    for(unsigned t=0;t<=2000;t+=125){r.accepted_samples++;r.last_valid_ms=r.last_seen_ms=t;assert(dragon_update(&c,&r,t));}
    assert(c.stationary&&c.mode==DRAGON_HOLD);
    assert(dragon_update(&c,&r,2300)&&c.stationary);
    assert(dragon_update(&c,&r,2301)&&!c.stationary&&c.mode==DRAGON_TRACKING);
    uint64_t observations=c.observations;assert(dragon_update(&c,&r,2301)&&c.observations==observations);
    puts("PASS dragon behavior: production 8Hz inputs; 30/60/120Hz decisions, held, stationary, loss/reappearance, reset seed and mapping");
}
