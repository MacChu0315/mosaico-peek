/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include "dragon.h"
typedef struct {float membrane,lid;} eye_layers_t;
static inline float eye_layer_clamp(float p){return p<0?0:p>1?1:p;}
static inline float eye_layer_smooth(float p){p=eye_layer_clamp(p);return p*p*(3-2*p);}
/* The shared controller stores the quintic close fraction when waking. Invert
 * that existing snapshot, never manufacture a new clock or source observation. */
static inline float eye_close_elapsed(float fraction){
    if(fraction<=0)return 0;
    if(fraction>=1)return 450;
    float lo=0,hi=1;
    for(unsigned i=0;i<24;i++){
        float p=(lo+hi)*.5f,value=p*p*p*(p*(p*6-15)+10);
        if(value<fraction)lo=p;else hi=p;
    }
    return (lo+hi)*225;
}
static inline bool eye_character_dual_layers(unsigned character){return character==1||character==2;}
static inline eye_layers_t eye_organic_close(float elapsed){
    return (eye_layers_t){eye_layer_clamp(elapsed/100),eye_layer_clamp((elapsed-100)/350)};
}
/* Pure presentation. UI characters1/2 are organic R2; other source poses/timing
 * retain their existing path. Nearest9 selection happens in renderer prepare. */
static inline eye_layers_t eye_character_layers(unsigned character,const dragon_t *role){
    if(!eye_character_dual_layers(character))return (eye_layers_t){0,role->pose.blink};
    if(role->sleeping){
        uint64_t age=role->now_ms>=role->phase_ms?role->now_ms-role->phase_ms:0;
        return eye_organic_close(age>10000?(float)(age-10000):0);
    }
    if(role->waking){
        eye_layers_t start=eye_organic_close(eye_close_elapsed(role->wake_blink));
        float age=role->now_ms>=role->wake_ms?(float)(role->now_ms-role->wake_ms):0;
        /* Partial closure opens proportionally, avoiding a discontinuous
         *97.5ms membrane delay from inverse-ease noise near zero lid. */
        float lid_end=97.5f*start.lid;
        return (eye_layers_t){start.membrane*eye_layer_clamp((150-age)/(150-lid_end)),
            lid_end>0?start.lid*eye_layer_clamp(1-age/lid_end):0};
    }
    if(role->now_ms<role->next_blink_ms)return (eye_layers_t){0,0};
    uint64_t age=role->now_ms-role->next_blink_ms;
    float membrane=age<100?eye_layer_smooth(age/100.f):age<120?1:age<240?1-eye_layer_smooth((age-120)/120.f):0;
    return (eye_layers_t){membrane,0};
}
