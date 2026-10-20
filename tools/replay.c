/* SPDX-License-Identifier: Apache-2.0 */
#include "replay.h"
#include <stdlib.h>
static peek_detector_t detector;
int main(int argc,char **argv){
    if(argc!=2){fprintf(stderr,"usage: peek_replay FILE.peek\n");return 2;}
    peek_replay_t replay={0};if(!peek_init(&detector,NULL)||!peek_replay_open(&replay,argv[1])){fprintf(stderr,"%s\n",replay.error);peek_replay_close(&replay);return 1;}
    while(replay.ready){
        if(replay.sample)(void)peek_submit(&detector,&replay.frame,replay.due_ms);else (void)peek_tick(&detector,replay.due_ms);
        peek_write_result(stdout,&detector);putchar('\n');
        if(!peek_replay_next(&replay)){fprintf(stderr,"%s\n",replay.error);peek_replay_close(&replay);return 1;}
    }
    peek_replay_close(&replay);return 0;
}
