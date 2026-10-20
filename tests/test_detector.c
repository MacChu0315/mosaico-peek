/* SPDX-License-Identifier: Apache-2.0 */
#include "peek.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static peek_detector_t d;
static peek_frame_t f;
static uint64_t seq, now;
static void reset(void) {
    assert(peek_init(&d, NULL)); seq=now=0;
}
static void frame(int x, int y) {
    f=(peek_frame_t){.sequence=++seq,.captured_ms=(now+=125),.complete=true};
    for(int i=0;i<768;i++){f.c[i]=22;f.valid[i]=1;}
    if(x>=0)for(int j=y;j<y+4;j++)for(int i=x;i<x+4;i++)f.c[j*32+i]=30;
}
static void submit(int x,int y){frame(x,y);assert(peek_submit(&d,&f,now)==PEEK_ACCEPTED);}
int main(void) {
    reset();assert(d.result.data==PEEK_WAITING);
    for(int i=0;i<100;i++)submit(-1,0);
    assert(!d.result.has_target && d.result.data==PEEK_VALID);
    submit(4,8);assert(!d.result.has_target);
    uint64_t last=d.result.last_valid_ms, count=d.result.accepted_samples;
    for(int i=0;i<100;i++)assert(peek_submit(&d,&f,now)==PEEK_DUPLICATE);
    assert(!d.result.has_target && d.result.accepted_samples==count && d.result.last_valid_ms==last);
    submit(4,8);submit(4,8);assert(d.result.has_target);
    for(int i=0;i<300;i++)submit(4,8);
    assert(d.result.has_target && fabsf(d.result.x-5.5f)<0.01f);
    for(int x=5;x<20;x++)submit(x,8);
    assert(d.result.has_target && fabsf(d.result.x-20.5f)<2.1f);
    submit(-1,0);assert(d.result.held);submit(-1,0);assert(!d.result.has_target);
    reset();for(int i=0;i<3;i++)submit(3,4);
    for(int k=0;k<20;k++){
        frame(3,4);for(int y=15;y<20;y++)for(int x=23;x<29;x++)f.c[y*32+x]=45;
        assert(peek_submit(&d,&f,now)==PEEK_ACCEPTED);assert(d.result.x<8);
    }
    last=d.result.last_valid_ms;count=d.result.accepted_samples;
    assert(peek_tick(&d,now+250));assert(d.result.has_target);
    assert(peek_submit(&d,&f,now+300)==PEEK_DUPLICATE);
    assert(d.result.last_valid_ms==last && d.result.accepted_samples==count);
    assert(peek_tick(&d,now+750));assert(d.result.data==PEEK_STALE && !d.result.has_target);
    assert(!peek_tick(&d,now));
    /* New epoch must reset both time and frame identity. */
    reset();for(int i=0;i<3;i++)submit(2,2);
    frame(2,2);f.complete=false;assert(peek_submit(&d,&f,now)==PEEK_REJECTED);
    assert(d.result.data==PEEK_INVALID && !d.result.has_target);
    assert(d.result.last_valid_ms==now-125);
    submit(2,2);assert(!d.result.has_target);
    submit(2,2);submit(2,2);assert(d.result.has_target);
    frame(2,2);f.c[99]=NAN;assert(peek_submit(&d,&f,now)==PEEK_REJECTED);
    assert(d.result.data==PEEK_INVALID);
    frame(2,2);f.valid[0]=0;assert(peek_submit(&d,&f,now)==PEEK_REJECTED);
    frame(2,2);f.c[0]=INFINITY;assert(peek_submit(&d,&f,now)==PEEK_REJECTED);
    reset();frame(2,2);f.captured_ms=now+1;
    assert(peek_submit(&d,&f,now)==PEEK_REJECTED && !d.result.has_valid);
    reset();submit(2,2);frame(2,2);f.captured_ms=0;
    assert(peek_submit(&d,&f,now)==PEEK_REJECTED);
    reset();submit(2,2);submit(-1,0);submit(2,2);assert(!d.result.has_target);
    reset();frame(-1,0);f.c[0]=50;assert(peek_submit(&d,&f,now)==PEEK_ACCEPTED);
    assert(!d.result.has_target && d.result.candidates==0);
    reset();for(int i=0;i<3;i++)submit(2,2);
    last=d.result.last_valid_ms;count=d.result.accepted_samples;
    f.sequence=seq-1;f.captured_ms=last-125;
    assert(peek_submit(&d,&f,now+1)==PEEK_DUPLICATE);
    assert(d.result.has_target && d.result.last_valid_ms==last && d.result.accepted_samples==count);
    assert(peek_tick(&d,now+499) && d.result.has_target);
    assert(peek_tick(&d,now+500) && !d.result.has_target && d.result.data==PEEK_VALID);
    assert(d.result.x==-1 && d.result.y==-1);
    peek_config_t cfg=peek_default_config();cfg.smoothing=NAN;assert(!peek_init(&d,&cfg));
    reset();for(int i=0;i<3;i++)submit(2,2);
    last=d.result.last_valid_ms;count=d.result.accepted_samples;
    assert(peek_fault(&d,now+50));assert(d.result.data==PEEK_INVALID && !d.result.has_target);
    assert(d.result.sequence==seq && d.result.accepted_samples==count && d.result.last_valid_ms==last);
    puts("PASS detector: empty/stationary/moving/multi/repeat/gaps/timeout/invalid/time/config");
    return 0;
}
