#!/usr/bin/env python3
"""Offline reference compositor only; not a C/GSP or sensor implementation.

The inverse projection arithmetic follows the supplied eye_projection.h snapshot.
The new C design composites shutter in texture space, then the fixed mount.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CX, CY, R = 240, 245, 233
SIZE = 480
SHUTTER_ORIGIN = (120,125)
Y,X = np.mgrid[:SIZE,:SIZE]
NX = np.clip(np.rint((X-CX).astype(np.float32)*np.float32(32768/R)),-32768,32767).astype(np.int64)
NY = np.clip(np.rint((Y-CY).astype(np.float32)*np.float32(32768/R)),-32768,32767).astype(np.int64)
FXN,FYN = NX.astype(np.float32)/np.float32(32768),NY.astype(np.float32)/np.float32(32768)
Z = np.float32(1)-FXN*FXN-FYN*FYN
NZ = (np.sqrt(np.maximum(0,Z))*np.float32(32767)).astype(np.int64)

def sample_bilinear(a,u,v):
    ix,iy = np.floor(u).astype(int),np.floor(v).astype(int)
    fx,fy = u-ix,v-iy
    out = np.zeros((*u.shape,4),dtype=np.float64)
    for j in (0,1):
        for i in (0,1):
            xx,yy=ix+i,iy+j
            good=(xx>=0)&(yy>=0)&(xx<a.shape[1])&(yy<a.shape[0])
            w=(fx if i else 1-fx)*(fy if j else 1-fy)
            out[good]+=a[yy[good],xx[good]]*w[good,None]
    return out

def projection(gx,gy):
    gx,gy=float(np.clip(gx,-.78,.78)),float(np.clip(gy,-.58,.58))
    if gx==0 and gy==0:
        return X.astype(float),Y.astype(float)
    yaw=np.float32(np.float32(gx)/np.float32(.78))*np.float32(math.asin(np.float32(120)/np.float32(R)))
    pitch=np.float32(np.float32(gy)/np.float32(.58))*np.float32(math.asin(np.float32(80)/np.float32(R)))
    q=lambda v:int(np.rint(np.float32(v)*np.float32(32768)))
    c,s=q(math.cos(yaw)),q(math.sin(yaw))
    cp,sp=q(math.cos(pitch)),q(math.sin(pitch))
    lx=(c*NX-s*NZ)>>15
    az=(s*NX+c*NZ)>>15
    ly=(cp*NY-sp*az)>>15
    u=np.float32(CX)+lx.astype(np.float32)*np.float32(R/32768)
    v=np.float32(CY)+ly.astype(np.float32)*np.float32(R/32768)
    return np.where(Z<0,X,u),np.where(Z<0,Y,v)

def premultiplied(path):
    a=np.asarray(Image.open(path).convert('RGBA'),dtype=np.float64)/255
    a[...,:3]*=a[...,3:4]
    return a

class Renderer:
    def __init__(self,root=ROOT):
        self.root=Path(root)
        a=self.root/'assets/processed'
        self.surface=premultiplied(a/'eye_surface.png')
        self.frame=premultiplied(a/'frame.png')
        self.shutters=[premultiplied(a/f'shutter/shutter_{i:02d}.png') for i in range(9)]
        self.textures=[]
        for shutter in self.shutters:
            tex=self.surface.copy()
            ox,oy=SHUTTER_ORIGIN
            h,w=shutter.shape[:2]
            dst=tex[oy:oy+h,ox:ox+w]
            dst[...,:3]=shutter[...,:3]+dst[...,:3]*(1-shutter[...,3:4])
            dst[...,3]=shutter[...,3]+dst[...,3]*(1-shutter[...,3])
            self.textures.append(tex)

    def render(self,gx=0,gy=0,closure=0,active=True,quantize=True):
        if not active:
            return Image.new('RGB',(SIZE,SIZE),'black')
        # Nearest indexed frame avoids double blade edges from frame cross-fade.
        index=int(math.floor(float(np.clip(closure,0,1))*8+.5))
        u,v=projection(gx,gy)
        rgba=sample_bilinear(self.textures[index],u,v)
        rgba[...,:3]=self.frame[...,:3]+rgba[...,:3]*(1-self.frame[...,3:4])
        rgb=np.clip(rgba[...,:3],0,1)
        if quantize:
            bits=np.array([31,63,31])
            rgb=np.floor(rgb*bits+.5)/bits
        return Image.fromarray(np.floor(rgb*255+.5).astype(np.uint8),'RGB')

def timeline_sample(timeline,t_ms):
    keys=timeline['frames']
    if t_ms<=keys[0]['t_ms']:
        return dict(keys[0])
    for i in range(len(keys)-1):
        a,b=keys[i],keys[i+1]
        if a['t_ms']<=t_ms<b['t_ms']:
            result=dict(a)
            f=(t_ms-a['t_ms'])/(b['t_ms']-a['t_ms'])
            interpolation=a.get('interp','linear')
            if interpolation=='step': f=0
            elif interpolation=='smoothstep': f=f*f*(3-2*f)
            for field in ('gaze_x','gaze_y','shutter'):
                result[field]=a[field]+(b[field]-a[field])*f
            result['t_ms']=t_ms
            return result
    return dict(keys[-1])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gaze-x',type=float,default=0)
    p.add_argument('--gaze-y',type=float,default=0)
    p.add_argument('--shutter',type=float,default=0)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    Renderer().render(a.gaze_x,a.gaze_y,a.shutter).save(a.output)

if __name__=='__main__': main()
