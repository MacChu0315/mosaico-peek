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
    unsigned theme,lo,hi;float dx,dy,mix;bool selected,prepared,open;
    /* Immutable Q15 sphere normals, prepared at theme selection. */
    int16_t nx[480],ny[480],*nz;eye_projection_t projection;
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
    r->storage=bulk_alloc(FRAME_BYTES+EYE_BYTES+2*LAYER_BYTES);
    r->nz=bulk_alloc(EYE_DEPTH_BYTES);
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
    /* Opaque fixed pixels need only their final RGB565. Keep alpha and all
     * partial-alpha RGBA bytes intact; the frame is never spatially sampled. */
    for(unsigned i=0;i<480*480;i++){
        unsigned char *p=r->frame+i*4;
        if(p[3]==255){
            unsigned color=(((unsigned)p[0]*31+127)/255)<<11;
            color|=(((unsigned)p[1]*63+127)/255)<<5;
            color|=((unsigned)p[2]*31+127)/255;
            p[0]=(unsigned char)color;p[1]=(unsigned char)(color>>8);
        }
    }
    for(int i=0;i<480;i++){r->nx[i]=eye_normal(i,t->cx);r->ny[i]=eye_normal(i,t->cy);}
    for(int y=0;y<480;y++)for(int x=0;x<480;x++)r->nz[y*480+x]=eye_depth(r->nx[x],r->ny[y]);
    r->theme=theme;r->lo=r->hi=99;r->selected=true;return true;
}
bool eye_pack_prepare(eye_pack_t *r,const dragon_pose_t *p){
    if(!r||!r->selected||!p||!isfinite(p->gaze_x)||!isfinite(p->gaze_y)||!isfinite(p->blink)||fabsf(p->gaze_x)>.78001f||fabsf(p->gaze_y)>.58001f||p->blink<0||p->blink>1)return false;
    const eye_theme_t *t=&eye_themes[r->theme];
    float lid=p->blink*8;unsigned lo=(unsigned)floorf(lid),hi=lo<8?lo+1:8;
    r->prepared=false;
    r->open=p->blink==0;r->mix=lid-lo;
    if(!r->open){
        if(lo!=r->lo){if(!decode(r,r->lid[0],&t->layers[2+lo]))return false;r->lo=lo;}
        if(r->mix!=0 && hi!=r->hi){if(!decode(r,r->lid[1],&t->layers[2+hi]))return false;r->hi=hi;}
    }
    r->dx=p->gaze_x/.78f*t->amp_x;r->dy=p->gaze_y/.58f*t->amp_y;
    r->projection=eye_projection(p->gaze_x,p->gaze_y,t->amp_x,t->amp_y,t->cx,t->cy);
    r->prepared=true;return true;
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
static void sample_prepared(const eye_pack_t *r,unsigned w,unsigned h,int px,int py,float *c){
    float u,v;eye_project(&r->projection,r->nx[px],r->ny[py],r->nz[py*480+px],px,py,&u,&v);
    const eye_theme_t *t=&eye_themes[r->theme];u-=t->eye_x;v-=t->eye_y;
    if(u<0||v<0||u>=w-1||v>=h-1){sample(r->eye,w,h,u,v,c);return;}
    int x=(int)u,y=(int)v;
    const unsigned char *a=r->eye+((size_t)y*w+x)*4,*b=a+4,*d=a+w*4,*e=d+4;
    if(a[3]!=255||b[3]!=255||d[3]!=255||e[3]!=255){sample(r->eye,w,h,u,v,c);return;}
    float fx=u-x,fy=v-y;
    float w0=(1-fx)*(1-fy),w1=fx*(1-fy),w2=(1-fx)*fy,w3=fx*fy;
    /* Same float products and addition order as the scalar RGBA sampler;
     * opaque source alpha is exactly1, so its multiplication is redundant. */
    c[0]=(float)a[0]*w0;c[0]+=(float)b[0]*w1;c[0]+=(float)d[0]*w2;c[0]+=(float)e[0]*w3;
    c[1]=(float)a[1]*w0;c[1]+=(float)b[1]*w1;c[1]+=(float)d[1]*w2;c[1]+=(float)e[1]*w3;
    c[2]=(float)a[2]*w0;c[2]+=(float)b[2]*w1;c[2]+=(float)d[2]*w2;c[2]+=(float)e[2]*w3;
}
bool eye_pack_draw(const eye_pack_t *r,void *pixels,size_t stride,int x,int y,int w,int h){
    if(!r||!r->prepared||!pixels||x<0||y<0||w<=0||h<=0||x>480-w||y>480-h||stride<(size_t)w*2||stride%2)return false;
    const eye_theme_t *t=&eye_themes[r->theme];unsigned ew=t->layers[1].w,eh=t->layers[1].h,lw=t->layers[2].w,lh=t->layers[2].h;
    for(int yy=0;yy<h;yy++){
        uint16_t *row=(uint16_t *)((unsigned char *)pixels+(size_t)yy*stride);
        for(int xx=0;xx<w;xx++){
            int px=x+xx,py=y+yy,lx=px-t->x,ly=py-t->y;float c[4],a[4],b[4],front[4];
            const unsigned char *fp=r->frame+((size_t)py*480+px)*4;
            if(fp[3]==255){row[xx]=(uint16_t)(fp[0]|((unsigned)fp[1]<<8));continue;}
            if(r->open)sample_prepared(r,ew,eh,px,py,c);
            else {
                a[0]=a[1]=a[2]=a[3]=0;
                if(lx>=0&&ly>=0&&lx<(int)lw&&ly<(int)lh){
                    size_t off=((size_t)ly*lw+lx)*4;rgba(r->lid[0]+off,a);
                    if(r->mix!=0){rgba(r->lid[1]+off,b);for(unsigned k=0;k<4;k++)a[k]+=r->mix*(b[k]-a[k]);}
                }
                if(a[3]==1){c[0]=a[0];c[1]=a[1];c[2]=a[2];}
                else {sample_prepared(r,ew,eh,px,py,c);over(c,a);}
            }
            if(fp[3]){rgba(fp,front);over(c,front);}
            /* Convex RGBA sampling/composition bounds channels to0..255
             * (float roundoff <.001). The rounded 5/6-bit values stay in range.
             * Cast of this nonnegative expression equals floorf, retaining
             * the original multiply/divide/add order without per-pixel libm. */
            unsigned red=(unsigned)(c[0]*31/255+.5f),green=(unsigned)(c[1]*63/255+.5f),blue=(unsigned)(c[2]*31/255+.5f);
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
