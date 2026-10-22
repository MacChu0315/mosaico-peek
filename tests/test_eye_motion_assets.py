#!/usr/bin/env python3
"""Neutral identity and full sphere coverage for the widened motion recipe."""
import io,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BUILD=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build-host';GEN=BUILD/'eye-generated';PACK=ROOT/'assets/eye-pack/assets/processed'
m=json.loads((GEN/'eye_pack.json').read_text());checks=[]
def codes(a):return np.rint(a.astype(float)/255*np.array([31,63,31])).astype(int)
for i,t in enumerate(m['themes']):
 eye=np.asarray(Image.open(GEN/(t['theme']+'-wide-eye.png')));assert eye.shape==(480,480,4) and (eye[:,:,3]==255).all()
 frame=np.asarray(Image.open(ROOT/'assets/mechanical-c/assets/processed/frame.png' if t['theme']=='mechanical' else PACK/t['theme']/'frame.png'));ys,xs=np.nonzero(frame[:,:,3]<255);cx,cy=t['eye_center'];nx=(xs-cx)/233;ny=(ys-cy)/233
 assert (1-nx*nx-ny*ny>=0).all();nz=np.sqrt(1-nx*nx-ny*ny)
 for gx in (-1,0,1):
  for gy in (-1,0,1):
   yaw=gx*np.arcsin(120/233);pitch=gy*np.arcsin(80/233)
   lx=np.cos(yaw)*nx-np.sin(yaw)*nz;az=np.sin(yaw)*nx+np.cos(yaw)*nz;ly=np.cos(pitch)*ny-np.sin(pitch)*az
   u=cx+233*lx;v=cy+233*ly;assert u.min()>1 and v.min()>1 and u.max()<478 and v.max()<478
 ppm=subprocess.check_output([str(BUILD/'eye_snapshot'),str(i),'0','0','0']);pixels=np.asarray(Image.open(io.BytesIO(ppm)))
 if t['theme']!='mechanical':assert np.array_equal(codes(pixels),codes(np.asarray(Image.open(ROOT/'tests/reference/eye-neutral-v105'/(t['theme']+'.png')))))
 checks.append(dict(theme=t['theme'],eye_size=t['eye_size'],eye_origin=t['eye_origin'],projected_center_excursion_px=[120,80],neutral_exact=(t['theme']!='mechanical'),mechanical_reference_test=(t['theme']=='mechanical'),nine_grid_sphere_uv_covered=True))
out=ROOT/'evidence/mechanical-c/pixels';out.mkdir(parents=True,exist_ok=True);(out/'asset-checks.json').write_text(json.dumps(checks,indent=2)+'\n');print('PASS two retained C-neutral frames exact; new mechanical reference covered separately and27 full-aperture sphere coverage bounds')
