/* SPDX-License-Identifier: Apache-2.0 */
#pragma once
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#define EYE_RADIUS 233
#define EYE_DEPTH_BYTES (480u*480u*sizeof(int16_t))
typedef struct {int cx,cy;int32_t cyaw,syaw,cpitch,spitch;bool neutral;} eye_projection_t;
static inline int16_t eye_normal(int pixel,int center){
    long n=lroundf((pixel-center)*(32768.f/EYE_RADIUS));
    return (int16_t)(n< -32768?-32768:n>32767?32767:n);
}
static inline int16_t eye_depth(int16_t nx,int16_t ny){
    float x=nx/32768.f,y=ny/32768.f,z=1-x*x-y*y;
    return z<0?-1:(int16_t)(sqrtf(z)*32767.f);
}
static inline eye_projection_t eye_projection(float gx,float gy,int ax,int ay,int cx,int cy){
    float yaw=(gx/.78f)*asinf(ax/(float)EYE_RADIUS),pitch=(gy/.58f)*asinf(ay/(float)EYE_RADIUS);
    return (eye_projection_t){cx,cy,(int32_t)lroundf(cosf(yaw)*32768.f),(int32_t)lroundf(sinf(yaw)*32768.f),(int32_t)lroundf(cosf(pitch)*32768.f),(int32_t)lroundf(sinf(pitch)*32768.f),gx==0&&gy==0};
}
static inline void eye_project(const eye_projection_t *p,int16_t nx,int16_t ny,int16_t nz,int x,int y,float *u,float *v){
    if(p->neutral||nz<0){*u=(float)x;*v=(float)y;return;}
    int32_t lx=(p->cyaw*nx-p->syaw*nz)>>15;
    int32_t az=(p->syaw*nx+p->cyaw*nz)>>15;
    int32_t ly=(p->cpitch*ny-p->spitch*az)>>15;
    *u=p->cx+lx*(EYE_RADIUS/32768.f);*v=p->cy+ly*(EYE_RADIUS/32768.f);
}
