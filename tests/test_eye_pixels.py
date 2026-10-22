#!/usr/bin/env python3
"""Independent float64 PNG compositor vs full-resolution production C pixels."""
import io,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'assets/eye-pack';OUT=ROOT/'evidence/mechanical-c/pixels';GENERATED=ROOT/'build-host/eye-generated'
def source(path):
    a=np.asarray(Image.open(path).convert('RGBA'),dtype=np.float64)/255
    a[...,:3]*=a[...,3:4];return a

_mechanical_reference=None
def oracle(theme,gx,gy,lid):
    global _mechanical_reference
    if theme['id']=='mechanical':
        if _mechanical_reference is None:
            sys.path.insert(0,str(ROOT/'assets/mechanical-c/preview'))
            from reference_render import Renderer
            _mechanical_reference=Renderer()
        return np.rint(np.asarray(_mechanical_reference.render(gx,gy,lid))/255*np.array([31,63,31])).astype(int)
    folder=PACK/'assets/processed'/theme['id'];eye=source(GENERATED/(theme['id']+'-wide-eye.png'));frame=source(folder/'frame.png')
    generated=next(t for t in json.loads((GENERATED/'eye_pack.json').read_text())['themes'] if t['theme']==theme['id'])
    x,y=np.meshgrid(np.arange(480),np.arange(480));amp=generated['max_gaze_translation_px'];ox,oy=generated['eye_origin']
    cx,cy=generated['eye_center']
    def projection(gx,gy):
        nx=np.clip(np.rint((x-cx).astype(np.float32)*np.float32(32768/233)),-32768,32767).astype(np.int64)
        ny=np.clip(np.rint((y-cy).astype(np.float32)*np.float32(32768/233)),-32768,32767).astype(np.int64)
        fxn=nx.astype(np.float32)/np.float32(32768);fyn=ny.astype(np.float32)/np.float32(32768)
        z=np.float32(1)-fxn*fxn-fyn*fyn;nz=(np.sqrt(np.maximum(0,z))*np.float32(32767)).astype(np.int64)
        if gx==gy==0:return x-ox,y-oy
        import math
        yaw=np.float32(np.float32(gx)/np.float32(.78))*np.float32(math.asin(np.float32(amp[0])/np.float32(233)))
        pitch=np.float32(np.float32(gy)/np.float32(.58))*np.float32(math.asin(np.float32(amp[1])/np.float32(233)))
        q=lambda value:int(np.rint(np.float32(value)*np.float32(32768)))
        c,s=q(math.cos(yaw)),q(math.sin(yaw));cp,sp=q(math.cos(pitch)),q(math.sin(pitch))
        lx=(c*nx-s*nz)>>15;az=(s*nx+c*nz)>>15;ly=(cp*ny-sp*az)>>15
        u=np.float32(cx)+lx.astype(np.float32)*np.float32(233/32768);v=np.float32(cy)+ly.astype(np.float32)*np.float32(233/32768)
        return np.where(z<0,x,u)-ox,np.where(z<0,y,v)-oy
    sx,sy=projection(gx,gy);ix=np.floor(sx).astype(int);iy=np.floor(sy).astype(int);fx=sx-ix;fy=sy-iy
    c=np.zeros((480,480,4))
    for j in (0,1):
        for i in (0,1):
            xx=ix+i;yy=iy+j;valid=(xx>=0)&(yy>=0)&(xx<eye.shape[1])&(yy<eye.shape[0]);weight=(fx if i else 1-fx)*(fy if j else 1-fy)
            c[valid]+=eye[yy[valid],xx[valid]]*weight[valid,None]
    n=lid*8;lo=int(n);hi=min(8,lo+1);u=n-lo
    a=source(folder/f'lid_{lo:02}.png')*(1-u)+source(folder/f'lid_{hi:02}.png')*u
    lx=x-theme['lid_origin'][0];ly=y-theme['lid_origin'][1];valid=(lx>=0)&(ly>=0)&(lx<a.shape[1])&(ly<a.shape[0]);b=np.zeros_like(c);b[valid]=a[ly[valid],lx[valid]]
    c[...,:3]=b[...,:3]+c[...,:3]*(1-b[...,3:4]);c[...,:3]=frame[...,:3]+c[...,:3]*(1-frame[...,3:4])
    bits=np.array([31,63,31]);return np.floor(np.clip(c[...,:3],0,1)*bits+.5).astype(int)
def main():
    themes=json.loads((PACK/'assets/manifest.json').read_text())['themes'];checks=[]
    for i,t in enumerate(themes):
        poses=[(0,0,0)]+[(x*.78,y*.58,0) for x in (-1,0,1) for y in (-1,0,1)]+[(.253,-.217,b) for b in (0,.0625,.13,.25,.49,.5,.75,.93,1)]
        for gx,gy,lid in poses:
            ppm=subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),str(i),str(gx),str(gy),str(lid)])
            actual=np.asarray(Image.open(io.BytesIO(ppm))).astype(int)
            actual=np.rint(actual/255*np.array([31,63,31])).astype(int)
            expected=oracle(t,gx,gy,lid);delta=np.abs(actual-expected)
            assert delta.max()<=1,(t['id'],gx,gy,lid,delta.max())
            assert (delta>0).sum()<500,(t['id'],(delta>0).sum())
            if gx==gy==lid==0 and t['id']!='mechanical':
                neutral=np.asarray(Image.open(PACK/'assets/processed'/t['id']/'neutral.png'))[...,:3]
                native=np.floor(neutral/255*np.array([31,63,31])+.5).astype(int)
                assert np.max(np.abs(actual-native))<=1
            checks.append(dict(theme=t['id'],gaze=[gx,gy],lid=lid,max_rgb565_channel_delta=int(delta.max()),different_channels=int((delta>0).sum())))
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'independent-pixels.json').write_text(json.dumps(dict(checks=checks,note='Independent float64 oracle; <=1 RGB565 channel code only at rounding boundaries versus C float32. No palette/downsample.'),indent=2)+'\n')
    print('PASS',len(checks),'independent full480 layer comparisons')
if __name__=='__main__':main()
