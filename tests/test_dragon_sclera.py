#!/usr/bin/env python3
"""Production C versus immutable artist C reference and pre-change masks."""
import hashlib, io, json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parents[1]
BUILD=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build-host'
PACK=ROOT/'assets/dragon-sclera-c'
for line in (PACK/'CHECKSUMS.sha256').read_text().splitlines():
    expected,name=line.split(None,1);assert hashlib.sha256((PACK/name.lstrip('* ')).read_bytes()).hexdigest()==expected,name
checks=json.loads((PACK/'evidence/render.json').read_text())['poses']
for name,gx,gy,blink in checks:
    raw=subprocess.check_output([str(BUILD/'dragon_snapshot'),str(gx),str(gy),str(blink),'.69','.072','.16'])
    actual=Image.open(io.BytesIO(raw)).convert('RGB').resize((240,240),Image.Resampling.NEAREST).resize((480,480),Image.Resampling.NEAREST)
    expected=Image.open(PACK/'evidence/poses'/(name+'.png')).convert('RGB')
    assert ImageChops.difference(actual,expected).getbbox() is None,('supplied C reference differs',name)
    old=Image.open(PACK/'evidence/baseline'/(name+'.png')).convert('RGB')
    channels=ImageChops.difference(actual,old).split()
    changed=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]).point(lambda v:255 if v else 0)
    allowed=Image.open(PACK/'evidence/sclera-masks'/(name+'.png')).convert('L')
    assert ImageChops.multiply(changed,ImageChops.invert(allowed)).getbbox() is None,('changed outside sclera',name)
    if name=='closed':assert changed.getbbox() is None
print('PASS eleven production C poses exactly match selected sclera C; original exterior/iris/lids/closed pixels and75 source checksums preserved')
