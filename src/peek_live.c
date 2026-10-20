/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_live.h"
#include <string.h>
bool peek_live_init(peek_live_t *s){
    if(!s)return false;
    memset(s,0,sizeof(*s));dragon_reset(&s->dragon,90640);
    return peek_init(&s->detector,NULL);
}
bool peek_live_event(peek_live_t *s,const peek_frame_t *f,bool fault,uint64_t now){
    if(!s || (f&&fault))return false;
    if(f){
        if(peek_submit(&s->detector,f,now)==PEEK_ACCEPTED){s->displayed=*f;s->has_frame=true;}
    }else if(fault){if(!peek_fault(&s->detector,now))return false;}
    else if(!peek_tick(&s->detector,now))return false;
    return dragon_update(&s->dragon,&s->detector.result,now);
}
