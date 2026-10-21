#!/usr/bin/env python3
"""Compare same thermal-array native checkpoints across the mapping correction."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=json.loads((ROOT/'evidence/eye-ui/performance/native/native-checks.json').read_text())[0]['state']
b=json.loads((ROOT/'evidence/eye-ui/motion/native-switch/native-checks.json').read_text())[0]['state']
assert a['flip_x'] and a['flip_y'] and not b['flip_x'] and not b['flip_y']
assert a['result']==b['result']
for key in ['mode','stationary','sleeping','waking']:
    assert a['role'][key]==b['role'][key]
for axis in ['x','y']:
    assert a['role']['pose']['gaze_'+axis]<0<b['role']['pose']['gaze_'+axis]
for key in ['blink','squint','pupil_width','tension']:
    assert a['role']['pose'][key]==b['role']['pose'][key]
print('PASS native87-sample checkpoint: identical raw detector result/state; both gaze signs reversed, other pose channels unchanged. Physical direction acceptance remains separate.')
