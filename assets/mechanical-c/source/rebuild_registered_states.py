#!/usr/bin/env python3
"""Recreate the three registered C concept crops from the immutable triptych."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'source/registration.json').read_text())
image=Image.open(ROOT/'assets/originals/concept-C-triptych.png').convert('RGBA')
out=ROOT/'source/registered_states';out.mkdir(exist_ok=True)
for name,state in spec['states'].items():
    s=spec['scale'];cx,cy=state['source_center']
    im=image.transform((480,480),Image.Transform.AFFINE,
        (1/s,0,cx-240/s,0,1/s,cy-245/s),resample=Image.Resampling.BICUBIC)
    im.putalpha(255);im.save(out/f'concept-{name}-480.png')
