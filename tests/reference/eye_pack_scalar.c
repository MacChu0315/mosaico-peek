/* Scalar1.0.4 arithmetic; asset geometry adapted for user-requested wider motion.
 * The byte-identical original remains in eye_pack_v104.c. */
/* SPDX-License-Identifier: Apache-2.0 */
#include "eye_pack.h"
#include "eye_projection.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#include "miniz.h"
#else
#include <zlib.h>
#endif
typedef struct {const unsigned char *data;size_t bytes;unsigned w,h;} eye_stream_t;
typedef struct {const char *name;int x,y,amp_x,amp_y,eye_x,eye_y,cx,cy;eye_stream_t layers[11];} eye_theme_t;
#include "eye_pack.inc"
/* Allocate the same capacity for each theme; no allocation during blink/draw. */
#define FRAME_BYTES (480u*480u*4u)
#define EYE_BYTES EYE_PACK_EYE_BYTES
#define LAYER_BYTES (507u*272u*4u)
struct eye_pack {
    unsigned char *storage,*frame,*eye,*lid[2];
    unsigned theme,lo,hi;float dx,dy,mix;bool selected,prepared;
    eye_projection_t projection;int16_t nx[480],ny[480],*nz;
#ifdef ESP_PLATFORM
    tinfl_decompressor *inflater;
#endif
};
static void *bulk_alloc(size_t n){
#ifdef ESP_PLATFORM
    return heap_caps_malloc(n,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
#else
    return malloc(n);
#endif
}
eye_pack_t *eye_pack_create(void){
    eye_pack_t *r=calloc(1,sizeof(*r));if(!r)return NULL;
    r->storage=bulk_alloc(FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES);r->nz=bulk_alloc(EYE_DEPTH_BYTES);
#ifdef ESP_PLATFORM
    r->inflater=bulk_alloc(sizeof(*r->inflater));
    if(!r->inflater){eye_pack_destroy(r);return NULL;}
#endif
    if(!r->storage||!r->nz){eye_pack_destroy(r);return NULL;}
    r->frame=r->storage;r->eye=r->frame+FRAME_BYTES;r->lid[0]=r->eye+EYE_BYTES;r->lid[1]=r->lid[0]+LAYER_BYTES;
    return r;
}
void eye_pack_destroy(eye_pack_t *r){if(!r)return;free(r->storage);free(r->nz);
#ifdef ESP_PLATFORM
    free(r->inflater);
#endif
    free(r);
}
static bool decode(eye_pack_t *r,unsigned char *out,const eye_stream_t *s){
    size_t size=(size_t)s->w*s->h*4;
#ifdef ESP_PLATFORM
    size_t in=s->bytes,n=size;tinfl_init(r->inflater);
    return tinfl_decompress(r->inflater,s->data,&in,out,out,&n,TINFL_FLAG_PARSE_ZLIB_HEADER|TINFL_FLAG_USING_NON_WRAPPING_OUTPUT_BUF)==TINFL_STATUS_DONE && n==size && in==s->bytes;
#else
    (void)r;uLongf n=size;return uncompress(out,&n,s->data,s->bytes)==Z_OK && n==size;
#endif
}
bool eye_pack_select(eye_pack_t *r,unsigned theme){
    if(!r||theme>=3)return false;
    if(r->selected && r->theme==theme)return true;
    r->prepared=false;r->selected=false;const eye_theme_t *t=&eye_themes[theme];
    if(!decode(r,r->frame,&t->layers[0])||!decode(r,r->eye,&t->layers[1]))return false;
    for(int i=0;i<480;i++){r->nx[i]=eye_normal(i,t->cx);r->ny[i]=eye_normal(i,t->cy);}
    for(int y=0;y<480;y++)for(int x=0;x<480;x++)r->nz[y*480+x]=eye_depth(r->nx[x],r->ny[y]);
    r->theme=theme;r->lo=r->hi=99;r->selected=true;return true;
}
bool eye_pack_prepare(eye_pack_t *r,const dragon_pose_t *p){
    if(!r||!r->selected||!p||!isfinite(p->gaze_x)||!isfinite(p->gaze_y)||!isfinite(p->blink)||fabsf(p->gaze_x)>.78001f||fabsf(p->gaze_y)>.58001f||p->blink<0||p->blink>1)return false;
    const eye_theme_t *t=&eye_themes[r->theme];
    float lid=p->blink*8;unsigned lo=(unsigned)floorf(lid),hi=lo<8?lo+1:8;
    r->prepared=false;
    if(lo!=r->lo && !decode(r,r->lid[0],&t->layers[2+lo]))return false;
    if(hi!=r->hi && !decode(r,r->lid[1],&t->layers[2+hi]))return false;
    r->lo=lo;r->hi=hi;r->mix=lid-lo;r->dx=p->gaze_x/.78f*t->amp_x;r->dy=p->gaze_y/.58f*t->amp_y;r->projection=eye_projection(p->gaze_x,p->gaze_y,t->amp_x,t->amp_y,t->cx,t->cy);r->prepared=true;return true;
}
/* Premultiplied channels remain floating point until the final RGB565 write. */
static void rgba(const unsigned char *p,float *c){float a=p[3]/255.f;c[0]=p[0]*a;c[1]=p[1]*a;c[2]=p[2]*a;c[3]=a;}
static void sample(const unsigned char *pixels,unsigned w,unsigned h,float x,float y,float *c){
    int ix=(int)floorf(x),iy=(int)floorf(y);float fx=x-ix,fy=y-iy;
    memset(c,0,4*sizeof(*c));
    for(int j=0;j<2;j++)for(int i=0;i<2;i++){
        int px=ix+i,py=iy+j;if(px<0||py<0||px>=(int)w||py>=(int)h)continue;
        float a[4],weight=(i?fx:1-fx)*(j?fy:1-fy);rgba(pixels+((size_t)py*w+px)*4,a);
        for(unsigned k=0;k<4;k++)c[k]+=a[k]*weight;
    }
}
static void over(float *dst,const float *src){for(unsigned k=0;k<3;k++)dst[k]=src[k]+dst[k]*(1-src[3]);}
bool eye_pack_draw(const eye_pack_t *r,void *pixels,size_t stride,int x,int y,int w,int h){
    if(!r||!r->prepared||!pixels||x<0||y<0||w<=0||h<=0||x>480-w||y>480-h||stride<(size_t)w*2||stride%2)return false;
    const eye_theme_t *t=&eye_themes[r->theme];unsigned ew=t->layers[1].w,eh=t->layers[1].h,lw=t->layers[2].w,lh=t->layers[2].h;
    for(int yy=0;yy<h;yy++){
        uint16_t *row=(uint16_t *)((unsigned char *)pixels+(size_t)yy*stride);
        for(int xx=0;xx<w;xx++){
            int px=x+xx,py=y+yy,lx=px-t->x,ly=py-t->y;float c[4],a[4],b[4],front[4];
            const unsigned char *fp=r->frame+((size_t)py*480+px)*4;
            if(fp[3]==255){c[0]=fp[0];c[1]=fp[1];c[2]=fp[2];}
            else {
                float u,v;eye_project(&r->projection,r->nx[px],r->ny[py],r->nz[py*480+px],px,py,&u,&v);sample(r->eye,ew,eh,u-t->eye_x,v-t->eye_y,c);
                if(lx>=0&&ly>=0&&lx<(int)lw&&ly<(int)lh){
                    size_t off=((size_t)ly*lw+lx)*4;rgba(r->lid[0]+off,a);rgba(r->lid[1]+off,b);
                    for(unsigned k=0;k<4;k++)a[k]+=r->mix*(b[k]-a[k]);
                    over(c,a);
                }
                rgba(fp,front);over(c,front);
            }
            unsigned red=(unsigned)floorf(fminf(255,fmaxf(0,c[0]))*31/255+.5f),green=(unsigned)floorf(fminf(255,fmaxf(0,c[1]))*63/255+.5f),blue=(unsigned)floorf(fminf(255,fmaxf(0,c[2]))*31/255+.5f);
            row[xx]=(uint16_t)((red<<11)|(green<<5)|blue);
        }
    }
    return true;
}
size_t eye_pack_heap_bytes(void){return sizeof(eye_pack_t)+FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES+EYE_DEPTH_BYTES
#ifdef ESP_PLATFORM
    +sizeof(tinfl_decompressor)
#endif
    ;}
size_t eye_pack_asset_bytes(void){size_t n=sizeof(eye_themes);for(unsigned t=0;t<3;t++)for(unsigned i=0;i<11;i++)n+=eye_themes[t].layers[i].bytes;return n;}
const char *eye_pack_name(unsigned theme){return theme<3?eye_themes[theme].name:NULL;}
