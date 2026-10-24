/* SPDX-License-Identifier: Apache-2.0 */
/* Exported-pose raster oracle only. Application input remains thermal arrays. */
#include "eye_pack.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
    if(argc!=5&&argc!=7)return 2;
    dragon_pose_t p={0};p.gaze_x=strtof(argv[2],NULL);p.gaze_y=strtof(argv[3],NULL);p.blink=strtof(argv[4],NULL);
    eye_pack_t *r=eye_pack_create();uint16_t *out=malloc(480*480*2);
    if(!r||!out||!eye_pack_select(r,(unsigned)strtoul(argv[1],NULL,10))||
       !(argc==7?eye_pack_prepare_layers(r,&p,strtof(argv[5],NULL),strtof(argv[6],NULL)):eye_pack_prepare(r,&p))||!eye_pack_draw(r,out,960,0,0,480,480)){free(out);eye_pack_destroy(r);return 1;}
    fputs("P6\n480 480\n255\n",stdout);
    for(unsigned i=0;i<480*480;i++){uint16_t v=out[i];unsigned char c[3]={(v>>11)*255/31,((v>>5)&63)*255/63,(v&31)*255/31};if(fwrite(c,1,3,stdout)!=3)return 1;}
    free(out);eye_pack_destroy(r);return 0;
}
