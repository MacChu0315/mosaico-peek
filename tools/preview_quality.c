/* SPDX-License-Identifier: Apache-2.0 */
/* Offline quality comparison only, not a detector/replay input. Uses the actual
 * approved C rasterizer; step2 replicates each sampled RGB565 into a2x2 cell. */
#include "dragon_render.h"
#include <stdlib.h>
#include <stdio.h>
int main(int argc,char **argv){
    if(argc!=2)return 2;
    int step=atoi(argv[1]);if(step!=1&&step!=2)return 2;
    dragon_pose_t pose={-.05f,.035f,0,.69f,.072f,.16f};
    dragon_renderer_t *r=dragon_renderer_create();if(!r||!dragon_renderer_prepare(r,&pose))return 2;
    puts("P6\n480 480\n255");
    for(unsigned y=0;y<480;y++)for(unsigned x=0;x<480;x++){
        uint16_t pixel;if(!dragon_renderer_draw(r,&pixel,2,step==2?(x|1):x,step==2?(y|1):y,1,1))return 2;
        unsigned char p[3]={((pixel>>11)&31)*255/31,((pixel>>5)&63)*255/63,(pixel&31)*255/31};
        if(fwrite(p,1,3,stdout)!=3)return 2;
    }
    dragon_renderer_destroy(r);return 0;
}
