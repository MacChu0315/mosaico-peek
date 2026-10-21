/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
static unsigned allocations,frees,fail_at;
static void *allocate(size_t a,size_t b){allocations++;return allocations==fail_at?NULL:calloc(a,b);}
static void release(void *p){if(p)frees++;free(p);}
#define calloc allocate
#define free release
#include "../src/dragon_render.c"
#undef calloc
#undef free
static uint32_t seed=90640;
static float random_unit(void){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return (seed&65535)/65535.0f;}
int main(void){
    allocations=frees=0;fail_at=1;assert(!dragon_renderer_create()&&frees==0);
    allocations=frees=0;fail_at=2;assert(!dragon_renderer_create()&&frees==1);
    allocations=frees=0;fail_at=3;assert(!dragon_renderer_create()&&frees==2);
    allocations=frees=fail_at=0;dragon_renderer_t *r=dragon_renderer_create();assert(r&&allocations==3);
    dragon_fixed_pixel_t *cache=r->fixed_pixels;
    size_t bytes=FIXED_PIXELS*sizeof(*cache);void *original=malloc(bytes);assert(original);memcpy(original,cache,bytes);
    uint16_t *a=malloc(480*480*2),*b=malloc(480*480*2);assert(a&&b);
    for(unsigned i=0;i<32;i++){
        dragon_pose_t p={(random_unit()*2-1)*.85f,(random_unit()*2-1)*.65f,i%2?random_unit():0,.5f+random_unit()*.4f,.04f+random_unit()*.08f,random_unit()};
        assert(dragon_renderer_prepare(r,&p));assert(dragon_renderer_draw(r,a,960,0,0,480,480));
        r->fixed_pixels=NULL;assert(dragon_renderer_draw(r,b,960,0,0,480,480));r->fixed_pixels=cache;
        assert(!memcmp(a,b,480*480*2));
    }
    assert(!memcmp(original,cache,bytes));
    dragon_renderer_destroy(r);assert(frees==3);dragon_renderer_destroy(NULL);
    free(original);free(a);free(b);
    puts("PASS renderer cache:32 cached/uncached full frames identical; immutable cache and all three allocation failures release correctly");
}
