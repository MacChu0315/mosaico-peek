/* SPDX-License-Identifier: Apache-2.0 */
/* Production workspace invariants: immutable base, no accumulated blend or draw mutation. */
#include <assert.h>
#include <stdio.h>
#include "../src/eye_pack.c"
int main(void){
    eye_pack_t *r=eye_pack_create();assert(r&&eye_pack_select(r,2));assert(eye_themes[2].rotating_shutter);
    unsigned char *base=malloc(EYE_BYTES),*prepared=malloc(FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES);
    uint16_t *open=malloc(480*480*2),*frame=malloc(480*480*2);assert(base&&prepared&&open&&frame);
    memcpy(base,r->eye,EYE_BYTES);dragon_pose_t p={.gaze_x=.52f,.gaze_y=-.37f};
    assert(eye_pack_prepare(r,&p)&&eye_pack_draw(r,open,960,0,0,480,480));
    for(unsigned pass=0;pass<2;pass++)for(unsigned i=0;i<9;i++){
        unsigned index=pass?8-i:i;p.blink=index/8.f;
        assert(eye_pack_prepare(r,&p)&&r->lo==index);assert(!memcmp(base,r->eye,EYE_BYTES));
        memcpy(prepared,r->storage,FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES);
        assert(eye_pack_draw(r,frame,960,0,0,480,480));assert(!memcmp(prepared,r->storage,FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES));
        if(!index)assert(!memcmp(open,frame,480*480*2));
    }
    assert(!eye_pack_select(r,0));assert(eye_pack_select(r,1));p.blink=.5f;assert(eye_pack_prepare(r,&p));
    assert(eye_pack_select(r,2));p.blink=0;assert(eye_pack_prepare(r,&p)&&eye_pack_draw(r,frame,960,0,0,480,480));assert(!memcmp(open,frame,480*480*2));
    free(base);free(prepared);free(open);free(frame);eye_pack_destroy(r);puts("PASS shutter full open-close-open and theme reentry; base/draw immutable");
}
