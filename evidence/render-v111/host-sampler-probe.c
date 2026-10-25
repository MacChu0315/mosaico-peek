#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <time.h>
#include "eye_pack.c"
static double ms(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000.+t.tv_nsec/1e6;}
int main(void){
 eye_pack_t*r=eye_pack_create();uint16_t*out=malloc(480*480*2);if(!r||!out)return 1;
 for(unsigned theme=1;theme<=2;theme++){
  if(!eye_pack_select(r,theme))return 2;
  unsigned opaque=0,partial=0;for(unsigned i=0;i<480*480;i++){unsigned a=r->frame[4*i+3];opaque+=a==255;partial+=a>0&&a<255;}
  printf("%s fixed_frame_opaque=%u partial=%u total=230400\n",eye_pack_name(theme),opaque,partial);
  for(unsigned state=0;state<3;state++){
   dragon_pose_t pose={0};pose.gaze_x=state==1?.5f:0;pose.gaze_y=state==1?.3f:0;pose.blink=state==2?1:0;
   double begin=ms();if(!eye_pack_prepare(r,&pose))return 3;double initial=ms()-begin;
   begin=ms();for(int n=0;n<100;n++)if(!eye_pack_prepare(r,&pose))return 4;double cached=(ms()-begin)/100;
   unsigned visible_sphere=0,integer_uv=0;
   const eye_theme_t*t=&eye_themes[theme];
   for(int y=0;y<480;y++)for(int x=0;x<480;x++){
    if(r->frame[(y*480+x)*4+3]==255)continue;
    if(theme==1&&state==2){int lx=x-t->x,ly=y-t->y;if(lx>=0&&ly>=0&&lx<(int)t->layers[2].w&&ly<(int)t->layers[2].h&&r->lid[1][(ly*t->layers[2].w+lx)*4+3]==255)continue;}
    visible_sphere++;float u,v;eye_project(&r->projection,r->nx[x],r->ny[y],r->nz[y*480+x],x,y,&u,&v);
    integer_uv+=(u==floorf(u)&&v==floorf(v));
   }
   begin=ms();for(int n=0;n<40;n++)if(!eye_pack_draw(r,out,960,0,0,480,480))return 5;double draw=(ms()-begin)/40;
   printf("state=%u sphere_pixels=%u integer_uv=%u prepare_initial_ms=%.3f prepare_cached_ms=%.6f draw_host_ms=%.3f\n",state,visible_sphere,integer_uv,initial,cached,draw);
  }
 }
 eye_pack_destroy(r);free(out);return 0;
}
