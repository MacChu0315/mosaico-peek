#!/usr/bin/env python3
"""Independent R1 art reconstruction. Input read-only; outputs only build/review."""
import argparse,ctypes,hashlib,json,math,subprocess,sys
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import PIL
ROOT=Path(__file__).resolve().parents[1]
RECIPE=json.loads((ROOT/'recipe.json').read_text())
W=H=480;YY,XX=np.indices((H,W),dtype=np.float32)
FONT_PATH='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

@lru_cache(maxsize=8)
def font(n):
    try:return ImageFont.truetype(FONT_PATH,n)
    except OSError:return ImageFont.load_default()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(a,p):
    p.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(np.clip(np.rint(a),0,255).astype(np.uint8)).save(p)
def load(p):return np.asarray(Image.open(p).convert('RGBA'),dtype=np.float32)
def resize(p):return np.asarray(Image.open(p).convert('RGBA').resize((480,480),Image.Resampling.LANCZOS),dtype=np.float32)
def sample(a,u,v):
    x=np.floor(u).astype(np.int32);y=np.floor(v).astype(np.int32);fx=u-x;fy=v-y
    out=np.zeros(u.shape+(a.shape[-1],),dtype=np.float32)
    for j in (0,1):
        for i in (0,1):
            xi=x+i;yi=y+j;valid=(xi>=0)&(xi<480)&(yi>=0)&(yi<480)
            weight=((fx if i else 1-fx)*(fy if j else 1-fy)*valid)[...,None]
            out+=a[np.clip(yi,0,479),np.clip(xi,0,479)]*weight
    return out

def over(base,layer,opacity=1):
    alpha=layer[...,3:4]/255*opacity
    return base*(1-alpha)+layer[...,:3]*alpha

def quantize(a):
    levels=np.array([31,63,31],dtype=np.float32)
    return np.rint(np.floor(np.clip(a,0,255)*levels/255+.5)*255/levels).astype(np.uint8)

def verify_inputs():
    manifest=json.loads((ROOT/'INPUTS.json').read_text())
    for n,h in manifest['source_files'].items():assert digest(ROOT/n)==h,n
    return {n:(digest(ROOT/n),(ROOT/n).stat().st_mtime_ns) for n in manifest['source_files']}

class Geometry:
    def __init__(self):
        target=ROOT/'build/project.so'
        subprocess.run(['cc','-std=c11','-O2','-ffp-contract=off','-fPIC','-shared','-I'+str(ROOT/'input/engineering'),str(ROOT/'scripts/project.c'),'-lm','-o',str(target)],check=True)
        self.lib=ctypes.CDLL(str(target));self.lib.project.argtypes=[ctypes.c_float,ctypes.c_float,ctypes.POINTER(ctypes.c_float)]
        self.maps={}
    def map(self,gx,gy):
        key=(float(gx),float(gy))
        if key not in self.maps:
            uv=np.empty((480,480,2),np.float32);self.lib.project(gx,gy,uv.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
            if len(self.maps)>=32:self.maps.pop(next(iter(self.maps)))
            self.maps[key]=uv
        return self.maps[key]

class Theme:
    def __init__(self,name):
        self.name=name;self.cfg=RECIPE['themes'][name]
        raw=ROOT/'input/originals/assets/raw'/name;eng=ROOT/'input/engineering'/name
        self.original=load(eng/'neutral.png');self.frame=load(eng/'frame.png')
        self.hole=255-self.frame[...,3]
        self.guard=np.asarray(Image.fromarray((self.hole>0).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(9)),dtype=np.float32)/255
        # Preserve the existing accepted480 raster, whose source portrait hash
        # was verified at intake. Do not substitute a different resize filter.
        source=resize(raw/'expanded_eye_source.png');dx,dy=self.cfg['eye_shift']
        u=XX-dx*np.sin(np.pi*XX/479)**2;v=YY-dy*np.sin(np.pi*YY/479)**2
        registered=sample(source,u,v)
        cx,cy,rx,ry=self.cfg['protected_ellipse'];ellipse=((XX-cx)/rx)**2+((YY-cy)/ry)**2<=1
        eroded=np.asarray(Image.fromarray((self.hole>250).astype(np.uint8)*255).filter(ImageFilter.MinFilter(27)))>0
        self.core=ellipse&eroded
        soft=np.asarray(Image.fromarray(self.core.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(4)),dtype=np.float32)/255
        soft[self.core]=1;soft*=self.hole/255;soft[self.core]=1
        self.surface=np.clip(np.rint(self.original*soft[...,None]+registered*(1-soft[...,None])),0,255).astype(np.uint8)
        self.surface[...,3]=255
        changed=np.any(self.surface[...,:3]!=self.original[...,:3],axis=2)&(self.hole>0)
        self.rim=self.original.copy();self.rim[...,3]=changed.astype(np.float32)*255
        self.closed=resize(raw/'closed_lid_source.png')
        self.membrane=resize(raw/'membrane_texture_source.png')
        self.membrane[...,:3]*=self.cfg['membrane_rgb_gain']
        self.membrane[...,3]*=self.cfg['membrane_opacity_scale']
        assert Image.open(raw/'membrane_texture_source.png').mode=='RGBA'
        seam=np.array(self.cfg['seam']);self.seam=np.interp(np.arange(480),seam[:,0],seam[:,1])[None,:]
        if name=='night_owl':self.q=XX-self.cfg['membrane_slope']*(YY-250)+self.cfg['membrane_curve']*(YY-250)**2
        else:self.q=YY-self.cfg['membrane_slope']*(XX-240)-self.cfg['membrane_curve']*(XX-240)**2
        visible=self.q[self.hole>250];self.qmin=float(visible.min()-8);self.qmid=float(np.median(visible));self.qmax=float(visible.max()+8)
        bounds=np.where(self.hole>0);self.top=float(bounds[0].min());self.bottom=float(bounds[0].max())
        columns=np.where((self.hole>0).any(axis=0))[0]
        tops=[np.where(self.hole[:,x]>0)[0][0] for x in columns]
        bottoms=[np.where(self.hole[:,x]>0)[0][-1] for x in columns]
        self.top_profile=np.interp(np.arange(480),columns,tops)[None,:]
        self.bottom_profile=np.interp(np.arange(480),columns,bottoms)[None,:]
        self.membranes=[self.membrane_layer(i/8) for i in range(9)]
        self.lids=[self.lid_layer(i/8) for i in range(9)]
        folder=ROOT/'build/processed'/name;maskdir=ROOT/'build/masks'/name
        save(self.surface,folder/'eye_surface.png');save(self.frame,folder/'frame.png');save(self.rim,folder/'rim_restore.png')
        save(self.core*255,maskdir/'protected_iris_pupil.png');save(soft*255,maskdir/'join_weight.png');save(self.hole,maskdir/'aperture.png')
        save(registered,maskdir/'registered_expanded_source.png')
        for i in range(9):
            save(self.membranes[i][128:368],folder/'membrane'/f'membrane_{i:02d}.png')
            save(self.lids[i][128:368],folder/'lids'/f'lid_{i:02d}.png')
            save(self.membranes[i][...,3],maskdir/f'membrane_{i:02d}.png');save(self.lids[i][...,3],maskdir/f'lid_{i:02d}.png')
    def membrane_layer(self,p):
        layer=self.membrane.copy()
        if p==0:coverage=np.zeros((480,480))
        elif p==1:coverage=np.ones((480,480))
        else:
            t=p if self.name=='night_owl' else 1-p
            threshold=self.qmin+(self.qmid-self.qmin)*t*2 if t<=.5 else self.qmid+(self.qmax-self.qmid)*(t-.5)*2
            distance=threshold-self.q if self.name=='night_owl' else self.q-threshold
            coverage=np.clip(distance/1.5+.5,0,1)
        layer[...,3]*=coverage*self.guard
        layer[:128,:,3]=0;layer[368:,:,3]=0
        return np.rint(layer).astype(np.uint8)
    def lid_layer(self,p):
        if p==1:
            layer=self.closed.copy();layer[...,3]=255*self.guard
        elif p==0:
            layer=self.closed.copy();layer[...,3]=0
        else:
            upper_shift=-(1-p)*(self.seam-self.top_profile+2)
            lower_shift=(1-p)*(self.bottom_profile-self.seam+2)
            upper=sample(self.closed,XX,YY-upper_shift);lower=sample(self.closed,XX,YY-lower_shift)
            au=np.clip((self.seam-(YY-upper_shift))/.9+.5,0,1)
            al=np.clip(((YY-lower_shift)-self.seam)/.9+.5,0,1)
            valid_u=((YY-upper_shift)>=0)&((YY-upper_shift)<480);valid_l=((YY-lower_shift)>=0)&((YY-lower_shift)<480)
            au*=valid_u;al*=valid_l;total=au+al
            rgb=(upper[...,:3]*au[...,None]+lower[...,:3]*al[...,None])/np.maximum(total[...,None],1e-6)
            layer=np.concatenate([rgb,(np.clip(total,0,1)*255*self.guard)[...,None]],axis=2)
        layer[:128,:,3]=0;layer[368:,:,3]=0
        return np.rint(layer).astype(np.uint8)
    def render(self,geo,gx=0,gy=0,membrane=0,lid=0):
        uv=geo.map(gx,gy);rgb=sample(self.surface.astype(np.float32),uv[...,0],uv[...,1])[...,:3]
        s=min(1,max(abs(gx)/.16,abs(gy)/.12));fade=1-s*s*(3-2*s)
        rgb=over(rgb,self.rim,fade)
        rgb=over(rgb,self.membranes[min(8,int(membrane*8+.5))])
        rgb=over(rgb,self.lids[min(8,int(lid*8+.5))])
        return quantize(over(rgb,self.frame))

CASES=[('neutral','正视',0,0,0,0),('left','左极限',-.78,0,0,0),('right','右极限',.78,0,0,0),('up','上极限',0,-.58,0,0),('down','下极限',0,.58,0,0),('membrane-half','瞬膜半覆盖',0,0,.5,0),('closed','全闭眼',0,0,1,1)]

def panel(images,labels,title,columns=4):
    rows=math.ceil(len(images)/columns);canvas=Image.new('RGB',(480*columns,54+520*rows),'#151b1d');d=ImageDraw.Draw(canvas);d.text((16,8),title,font=font(23),fill='#e4e7df')
    for i,(im,label) in enumerate(zip(images,labels)):
        x=i%columns*480;y=54+i//columns*520;canvas.paste(im,(x,y));d.text((x+12,y+485),label,font=font(19),fill='#d3d9d4')
    return canvas

def gap_board(t,geo):
    # Mark actual absent source components rather than paint them into layers.
    a=Image.fromarray(t.render(geo,0,.58));d=ImageDraw.Draw(a)
    d.rectangle((105,145,335,251),outline='#ffad57',width=3);d.text((112,150),'A',font=font(27),fill='#ffad57')
    b=Image.fromarray(t.render(geo,0,0,.5,0));d=ImageDraw.Draw(b)
    # Trace the actual half membrane edge from this reconstruction.
    pts=[]
    if t.name=='night_owl':
        for y in range(145,355,3):pts.append((t.qmid+t.cfg['membrane_slope']*(y-250)-t.cfg['membrane_curve']*(y-250)**2,y))
    else:
        for x in range(28,455,3):pts.append((x,t.qmid+t.cfg['membrane_slope']*(x-240)+t.cfg['membrane_curve']*(x-240)**2))
    d.line(pts,fill='#ffad57',width=3);d.text((230,175),'B',font=font(27),fill='#ffad57')
    c=Image.fromarray(t.render(geo,0,0,1,.5));d=ImageDraw.Draw(c);d.rectangle((45,163,443,338),outline='#ffad57',width=3);d.text((52,168),'C',font=font(27),fill='#ffad57')
    sheet=panel([a,b,c],['A 下转：原虹膜/扩展高光接合','B 缺独立瞬膜湿润前缘','C 缺独立上下眼皮运动源'],t.cfg['label']+' · 缺口标注（橙线不进入素材）',3)
    sheet.save(ROOT/'review'/('gaps-'+t.name+'.png'))

def pose_at(time):
    points=[(0,0),(-.78,0),(.78,0),(0,-.58),(0,.58),(-.78,-.58),(.78,.58),(0,0)]
    if time<7:
        q=time;i=min(6,int(q));v=q-i;v=v*v*(3-2*v);gx=points[i][0]*(1-v)+points[i+1][0]*v;gy=points[i][1]*(1-v)+points[i+1][1]*v
        return gx,gy,0,0,'摆幅测试 · 预设输入'
    if time<8.4:
        p=(time-7)/1.4;m=math.sin(math.pi*p)**2
        return 0,0,m,0,'独立瞬膜扫过 · 预设动作'
    if time<10:return 0,0,0,0,'回中停留 · 非真实检测'
    if time<10.45:
        p=(time-10)/.45;m=min(1,p/.35);l=max(0,(p-.35)/.65)
        return 0,0,m,l,'450ms 闭合 · 膜先/外眼皮后'
    if time<11.6:return 0,0,1,1,'闭眼停留'
    if time<11.75:
        p=(time-11.6)/.15;l=max(0,1-p/.65);m=min(1,(1-p)/.35)
        return 0,0,m,l,'150ms 打开 · 外眼皮先/膜后'
    return 0,0,0,0,'回到起点 · 可循环'

def movie(themes,geo):
    target=ROOT/'review/rotation-and-close.mp4';frames=400;fps=32;timeline=[]
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','960x558','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],stdin=subprocess.PIPE)
    for i in range(frames):
        time=i/fps;gx,gy,m,l,phase=pose_at(time);im=Image.new('RGB',(960,558),'#151b1d');d=ImageDraw.Draw(im)
        for j,t in enumerate(themes):im.paste(Image.fromarray(t.render(geo,gx,gy,m,l)),(j*480,42));d.text((j*480+12,7),t.cfg['label'],font=font(21),fill='#e6e7df')
        d.text((12,528),f'R1 新重制审阅 | {time:05.2f}s | {phase} | 非设备录像',font=font(16),fill='#bcc8c5');proc.stdin.write(im.tobytes());timeline.append(dict(frame=i,time_s=time,gaze_x=gx,gaze_y=gy,membrane=m,lid=l,phase=phase))
        if i%100==0:print('movie frames',i,flush=True)
    proc.stdin.close();assert proc.wait()==0
    (ROOT/'review/timeline.json').write_text(json.dumps(dict(duration_s=frames/fps,fps=fps,units='seconds',input='preset artwork review; no detector/source state',frames=timeline),ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--movie',action='store_true');args=parser.parse_args()
    before=verify_inputs();geo=Geometry();themes=[Theme(n) for n in RECIPE['themes']];checks=[]
    for t in themes:
        base=quantize(over(t.original[...,:3],t.frame));actual=t.render(geo)
        assert np.array_equal(actual,base),'neutral does not preserve accepted layer composite'
        assert np.array_equal(t.surface[...,:3][t.core],t.original[...,:3][t.core]),'protected iris/pupil changed'
        assert (t.surface[...,3]==255).all()
        assert np.array_equal(t.render(geo,0,0,1,1),quantize(over(t.closed[...,:3],t.frame))),'closed source coverage differs'
        for membrane in t.membranes:assert np.array_equal(membrane[...,:3],np.rint(t.membrane[...,:3]).astype(np.uint8)),'membrane RGB must come only from independent texture'
        frames=[];labels=[]
        for name,label,gx,gy,m,l in CASES:
            a=t.render(geo,gx,gy,m,l);save(a,ROOT/'review'/t.name/(name+'.png'));frames.append(Image.fromarray(a));labels.append(label)
        panel(frames,labels,t.cfg['label']+' · R1 新重制 / 待审阅',4).save(ROOT/'review'/('comparison-'+t.name+'.png'))
        for name,gx,gy in [('up-left',-.78,-.58),('up-right',.78,-.58),('down-left',-.78,.58),('down-right',.78,.58)]:save(t.render(geo,gx,gy),ROOT/'review'/t.name/(name+'.png'))
        gap_board(t,geo)
        checker=np.where(((XX//24+YY//24)%2)[...,None]>0,np.array([84,89,90]),np.array([130,135,136])).astype(np.float32)
        masks=[Image.fromarray(t.surface),Image.fromarray(t.core.astype(np.uint8)*255).convert('RGB'),Image.fromarray(np.rint(over(checker,t.membranes[4])).astype(np.uint8)),Image.fromarray(np.rint(over(checker,t.lids[4])).astype(np.uint8))]
        panel(masks,['重制眼球表面','原虹膜/瞳孔保护区','独立材质膜层（无原眼睛）','闭眼原图推导的外眼皮'],t.cfg['label']+' · 图层审查',4).save(ROOT/'review'/('layers-'+t.name+'.png'))
        checks.append(dict(theme=t.name,protected_pixels=int(t.core.sum()),protected_pixels_changed=0,neutral_layer_composite_pixel_difference=0,closed_source_composite_pixel_difference=0,membrane_RGB_source='independent RGBA membrane_texture_source.png only; explicit gain/opacity in recipe; approved composite never loaded by processing',opaque_surface=True,sprite_origin=[0,128],sprite_dimensions=[480,240]))
    # Pin the existing approved pure-axis range via the exact C map.
    for gx,gy,x,y in [(0.78,0,360,250),(-.78,0,120,250),(0,.58,240,330),(0,-.58,240,170)]:
        uv=geo.map(gx,gy)[y,x];assert np.max(np.abs(uv-[240,250]))<.04
    if args.movie:movie(themes,geo)
    assert verify_inputs()==before
    report=dict(version=RECIPE['version'],status='NEW REMAKE - visual review pending',Pillow=PIL.__version__,numpy=np.__version__,checks=checks,range_preserved=[120,80],source_hashes_and_mtimes_unchanged=True,production_or_device_operated=False,limitations=['Not exact v2 recovery','Missing independently authored membrane wet-edge strip','Intermediate eyelid movement inferred from one closed image per theme','Original iris hidden behind lids not reconstructable exactly; expanded source supplies unseen regions','No native GSP, real thermal input or performance validation'])
    (ROOT/'review/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
