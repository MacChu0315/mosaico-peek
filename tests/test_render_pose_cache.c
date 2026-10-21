/* SPDX-License-Identifier: Apache-2.0 */
#include "../src/dragon_render.c"
#include <assert.h>
#include <stdio.h>
int main(void){
    dragon_renderer_t *r=dragon_renderer_create();assert(r);
    assert(dragon_renderer_set_sample_step(r,2));
    uint16_t *a=malloc(480*480*2),*b=malloc(480*480*2);assert(a&&b);
    unsigned kinds[3]={0};uint32_t seed=90640;
    for(unsigned i=0;i<40;i++){
        seed=seed*1664525u+1013904223u;
        dragon_pose_t p={(int)(seed&255)/128.0f-1,(int)((seed>>8)&255)/128.0f-1,
            i%4==0?1:i%4==1?.5f:0,.69f+(i%5)*.02f,.06f,.16f+(i%7)*.08f};
        assert(dragon_renderer_prepare(r,&p));assert(!r->fast_cache_valid);
        assert(dragon_renderer_prepare(r,&p));assert(r->fast_cache_valid);
        for(unsigned j=0;j<FAST_PIXELS;j++)kinds[r->fast_pixels[j].kind]++;
        assert(dragon_renderer_draw(r,a,960,0,0,480,480));
        r->fast_cache_valid=false;assert(dragon_renderer_draw(r,b,960,0,0,480,480));
        assert(!memcmp(a,b,480*480*2));r->fast_cache_valid=true;
        /* Gaze and pupil change cannot invalidate geometry, but final eye
         * pixels must still come from the new prepared dynamic pose. */
        p.gaze_x=-p.gaze_x;p.gaze_y=-p.gaze_y;p.pupil_width=.08f;
        assert(dragon_renderer_prepare(r,&p));assert(r->fast_cache_valid);
        assert(dragon_renderer_draw(r,a,960,0,0,480,480));
        r->fast_cache_valid=false;assert(dragon_renderer_draw(r,b,960,0,0,480,480));assert(!memcmp(a,b,480*480*2));
        assert(dragon_renderer_set_sample_step(r,1));assert(!r->fast_cache_valid);
        assert(dragon_renderer_set_sample_step(r,2));
    }
    assert(kinds[0] && kinds[1] && kinds[2]);
    printf("PASS prepared geometry:80 full sampled frames equal scalar; static/interior/fallback pixels %u/%u/%u; gaze/pupil remain dynamic\n",kinds[0],kinds[1],kinds[2]);
    free(a);free(b);dragon_renderer_destroy(r);
}
