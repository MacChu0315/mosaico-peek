/* SPDX-License-Identifier: Apache-2.0 */
#include "replay.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static peek_detector_t d;
static peek_frame_t f;
static void make(unsigned seq,unsigned captured){
    f=(peek_frame_t){.sequence=seq,.captured_ms=captured,.complete=true};
    for(unsigned i=0;i<768;i++){f.c[i]=22;f.valid[i]=1;}
    for(unsigned y=8;y<12;y++)for(unsigned x=8;x<12;x++)f.c[y*32+x]=30;
}
static void unchanged_at(uint64_t now){
    peek_result_t before=d.result;assert(peek_tick(&d,now));
    assert(memcmp(&before,&d.result,sizeof(before))==0);
}
int main(void){
    assert(peek_init(&d,NULL));
    for(unsigned i=0;i<3;i++){make(i+1,i*125);assert(peek_submit(&d,&f,i*125+600)==PEEK_ACCEPTED);unchanged_at(i*125+600);}
    assert(!d.result.has_target && d.result.x==-1 && d.result.last_valid_ms==250);
    for(unsigned failure=0;failure<3;failure++){
        assert(peek_init(&d,NULL));
        for(unsigned i=0;i<3;i++){make(i+1,i*125);assert(peek_submit(&d,&f,i*125)==PEEK_ACCEPTED);}
        if(failure==0){make(4,1000);f.complete=false;assert(peek_submit(&d,&f,1000)==PEEK_REJECTED);}
        if(failure==1)assert(peek_fault(&d,1000));
        if(failure==2){make(4,1001);assert(peek_submit(&d,&f,1000)==PEEK_REJECTED);}
        assert(d.result.data==PEEK_STALE && !d.result.has_target);unchanged_at(1000);
    }
    assert(peek_init(&d,NULL));assert(peek_fault(&d,0));assert(d.result.data==PEEK_INVALID);unchanged_at(0);
    puts("PASS core event aging: delayed acquisition, invalid/fault/future -> STALE priority, same-time idempotence");
}
