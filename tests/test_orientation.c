/* SPDX-License-Identifier: Apache-2.0 */
#include "peek_orientation.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static void sample(peek_orientation_t *s,float x,float y,float z,float rate,uint64_t t){
    peek_orientation_sample(s,x,y,z,rate,true,t);
}
static void settle(peek_orientation_t *s,float x,float y,uint64_t start){
    for(unsigned i=0;i<=30;i++)sample(s,x,y,0,0,start+i*20);
}
int main(void){
    peek_orientation_t s={0};
    /* Inputs are gravity-down in screen coordinates, not raw accelerometer. */
    settle(&s,0,1,0);assert(s.rotation==0);
    sample(&s,-1,0,0,0,620);assert(s.rotation==0);
    settle(&s,-1,0,640);assert(s.rotation==90);
    settle(&s,0,-1,1260);assert(s.rotation==180);
    settle(&s,1,0,1880);assert(s.rotation==270);
    settle(&s,0,1,2500);assert(s.rotation==0);
    for(unsigned i=0;i<80;i++)sample(&s,-.7f,.71f,0,0,3120+i*20);
    assert(s.rotation==0); /* near diagonal never chatters */
    for(unsigned i=0;i<40;i++)sample(&s,-1,0,0,40,4720+i*20);
    assert(s.rotation==0); /* rotating: no orientation commitment */
    for(unsigned i=0;i<40;i++)sample(&s,0,0,1,0,5520+i*20);
    assert(s.rotation==0); /* flat: no screen up */
    peek_orientation_sample(&s,-1,0,0,0,false,6320);
    sample(&s,NAN,0,0,0,6340);assert(s.rotation==0);
    sample(&s,-1,0,0,0,6360);sample(&s,-1,0,0,0,9000);
    assert(s.rotation==0); /* a long gap does not count as settling */
    for(unsigned i=0;i<40;i++)sample(&s,-1,0,0,0,9000);
    assert(s.rotation==0); /* duplicate timestamps cannot manufacture evidence */
    settle(&s,-1,0,9020);assert(s.rotation==90);
    sample(&s,1,0,0,0,1);assert(s.rotation==90);
    unsigned lx,ly;peek_orientation_point(90,10,20,&lx,&ly);assert(lx==20&&ly==469);
    peek_orientation_point(180,10,20,&lx,&ly);assert(lx==469&&ly==459);
    peek_orientation_point(270,10,20,&lx,&ly);assert(lx==459&&ly==10);
    float x,y;peek_orientation_gaze(90,.39f,.145f,&x,&y);
    assert(fabsf(x-.195f)<1e-6f&&fabsf(y+.29f)<1e-6f);
    peek_orientation_gaze(180,.39f,.145f,&x,&y);assert(x==-.39f&&y==-.145f);
    peek_orientation_gaze(270,.39f,.145f,&x,&y);
    assert(fabsf(x+.195f)<1e-6f&&fabsf(y-.29f)<1e-6f);
    puts("PASS orientation dwell, uncertainty, faults, time and coordinate transforms");
}
