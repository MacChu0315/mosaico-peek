/* SPDX-License-Identifier: Apache-2.0 */
#include "dragon.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void run(unsigned hz){
    dragon_t c;dragon_reset(&c,90640);peek_result_t r={.data=PEEK_VALID,.has_valid=true};
    for(unsigned i=0;i<=hz*12;i++){
        uint64_t now=(uint64_t)i*1000/hz;r.last_valid_ms=now;
        assert(dragon_update(&c,&r,now));
        if(now<10000)assert(!c.sleeping);
        if(now>=10450)assert(c.sleeping && c.pose.blink==1 && c.mode==DRAGON_IDLE);
    }
    dragon_t sleeping=c;assert(dragon_update(&c,&r,12000));assert(!memcmp(&sleeping,&c,sizeof(c)));
    /* A real acquired result wakes, a fault never creates an observation. */
    r.data=PEEK_STALE;assert(dragon_update(&c,&r,12100));assert(c.pose.blink==1);
    r=(peek_result_t){.data=PEEK_VALID,.has_valid=true,.has_target=true,.x=4,.y=6,.accepted_samples=3,.last_valid_ms=12200,.last_seen_ms=12200};
    assert(dragon_update(&c,&r,12200));assert(!c.sleeping && c.waking && c.mode==DRAGON_NOTICE && c.pose.blink==1);
    uint64_t count=c.observations;assert(dragon_update(&c,&r,12275));assert(c.pose.blink>0 && c.pose.blink<1 && c.observations==count);
    assert(dragon_update(&c,&r,12350));assert(!c.waking && c.pose.blink==0 && c.observations==count);
    r.has_target=false;assert(dragon_update(&c,&r,12400));assert(c.mode==DRAGON_LEAVE);
    assert(dragon_update(&c,&r,13600));assert(c.mode==DRAGON_IDLE && !c.sleeping);
    assert(dragon_update(&c,&r,23599));assert(!c.sleeping);
    assert(dragon_update(&c,&r,24050));assert(c.sleeping && c.pose.blink==1);
    /* No callback between the idle deadline and acquisition: same wake. */
    dragon_reset(&c,90640);r.has_target=true;r.last_valid_ms=r.last_seen_ms=15000;
    assert(dragon_update(&c,&r,15000));assert(c.waking && c.pose.blink==1);
}
int main(void){run(8);run(30);run(120);puts("PASS idle sleep:10s idle,450ms close,150ms acquired-target wake, stale stays closed, same-time pure, reentry resets deadline");}
