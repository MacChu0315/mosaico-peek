#!/usr/bin/env python3
"""Deterministic asset preparation; no model calls, network or project mutation.

The optical region is copied from the selected C concept. Only the peripheral
metal sampling surface comes from the separately generated backing.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'assets/originals'
OUT = ROOT / 'assets/processed'
OUT.mkdir(parents=True, exist_ok=True)
SIZE = (480, 480)
CX, CY = 240, 245
y, x = np.mgrid[:480, :480]
r = np.hypot(x-CX, y-CY)

def save(arr, path):
    im = Image.fromarray(np.asarray(arr, dtype=np.uint8), 'RGBA')
    tmp = path.with_suffix('.tmp.png')
    im.save(tmp, compress_level=9)
    with Image.open(tmp) as check:
        check.verify()
    tmp.replace(path)

approved = np.asarray(Image.open(ROOT/'source/registered_states/concept-open-480.png').convert('RGBA'))
generated = Image.open(RAW/'generated-metal-backing.png').convert('RGBA')
generated = generated.resize((500,500), Image.Resampling.LANCZOS).crop((10,1,490,481))
generated = np.asarray(generated).copy()
generated[...,3] = 255
save(generated, ROOT/'source/generated-metal-registered.png')

# Full lens + retaining optics are copied exactly. Blend is in plain metal only.
t = np.clip((r-184.0)/12.0, 0, 1)
w = (t*t*(3-2*t))[...,None]
surface = np.rint(approved.astype(float)*(1-w)+generated.astype(float)*w).astype(np.uint8)
surface[...,3] = 255
save(surface, OUT/'eye_surface.png')

# Keep only a narrow outer mounting ring. Image-board borders are never copied.
# Frame RGB is premultiplied only when compositing; stored PNG uses straight alpha.
frame = np.zeros((480,480,4), dtype=np.uint8)
frame[...,:3] = approved[...,:3]
inner = np.clip((r-221.0)/1.0,0,1)
outer = np.clip((232.0-r)/1.0,0,1)
# Source-ring contribution fades to opaque black outside radius 232.
frame[...,:3] = np.rint(frame[...,:3]*outer[...,None]).astype(np.uint8)
frame[...,3] = np.rint(inner*255).astype(np.uint8)
frame[frame[...,3]==0,:3] = 0
save(frame, OUT/'frame.png')

preserved = r <= 184
report = {
    'canvas':[480,480], 'eye_center':[CX,CY], 'sphere_radius':233,
    'generation_registration':{'resize':[500,500],'crop':[10,1,490,481]},
    'original_protection':{'center':[CX,CY],'radius':184,'pixels':int(preserved.sum()),
        'changed_pixels':int(np.any(surface[preserved]!=approved[preserved],axis=1).sum())},
    'metal_join_annulus':[184,196],
    'frame':{'transparent_inside_radius':221,'inner_antialias_width':1,
        'source_ring_outer_fade':[231,232], 'opaque_black_outside_radius':232},
    'notes':['This is a new C layer design, not compatible with the old entire-aperture pixel lock.',
        'No fixed frame/eyelid or source-board border is baked into the eye surface.',
        'Native C/GSP and device rendering are not verified.']}
(ROOT/'source/surface-preparation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
