/* SPDX-License-Identifier: Apache-2.0 */
#include "eye_character_pose.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
/* Role-result fixture only; native acceptance separately feeds temperature arrays. */
static void interrupted_close(void){
    for(unsigned age=1;age<450;age++){
        dragon_t role;dragon_reset(&role,90640);
        peek_result_t r={.data=PEEK_VALID,.has_valid=true};assert(dragon_update(&role,&r,0));
        uint64_t now=10000+age;r.last_valid_ms=now;assert(dragon_update(&role,&r,now));
        dragon_pose_t before=eye_character_pose(3,&role);
        r.has_target=true;r.x=4;r.y=6;r.accepted_samples=3;r.last_seen_ms=now;
        assert(dragon_update(&role,&r,now));dragon_pose_t after=eye_character_pose(3,&role);
        assert(before.gaze_x==after.gaze_x&&before.gaze_y==after.gaze_y&&before.blink==after.blink);
        dragon_t same=role;assert(dragon_update(&role,&r,now));assert(!memcmp(&same,&role,sizeof(role)));
        assert(dragon_update(&role,&r,now+150));after=eye_character_pose(3,&role);assert(!role.waking&&!role.sleeping&&role.pose.blink==0);assert(!memcmp(&after,&role.pose,sizeof(after)));
    }
}
int main(void){
    interrupted_close();
    dragon_t role={0};role.pose=(dragon_pose_t){.6f,-.4f,0,.7f,.06f,.3f};role.mode=DRAGON_IDLE;
    for(unsigned phase=0;phase<3;phase++)for(unsigned step=0;step<=8;step++){
        role.sleeping=phase==1;role.waking=phase==2;role.pose.blink=step/8.f;
        dragon_t unchanged=role;
        for(unsigned character=0;character<4;character++){
            dragon_pose_t p=eye_character_pose(character,&role);
            if(character!=3||phase==0)assert(!memcmp(&p,&role.pose,sizeof(p)));
            else {float follow=1-role.pose.blink/(7.5f/8.f);if(follow<0)follow=0;assert(p.gaze_x==role.pose.gaze_x*follow);assert(p.gaze_y==role.pose.gaze_y*follow);assert(p.blink==role.pose.blink);}
        }
        assert(!memcmp(&role,&unchanged,sizeof(role)));
    }
    role.sleeping=true;role.pose.blink=7.5f/8.f;dragon_pose_t closed=eye_character_pose(3,&role);assert(closed.gaze_x==0&&closed.gaze_y==0);
    role.sleeping=true;role.waking=false;role.pose.blink=1;
    for(int i=0;i<50;i++){role.pose.gaze_x=i*.01f-.25f;role.pose.gaze_y=.2f-i*.008f;dragon_pose_t p=eye_character_pose(3,&role);assert(p.gaze_x==0&&p.gaze_y==0);}
    puts("PASS mechanical sleep closes to fixed center and wakes to source gaze; ordinary blinks/other characters/source immutable");
}
