#!/usr/bin/env python3
"""Art-only C raster reference. The optional sampler is NOT a firmware adapter."""
import argparse, hashlib, io, json, math, os, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent
HOOK = r'''
/* Handoff-only raw RGB sampler; original renderer below remains unchanged. */
static unsigned char review_rgb[480*480*3];
static int review_loaded,review_mask;
static color_t review_sample(int lx,int ly){
    int u=clamp_int((int)((int64_t)lx*466)+240*Q16,0,479*Q16);
    int v=clamp_int((int)((int64_t)ly*466)+240*Q16,0,479*Q16);
    int x=u>>16,y=v>>16,x1=x<479?x+1:x,y1=y<479?y+1:y;
    const unsigned char *a=review_rgb+(y*480+x)*3,*b=review_rgb+(y*480+x1)*3;
    const unsigned char *c=review_rgb+(y1*480+x)*3,*d=review_rgb+(y1*480+x1)*3;
    color_t top=over((color_t){a[0],a[1],a[2]},(color_t){b[0],b[1],b[2]},(u&65535)>>8);
    color_t bot=over((color_t){c[0],c[1],c[2]},(color_t){d[0],d[1],d[2]},(u&65535)>>8);
    return over(top,bot,(v&65535)>>8);
}
'''
MAIN = r'''
#include <stdio.h>
#include "review_renderer.c"
static void rgb(color_t c){unsigned char b[3]={clamp_int(c.r,0,255),clamp_int(c.g,0,255),clamp_int(c.b,0,255)};if(fwrite(b,1,3,stdout)!=3)exit(4);}
int main(int argc,char **argv){
    if(argc==2 && !strcmp(argv[1],"--template")){
        fputs("P6\n480 480\n255\n",stdout);
        for(int y=0;y<480;y++)for(int x=0;x<480;x++){
            int lx=lround((x-240)*32768./233),ly=lround((y-240)*32768./233);
            int vein=(sine(lx*75+ly*18)*sine(ly*53-lx*29))>>15;
            rgb((color_t){49+(vein*5>>15),63+(vein*7>>15),23+(vein*4>>15)});
        }return 0;
    }
    if(argc!=7)return 2;
    dragon_pose_t p={strtof(argv[1],NULL),strtof(argv[2],NULL),strtof(argv[3],NULL),.69f,.072f,.16f};
    if(strcmp(argv[5],"-")){FILE *f=fopen(argv[5],"rb");if(!f)return 3;review_loaded=fread(review_rgb,1,sizeof(review_rgb),f)==sizeof(review_rgb);int extra=fgetc(f);fclose(f);if(!review_loaded||extra!=EOF)return 3;}
    review_mask=atoi(argv[6]);
    dragon_renderer_t *r=dragon_renderer_create();uint16_t *pixels=malloc(480*480*2);
    if(!r||!pixels||!dragon_renderer_set_sample_step(r,atoi(argv[4]))||!dragon_renderer_prepare(r,&p)||!dragon_renderer_draw(r,pixels,960,0,0,480,480))return 3;
    fputs("P6\n480 480\n255\n",stdout);
    for(unsigned i=0;i<480*480;i++){unsigned c=pixels[i];rgb((color_t){((c>>11)&31)*255/31,((c>>5)&63)*255/63,(c&31)*255/31});}
    free(pixels);dragon_renderer_destroy(r);return 0;
}
'''
POSES = [('center',0,0,0),('left',-.78,0,0),('right',.78,0,0),
         ('up',0,-.58,0),('down',0,.58,0),('up-left',-.78,-.58,0),
         ('up-right',.78,-.58,0),('down-left',-.78,.58,0),
         ('down-right',.78,.58,0),('half-closed',0,0,.5),('closed',0,0,1)]

def build():
    directory=ROOT/'build';directory.mkdir(exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'source/tools/bake_dragon.py'),'--output',str(directory/'dragon_assets.inc')],check=True,stdout=subprocess.DEVNULL)
    source=(ROOT/'source/src/dragon_render.c').read_text()
    needle='c = (color_t){49+(vein*5 >> 15), 63+(vein*7 >> 15), 23+(vein*4 >> 15)};'
    assert source.count(needle)==1
    source=source.replace(needle,needle+'\n        if(review_mask)c=review_mask==1?(color_t){0,0,0}:(color_t){255,255,255};\n        else if(review_loaded)c=review_sample(lx,ly);')
    source=source.replace('static color_t eyeball(',HOOK+'\nstatic color_t eyeball(',1)
    (directory/'review_renderer.c').write_text(source);(directory/'snapshot.c').write_text(MAIN)
    exe=directory/'snapshot'
    subprocess.run([os.environ.get('CC','cc'),'-std=c11','-O2','-ffp-contract=off','-I'+str(ROOT/'source/src'),'-I'+str(directory),str(directory/'snapshot.c'),'-lm','-o',str(exe)],check=True)
    return exe

def raster(exe,pose,step,surface='-',mask=0):
    data=subprocess.check_output([str(exe),*[str(v) for v in pose],str(step),str(surface),str(mask)])
    return Image.open(io.BytesIO(data)).convert('RGB')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--surface',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--sample-step',type=int,choices=[1,2],default=2);p.add_argument('--movie',action='store_true');a=p.parse_args()
    surface='-'
    if a.surface:
        im=Image.open(a.surface)
        if im.size!=(480,480) or im.mode not in ('RGB','RGBA') or im.convert('RGBA').getchannel('A').getextrema()!=(255,255):p.error('surface must be480x480 RGB or fully opaque RGBA PNG')
        if im.format!='PNG':p.error('surface must be PNG')
        pixels=im.convert('RGB').tobytes()
    exe=build()
    if a.surface:surface=ROOT/'build/candidate.rgb';surface.write_bytes(pixels)
    a.output.mkdir(parents=True,exist_ok=False)
    sheet=Image.new('RGB',(480*3,510*4),(24,24,24));draw=ImageDraw.Draw(sheet)
    for n,(name,*pose) in enumerate(POSES):
        im=raster(exe,pose,a.sample_step,surface);im.save(a.output/(name+'.png'))
        black=raster(exe,pose,a.sample_step,mask=1);white=raster(exe,pose,a.sample_step,mask=2)
        diff=ImageChops.difference(black,white);mask=ImageChops.lighter(ImageChops.lighter(diff.getchannel('R'),diff.getchannel('G')),diff.getchannel('B')).point(lambda v:255 if v else 0)
        mask.save(a.output/(name+'-sclera-mask.png'))
        if name=='closed':assert mask.getbbox() is None
        sheet.paste(im,(n%3*480,n//3*510));draw.text((n%3*480+8,n//3*510+484),name,fill='white')
    sheet.save(a.output/'contact-sheet.png')
    if a.movie:
        ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','480x480','-framerate','25','-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p',str(a.output/'motion.mp4')],stdin=subprocess.PIPE)
        points=[(0,0,0),(-.78,0,0),(.78,0,0),(0,-.58,0),(0,.58,0),(-.78,-.58,0),(.78,.58,0),(0,0,0)]
        for frame in range(200):
            t=frame/25
            if t<5:
                pos=t/5*7;i=min(6,int(pos));f=pos-i;f=f*f*(3-2*f);pose=[points[i][k]*(1-f)+points[i+1][k]*f for k in range(3)]
            else:
                blink=min(1,(t-5)/.5) if t<6.5 else max(0,1-(t-6.5)/.5);pose=[0,0,blink*blink*(3-2*blink)]
            ff.stdin.write(raster(exe,pose,a.sample_step,surface).tobytes())
        ff.stdin.close();assert ff.wait()==0
    (a.output/'render.json').write_text(json.dumps(dict(surface_sha256=hashlib.sha256(a.surface.read_bytes()).hexdigest() if a.surface else None,sample_step=a.sample_step,poses=POSES,movie_seconds=8 if a.movie else None,movie_fps=25 if a.movie else None,input='Explicit synthetic pose test; not detector input or device performance',candidate_adapter='Preview-only rawRGB bilinear sampler; production format not implemented'),indent=2)+'\n')
    print('PASS eleven C pose renders, sclera masks and closed exclusion:',a.output)

if __name__=='__main__':main()
