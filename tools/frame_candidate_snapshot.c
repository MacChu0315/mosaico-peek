/* SPDX-License-Identifier: Apache-2.0 */
/* Review-only frame substitution; uses the unmodified production eye/shutter shader.
 * Not linked into firmware. Input is an exactly480x480 straight RGBA frame. */
#include <stdio.h>
#include <stdlib.h>
#include "../src/eye_pack.c"
int main(int argc,char **argv){
    if(argc!=5)return 2;
    eye_pack_t *r=eye_pack_create();uint16_t *out=malloc(480*480*2);
    if(!r||!out||!eye_pack_select(r,2))return 1;
    FILE *f=fopen(argv[1],"rb");if(!f)return 1;
    size_t bytes=fread(r->frame,1,FRAME_BYTES,f);int extra=fgetc(f);fclose(f);
    if(bytes!=FRAME_BYTES||extra!=EOF)return 1;
    /* Same fixed-frame cache encoding used by eye_pack_select. */
    for(unsigned i=0;i<480*480;i++){
        unsigned char *p=r->frame+i*4;
        if(p[3]==255){unsigned color=(((unsigned)p[0]*31+127)/255)<<11; color|=(((unsigned)p[1]*63+127)/255)<<5;color|=((unsigned)p[2]*31+127)/255;p[0]=(unsigned char)color;p[1]=(unsigned char)(color>>8);}
    }
    dragon_pose_t pose={0};pose.gaze_x=strtof(argv[2],NULL);pose.gaze_y=strtof(argv[3],NULL);pose.blink=strtof(argv[4],NULL);
    if(!eye_pack_prepare(r,&pose)||!eye_pack_draw(r,out,960,0,0,480,480))return 1;
    fputs("P6\n480 480\n255\n",stdout);
    for(unsigned i=0;i<480*480;i++){unsigned v=out[i];unsigned char c[3]={(v>>11)*255/31,((v>>5)&63)*255/63,(v&31)*255/31};if(fwrite(c,1,3,stdout)!=3)return 1;}
    free(out);eye_pack_destroy(r);return 0;
}
