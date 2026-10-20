/* SPDX-License-Identifier: Apache-2.0 */
/* Golden full-frame raster from an EXPORTED pose, for GSP cache/parity QA only.
 * This is never an application input and never replaces temperature detection. */
#include "dragon_render.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
    if(argc!=7)return 2;
    dragon_pose_t p={(float)strtod(argv[1],NULL),(float)strtod(argv[2],NULL),(float)strtod(argv[3],NULL),(float)strtod(argv[4],NULL),(float)strtod(argv[5],NULL),(float)strtod(argv[6],NULL)};
    dragon_renderer_t *r=dragon_renderer_create();uint16_t *pixels=malloc(480*480*2);
    if(!r||!pixels||!dragon_renderer_prepare(r,&p)||!dragon_renderer_draw(r,pixels,960,0,0,480,480)){free(pixels);dragon_renderer_destroy(r);return 1;}
    fputs("P6\n480 480\n255\n",stdout);
    for(unsigned i=0;i<480*480;i++){
        uint16_t v=pixels[i];unsigned char rgb[3]={(unsigned char)(((v>>11)&31)*255/31),(unsigned char)(((v>>5)&63)*255/63),(unsigned char)((v&31)*255/31)};
        if(fwrite(rgb,1,3,stdout)!=3){free(pixels);dragon_renderer_destroy(r);return 1;}
    }
    free(pixels);dragon_renderer_destroy(r);return 0;
}
