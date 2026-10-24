/* Standalone review map; uses an immutable snapshot of production geometry. */
#include "eye_projection.h"
void project(float gx,float gy,float *uv){
    eye_projection_t p=eye_projection(gx,gy,120,80,240,250);
    for(int y=0;y<480;y++)for(int x=0;x<480;x++){
        int16_t nx=eye_normal(x,240),ny=eye_normal(y,250),nz=eye_depth(nx,ny);
        eye_project(&p,nx,ny,nz,x,y,uv+2*(y*480+x),uv+2*(y*480+x)+1);
    }
}
