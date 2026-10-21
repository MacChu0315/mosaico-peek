/* SPDX-License-Identifier: Apache-2.0 */
#include "eye_pack.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void){
    eye_pack_t *r=eye_pack_create();assert(r);
    uint16_t *full=malloc(480*480*2);assert(full);
    uint16_t tile[25*19];
    for(unsigned theme=0;theme<3;theme++){
        assert(eye_pack_select(r,theme));
        for(unsigned i=0;i<11;i++){
            dragon_pose_t p={0};p.gaze_x=(i%3-1.0f)*.78f;p.gaze_y=(i%3-1.0f)*.58f;p.blink=i/10.0f;
            assert(eye_pack_prepare(r,&p));assert(eye_pack_draw(r,full,960,0,0,480,480));
            memset(tile,0xa5,sizeof(tile));assert(eye_pack_draw(r,tile,50,17,119,23,19));
            for(unsigned y=0;y<19;y++){
                for(unsigned x=0;x<23;x++)assert(tile[y*25+x]==full[(119+y)*480+17+x]);
                assert(tile[y*25+23]==0xa5a5 && tile[y*25+24]==0xa5a5);
            }
        }
    }
    dragon_pose_t p={0};p.blink=NAN;assert(!eye_pack_prepare(r,&p));
    assert(!eye_pack_select(r,3));assert(!eye_pack_draw(r,full,1,0,0,480,480));
    assert(!eye_pack_draw(r,full,960,-1,0,480,480));
    free(full);eye_pack_destroy(r);puts("PASS layer tiles/stride, three themes, all lids and invalid inputs");
}
