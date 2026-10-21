#!/usr/bin/env python3
"""Independent float64 PNG compositor vs full-resolution production C pixels."""
import io,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'assets/eye-pack';OUT=ROOT/'evidence/eye-ui'
def source(path):
    a=np.asarray(Image.open(path).convert('RGBA'),dtype=np.float64)/255
    a[...,:3]*=a[...,3:4];return a

def oracle(theme,gx,gy,lid):
    folder=PACK/'assets/processed'/theme['id'];eye=source(folder/'eye.png');frame=source(folder/'frame.png')
    x,y=np.meshgrid(np.arange(480),np.arange(480));amp=theme['max_gaze_translation_px'];ox,oy=theme['eye_origin']
    sx=x-ox-gx/.78*amp[0];sy=y-oy-gy/.58*amp[1];ix=np.floor(sx).astype(int);iy=np.floor(sy).astype(int);fx=sx-ix;fy=sy-iy
    c=np.zeros((480,480,4))
    for j in (0,1):
        for i in (0,1):
            xx=ix+i;yy=iy+j;valid=(xx>=0)&(yy>=0)&(xx<eye.shape[1])&(yy<eye.shape[0]);weight=(fx if i else 1-fx)*(fy if j else 1-fy)
            c[valid]+=eye[yy[valid],xx[valid]]*weight[valid,None]
    n=lid*8;lo=int(n);hi=min(8,lo+1);u=n-lo
    a=source(folder/f'lid_{lo:02}.png')*(1-u)+source(folder/f'lid_{hi:02}.png')*u
    lx=x-ox;ly=y-oy;valid=(lx>=0)&(ly>=0)&(lx<a.shape[1])&(ly<a.shape[0]);b=np.zeros_like(c);b[valid]=a[ly[valid],lx[valid]]
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
            if gx==gy==lid==0:
                neutral=np.asarray(Image.open(PACK/'assets/processed'/t['id']/'neutral.png'))[...,:3]
                native=np.floor(neutral/255*np.array([31,63,31])+.5).astype(int)
                assert np.max(np.abs(actual-native))<=1
            checks.append(dict(theme=t['id'],gaze=[gx,gy],lid=lid,max_rgb565_channel_delta=int(delta.max()),different_channels=int((delta>0).sum())))
    OUT.mkdir(exist_ok=True);(OUT/'independent-pixels.json').write_text(json.dumps(dict(checks=checks,note='Independent float64 oracle; <=1 RGB565 channel code only at rounding boundaries versus C float32. No palette/downsample.'),indent=2)+'\n')
    print('PASS',len(checks),'independent full480 layer comparisons')
if __name__=='__main__':main()
