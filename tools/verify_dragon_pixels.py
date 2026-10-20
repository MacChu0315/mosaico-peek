#!/usr/bin/env python3
"""Verify retained actual GSP frames against full C raster and independent aperture geometry."""
import io,json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def bezier(points,t):
    u=1-t;w=[u**3,3*u*u*t,3*u*t*t,t**3]
    return tuple(sum(w[i]*points[i][j] for i in range(4)) for j in range(2))
def mask(p):
    b=p['blink'];s=p['squint'];t=p['tension'];mix=lambda a,z:a*(1-b)+z*b
    left=(-214,8);right=(214,-8);top=158-s*55-t*7;low=186-s*19
    upper=[left,(-135,mix(-top,30)),(61,mix(-top*1.19,43)),right]
    lower=[right,(mix(130,61),mix(low,43)),(mix(-91,-135),mix(low*1.04,30)),left]
    points=[]
    for curve in (upper,lower):
        for i in range(301):
            x,y=bezier(curve,i/300);points.append((240+math.cos(-.16)*x-math.sin(-.16)*y,247+math.sin(-.16)*x+math.cos(-.16)*y))
    out=Image.new('1',(480,480));ImageDraw.Draw(out).polygon(points,fill=1);return out

def main():
    root=ROOT/'evidence/phase2/dragon';records=json.loads((root/'frames.json').read_text());report=[]
    for item in records:
        p=item['state']['role']['pose'];path=root/(item['name']+'.png');actual=Image.open(path).convert('RGB');assert actual.size==(480,480)
        raw=subprocess.check_output([str(ROOT/'build-host/dragon_snapshot'),*[str(p[k]) for k in ('gaze_x','gaze_y','blink','squint','pupil_width','tension')]])
        full=Image.open(io.BytesIO(raw)).convert('RGB');aperture=mask(p);bright=outside=changed=0
        for i,(a,e) in enumerate(zip(actual.getdata(),full.getdata())):
            qa=(a[0]>>3,a[1]>>2,a[2]>>3);qe=(e[0]>>3,e[1]>>2,e[2]>>3)
            # Nine significant decimal digits round-trip the C float pose.
            if qa!=qe:changed+=1
            if a[0]>80 and a[1]>75 and a[2]*2<a[0] and a[2]*2<a[1]:
                bright+=1
                if not aperture.getpixel((i%480,i//480)):outside+=1
        assert changed==0,(item['name'],'full-raster mismatch',changed)
        assert outside==0,(item['name'],'iris outside independent aperture',outside)
        if p['blink']==1:assert bright==0,(item['name'],'incomplete closure',bright)
        report.append({'name':item['name'],'blink':p['blink'],'bright_iris_pixels':bright,'bright_outside_aperture':outside,'RGB565_pixels_differing_from_full_C_raster':changed,'note':'nine-digit exported C float pose; all230400 RGB565 pixels must match'})
    (root/'pixel-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS {len(report)} retained native GSP frames: full-raster parity, independent aperture mask, real closed-eye pixels')
if __name__=='__main__':main()
