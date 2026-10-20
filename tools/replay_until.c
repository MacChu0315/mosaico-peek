/* SPDX-License-Identifier: Apache-2.0 */
#include "replay.h"
static peek_detector_t detector;
int main(int argc,char **argv){
    if(argc!=2)return 2;
    peek_replay_t r={0};
    if(!peek_init(&detector,NULL)||!peek_replay_open(&r,argv[1])){fprintf(stderr,"%s\n",r.error);peek_replay_close(&r);return 1;}
    while(r.ready){
        uint64_t now=r.due_ms;
        if(!peek_replay_until(&r,&detector,now)){fprintf(stderr,"%s\n",r.error);peek_replay_close(&r);return 1;}
        peek_write_result(stdout,&detector);putchar('\n');
    }
    peek_replay_close(&r);return 0;
}
