/* SPDX-License-Identifier: Apache-2.0 */
/* Compare optimized production output against scalar1.0.4 arithmetic with the current asset geometry. */
#include "eye_pack.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
typedef struct eye_reference eye_ref_t;
eye_ref_t *eye_ref_create(void);
void eye_ref_destroy(eye_ref_t *);
bool eye_ref_select(eye_ref_t *,unsigned);
bool eye_ref_prepare(eye_ref_t *,const dragon_pose_t *);
bool eye_ref_prepare_layers(eye_ref_t *,const dragon_pose_t *,float,float);
bool eye_ref_draw(const eye_ref_t *,void *,size_t,int,int,int,int);
static uint32_t seed=90640;
static float random_unit(void){seed=1664525*seed+1013904223;return (seed>>8)*(1.f/16777216.f);}
int main(void){
    eye_pack_t *fast=eye_pack_create();eye_ref_t *ref=eye_ref_create();assert(fast&&ref);
    uint16_t *a=malloc(480*480*2),*b=malloc(480*480*2);assert(a&&b);
    unsigned count=0;double fast_s=0,ref_s=0;
    for(unsigned theme=1;theme<3;theme++){
        assert(eye_pack_select(fast,theme)&&eye_ref_select(ref,theme));
        for(unsigned i=0;i<144;i++){
            dragon_pose_t p={0};p.gaze_x=(random_unit()*2-1)*.78f;p.gaze_y=(random_unit()*2-1)*.58f;
            p.blink=i%4?0:random_unit();
            if(i<27){p.gaze_x=((int)(i%3)-1)*.78f;p.gaze_y=((int)(i/3%3)-1)*.58f;p.blink=(i/9)*.5f;}
            if(i>=27 && i<44)p.blink=(i-27)/16.f;
            if(i>=128){p.gaze_x=0;p.gaze_y=0;p.blink=(i-128)%9/8.f;}
            if(theme<2){
                float membrane=i%4==3?random_unit():p.blink,lid=i%4==2?random_unit():p.blink;
                assert(eye_pack_prepare_layers(fast,&p,membrane,lid)&&eye_ref_prepare_layers(ref,&p,membrane,lid));
            }else assert(eye_pack_prepare(fast,&p)&&eye_ref_prepare(ref,&p));
            clock_t start=clock();assert(eye_pack_draw(fast,a,960,0,0,480,480));fast_s+=(double)(clock()-start)/CLOCKS_PER_SEC;
            start=clock();assert(eye_ref_draw(ref,b,960,0,0,480,480));ref_s+=(double)(clock()-start)/CLOCKS_PER_SEC;
            for(unsigned pixel=0;pixel<480*480;pixel++)if(a[pixel]!=b[pixel]){
                fprintf(stderr,"mismatch theme%u frame%u pixel%u gaze%.9g,%.9g lid%.9g fast%04x ref%04x\n",theme,i,pixel,p.gaze_x,p.gaze_y,p.blink,a[pixel],b[pixel]);return 1;
            }
            uint16_t tile[19*25];memset(tile,0xa5,sizeof(tile));assert(eye_pack_draw(fast,tile,50,17,119,23,19));
            for(unsigned y=0;y<19;y++){for(unsigned x=0;x<23;x++)assert(tile[y*25+x]==b[(119+y)*480+17+x]);assert(tile[y*25+23]==0xa5a5&&tile[y*25+24]==0xa5a5);}
            count++;
        }
    }
    free(a);free(b);eye_pack_destroy(fast);eye_ref_destroy(ref);
    printf("PASS %u full480 frames bit-identical; exact fractional gaze/lids, bounds, opaque edges, tiles. Host draw CPU fast=%.3fs reference=%.3fs (not device FPS)\n",count,fast_s,ref_s);
}
