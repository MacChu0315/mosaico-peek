#!/usr/bin/env python3
"""Build-local frame normalization and same-production-C candidate comparison."""
import io,json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'build-host/frame-candidates';OUT=ROOT/'evidence/mechanical-c/frame-candidates';BUILD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
frames={'A':ROOT/'assets/eye-pack/assets/processed/mechanical/frame.png','B':ROOT/'assets/mechanical-candidates/frame-b-original.png','current':ROOT/json.loads((ROOT/'assets/mechanical-c-adaptation.json').read_text())['fixed_frame_source']}
poses=[('center',0,0,0),('right',.78,0,0),('diagonal',.78,.58,0),('sleep-center',0,0,1),('left',-.78,0,0),('up',0,-.58,0),('down',0,.58,0),('left-up',-.78,-.58,0),('right-up',.78,-.58,0),('left-down',-.78,.58,0)]
checks=[]
for label,path in frames.items():
 im=Image.open(path).convert('RGBA');source_size=list(im.size)
 if im.size!=(480,480):im=im.resize((480,480),Image.Resampling.LANCZOS)
 raw=BUILD/(label+'.rgba');raw.write_bytes(im.tobytes());im.save(BUILD/(label+'-frame.png'))
 for name,gx,gy,blink in poses:
  ppm=subprocess.check_output([str(ROOT/'build-host/frame_candidate_snapshot'),str(raw),str(gx),str(gy),str(blink)])
  picture=Image.open(io.BytesIO(ppm));picture.save(OUT/f'{label}-{name}.png')
  if label=='current':assert ppm==subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),'2',str(gx),str(gy),str(blink)])
 checks.append(dict(candidate=label,source=str(path.relative_to(ROOT)),source_size=source_size,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),render_canvas=[480,480],normalization='Pillow10.4.0 RGBA Lanczos build-only resize' if source_size!=[480,480] else 'none'))
sheet=Image.new('RGB',(4*480,2*520),'#111318');draw=ImageDraw.Draw(sheet)
for row,label in enumerate(['A','B']):
 for col,(name,*_) in enumerate(poses[:4]):
  sheet.paste(Image.open(OUT/f'{label}-{name}.png'),(col*480,row*520));draw.text((col*480+12,row*520+487),f'{label} / {name} / C pose test, not sensor input',fill='white')
sheet.save(OUT/'comparison.png')
(OUT/'manifest.json').write_text(json.dumps(dict(candidates=checks,poses=poses,shader='Production eye_pack.c; only fixed frame substituted in review-only executable',device_installed=False,selected_candidate='A',visual_approval={'A':True,'B':False},scope='A reuses original fixed metal socket; B uses new generated housing. Both preserve new eye/shutter,480 detail and120/80 gaze range. Current-frame substitution matches original snapshot byte-for-byte.'),indent=2)+'\n')
print('PASS current-frame substitution pixel exact; A/B share production C globe/shutter; candidates not installed')
