/* SPDX-License-Identifier: Apache-2.0 */
#include "replay.h"
#include "peek_live.h"
#include <inttypes.h>
static peek_live_t live;
#define detector live.detector
int main(int argc,char **argv){
    if(argc!=2)return 2;
    peek_replay_t r={0};
    if(!peek_live_init(&live)||!peek_replay_open(&r,argv[1]))return 2;
    while(r.ready){
        if(!peek_live_event(&live,r.sample?&r.frame:NULL,r.fault,r.due_ms))return 2;
        const dragon_t c=live.dragon;
        fputs("{\"result\":",stdout);peek_write_result(stdout,&detector);
        printf(",\"role\":\"%s\",\"stationary\":%s,\"observations\":%" PRIu64 ",\"gaze_x\":%.9g,\"gaze_y\":%.9g}\n",dragon_mode_name(c.mode),c.stationary?"true":"false",c.observations,c.pose.gaze_x,c.pose.gaze_y);
        if(!peek_replay_next(&r)){fprintf(stderr,"%s\n",r.error);return 2;}
    }
    peek_replay_close(&r);return 0;
}
