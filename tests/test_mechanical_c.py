#!/usr/bin/env python3
"""New mechanical reference: pre-projection shutter, exact bounds and frame policy."""
import io,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BUILD=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build-host'
sys.path.insert(0,str(ROOT/'assets/mechanical-c/preview'))
from reference_render import Renderer,premultiplied
reference=Renderer();adaptation=json.loads((ROOT/'assets/mechanical-c-adaptation.json').read_text());reference.frame=premultiplied(ROOT/adaptation['fixed_frame_source']);checks=[]
def render(gx,gy,blink):
 raw=subprocess.check_output([str(BUILD/'eye_snapshot'),'2',str(gx),str(gy),str(blink)])
 return np.asarray(Image.open(io.BytesIO(raw)))
def codes(a):return np.rint(a.astype(float)/255*np.array([31,63,31])).astype(int)
for gx in (-.78,0,.78):
 for gy in (-.58,0,.58):
  for stage in range(9):
   actual=render(gx,gy,stage/8);expected=np.asarray(reference.render(gx,gy,stage/8));diff=np.abs(codes(actual)-codes(expected))
   assert diff.max()<=1 and (diff>0).sum()<500,(gx,gy,stage,int(diff.max()),int((diff>0).sum()))
   checks.append(dict(gaze=[gx,gy],stage=stage,max_channel_difference=int(diff.max()),different_channels=int((diff>0).sum())))
for stage in range(8):
 threshold=(stage+.5)/8
 assert np.array_equal(render(.52,-.37,threshold-.0001),render(.52,-.37,stage/8))
 assert np.array_equal(render(.52,-.37,threshold+.0001),render(.52,-.37,(stage+1)/8))
out=BUILD/'mechanical-checks.json';out.write_text(json.dumps(checks,indent=2)+'\n')
print('PASS81 mechanical C direction/stage references;16 nearest-frame boundaries. Float64 reference vs C <=1 RGB565 channel at rounding boundaries, <500 channels/frame.')
