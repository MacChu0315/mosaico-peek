#!/usr/bin/env python3
"""Actual native pixels must equal the approved odd-center2x2 sample policy."""
import io,json,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from verify_dragon_pixels import mask
OUT=ROOT/'evidence/sampling240/native'
def main():
    records=json.loads((OUT/'frames.json').read_text());report=[]
    for item in records:
        p=item['state']['role']['pose'];assert item['state']['sample_step']==2
        raw=subprocess.check_output([str(ROOT/'build-host/dragon_snapshot'),*[str(p[k]) for k in ('gaze_x','gaze_y','blink','squint','pupil_width','tension')]])
        reference=Image.open(io.BytesIO(raw)).convert('RGB');actual=Image.open(OUT/(item['name']+'.png')).convert('RGB');assert actual.size==(480,480)
        ref=reference.load();aperture=mask(p);changed=outside=bright=0
        for i,a in enumerate(actual.getdata()):
            x=i%480;y=i//480;sx=x|1;sy=y|1;e=ref[sx,sy]
            changed+=(a[0]>>3,a[1]>>2,a[2]>>3)!=(e[0]>>3,e[1]>>2,e[2]>>3)
            if a[0]>80 and a[1]>75 and a[2]*2<a[0] and a[2]*2<a[1]:
                bright+=1;outside+=not aperture.getpixel((sx,sy))
        assert changed==outside==0,(item['name'],changed,outside)
        if p['blink']==1:assert bright==0
        report.append(dict(name=item['name'],pixels=230400,RGB565_mismatches=changed,bright_outside_sampled_aperture=outside,bright_pixels=bright))
    (OUT/'pixel-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS {len(records)} actual native GSP frames x230400 pixels: exact approved2x2 rule, sampled aperture and full closure')
if __name__=='__main__':main()
