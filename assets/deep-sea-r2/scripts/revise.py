#!/usr/bin/env python3
"""Deep-sea-only R2, independent visual review; no main project/device writes."""
import argparse,json,hashlib,subprocess,sys,math,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import r1_reference as ref
ROOT=ref.ROOT;CFG=ref.RECIPE['correction'];XX=ref.XX;YY=ref.YY

def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def blur(a,r):return np.asarray(Image.fromarray(np.clip(np.rint(a),0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)),dtype=np.float32)
def ellipse(values):
    x,y,rx,ry=values;return np.sqrt(((XX-x)/rx)**2+((YY-y)/ry)**2)

class Revised:
    def __init__(self,old):
        self.old=old;self.frame=old.frame
        registered=ref.load(ROOT/'build/masks/deep_sea/registered_expanded_source.png')
        original=old.original
        weights=np.array([.2126,.7152,.0722],dtype=np.float32)
        a=(original[...,:3]*weights).sum(2);b=(registered[...,:3]*weights).sum(2)
        radius=CFG['light_normalization_blur_px'];gain=np.clip((blur(b,radius)+8)/(blur(a,radius)+8),*CFG['gain_range'])
        restored=np.clip(original[...,:3]*gain[...,None],0,255)
        r=ellipse(CFG['iris_patch_ellipse']);inner,outer=CFG['patch_feather_normalized'];mix=1-smooth((r-inner)/(outer-inner))
        # Hard original pupil/gloss lock; transition around it is also geometric,
        # never the contour of the fixed socket aperture.
        p=ellipse(CFG['pupil_lock_ellipse']);lock=p<=1
        pweight=1-smooth((p-1)/.2)
        corrected=registered[...,:3]*(1-mix[...,None])+restored*mix[...,None]
        corrected=corrected*(1-pweight[...,None])+original[...,:3]*pweight[...,None]
        self.surface=np.concatenate([np.rint(corrected),np.full((480,480,1),255)],axis=2).astype(np.uint8)
        self.lock=lock;self.mix=mix;self.gain=gain;self.pweight=pweight
        folder=ROOT/'build/r2/deep_sea';ref.save(self.surface,folder/'eye_surface.png');ref.save(self.frame,folder/'frame.png')
        ref.save(np.zeros((480,480,4)),folder/'rim_restore_disabled.png')
        ref.save(lock*255,ROOT/'build/r2/masks/pupil_lock.png');ref.save(mix*255,ROOT/'build/r2/masks/iris_blend.png');ref.save(gain/CFG['gain_range'][1]*255,ROOT/'build/r2/masks/light_estimate.png')
        for kind in ('membrane','lids'):
            for path in (ROOT/'build/processed/deep_sea'/kind).glob('*.png'):
                target=folder/kind/path.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        assert np.array_equal(self.surface[...,:3][lock],original[...,:3][lock])
    def render(self,geo,gx=0,gy=0,membrane=0,lid=0):
        uv=geo.map(gx,gy);rgb=ref.sample(self.surface.astype(np.float32),uv[...,0],uv[...,1])[...,:3]
        # No gaze-dependent image replacement or rim-opacity branch.
        rgb=ref.over(rgb,self.old.membranes[min(8,int(membrane*8+.5))])
        rgb=ref.over(rgb,self.old.lids[min(8,int(lid*8+.5))])
        return ref.quantize(ref.over(rgb,self.frame))

def membrane_at(t,fast):
    if not fast:
        return math.sin(math.pi*t/1.4)**2 if 0<=t<1.4 else 0
    timing=CFG['membrane_sweep_ms'];close=timing['cover']/1000;hold=timing['hold']/1000;opening=timing['uncover']/1000
    if t<0:return 0
    if t<close:return float(smooth(t/close))
    if t<close+hold:return 1
    if t<close+hold+opening:return float(1-smooth((t-close-hold)/opening))
    return 0

def pose_at(t,fast):
    keys=[(0,0,0),(.8,-.78,0),(1.6,.78,0),(2.4,0,-.58),(3.2,0,.58),(4,-.78,-.58),(4.8,.78,.58),(5.25,.18,.12),(5.65,.07,.04),(6.1,0,0)]
    if t<6.1:
        for a,b in zip(keys,keys[1:]):
            if a[0]<=t<b[0]:
                u=float(smooth((t-a[0])/(b[0]-a[0])));return a[1]*(1-u)+b[1]*u,a[2]*(1-u)+b[2]*u,0,0,'转动/慢回正 · 预设动作'
    if t<10:
        m=max(membrane_at(t-6.3,fast),membrane_at(t-8.1,fast));return 0,0,m,0,'独立瞬膜：R1 1400ms / R2 240ms'
    if t<10.45:
        elapsed=t-10
        if fast:return 0,0,min(1,elapsed/.1),max(0,(elapsed-.1)/.35),'闭眼总时长450ms保持'
        q=elapsed/.45;return 0,0,min(1,q/.35),max(0,(q-.35)/.65),'闭眼总时长450ms保持'
    if t<11.6:return 0,0,1,1,'全闭眼保持不变'
    if t<11.75:
        q=(t-11.6)/.15;return 0,0,min(1,(1-q)/.35),max(0,1-q/.65),'睁眼总时长150ms保持'
    return 0,0,0,0,'回到正视'

def movie(old,new,geo):
    fps=60;count=750;timeline=[];path=ROOT/'review/deep-sea-r1-vs-r2.mp4'
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','960x558','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',str(path)],stdin=subprocess.PIPE)
    for i in range(count):
        t=i/fps;a=pose_at(t,False);b=pose_at(t,True);im=Image.new('RGB',(960,558),'#131b1e');d=ImageDraw.Draw(im)
        im.paste(Image.fromarray(old.render(geo,*a[:4])),(0,42));im.paste(Image.fromarray(new.render(geo,*b[:4])),(480,42))
        d.text((12,7),'R1 原审阅稿',font=ref.font(21),fill='#abb8bb');d.text((492,7),'R2 深海修订 · 待审阅',font=ref.font(21),fill='#e2cf9c');d.text((12,528),f'{t:05.2f}s  {b[4]} · 非设备录像',font=ref.font(16),fill='#bdcbca')
        proc.stdin.write(im.tobytes());timeline.append(dict(frame=i,t_seconds=t,R1=a[:4],R2=b[:4]))
        if i%150==0:print('movie',i,flush=True)
    proc.stdin.close();assert proc.wait()==0
    (ROOT/'review/timeline.json').write_text(json.dumps(dict(duration_s=12.5,fps=60,frames=timeline,input='preset review only; no real sensor/production state machine'),indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--movie',action='store_true');args=p.parse_args();before=ref.verify_inputs();geo=ref.Geometry();old=ref.Theme('deep_sea');new=Revised(old)
    labels=[];ims=[]
    for name,label,gx,gy,m,l in ref.CASES:
        a=old.render(geo,gx,gy,m,l);b=new.render(geo,gx,gy,m,l)
        ref.save(a,ROOT/'review/r1'/(name+'.png'));ref.save(b,ROOT/'review/r2'/(name+'.png'))
        ims.extend([Image.fromarray(a),Image.fromarray(b)]);labels.extend(['R1 '+label,'R2 '+label])
    ref.panel(ims,labels,'深海 · 同姿态 R1/R2（左旧右新）',4).save(ROOT/'review/static-r1-vs-r2.png')
    surface_a=Image.fromarray(old.surface);surface_b=Image.fromarray(new.surface)
    ref.panel([surface_a,surface_b],['R1 开口形状贴片混入阴影','R2 明暗匹配/椭圆接合；无回正补圈'],'眼球纹理检查：阴影不能随眼珠转动',2).save(ROOT/'review/surfaces-r1-vs-r2.png')
    # Same texture, no discontinuous material switch near the former rim threshold.
    returns=[];return_labels=[]
    for gx in (.18,.10,.05,.02,0):returns.append(Image.fromarray(new.render(geo,gx,0)));return_labels.append(f'R2 gaze_x={gx:.2f}')
    ref.panel(returns,return_labels,'慢回正检查 · 同一张眼球纹理，零 rim_restore 淡入',5).save(ROOT/'review/return-to-center.png')
    assert np.array_equal(new.render(geo,0,0,1,1),old.render(geo,0,0,1,1))
    for t in (-1,0,.10,.12,.24,.5,1.4):assert 0<=membrane_at(t,True)<=1
    assert membrane_at(.1,True)==1 and membrane_at(.12,True)==1 and membrane_at(.24,True)==0
    assert ref.verify_inputs()==before
    if args.movie:movie(old,new,geo)
    report=dict(version=ref.RECIPE['version'],scope='Deep sea only; independent review',hard_original_pupil_gloss_pixels=int(new.lock.sum()),hard_original_pixels_changed=0,iris_detail_note='Original iris detail is photometrically matched before blending; no whole-neutral pixel-identity claim in R2',rim_restore_opacity=0,membrane_roundtrip_ms=240,previous_membrane_roundtrip_ms=1400,closed_pixels_unchanged=True,frame_and_overlay_assets_unchanged=True,source_hashes_mtimes_unchanged=True,main_project_or_device_actions=False,remaining_limit='Unlit whole original iris is unavailable; low-frequency brightness separation is estimated, not recovered source artwork. Inspect residual joins/glints.')
    (ROOT/'review/validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
