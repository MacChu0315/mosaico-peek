#!/usr/bin/env python3
"""Actual native sleep/wake acceptance; temperature arrays drive production C."""
import json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=ROOT/'evidence/sleep-performance/native';OUT.mkdir(parents=True,exist_ok=True)
def main():
    ready=json.loads((ROOT/'.run/ready.json').read_text());checks=[];frames=[]
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def advance(at):command(f'advance {at-state()["result"]["now_ms"]}')
        def capture(name):
            waited=api.call('wait',{'frames':2});assert 'error' not in waited
            reply=api.call('screenshot',{'path':str(OUT/(name+'.png')),'format':'png'});assert 'error' not in reply
            s=state();assert not s['error'];frames.append(dict(name=name,state=s));return s
        command('case sleep')
        for at,name in [(9950,'awake-idle'),(10225,'closing'),(10450,'asleep'),(12000,'candidate-not-acquired'),(12250,'wake-start'),(12325,'opening'),(12400,'awake-follow'),(16000,'held-follow'),(19500,'idle-again'),(30000,'asleep-again')]:
            advance(at);s=capture(name);r=s['role'];p=r['pose'];checks.append(dict(at=at,name=name,state=s))
            if name=='awake-idle':assert r['mode']=='IDLE' and not r['sleeping']
            if name=='closing':assert r['sleeping'] and 0<p['blink']<1
            if name in ('asleep','candidate-not-acquired','asleep-again'):assert r['sleeping'] and p['blink']==1 and not s['result']['target']
            if name=='wake-start':assert r['waking'] and not r['sleeping'] and p['blink']==1 and s['result']['target']
            if name=='opening':assert r['waking'] and 0<p['blink']<1
            if name=='awake-follow':assert not r['waking'] and p['blink']==0 and s['result']['target']
        command('replay');advance(12325);first=state();command('draw');assert first['role']==state()['role']
        command('replay');advance(12325);second=state();assert first['role']==second['role'] and first['result']==second['result']
        command('case sleep');command('play');start=time.monotonic();next_capture=start;records=[];captures=[]
        live=ROOT/'.run/sleep-live';live.mkdir(exist_ok=True)
        while time.monotonic()-start<38:
            s=state();assert not s['error'];records.append(dict(wall_s=time.monotonic()-start,**s))
            if time.monotonic()>=next_capture:
                file=live/f'{len(captures):04d}.png';reply=api.call('screenshot',{'path':str(file),'format':'png'});assert 'error' not in reply
                captures.append(dict(file=file.name,wall_s=time.monotonic()-start,logical_ms=s['result']['now_ms']));next_capture=time.monotonic()+.125
            if s['eof']:break
            time.sleep(.025)
        assert s['eof'];assert any(r['role']['sleeping'] for r in records) and any(r['role']['waking'] for r in records)
        assert any(r['result']['target'] and not r['role']['sleeping'] for r in records)
        report=dict(checkpoints=len(checks),wall_s=time.monotonic()-start,all_complete_arrays=True,pause_pure=True,replay_identical=True,screenshot_count=len(captures),note='Actual native C/GSP pixels from synthetic temperature arrays. Encoded8fps is presentation of sampled screenshots, not runtime or physical FPS.')
        for name,v in [('checks.json',checks),('frames.json',frames),('live-states.json',records),('live-captures.json',captures),('report.json',report)]: (OUT/name).write_text(json.dumps(v,indent=2)+'\n')
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','8','-i',str(live/'%04d.png'),'-frames:v',str(len(captures)),'-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'sleep-live.mp4')],check=True)
        print(json.dumps(report,indent=2))
if __name__=='__main__':main()
