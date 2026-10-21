#!/usr/bin/env python3
"""Real GSP pointer routing; the native app remains driven by temperature arrays."""
import hashlib,io,json,os,subprocess,sys,time
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'evidence/eye-ui/switching'));OUT.mkdir(parents=True,exist_ok=True)
THEMES=['dragon','night_owl','deep_sea','mechanical']
def main():
    ready=json.loads((ROOT/'.run/ready.json').read_text());checks=[]
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def call(method,params=None):
            r=api.call(method,params);assert 'result' in r,r;return r['result']
        caps=call('capabilities');assert caps['bridge_pointer_version']==1
        command('view dragon');command('case dragon');command('advance 10750');initial=state()
        def settle(expected,label):
            deadline=time.monotonic()+3
            while state()['view']!=expected and time.monotonic()<deadline:time.sleep(.01)
            call('wait',{'frames':3});s=state();assert s['view']==expected and not s['error'],(label,s)
            assert s['result']==initial['result'] and s['role']==initial['role'],label
            assert s['flip_x']==initial['flip_x'] and s['flip_y']==initial['flip_y'] and s['paused']
            checks.append(dict(label=label,state=s));return s
        def pointer(x,y,pressed):
            call('feed_pointer',dict(x=x,y=y,pressed=pressed));call('wait',{'frames':2})
        def tap(x,y):
            pointer(x,y,True);pointer(x,y,False)
        def drag(x1,y1,x2,y2):
            pointer(x1,y1,True)
            for i in range(1,5):pointer(round(x1+(x2-x1)*i/4),round(y1+(y2-y1)*i/4),True)
            pointer(x2,y2,False)
        def capture(name):
            s=state();file=OUT/(name+'.png');call('screenshot',dict(path=str(file),format='png'));p=s['role']['pose']
            if s['view']=='dragon':
                ppm=subprocess.check_output([str(ROOT/'build-host/dragon_snapshot'),*[str(p[k]) for k in ['gaze_x','gaze_y','blink','squint','pupil_width','tension']]])
                expected=np.asarray(Image.open(io.BytesIO(ppm)));expected=np.repeat(np.repeat(expected[1::2,1::2],2,axis=0),2,axis=1)
            else:
                ppm=subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),str(THEMES.index(s['view'])-1),str(p['gaze_x']),str(p['gaze_y']),str(p['blink'])]);expected=np.asarray(Image.open(io.BytesIO(ppm)))
            actual=np.asarray(Image.open(file).convert('RGB'));codes=lambda a:np.rint(a.astype(float)/255*np.array([31,63,31])).astype(int)
            assert np.array_equal(codes(expected),codes(actual)),name
        tap(240,240);settle('night_owl','tap advances');capture('night-owl-after-tap')
        pointer(240,240,True);pointer(246,245,True);pointer(246,245,False);settle('deep_sea','tap jitter advances');capture('deep-sea-after-tap')
        before=state()['actions'];pointer(400,240,True);pointer(200,240,True);assert state()['view']=='deep_sea';pointer(80,240,False)
        s=settle('mechanical','left swipe advances once');assert s['actions']==before+1;capture('mechanical-after-swipe')
        pointer(80,240,False);assert settle('mechanical','duplicate up ignored')['actions']==before+1
        drag(80,240,400,240);settle('deep_sea','right swipe goes back')
        tap(240,240);settle('mechanical','tap3');tap(240,240);settle('dragon','forward wrap');capture('dragon-after-wrap')
        drag(80,240,400,240);settle('mechanical','backward wrap')
        pointer(240,100,True);pointer(240,300,False);settle('mechanical','vertical drag ignored')
        pointer(240,240,True);pointer(340,240,True);pointer(240,240,False);settle('mechanical','drag return is not tap')
        pointer(240,240,True);time.sleep(.7);pointer(240,240,False);settle('mechanical','long hold ignored')
        pointer(240,240,True);command('view deep_sea');pointer(240,240,False);settle('deep_sea','view change cancels old touch')
        command('view diagnostic');pointer(88,454,True);command('view dragon');pointer(88,454,False);settle('dragon','hidden diagnostic click cannot reset source')
        command('next');settle('night_owl','shared next command');command('previous');settle('dragon','shared previous command')
        command('case sleep');command('advance 10450');asleep=state();assert asleep['role']['sleeping']
        tap(240,240);call('wait',{'frames':3});s=state();assert s['view']=='night_owl' and s['role']==asleep['role'] and s['result']==asleep['result']
        checks.append(dict(label='tap changes artwork without waking sleep',state=s))
        command('replay');command('advance 10450');assert state()['role']==asleep['role'] and state()['result']==asleep['result']
    artifacts={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'build-sim/peek_backend',ROOT/'build-sim/peek_backend_assets/app.gspb',ROOT/'build-sim/peek_backend_assets/bundle_gsp.api.json']}
    (OUT/'native-checks.json').write_text(json.dumps(checks,indent=2)+'\n');(OUT/'native-report.json').write_text(json.dumps(dict(checks=len(checks),capabilities=caps,artifacts=artifacts,note='Actual official GSP native pointer routing. BSP AI binding/concurrent handoff is covered by production-code Host fixtures; hardware inputs untested until installation.'),indent=2)+'\n');print('PASS native GSP:',len(checks),'input checks; four exact-pixel artwork captures; detector/role/time unchanged')
if __name__=='__main__':main()
