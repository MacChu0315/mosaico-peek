/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_orientation.h"
#include <math.h>
void peek_orientation_sample(peek_orientation_t *s,float x,float y,float z,float rate,bool valid,uint64_t now){
    if(s->started && now<=s->last_ms)return;
    bool gap=s->started && now-s->last_ms>100;
    s->started=true;s->last_ms=now;
    float mag=sqrtf(x*x+y*y+z*z);
    if(gap){s->filtered=false;s->pending=false;}
    if(!valid||!isfinite(mag)||!isfinite(rate)||mag<.85f||mag>1.15f||fabsf(rate)>12.f){
        s->filtered=false;s->pending=false;return;
    }
    if(!s->filtered){s->x=x;s->y=y;s->z=z;s->filtered=true;}
    else {s->x+=.25f*(x-s->x);s->y+=.25f*(y-s->y);s->z+=.25f*(z-s->z);}
    float plane=hypotf(s->x,s->y),rx=fabsf(s->x),ry=fabsf(s->y);
    /* Require both current and filtered samples to be away from flat and the
     * 45-degree boundary. A 1.4 axis ratio gives a deadband around diagonals. */
    if(hypotf(x,y)<.5f||plane<.5f||fmaxf(rx,ry)<1.4f*fminf(rx,ry)){
        s->pending=false;return;
    }
    unsigned q=rx>ry?(s->x>0?270:90):(s->y>0?0:180);
    unsigned raw=fabsf(x)>fabsf(y)?(x>0?270:90):(y>0?0:180);
    if(q!=raw||fmaxf(fabsf(x),fabsf(y))<1.4f*fminf(fabsf(x),fabsf(y))||q==s->rotation){s->pending=false;return;}
    if(!s->pending||s->candidate!=q){s->candidate=q;s->since_ms=now;s->pending=true;}
    if(now-s->since_ms>=400){s->rotation=q;s->pending=false;}
}
void peek_orientation_point(unsigned q,unsigned x,unsigned y,unsigned *lx,unsigned *ly){
    switch(q){
        case 90:*lx=y;*ly=479-x;break;
        case 180:*lx=479-x;*ly=479-y;break;
        case 270:*lx=479-y;*ly=x;break;
        default:*lx=x;*ly=y;break;
    }
}
void peek_orientation_gaze(unsigned q,float x,float y,float *lx,float *ly){
    /* Normalize BEFORE swapping: authored horizontal/vertical amplitudes differ. */
    switch(q){
        case 90:*lx=y*(.78f/.58f);*ly=-x*(.58f/.78f);break;
        case 180:*lx=-x;*ly=-y;break;
        case 270:*lx=-y*(.78f/.58f);*ly=x*(.58f/.78f);break;
        default:*lx=x;*ly=y;break;
    }
}
