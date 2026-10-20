/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_live.h"
#include <assert.h>
#include <stdio.h>
static peek_live_t source,display;
static peek_frame_t frame;
int main(void){
    assert(peek_live_init(&source));
    for(unsigned i=0;i<768;i++){frame.c[i]=22;frame.valid[i]=1;}
    frame.complete=true;
    for(unsigned y=9;y<14;y++)for(unsigned x=12;x<17;x++)frame.c[y*32+x]=32;
    /* Render only samples a mailbox every750ms. Acquisition still processes
     * all8Hz observations; the old render-owned detector could never acquire. */
    for(unsigned i=0;i<40;i++){
        frame.sequence=i+1;frame.captured_ms=i*125;
        assert(peek_live_event(&source,&frame,false,frame.captured_ms));
        if(i>=2)assert(source.detector.result.has_target);
        if(i%6==0)display=source;
        if(i>=11)assert(source.dragon.mode==DRAGON_HOLD);
    }
    assert(source.detector.result.accepted_samples==40);
    assert(display.detector.result.accepted_samples==37);
    assert(peek_live_event(&display,NULL,false,5000));
    assert(source.detector.now_ms==4875 && source.dragon.now_ms==4875);
    assert(source.dragon.observations==display.dragon.observations+3);
    assert(peek_live_event(&source,NULL,true,5625));
    assert(source.detector.result.data==PEEK_STALE && !source.detector.result.has_target);
    assert(source.detector.result.accepted_samples==40);
    assert(peek_live_event(&source,NULL,false,7000));assert(source.dragon.mode==DRAGON_IDLE);
    puts("PASS live ownership: slow renderer cannot discard detection samples; stationary hold, copy isolation and stale fault remain correct");
}
