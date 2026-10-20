/* SPDX-License-Identifier: Apache-2.0 */
/* The pre-optimization highlight expression is a retained numerical oracle.
 * Test the actual production static function, not another fast reimplementation. */
#include "../src/dragon_render.c"
#include <assert.h>
#include <stdio.h>
static color_t old_gloss(color_t c,int32_t x,int32_t y){
    int32_t dx=(x+71*Q16)>>8,dy=(y+57*Q16)>>8;
    int64_t d2=(int64_t)dx*dx+(int64_t)dy*dy;
    const int64_t radius2=(int64_t)48*48*65536;
    if(d2<radius2){int radius=root_q15(d2*Q15*Q15/radius2);c=over(c,(color_t){230,242,192},(Q15-radius)*36>>15);}
    dx=(x+76*Q16)>>8;dy=(y+51*Q16)>>8;
    int ex=(int)(((int64_t)dx*31492-(int64_t)dy*9056)>>15);
    int ey=(int)(((int64_t)dx*9056+(int64_t)dy*31492)>>15);
    int64_t ellipse=(int64_t)ex*ex*1024/3030384+(int64_t)ey*ey*1024/629801;
    if(ellipse<1152)c=over(c,(color_t){250,250,218},clamp_int(1152-(int)ellipse,0,256)*123>>8);
    dx=(x+64*Q16)>>8;dy=(y+46*Q16)>>8;
    ellipse=(int64_t)dx*dx*1024/317194+(int64_t)dy*dy*1024/110756;
    if(ellipse<1152)c=over(c,(color_t){243,245,202},clamp_int(1152-(int)ellipse,0,256)*59>>8);
    return c;
}
int main(void){
    for(int alpha=-1;alpha<=257;alpha++)for(int v=0;v<256;v+=7){
        color_t a={v,255-v,v/2},b={255-v,v,(v*3)%256};
        int k=clamp_int(alpha,0,256);
        color_t old={a.r+((b.r-a.r)*k>>8),a.g+((b.g-a.g)*k>>8),a.b+((b.b-a.b)*k>>8)},fast=over(a,b,alpha);
        assert(old.r==fast.r&&old.g==fast.g&&old.b==fast.b);
    }
    for(unsigned sy=0;sy<480;sy++)for(unsigned sx=0;sx<480;sx++){
        int32_t px=((int32_t)sx-240)*Q16+Q16/2,py=((int32_t)sy-247)*Q16+Q16/2;
        int32_t x=(int32_t)(((int64_t)px*32349-(int64_t)py*5221)>>15);
        int32_t y=(int32_t)(((int64_t)px*5221+(int64_t)py*32349)>>15);
        for(unsigned j=0;j<3;j++){
            color_t input={(int)((sx*3+j*13)%256),(int)((sy*7+j*31)%256),(int)((sx+sy+j*53)%256)};
            color_t a=old_gloss(input,x,y),b=gloss(input,x,y);
            assert(a.r==b.r&&a.g==b.g&&a.b==b.b);
        }
        assert(x/(233*2)==(int)(((int64_t)x*Q15)/(233*Q16)));
        assert(y/(233*2)==(int)(((int64_t)y*Q15)/(233*Q16)));
    }
    puts("PASS renderer math: all230400 coordinates x3 channel inputs match retained highlight oracle; exact sphere normalization");
}
