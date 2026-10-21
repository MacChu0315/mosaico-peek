/* SPDX-License-Identifier: Apache-2.0 */
#include "dragon_render.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#define N 480u
#define STRIDE 487u
static uint16_t full[N*N],sampled[N*N],tiles[N*STRIDE];
int main(void){
    dragon_renderer_t *r=dragon_renderer_create();assert(r);
    assert(!dragon_renderer_set_sample_step(NULL,2));
    const dragon_pose_t poses[]={ {-.05f,.035f,0,.69f,.072f,.16f},{.78f,-.58f,0,.73f,.06f,.5f},{-.78f,.58f,.43f,.75f,.062f,.46f},{0,0,1,.69f,.072f,.16f} };
    for(unsigned p=0;p<sizeof(poses)/sizeof(*poses);p++){
        assert(dragon_renderer_prepare(r,poses+p));
        assert(dragon_renderer_set_sample_step(r,1));assert(dragon_renderer_draw(r,full,N*2,0,0,N,N));
        assert(dragon_renderer_set_sample_step(r,2));assert(!dragon_renderer_set_sample_step(r,0));assert(!dragon_renderer_set_sample_step(r,3));
        assert(dragon_renderer_draw(r,sampled,N*2,0,0,N,N));
        for(unsigned y=0;y<N;y++)for(unsigned x=0;x<N;x++)assert(sampled[y*N+x]==full[(y|1u)*N+(x|1u)]);
        for(unsigned i=0;i<N*STRIDE;i++)tiles[i]=0xa55a;
        /* Odd tile sizes/origins force both partial2x2-cell boundaries. */
        for(unsigned y=0;y<N;y+=29)for(unsigned x=0;x<N;x+=37){
            unsigned w=N-x<37?N-x:37,h=N-y<29?N-y:29;
            assert(dragon_renderer_draw(r,tiles+y*STRIDE+x,STRIDE*2,x,y,w,h));
        }
        for(unsigned y=0;y<N;y++)for(unsigned x=0;x<STRIDE;x++)assert(tiles[y*STRIDE+x]==(x<N?sampled[y*N+x]:0xa55a));
        uint16_t point;assert(dragon_renderer_draw(r,&point,2,479,479,1,1));assert(point==sampled[N*N-1]);
    }
    dragon_renderer_destroy(r);
    puts("PASS sampling2:4 full poses match approved odd-center2x2 rule; odd tiles, padded stride, edges, invalid configuration");
}
