/* SPDX-License-Identifier: Apache-2.0 */
#include "eye_layers.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static unsigned stage(float p){return (unsigned)floorf(p*8+.5f);}
int main(void){
    dragon_t role;dragon_reset(&role,90640);
    for(unsigned age=0;age<=500;age++){
        role.now_ms=role.next_blink_ms+age;dragon_t before=role;
        eye_layers_t a=eye_character_layers(2,&role),b=eye_character_layers(2,&role);
        assert(a.membrane==b.membrane&&a.lid==0&&!memcmp(&role,&before,sizeof(role)));
        assert(!eye_character_dual_layers(1));
        assert(a.membrane>=0&&a.membrane<=1);
        if(age==0||age>=240)assert(a.membrane==0);
        if(age>=100&&age<=120)assert(a.membrane==1);
        for(unsigned c=0;c<4;c++)if(!eye_character_dual_layers(c)){eye_layers_t p=eye_character_layers(c,&role);assert(p.membrane==0&&p.lid==role.pose.blink);}
    }
    /* Every integer interrupted-close time must preserve the visible frame,
     * then complete150ms wake. Source result/role are never mutated by draw. */
    for(unsigned age=1;age<=450;age++){
        dragon_reset(&role,90640);peek_result_t r={.data=PEEK_VALID,.has_valid=true};assert(dragon_update(&role,&r,0));
        r.last_valid_ms=10000+age;assert(dragon_update(&role,&r,r.last_valid_ms));
        eye_layers_t a=eye_character_layers(2,&role);
        assert(role.sleeping&&fabsf(a.membrane-fminf(1,age/100.f))<1e-6f);
        assert(fabsf(a.lid-fmaxf(0,(age-100.f)/350.f))<1e-6f);
        r.has_target=true;r.x=4;r.y=6;r.accepted_samples=3;r.last_seen_ms=r.last_valid_ms;
        assert(dragon_update(&role,&r,r.last_valid_ms));eye_layers_t b=eye_character_layers(2,&role);
        assert(role.waking&&stage(a.membrane)==stage(b.membrane)&&stage(a.lid)==stage(b.lid));
        dragon_t same=role;assert(dragon_update(&role,&r,r.last_valid_ms));assert(!memcmp(&same,&role,sizeof(role)));
        assert(dragon_update(&role,&r,r.last_valid_ms+150));b=eye_character_layers(2,&role);assert(!role.waking&&b.membrane==0&&b.lid==0);
    }
    for(unsigned age=99;age<=101;age++){
        dragon_reset(&role,90640);peek_result_t r={.data=PEEK_VALID,.has_valid=true};assert(dragon_update(&role,&r,0));
        uint64_t at=10000+age;r.last_valid_ms=at;assert(dragon_update(&role,&r,at));
        r.has_target=true;r.x=4;r.y=6;r.accepted_samples=3;r.last_seen_ms=at;assert(dragon_update(&role,&r,at));
        assert(dragon_update(&role,&r,at+75));eye_layers_t mid=eye_character_layers(2,&role);
        assert(mid.membrane>.49f&&mid.membrane<.51f&&stage(mid.lid)==0);
    }
    dragon_reset(&role,90640);peek_result_t r={.data=PEEK_VALID,.has_valid=true};assert(dragon_update(&role,&r,0));
    r.last_valid_ms=11000;assert(dragon_update(&role,&r,11000));eye_layers_t p=eye_character_layers(2,&role);assert(p.membrane==1&&p.lid==1);
    r.data=PEEK_INVALID;assert(dragon_update(&role,&r,11500));p=eye_character_layers(2,&role);assert(role.sleeping&&!role.waking&&p.lid==1);
    puts("PASS deep-sea240ms membrane,450/150 sleep/wake,450 interrupted closes, faults, idempotence and source immutability");
}
