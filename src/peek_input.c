/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_input.h"
#include <stdlib.h>
void peek_input_cancel(peek_input_t *s){if(s->down)s->blocked=true;}
int peek_input_update(peek_input_t *s,int32_t x,int32_t y,bool pressed,bool enabled,uint64_t now){
    bool valid=x>=0&&x<480&&y>=0&&y<480;
    if(pressed && !s->down){
        s->down=true;s->blocked=!enabled||!valid;s->start_x=x;s->start_y=y;
        s->max_dx=s->max_dy=0;s->started_ms=now;return 0;
    }
    if(!s->down)return 0;
    if(!enabled||!valid||now<s->started_ms)s->blocked=true;
    int dx=0,dy=0;
    if(!s->blocked){
        dx=x-s->start_x;dy=y-s->start_y;
        if(abs(dx)>s->max_dx)s->max_dx=abs(dx);
        if(abs(dy)>s->max_dy)s->max_dy=abs(dy);
    }
    if(pressed)return 0;
    s->down=false;
    if(s->blocked)return 0;
    if(abs(dx)>=48 && abs(dx)>=2*abs(dy))return dx<0?1:-1;
    if(s->max_dx<=16 && s->max_dy<=16 && now-s->started_ms<=600)return 1;
    return 0;
}
