/* SPDX-License-Identifier: Apache-2.0 */
#include <zlib.h>
#include <assert.h>
#include <stdio.h>
static unsigned decodes;
static int counted_decode(Bytef *dst,uLongf *n,const Bytef *src,uLong size){decodes++;return uncompress(dst,n,src,size);}
#define uncompress counted_decode
#include "../src/eye_pack.c"
#undef uncompress
int main(void){
    eye_pack_t *r=eye_pack_create();assert(r&&eye_pack_select(r,1)&&decodes==2);
    dragon_pose_t p={0};assert(eye_pack_prepare_layers(r,&p,0,0)&&decodes==4);
    assert(eye_pack_prepare_layers(r,&p,0,0)&&decodes==4);
    p.gaze_x=.5f;assert(eye_pack_prepare_layers(r,&p,0,0)&&decodes==4);
    assert(eye_pack_prepare_layers(r,&p,.125f,0)&&decodes==5);
    assert(eye_pack_prepare_layers(r,&p,.125f,.125f)&&decodes==6);
    size_t size=FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES;void *copy=malloc(size);assert(copy);memcpy(copy,r->storage,size);
    eye_pack_t before=*r;uint16_t *pixels=malloc(480*480*2);assert(pixels);
    assert(eye_pack_draw(r,pixels,960,0,0,480,480)&&decodes==6);
    assert(!memcmp(copy,r->storage,size)&&!memcmp(&before,r,sizeof(before)));
    assert(!eye_pack_prepare_layers(r,&p,NAN,0)&&!eye_pack_prepare_layers(r,&p,0,1.1f));
    assert(decodes==6&&r->prepared);
    assert(!eye_pack_select(r,0));assert(eye_pack_name(0)==NULL);
    assert(eye_pack_draw(r,pixels,960,0,0,480,480));
    assert(!eye_pack_eye_occluded(r));
    assert(eye_pack_prepare_layers(r,&p,1,1)&&eye_pack_eye_occluded(r));
    assert(eye_pack_draw(r,pixels,960,0,0,480,480));
    uint16_t *closed=malloc(480*480*2);assert(closed);memcpy(closed,pixels,480*480*2);
    p.gaze_x=-.78f;p.gaze_y=.58f;
    assert(eye_pack_prepare_layers(r,&p,0,1)&&eye_pack_eye_occluded(r));
    assert(eye_pack_draw(r,pixels,960,0,0,480,480)&&!memcmp(closed,pixels,480*480*2));
    /* A transparent gap in an alternate lid must disable occlusion reuse. */
    unsigned off=((240-eye_themes[1].y)*480+240-eye_themes[1].x)*4+3;
    assert(r->frame[(240*480+240)*4+3]!=255);
    unsigned char alpha=r->lid[1][off];r->lid[1][off]=254;assert(!lid_covers_eye(r));r->lid[1][off]=alpha;
    assert(eye_pack_prepare_layers(r,&p,0,0)&&!eye_pack_eye_occluded(r));free(closed);
    assert(eye_pack_select(r,2)&&!eye_pack_prepare_layers(r,&p,0,0));
    free(copy);free(pixels);eye_pack_destroy(r);
    puts("PASS deep-sea independent decode keys, unchanged-stage/gaze reuse, draw-readonly and invalid-phase preservation");
}
