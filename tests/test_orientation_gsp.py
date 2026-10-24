#!/usr/bin/env python3
"""Verify the real GSP canvas output under deterministic four-way rotation."""
import ctypes, io, json, os, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parents[1]
component=Path(os.environ.get('ESP_GSP_COMPONENT_DIR',ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp'))
sys.path[:0]=[str(component/'tools/sim_bridge'),str(ROOT/'tools')]
from rpc_client import connect
from control import command,state
out=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'.run/orientation'));out.mkdir(parents=True,exist_ok=True)
checks=[]
ready=json.loads((ROOT/'.run/ready.json').read_text())
with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
    def call(name,args=None):
        reply=api.call(name,args);assert 'result' in reply,reply;return reply['result']
    def capture(name):
        call('wait',{'frames':3})
        path=out/(name+'.png');call('screenshot',{'path':str(path),'format':'png'})
        return Image.open(path).convert('RGB')
    def f32(value):return ctypes.c_float(value).value
    def verify_pixels(theme,angle,actual,s):
        p=dict(s['role']['pose']);x=f32(p['gaze_x']);y=f32(p['gaze_y'])
        if theme=='mechanical' and (s['role']['sleeping'] or s['role']['waking']):
            follow=max(0,f32(1-f32(f32(p['blink'])/f32(7.5/8))));x=f32(x*follow);y=f32(y*follow)
        p['gaze_x'],p['gaze_y']=x,y
        horizontal=f32(f32(.78)/f32(.58));vertical=f32(f32(.58)/f32(.78))
        if angle==90:p['gaze_x'],p['gaze_y']=f32(y*horizontal),f32(-x*vertical)
        if angle==180:p['gaze_x'],p['gaze_y']=-x,-y
        if angle==270:p['gaze_x'],p['gaze_y']=f32(-y*horizontal),f32(x*vertical)
        assert f32(s['render_pose']['gaze_x'])==p['gaze_x'] and f32(s['render_pose']['gaze_y'])==p['gaze_y'],('presentation telemetry',theme,angle)
        if theme=='dragon':
            args=['dragon_snapshot',*[str(p[k]) for k in ('gaze_x','gaze_y','blink','squint','pupil_width','tension')]]
        else:args=['eye_snapshot',str(['night_owl','deep_sea','mechanical'].index(theme)),str(p['gaze_x']),str(p['gaze_y']),str(p['blink'])]
        if theme=='deep_sea':args += [str(s['render_layers']['membrane']),str(s['render_layers']['lid'])]
        ppm=subprocess.check_output([str(ROOT/'build-host'/args[0]),*args[1:]])
        reference=Image.open(io.BytesIO(ppm)).convert('RGB')
        if theme=='dragon' and s['sample_step']==2:
            reference=reference.resize((240,240),Image.Resampling.NEAREST).resize((480,480),Image.Resampling.NEAREST)
        if angle:reference=reference.transpose({90:Image.Transpose.ROTATE_270,180:Image.Transpose.ROTATE_180,270:Image.Transpose.ROTATE_90}[angle])
        lut=[(i*maximum+127)//255 for maximum in (31,63,31) for i in range(256)]
        assert ImageChops.difference(reference.point(lut),actual.point(lut)).getbbox() is None,(theme,angle,s['role']['mode'])
        checks.append(dict(theme=theme,angle=angle,state=s))
    for theme in ['dragon','night_owl','deep_sea','mechanical']:
        command('orientation 0');command('view '+theme);command('case idle');command('advance 1200')
        baseline=state();verify_pixels(theme,0,capture(theme+'-0'),baseline)
        for angle,transpose in [(90,Image.Transpose.ROTATE_270),(180,Image.Transpose.ROTATE_180),(270,Image.Transpose.ROTATE_90)]:
            command('orientation '+str(angle));actual=capture(theme+'-'+str(angle));after=state()
            assert after['error']==0 and after['orientation']==angle,after
            assert after['result']==baseline['result'] and after['role']==baseline['role']
            verify_pixels(theme,angle,actual,after)
        command('case motion');command('advance 3000');baseline=state()
        assert baseline['result']['target']
        for angle in (0,90,180,270):
            command('orientation '+str(angle));actual=capture(theme+'-target-'+str(angle));after=state()
            verify_pixels(theme,angle,actual,after)
            assert after['error']==0 and after['result']==baseline['result'] and after['role']==baseline['role']
        command('replay');assert state()['orientation']==270
    command('view mechanical');command('case sleep')
    for at in (10450,12325):
        command('advance '+str(at-state()['result']['now_ms']));baseline=state()
        for angle in (0,90,180,270):
            command('orientation '+str(angle));actual=capture('mechanical-sleep-'+str(at)+'-'+str(angle));after=state();verify_pixels('mechanical',angle,actual,after)
            assert after['role']==baseline['role'] and after['result']==baseline['result']
    command('view deep_sea');command('case sleep')
    for at in (6090,10450,12325):
        command('advance '+str(at-state()['result']['now_ms']));baseline=state()
        for angle in (0,90,180,270):
            command('orientation '+str(angle));actual=capture('deep-sea-layers-'+str(at)+'-'+str(angle));after=state();verify_pixels('deep_sea',angle,actual,after)
            assert after['role']==baseline['role'] and after['result']==baseline['result'] and after['render_layers']==baseline['render_layers']
    command('orientation 0');command('view dragon')
(out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print('PASS GSP:',len(checks),'image comparisons; four-way idle/target/centered-sleep/wake; source unchanged and render telemetry exact')
