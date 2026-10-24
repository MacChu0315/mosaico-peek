#!/usr/bin/env python3
"""Actual native GSP layers from synthetic complete temperature arrays."""
import io,json,os,subprocess,sys
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'evidence/deep-sea-r2/native-phases'));OUT.mkdir(parents=True,exist_ok=True)
THEME=os.environ.get('PEEK_LAYER_THEME','deep_sea');assert THEME in ('night_owl','deep_sea');INDEX='0' if THEME=='night_owl' else '1'
ready=json.loads((ROOT/'.run/ready.json').read_text());checks=[]
with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
    def call(name,args=None):
        r=api.call(name,args);assert 'result' in r,r;return r['result']
    command('view '+THEME);command('orientation 0');command('case sleep')
    for at,m,l in [(6000,0,0),(6020,0,0),(6070,.5,0),(6120,1,0),(6140,1,0),(6200,.5,0),(6260,0,0),(10000,0,0),(10050,.5,0),(10100,1,0),(10275,1,.5),(10450,1,1),(12000,1,1),(12250,1,1),(12325,1,1-75/97.5),(12350,50/52.5,0),(12400,0,0)]:
        command('advance '+str(at-state()['result']['now_ms']));call('wait',{'frames':3});s=state()
        assert abs(s['render_layers']['membrane']-m)<2e-6 and abs(s['render_layers']['lid']-l)<2e-6,(at,s['render_layers'],m,l)
        p=s['render_pose'];file=OUT/f'{at:05}.png';call('screenshot',dict(path=str(file),format='png'))
        raw=subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),INDEX,str(p['gaze_x']),str(p['gaze_y']),str(p['blink']),str(s['render_layers']['membrane']),str(s['render_layers']['lid'])])
        expected=Image.open(io.BytesIO(raw)).convert('RGB');actual=Image.open(file).convert('RGB');lut=[(i*n+127)//255 for n in (31,63,31) for i in range(256)]
        assert ImageChops.difference(expected.point(lut),actual.point(lut)).getbbox() is None,at
        checks.append(dict(at=at,state=s))
        if at==6260:assert s['role']['pose']['blink']>0 and s['render_layers']=={'membrane':0,'lid':0}
        if at==6120:
            before=state();command('draw');call('wait',{'frames':3});after=state();assert before['result']==after['result'] and before['role']==after['role'] and before['render_layers']==after['render_layers']
            for name in ('night_owl','deep_sea','mechanical','dragon',THEME):command('view '+name);assert before['result']==state()['result'] and before['role']==state()['role']
            assert state()['render_layers']==before['render_layers']
    (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    # Repeat the same injected animation ticks as well as the same sensor events.
    # A single large advance is a different schedule for the existing NOTICE
    # tension/squint easing; it cannot be used as a full-pose identity oracle.
    command('replay')
    for checkpoint in checks:
        command('advance '+str(checkpoint['at']-state()['result']['now_ms']));s=state();expected=checkpoint['state']
        assert s['result']==expected['result'] and s['role']==expected['role'] and s['render_layers']==expected['render_layers']
(OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('PASS17 real GSP layer checkpoints;240ms pulse,450/150ms close/wake,paused redraw,switch/replay source invariance')
