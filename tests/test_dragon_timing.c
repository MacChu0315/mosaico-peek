/* SPDX-License-Identifier: Apache-2.0 */
#include "dragon.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#define SAMPLES 40
static peek_detector_t detector;
static peek_frame_t frame;
static dragon_t dragon;
typedef struct {dragon_mode_t mode;bool quiet,stationary,held;uint64_t quiet_since,observations,capture,phase;} decision_t;
static unsigned latency(unsigned scenario,unsigned capture){
    if(scenario==0)return 0;
    if(scenario==1)return 125;
    if(capture<2000)return 0;
    if(scenario==2 || scenario==6)return 200;
    if(scenario==3)return 175; /* old capture1875 expires only at2176, not2175 */
    if(scenario==4)return 176; /* arrival exactly at2176 must expire first */
    if(scenario==5)return 301; /* new capture itself also exceeds freshness */
    return capture<3000?200:125; /* legal receive-delay decrease, ordered events */
}
static void make_frame(unsigned k,unsigned scenario){
    frame=(peek_frame_t){.sequence=k+1,.captured_ms=k*125,.complete=true};
    for(unsigned i=0;i<768;i++){frame.c[i]=22;frame.valid[i]=1;}
    if(!(scenario==6 && k==20))for(unsigned y=8;y<12;y++)for(unsigned x=12;x<16;x++)frame.c[y*32+x]=30;
}
static decision_t decision(void){return (decision_t){dragon.mode,dragon.quiet,dragon.stationary,dragon.observation_held,dragon.quiet_since_ms,dragon.observations,dragon.last_capture_ms,dragon.phase_ms};}
static void run(unsigned hz,unsigned scenario,decision_t output[SAMPLES]){
    assert(peek_init(&detector,NULL));dragon_reset(&dragon,90640);unsigned k=0;
    for(unsigned tick=0;tick<=hz*7;tick++){
        uint64_t now=(uint64_t)tick*1000/hz;
        while(k<SAMPLES){
            unsigned capture=k*125;uint64_t due=capture+latency(scenario,capture);if(due>now)break;
            make_frame(k,scenario);assert(peek_submit(&detector,&frame,due)==PEEK_ACCEPTED);
            assert(dragon_update(&dragon,&detector.result,due));output[k]=decision();
            dragon_t before=dragon;assert(dragon_update(&dragon,&detector.result,due));assert(!memcmp(&before,&dragon,sizeof(before)));
            if(k==16)printf("scenario=%u hz=%u capture=%u receive=%" PRIu64 " mode=%s stationary=%u quiet_since=%" PRIu64 "\n",scenario,hz,capture,due,dragon_mode_name(dragon.mode),dragon.stationary,dragon.quiet_since_ms);
            k++;
        }
        assert(peek_tick(&detector,now));assert(dragon_update(&dragon,&detector.result,now));
        if(now>=6000)assert(!dragon.stationary && !dragon.target_active);
    }
    assert(k==SAMPLES);
}
static void equal(const decision_t *a,const decision_t *b){
    assert(a->mode==b->mode && a->quiet==b->quiet && a->stationary==b->stationary && a->held==b->held);
    assert(a->quiet_since==b->quiet_since && a->observations==b->observations && a->capture==b->capture && a->phase==b->phase);
}
int main(void){
    decision_t states[3][SAMPLES];unsigned rates[]={30,60,120};
    for(unsigned scenario=0;scenario<8;scenario++){
        for(unsigned i=0;i<3;i++)run(rates[i],scenario,states[i]);
        for(unsigned k=0;k<SAMPLES;k++)for(unsigned i=1;i<3;i++)equal(&states[0][k],&states[i][k]);
        if(scenario==0||scenario==1||scenario==3)assert(states[0][16].stationary && states[0][16].mode==DRAGON_HOLD);
        else assert(!states[0][16].stationary && states[0][16].mode==DRAGON_TRACKING && states[0][16].quiet_since==2000);
        if(scenario==6)assert(states[0][20].held && !states[0][20].stationary);
    }
    puts("PASS capture/receive timing:8 latency/boundary/held scenarios at30/60/120Hz, stopped stream and same-time idempotence");
}
