#!/usr/bin/env python3
"""Exercise the exported standalone art contract; does not modify its references."""
import importlib.util,io,json,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PACK=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'review/eye-surface-art-handoff-v1'
spec=importlib.util.spec_from_file_location('art_reference',PACK/'reference_renderer.py');renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer);renderer.GENERATED=PACK/'rejected'
themes=json.loads((PACK/'reference/source_pack/assets/manifest.json').read_text())['themes'];count=0
for i,t in enumerate(themes):
 for gx in [-.78,0,.78]:
  for gy in [-.58,0,.58]:
   pixels=np.asarray(Image.open(io.BytesIO(subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),str(i),str(gx),str(gy),'0']))))
   codes=np.rint(pixels/255*np.array([31,63,31])).astype(int);expected=renderer.oracle(t,gx,gy,0);delta=np.abs(codes-expected)
   assert delta.max()<=1 and (delta>0).sum()<500;count+=1
with tempfile.TemporaryDirectory(prefix='peek-art-contract-') as tmp:
 folder=Path(tmp);(folder/'input/mechanical').mkdir(parents=True);source=Image.open(PACK/'rejected/mechanical/eye_surface.png').convert('RGBA')
 variants={'size':source.resize((479,480)),'alpha':source.copy(),'locked':source.copy()}
 variants['alpha'].putpixel((0,0),(0,0,0,0));locked=np.asarray(Image.open(PACK/'guides/mechanical/locked_mask.png'))>0;y,x=np.argwhere(locked)[0];p=list(source.getpixel((int(x),int(y))));p[0]^=1;variants['locked'].putpixel((int(x),int(y)),tuple(p))
 for name,im in variants.items():
  im.save(folder/'input/mechanical/eye_surface.png')
  r=subprocess.run([sys.executable,str(PACK/'check_preview.py'),'--input',str(folder/'input'),'--output',str(folder/name),'--theme','mechanical'],capture_output=True,text=True)
  assert r.returncode!=0 and {'size':'expected RGBA8','alpha':'fully opaque','locked':'locked pixels changed'}[name] in r.stderr,(name,r.stdout,r.stderr)
print(f'PASS standalone handoff: {count} direction renders match C within1 RGB565 rounding code; malformed size, alpha and locked-pixel edits rejected. No visual approval claimed.')
