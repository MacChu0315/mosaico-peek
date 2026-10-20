#!/usr/bin/env python3
"""Exercise the running OFFICIAL GSP + native C backend. Never writes UI state via API."""
import json,os,sys,time,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
component=Path(os.environ.get('ESP_GSP_COMPONENT_DIR',ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp'))
sys.path[:0]=[str(component/'tools/sim_bridge'),str(ROOT/'tools')]
from rpc_client import connect
from control import command,state
EVIDENCE=ROOT/'evidence/gsp';EVIDENCE.mkdir(exist_ok=True)
records=[]
def record(label):
    s=state();assert s['error']==0,s;records.append(dict(check=label,**s));return s
def wait_for(test):
    until=time.monotonic()+3
    while time.monotonic()<until:
        if test():return
        time.sleep(.02)
    raise AssertionError('native state timeout')
def main():
    ready=json.loads((ROOT/'.run/ready.json').read_text())
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def call(name,args=None):
            out=api.call(name,args);assert 'result' in out,out;return out['result']
        def capture(name):
            call('wait',{'frames':3});call('screenshot',{'path':str(EVIDENCE/(name+'.png')),'format':'png'})
        caps=call('capabilities');assert caps['runtime_version']=='1.5.1' and caps['width']==caps['height']==480
        (EVIDENCE/'capabilities.json').write_text(json.dumps(caps,indent=2)+'\n')
        command('view diagnostic');command('case 1');capture('initial');record('initial motion paused')
        # Use actual GSP pointer events to exercise button callbacks.
        actions=state()['actions'];call('tap',{'x':240,'y':454})
        wait_for(lambda:state()['actions']==actions+1 and not state()['paused'])
        time.sleep(.25);call('tap',{'x':240,'y':454});wait_for(lambda:state()['paused'])
        before=record('GSP play then pause');time.sleep(.25);after=record('pause freezes injected clock')
        assert before['result']==after['result']
        call('tap',{'x':392,'y':454});wait_for(lambda:state()['result']['now_ms']==0)
        record('GSP replay resets epoch')
        call('tap',{'x':88,'y':454});wait_for(lambda:state()['case']=='multi');record('GSP case selection')
        # Exact 125ms input playback with real GSP renders, no coordinate injection.
        command('case 1')
        video=EVIDENCE/'motion';video.mkdir(exist_ok=True)
        for i in range(80):
            if i:command('advance 125')
            call('wait',{'frames':2})
            call('screenshot',{'path':str(video/f'{i:03d}.png'),'format':'png'})
            s=record(f'motion frame {i}')
            if i in (2,12,30,52,60):capture(f'motion-{i:02d}')
            if 10<=i<56:assert s['result']['target']
        command('case 2');command('advance 4000');s=record('multi holds left');assert s['result']['x']<8;capture('multi-left')
        command('advance 3000');s=record('multi reacquires right');assert s['result']['x']>20;capture('multi-right')
        command('case 3');command('advance 2125');s=record('short missing frames retained');assert s['result']['target']
        command('advance 1250');s=record('before invalid packet');assert s['result']['target']
        command('advance 125');s=record('invalid input clears target');assert s['result']['data']=='INVALID' and not s['result']['target'];capture('invalid')
        command('advance 625');assert record('new-frame recovery')['result']['target']
        command('advance 1500');s=record('sustained outage invalidates');assert s['result']['data']=='STALE' and not s['result']['target'];capture('stale')
        command('case 1');command('advance 3000');one=state()['result'];command('replay');command('advance 3000');two=state()['result'];assert one==two;record('native replay deterministic')
        # Paused redraws must not add samples, confirmations or sample timestamps.
        before=state()
        for _ in range(5):
            command('draw');call('wait',{'frames':3})
        time.sleep(.1);after=state()
        assert after['draws']>=before['draws']+5,(before,after)
        assert before['result']==after['result'];record('redraw leaves detector unchanged')
        command('case 4');command('advance 1000');s=record('recorded sparse gap preserved');assert s['result']['data']=='STALE';capture('recorded-sparse')
        command('case 0');command('advance 9875');s=record('empty stays empty');assert s['result']['data']=='VALID' and not s['result']['target'];capture('empty')
        # CLI, replay_until and native pump must expose the same aged result.
        expected=[json.loads(line) for line in subprocess.check_output([str(ROOT/'build-host/peek_replay'),str(ROOT/'data/aging.peek')],text=True).splitlines()]
        until=[json.loads(line) for line in subprocess.check_output([str(ROOT/'build-host/peek_replay_until'),str(ROOT/'data/aging.peek')],text=True).splitlines()]
        assert {r['now_ms']:r for r in expected}=={r['now_ms']:r for r in until}
        command('case 5');previous=0
        for target in (600,725,850,1000):
            command(f'advance {target-previous}');previous=target
            s=record(f'aging equivalence at {target}')
            assert s['result']==next(r for r in expected if r['now_ms']==target),(s,expected)
        command('case 1');command('advance 4000');capture('handoff-stationary')
    (EVIDENCE/'checks.json').write_text(json.dumps(records,indent=2)+'\n')
    print(f'PASS GSP: {len(records)} checks; pointer controls, pause/replay, native detection and actual rendered frames')
if __name__=='__main__':main()
