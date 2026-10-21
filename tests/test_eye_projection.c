/* SPDX-License-Identifier: Apache-2.0 */
#include "eye_projection.h"
#include <assert.h>
#include <stdio.h>
int main(void){
    for(int cy=245;cy<=250;cy+=5){
        const float gx[]={0,.78f,-.78f,0,0},gy[]={0,0,0,.58f,-.58f};
        const int dx[]={0,120,-120,0,0},dy[]={0,0,0,80,-80};
        for(unsigned i=0;i<5;i++){
            eye_projection_t p=eye_projection(gx[i],gy[i],120,80,240,cy);
            int x=240+dx[i],y=cy+dy[i];int16_t nx=eye_normal(x,240),ny=eye_normal(y,cy),nz=eye_depth(nx,ny);float u,v;
            eye_project(&p,nx,ny,nz,x,y,&u,&v);assert(fabsf(u-240)<.03f && fabsf(v-cy)<.03f);
            if(!i){eye_project(&p,0,0,32767,123,321,&u,&v);assert(u==123&&v==321);}
        }
    }
    puts("PASS shared sphere: pure-axis pupil centers move+/-120,+/-80px with matching signs; neutral is exact");
}
