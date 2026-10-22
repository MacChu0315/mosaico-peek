#!/usr/bin/env python3
"""Deterministic six-region visual morph for the approved C shutter.

This is an editable 2-D artwork construction, NOT a physical iris simulation.
Python 3 + Pillow + NumPy. No image generation, optical flow or extra runtime.
"""
from __future__ import annotations
import argparse, base64, io, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SIZE=240
ORIGIN=(120,125)
CENTER=np.array([120.,120.])
RADIUS=110.
SUPERSAMPLE=2

# Measured in the registered 240x240 ROI. Order clockwise from upper-left.
# Closed points outline the small central hexagonal patch in the generated
# concept; collapsing that patch produces six continuous closing sectors.
KEYS={
 'open': {'inner':[[89,67],[152,64],[184,124],[154,174],[94,174],[62,120]],
          'seam_angles_deg':[-155.3,-91.7,-27.3,24.4,72.5,142.2]},
 'contracted': {'inner':[[98,87],[141,96],[149,127],[128,147],[99,141],[91,112]],
          'seam_angles_deg':[-155.8,-91.8,-32.8,20.1,83.9,140.9]},
 'closed': {'inner':[[112,100],[138,108],[139,128],[120,138],[103,131],[103,108]],
          'seam_angles_deg':[-159.,-91.,-34.8,20.1,84.2,141.8]},
}

def outer_points(angles):
    # Eight short arc edges per blade preserve the circular outer boundary.
    arcs=[]
    for i in range(6):
        a,b=float(angles[i]),float(angles[(i+1)%6])
        if b<a:b+=360
        aa=np.deg2rad(np.linspace(a,b,9))
        arcs.append(CENTER+RADIUS*np.stack([np.cos(aa),np.sin(aa)],axis=-1))
    return arcs

def triangles(inner,angles):
    arcs=outer_points(angles)
    ts=[]; regions=[]
    for i in range(6):
        # Fan through the outer arc in reverse order: one continuous blade.
        polygon=np.vstack([inner[i],inner[(i+1)%6],arcs[i][::-1]])
        regions.append(polygon)
        for j in range(1,len(polygon)-1):ts.append(polygon[[0,j,j+1]])
    return ts,regions

def coordinate_map(source_inner,source_angles,target_inner,target_angles):
    st,_=triangles(source_inner,source_angles)
    tt,_=triangles(target_inner,target_angles)
    yy,xx=np.mgrid[:SIZE*SUPERSAMPLE,:SIZE*SUPERSAMPLE]
    px=(xx+.5)/SUPERSAMPLE-.5;py=(yy+.5)/SUPERSAMPLE-.5
    sx=px.copy();sy=py.copy()
    for src,dst in zip(st,tt):
        p0,p1,p2=dst
        det=(p1[1]-p2[1])*(p0[0]-p2[0])+(p2[0]-p1[0])*(p0[1]-p2[1])
        if abs(det)<1e-9:continue
        x0=max(0,int(math.floor((dst[:,0].min()+.5)*SUPERSAMPLE)))
        y0=max(0,int(math.floor((dst[:,1].min()+.5)*SUPERSAMPLE)))
        x1=min(SIZE*SUPERSAMPLE,int(math.ceil((dst[:,0].max()+.5)*SUPERSAMPLE))+1)
        y1=min(SIZE*SUPERSAMPLE,int(math.ceil((dst[:,1].max()+.5)*SUPERSAMPLE))+1)
        x=px[y0:y1,x0:x1];y=py[y0:y1,x0:x1]
        a=((p1[1]-p2[1])*(x-p2[0])+(p2[0]-p1[0])*(y-p2[1]))/det
        b=((p2[1]-p0[1])*(x-p2[0])+(p0[0]-p2[0])*(y-p2[1]))/det
        c=1-a-b;m=(a>=-1e-7)&(b>=-1e-7)&(c>=-1e-7)
        sx[y0:y1,x0:x1][m]=(a*src[0,0]+b*src[1,0]+c*src[2,0])[m]
        sy[y0:y1,x0:x1][m]=(a*src[0,1]+b*src[1,1]+c*src[2,1])[m]
    return sx,sy

def sample(a,sx,sy):
    x=np.clip(sx,0,SIZE-1.00001);y=np.clip(sy,0,SIZE-1.00001)
    ix=x.astype(int);iy=y.astype(int);fx=(x-ix)[...,None];fy=(y-iy)[...,None]
    return (a[iy,ix]*(1-fx)*(1-fy)+a[iy,ix+1]*fx*(1-fy)+
            a[iy+1,ix]*(1-fx)*fy+a[iy+1,ix+1]*fx*fy)

def polygon_mask(points,fill=255):
    m=Image.new('L',(SIZE*SUPERSAMPLE,)*2,0)
    if len(points)>=3:
        ps=[((float(x)+.5)*SUPERSAMPLE,(float(y)+.5)*SUPERSAMPLE) for x,y in points]
        ImageDraw.Draw(m).polygon(ps,fill=fill)
    return np.asarray(m,dtype=np.float64)/255.

def render_frame(images,k):
    q=k/8
    if k<=4:an,bn='open','contracted';u=k/4
    else:an,bn='contracted','closed';u=(k-4)/4
    ai=np.array(KEYS[an]['inner'],float);bi=np.array(KEYS[bn]['inner'],float)
    aa=np.array(KEYS[an]['seam_angles_deg']);ba=np.array(KEYS[bn]['seam_angles_deg'])
    target_b=bi if bn!='closed' else np.tile(CENTER,(6,1))
    target_inner=ai*(1-u)+target_b*u
    target_angles=aa*(1-u)+ba*u
    ma=coordinate_map(ai,aa,target_inner,target_angles)
    mb=coordinate_map(bi,ba,target_inner,target_angles)
    # Both inputs have FIRST been warped onto matching blade geometry. This
    # modest texture interpolation is not a crossfade of unregistered pupils.
    out=sample(images[an],*ma)*(1-u)+sample(images[bn],*mb)*u
    yy,xx=np.mgrid[:SIZE*SUPERSAMPLE,:SIZE*SUPERSAMPLE]
    rx=(xx+.5)/SUPERSAMPLE-.5-CENTER[0];ry=(yy+.5)/SUPERSAMPLE-.5-CENTER[1]
    rr=np.hypot(rx,ry)
    hole=polygon_mask(target_inner) if k<8 else np.zeros_like(rr)
    alpha=np.clip((RADIUS-rr)*SUPERSAMPLE+.5,0,1)*(1-hole)
    # Fade only a 6px outer overlap to the common OPEN backing, leaving the
    # richly detailed optical annulus perfectly fixed in the final composite.
    alpha*=np.clip((RADIUS-rr)/6.,0,1)
    rgba=np.dstack([np.clip(out,0,255),alpha*255]).round().astype(np.uint8)
    rgba[rgba[:,:,3]==0,:3]=0
    im=Image.fromarray(rgba).resize((SIZE,SIZE),Image.Resampling.LANCZOS)
    # Pillow straight-alpha resampling is used; all fully transparent RGB
    # channels are explicitly cleared for clean asset importers.
    a=np.array(im)
    # Preserve the two provided open-hole keyframes without an unnecessary
    # supersampling round trip. In particular, compositing frame 00 over the
    # common OPEN backing is byte-identical to that backing.
    if k==0:a[:,:,:3]=images['open'].astype(np.uint8)
    if k==4:a[:,:,:3]=images['contracted'].astype(np.uint8)
    a[a[:,:,3]==0,:3]=0;im=Image.fromarray(a)
    _,regions=triangles(target_inner,target_angles)
    return im, {'frame':k,'closure':q,'inner_polygon_px':target_inner.tolist(),
                'seam_angles_deg':target_angles.tolist(),
                'hole_area_model_px2':float(abs(np.dot(target_inner[:,0],np.roll(target_inner[:,1],1))-
                                    np.dot(target_inner[:,1],np.roll(target_inner[:,0],1)))/2)},regions

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args();out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    originals={n:Image.open(args.input_dir/f'concept-{n}-480.png').convert('RGB') for n in KEYS}
    ims={n:np.asarray(im.crop((*ORIGIN,ORIGIN[0]+SIZE,ORIGIN[1]+SIZE)),dtype=np.float64) for n,im in originals.items()}
    frames=[];composites=[];spec=[];all_regions=[]
    for k in range(9):
        frame,record,regions=render_frame(ims,k);frame.save(out/f'shutter_{k:02}.png')
        base=originals['open'].convert('RGBA');base.alpha_composite(frame,ORIGIN)
        base.save(out/f'composite_{k:02}.png');frames.append(frame);composites.append(base);spec.append(record);all_regions.append(regions)
    data={'format':'RGBA8 straight alpha','size':[SIZE,SIZE],'origin':list(ORIGIN),'center_local':CENTER.tolist(),
      'mask_radius_px':RADIUS,'feather_width_px':6,'frame_00':'open','frame_04':'contracted','frame_08':'closed',
      'source_registration':'Each input already 480x480, crop box [120,125,360,365].',
      'method':'Six corresponding blade sectors, piecewise affine morph, aperture polygon shrinks; key textures interpolate only AFTER geometric registration.',
      'limitations':['2D visual morph, not rigid-body/physical iris simulation.','Closed central generated hexagonal patch is collapsed to a six-way meeting point.','Nine frames are discrete; select nearest frame or provide temporal interpolation policy in the main project.','Use common open backing; do not composite against a changing full-eye keyframe.'],
      'key_landmarks':KEYS,'frames':spec}
    (out/'shutter-rig.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    # Source SVG: six individually addressable geometric blade regions in the
    # contracted state. Raster texture is embedded; paths and layer structure
    # remain directly editable. Rebuilding animation uses the JSON + script.
    buf=io.BytesIO();frames[4].save(buf,format='PNG');uri='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="240" height="240" viewBox="0 0 240 240">',
         '<title>C shutter, six editable blade regions, contracted pose</title>',
         '<metadata>2D artwork geometry; see shutter-rig.json and build_shutter.py. Not a physical iris.</metadata>','<defs>']
    for i,p in enumerate(all_regions[4]):
        pts=' '.join(f'{x:.4f},{y:.4f}' for x,y in p)
        svg.append(f'<clipPath id="blade-{i:02}-clip"><polygon points="{pts}"/></clipPath>')
    svg.append(f'<image id="contracted-texture" width="240" height="240" xlink:href="{uri}"/>')
    svg.append('</defs>')
    for i in range(6):svg.append(f'<g id="blade-{i:02}" clip-path="url(#blade-{i:02}-clip)"><use xlink:href="#contracted-texture"/></g>')
    svg.append('</svg>');(out/'shutter-rig.svg').write_text('\n'.join(svg)+'\n')
    board=Image.new('RGB',(960,1026),(15,17,19));d=ImageDraw.Draw(board)
    for k,im in enumerate(composites):
        x=(k%3)*320;y=(k//3)*342;board.paste(im.convert('RGB').resize((320,320),Image.Resampling.LANCZOS),(x,y))
        d.text((x+12,y+324),f'{k:02} / closure={k/8:.3f}',fill=(220,225,230))
    board.save(out/'contactsheet.png')
    seq=[0]*8+list(range(1,9))+[8]*8+list(range(7,-1,-1))
    gif=[composites[k].resize((360,360),Image.Resampling.LANCZOS).convert('RGB') for k in seq]
    gif[0].save(out/'shutter-demo.gif',save_all=True,append_images=gif[1:],duration=100,loop=0,optimize=False)
    print(json.dumps({'output':str(out),'frames':len(frames),'hole_areas':[x['hole_area_model_px2'] for x in spec]},indent=2))

if __name__=='__main__':main()
