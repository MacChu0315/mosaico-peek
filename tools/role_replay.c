/* SPDX-License-Identifier: Apache-2.0 */
#include "replay.h"
#include "dragon.h"
#include <inttypes.h>
static peek_detector_t detector;
int main(int argc,char **argv){
    if(argc!=2)return 2;
    peek_replay_t r={0};dragon_t c;dragon_reset(&c,90640);
    if(!peek_init(&detector,NULL)||!peek_replay_open(&r,argv[1]))return 2;
    while(r.ready){
        if(r.sample)(void)peek_submit(&detector,&r.frame,r.due_ms);
        else if(r.fault)(void)peek_fault(&detector,r.due_ms);
        else if(!peek_tick(&detector,r.due_ms))return 2;
        if(!dragon_update(&c,&detector.result,r.due_ms))return 2;
        fputs("{\"result\":",stdout);peek_write_result(stdout,&detector);
        printf(",\"role\":\"%s\",\"stationary\":%s,\"observations\":%" PRIu64 ",\"gaze_x\":%.9g,\"gaze_y\":%.9g}\n",dragon_mode_name(c.mode),c.stationary?"true":"false",c.observations,c.pose.gaze_x,c.pose.gaze_y);
        if(!peek_replay_next(&r)){fprintf(stderr,"%s\n",r.error);return 2;}
    }
    peek_replay_close(&r);return 0;
}
