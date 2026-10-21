#!/usr/bin/env python3
"""Actual native GSP acceptance, controlled checkpoints plus >=60s live idle.
Videos use live API screenshot samples; wall-time/callback metrics are separate.
"""
import argparse,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(Path(os.environ.get('ESP_GSP_COMPONENT_DIR',ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp'))/'tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=ROOT/'evidence/phase2/dragon';OUT.mkdir(parents=True,exist_ok=True)
checks=[]
frames=[]
def checked(label):
    s=state();assert s['error']==0,s;checks.append(dict(check=label,**s));return s

def main():
    p=argparse.ArgumentParser();p.add_argument('--idle-seconds',type=float,default=61);p.add_argument('--skip-live',action='store_true');args=p.parse_args()
    ready=json.loads((ROOT/'.run/ready.json').read_text())
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def call(method,params=None):
            result=api.call(method,params);assert 'result' in result,result;return result['result']
        def capture(name):
            call('wait',{'frames':2});call('screenshot',{'path':str(OUT/(name+'.png')),'format':'png'});frames.append(dict(name=name,state=state()))
        def advance_to(at):
            current=state()['result']['now_ms'];assert at>=current
            command(f'advance {at-current}')
        command('view dragon');command('case dragon');capture('native-rest');checked('initial actual native dragon')
        for at,name in [(2250,'notice'),(3200,'track-left'),(4800,'track-right'),(6250,'track-up'),(8750,'track-down'),(11000,'hold-start'),(15000,'held'),(15250,'leave'),(15800,'reappear'),(18125,'invalid'),(19000,'recover-pending'),(19875,'recover'),(22750,'stale'),(25000,'recover-again')]:
            advance_to(at);s=checked(name);capture(name)
            r=s['result'];role=s['role']
            if name=='notice':assert role['mode']=='NOTICE' and r['target']
            if name=='held':assert r['held'] and role['observation_held'] and not role['stationary'] and role['mode']!='HOLD'
            if name=='invalid':assert r['data']=='INVALID' and not r['target'] and role['mode']=='LEAVE'
            if name=='stale':assert r['data']=='STALE' and not r['target']
        # HOLD persists for more than 4 s with fresh samples (scene stillness starts at 9s).
        command('case dragon');advance_to(10750);one=checked('hold 0');assert one['role']['mode']=='HOLD'
        advance_to(14875);two=checked('hold after 4.125 seconds');assert two['role']['mode']=='HOLD' and two['role']['observations']>one['role']['observations']
        assert abs(two['role']['pose']['gaze_x']-one['role']['pose']['gaze_x'])<.02
        advance_to(15250);left=checked('leave pose before reappearance');advance_to(15750);again=checked('one new notice on reappearance')
        assert again['role']['mode']=='NOTICE' and again['role']['notices']==left['role']['notices']+1
        command('pause');before=checked('paused');time.sleep(.2)
        for _ in range(5):command('draw');call('wait',{'frames':3})
        after=checked('five real dragon redraws');assert after['draws']>=before['draws']+5
        assert before['result']==after['result'] and before['role']==after['role']
        command('step');stepped=checked('single actual input step');assert stepped['result']['samples']==before['result']['samples']+1
        command('case dragon');advance_to(13000);first=state();command('replay');advance_to(13000);second=checked('full replay determinism')
        assert first['result']==second['result'] and first['role']==second['role']
        # Closed/reopening at an extreme real detected gaze, including eyelid overlap.
        command('case dragon');advance_to(6160);assert state()['role']['pose']['blink']==1;capture('extreme-closed');checked('extreme gaze fully closed')
        advance_to(6300);capture('extreme-reopen');checked('extreme gaze reopening')
        command('case idle');advance_to(6180);capture('native-closed');checked('idle fully closed')
        advance_to(6300);capture('native-reopen');checked('idle reopening')
        if not args.skip_live:
            assert args.idle_seconds>=60
            live=[]
            def memory():
                info={}
                try:
                    parent=int(next(l for l in Path(f'/proc/{ready["pid"]}/status').read_text().splitlines() if l.startswith('PPid:')).split()[1])
                    ids=Path(f'/proc/{parent}/task/{parent}/children').read_text().split()
                    for pid in ids:
                        cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode()
                        status=Path(f'/proc/{pid}/status').read_text().splitlines()
                        info['backend' if Path(cmd.split()[0]).name=='peek_backend' else 'simulator']={line.split(':')[0]:line.split(':',1)[1].strip() for line in status if line.startswith(('VmRSS:','VmHWM:'))}
                except (OSError,StopIteration,ValueError):pass
                return info
            def run_live(case,duration):
                command('case '+case);before=state();start=time.monotonic();command('play');next_capture=start;records=[];captures=[];frames=ROOT/'.run'/('live-'+case);frames.mkdir(exist_ok=True)
                while time.monotonic()-start<duration:
                    s=state();assert s['error']==0,s
                    elapsed=time.monotonic()-start;records.append(dict(wall_s=elapsed,result=s['result'],role=s['role'],draws=s['draws'],render=s['render']))
                    if case=='idle':assert s['role']['mode']=='IDLE' and not s['result']['target']
                    if time.monotonic()>=next_capture:
                        path=frames/f'{len(captures):04d}.png';call('screenshot',{'path':str(path),'format':'png'})
                        captures.append({'file':path.name,'wall_s':time.monotonic()-start,'logical_ms':s['result']['now_ms']});next_capture+=.125
                        # Avoid a catch-up burst after an API/OS scheduling stall.
                        if next_capture<time.monotonic()-.125:next_capture=time.monotonic()+.125
                    time.sleep(.015)
                command('pause');after=state();elapsed=time.monotonic()-start
                metrics={'case':case,'wall_seconds':elapsed,'logical_ms':after['result']['now_ms'],'callback_count':after['draws']-before['draws'],'canvas_callback_hz':(after['draws']-before['draws'])/elapsed,'equivalent_full_canvas_hz':(after['render']['pixels']-before['render']['pixels'])/(480*480)/elapsed,'draw_us_mean':(after['render']['draw_us_total']-before['render']['draw_us_total'])/max(1,after['draws']-before['draws']),'draw_us_max_session':after['render']['draw_us_max'],'screenshot_count':len(captures),'memory':memory(),'evidence_method':'Live official GSP API screenshots, sampled on wall clock; encoded video does not independently establish real-time performance or device FPS.'}
                (OUT/f'{case}-live.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records));(OUT/f'{case}-captures.json').write_text(json.dumps(captures,indent=2)+'\n')
                if case=='idle':assert after['role']['sleeping'] and after['role']['pose']['blink']==1 and elapsed>=60 and after['result']['samples']>470
                else:
                    modes={r['role']['mode'] for r in records};assert {'IDLE','NOTICE','TRACKING','HOLD','LEAVE'}<=modes
                    assert any(r['result']['data']=='INVALID' for r in records) and any(r['result']['data']=='STALE' for r in records)
                live.append(metrics);print('LIVE',json.dumps(metrics),flush=True)
            run_live('idle',args.idle_seconds);run_live('dragon',30.5)
            (OUT/'live-metrics.json').write_text(json.dumps(live,indent=2)+'\n')
        (OUT/'frames.json').write_text(json.dumps(frames,indent=2)+'\n')
        (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(f'PASS dragon GSP: {len(checks)} controlled checkpoints; native captures and sample/time purity',flush=True)
if __name__=='__main__':main()
