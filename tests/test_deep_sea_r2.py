#!/usr/bin/env python3
"""Production C against frozen approved R2 artwork, not preset app inputs."""
import io,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BUILD=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build-host'
PACK=ROOT/'assets/deep-sea-r2'
cases=[('neutral',0,0,0,0),('left',-.78,0,0,0),('right',.78,0,0,0),('up',0,-.58,0,0),('down',0,.58,0,0),('membrane-half',0,0,.5,0),('closed',0,0,1,1)]
def codes(im):return np.rint(np.asarray(im.convert('RGB')).astype(float)/255*np.array([31,63,31])).astype(int)
reports=[]
for name,gx,gy,membrane,lid in cases:
    args=[str(BUILD/'eye_snapshot'),'1',str(gx),str(gy),str(lid)]
    if membrane!=lid:args += [str(membrane),str(lid)]
    actual=Image.open(io.BytesIO(subprocess.check_output(args)))
    wanted=Image.open(PACK/'evidence/r2'/(name+'.png'))
    delta=np.abs(codes(actual)-codes(wanted))
    # Approved static samples are bit-exact; randomized C arithmetic is also
    # compared against the independent scalar compositor.
    assert delta.max()==0,(name,int(delta.max()))
    reports.append(dict(name=name,max_RGB565_channel_code_delta=int(delta.max()),different_channels=int(np.count_nonzero(delta))))
out=BUILD/'deep-sea-reference.json';out.write_text(json.dumps(reports,indent=2)+'\n')
print('PASS seven approved deep-sea R2 states pixel-exact; exact native C parity is checked separately')
