/* SPDX-License-Identifier: Apache-2.0 */
#include "dragon.h"
#include <math.h>
#include <string.h>
static float clamp(float x,float lo,float hi){return fmaxf(lo,fminf(hi,x));}
static float ease(float x){x=clamp(x,0,1);return x*x*x*(x*(x*6-15)+10);}
static uint32_t random_next(dragon_t *c){uint32_t x=c->random;x^=x<<13;x^=x>>17;x^=x<<5;return c->random=x;}
static void enter(dragon_t *c,dragon_mode_t mode,uint64_t at){if(c->mode!=mode){c->mode=mode;c->phase_ms=at;c->transitions++;}}
void dragon_reset(dragon_t *c,uint32_t seed)
{
    memset(c,0,sizeof(*c));c->random=seed?seed:90640;c->mode=DRAGON_IDLE;c->next_blink_ms=6020;
    c->pose=(dragon_pose_t){-.05f,.035f,0,.69f,.072f,.16f};c->goal_x=-.05f;c->goal_y=.035f;
}
bool dragon_map(const dragon_mapping_t *m,float sx,float sy,float *x,float *y)
{
    if(!m||!x||!y||!isfinite(sx)||!isfinite(sy)||sx<0||sx>31||sy<0||sy>23)return false;
    /* Pixel centers: x=15.5,y=11.5 is array center. Physical outer edges
     * -0.5..31.5 / -0.5..23.5 map to -1..1 before bounded eye amplitude. */
    float a=2*(sx+.5f)/32-1,b=2*(sy+.5f)/24-1,t;
    switch(m->rotation){
        case 0:break;case 90:t=a;a=-b;b=t;break;case 180:a=-a;b=-b;break;case 270:t=a;a=b;b=-t;break;default:return false;
    }
    *x=(m->flip_x?-a:a)*.78f;*y=(m->flip_y?-b:b)*.58f;return true;
}
static void spring(float *position,float *velocity,float goal,float seconds,float omega)
{
    if(seconds<=0)return;
    float error=*position-goal,temp=*velocity+omega*error,decay=expf(-omega*seconds);
    *position=goal+(error+temp*seconds)*decay;
    *velocity=(*velocity-omega*temp*seconds)*decay;
}
static void idle_goal(uint64_t now,float *x,float *y)
{
    /* Authored calm holds from approved timeline; not sensor observations. */
    static const float at[]={0,1100,2450,3450,5050,6600,8000,10000};
    static const float gx[]={-.05f,-.05f,-.32f,-.32f,.27f,.27f,-.05f,-.05f};
    static const float gy[]={.035f,.035f,-.045f,-.045f,.01f,.01f,.035f,.035f};
    float t=(float)(now%10000);unsigned i=1;while(i<7&&t>at[i])i++;
    float amount=ease((t-at[i-1])/(at[i]-at[i-1]));
    *x=gx[i-1]+(gx[i]-gx[i-1])*amount;*y=gy[i-1]+(gy[i]-gy[i-1])*amount;
}
static void expire_stillness(dragon_t *c,uint64_t now)
{
    if(c->target_active&&c->has_observation&&now-c->last_capture_ms>300){
        c->quiet=c->stationary=false;
        if(c->mode==DRAGON_HOLD)enter(c,DRAGON_TRACKING,c->last_capture_ms+301);
    }
}
bool dragon_update(dragon_t *c,const peek_result_t *r,uint64_t now)
{
    if(!c||!r||(c->started&&now<c->now_ms))return false;
    float dt=(float)(now-c->now_ms)/1000;
    /* Analytic critically damped follow: no reset on NOTICE or reappearance. */
    spring(&c->pose.gaze_x,&c->vx,c->goal_x,dt,c->mode==DRAGON_LEAVE?3.5f:8.0f);
    spring(&c->pose.gaze_y,&c->vy,c->goal_y,dt,c->mode==DRAGON_LEAVE?3.5f:8.0f);
    c->now_ms=now;c->started=true;
    if(c->mode==DRAGON_NOTICE&&now-c->phase_ms>=320)enter(c,DRAGON_TRACKING,c->phase_ms+320);
    if(c->mode==DRAGON_LEAVE&&now-c->phase_ms>=1200)enter(c,DRAGON_IDLE,c->phase_ms+1200);
    /* Catch up the previous observation's deadline before a newly received
     * capture can overwrite it. Missing an animation tick must not preserve
     * quiet evidence that expired between capture and receipt. */
    expire_stillness(c,now);
    float mapped_x=0,mapped_y=0;
    bool active=r->data==PEEK_VALID && r->has_valid && r->has_target && r->last_valid_ms<=now && dragon_map(&c->mapping,r->x,r->y,&mapped_x,&mapped_y);
    c->observation_held=active&&r->held;
    /* Advance the previous idle deadline before acquisition, even when no
     * animation callback ran during the close. Faults cannot wake the eye. */
    bool idle_closing=c->mode==DRAGON_IDLE && now-c->phase_ms>=10000;
    float sleep_blink=idle_closing?ease((float)(now-c->phase_ms-10000)/450):0;
    if(active&&!c->target_active && idle_closing && sleep_blink>0){
        c->wake_ms=now;c->wake_blink=sleep_blink;c->waking=true;
        c->next_blink_ms=now+3500+random_next(c)%4500;
    }
    if(active&&!c->target_active){enter(c,DRAGON_NOTICE,now);c->notices++;c->has_observation=c->quiet=c->stationary=false;}
    if(!active&&c->target_active){enter(c,DRAGON_LEAVE,now);c->has_observation=c->quiet=c->stationary=false;}
    c->target_active=active;
    bool new_sample=r->accepted_samples>c->last_samples;
    if(new_sample){
        c->last_samples=r->accepted_samples;
        if(active&&!r->held&&r->last_seen_ms==r->last_valid_ms){
            uint64_t capture=r->last_seen_ms;
            bool continuous=c->has_observation&&capture>c->last_capture_ms&&capture-c->last_capture_ms<=300;
            c->speed_px_s=continuous?hypotf(r->x-c->previous_x,r->y-c->previous_y)*1000/(float)(capture-c->last_capture_ms):0;
            if(!continuous || c->speed_px_s>.8f){c->quiet_since_ms=capture;c->quiet=continuous&&c->speed_px_s<=.8f;}
            else if(!c->quiet){c->quiet_since_ms=capture;c->quiet=true;}
            c->stationary=c->quiet&&capture-c->quiet_since_ms>=900;
            c->previous_x=r->x;c->previous_y=r->y;c->last_capture_ms=capture;c->has_observation=true;c->observations++;
            if(c->mode!=DRAGON_NOTICE)enter(c,c->stationary?DRAGON_HOLD:DRAGON_TRACKING,now);
        }else{
            /* Held coordinates are not a fresh still observation. Once per
             * incoming sample, break the evidence; render ticks cannot toggle. */
            c->quiet=c->stationary=false;
            if(active&&c->mode==DRAGON_HOLD)enter(c,DRAGON_TRACKING,now);
        }
    }
    /* Stillness is evidence from fresh captures, not a timer on cached
     * coordinates. Break it at a fixed deadline even before core hold expiry. */
    expire_stillness(c,now);
    if(active){
        c->goal_x=mapped_x;c->goal_y=mapped_y;
        if(c->mode==DRAGON_HOLD){c->goal_x+=.003f*sinf((float)(now%6000)*.0010472f);c->goal_y+=.002f*sinf((float)(now%7000)*.0008976f);}
    }else if(c->mode==DRAGON_IDLE)idle_goal(now,&c->goal_x,&c->goal_y);
    else {c->goal_x=-.05f;c->goal_y=.035f;}
    float pupil=active?.060f:.072f,squint=active?.73f:.69f,tension=active?.50f:.16f;
    if(c->mode==DRAGON_NOTICE){float pulse=sinf(3.14159265f*clamp((float)(now-c->phase_ms)/320,0,1));squint+=.05f*pulse;pupil-=.004f*pulse;tension+=.07f*pulse;}
    if(c->mode==DRAGON_HOLD){squint=.75f;pupil=.062f;tension=.46f;}
    float alpha=1-expf(-dt*7);
    c->pose.squint+=(squint-c->pose.squint)*alpha;c->pose.pupil_width+=(pupil-c->pose.pupil_width)*alpha;c->pose.tension+=(tension-c->pose.tension)*alpha;
    /* Blinks use injected time and seeded intervals, unrelated to render dt. */
    while(now>=c->next_blink_ms+410){if(!idle_closing&&!c->waking)c->blinks++;c->next_blink_ms+=410+3500+random_next(c)%4500;}
    c->pose.blink=0;
    if(now>=c->next_blink_ms){uint64_t age=now-c->next_blink_ms;c->pose.blink=age<140?ease((float)age/140):age<180?1:1-ease((float)(age-180)/230);}
    c->sleeping=c->mode==DRAGON_IDLE && now-c->phase_ms>=10000;
    if(c->sleeping){
        c->pose.blink=ease((float)(now-c->phase_ms-10000)/450);c->waking=false;
    }else if(c->waking){
        uint64_t age=now-c->wake_ms;
        c->pose.blink=c->wake_blink*(1-ease((float)age/150));
        if(age>=150)c->waking=false;
    }
    c->pose.gaze_x=clamp(c->pose.gaze_x,-.85f,.85f);c->pose.gaze_y=clamp(c->pose.gaze_y,-.65f,.65f);
    return true;
}
const char *dragon_mode_name(dragon_mode_t mode){static const char *names[]={"IDLE","NOTICE","TRACKING","HOLD","LEAVE"};return mode<=DRAGON_LEAVE?names[mode]:"UNKNOWN";}
