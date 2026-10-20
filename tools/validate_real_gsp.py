#!/usr/bin/env python3
"""Wall-clock native GSP run of all exact recorded events, sampled at 4 Hz."""
import json,sys,time,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=ROOT/'evidence/real-input';FRAMES=ROOT/'.run/real-live';FRAMES.mkdir(exist_ok=True)
def main():
    ready=json.loads((ROOT/'.run/ready.json').read_text())
    command('view dragon');command('case live');command('play');begin=time.monotonic();next_capture=begin;captures=[];states=[]
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        while time.monotonic()-begin<75:
            s=state();assert not s['error'];states.append(dict(wall_s=time.monotonic()-begin,**s))
            if time.monotonic()>=next_capture:
                path=FRAMES/f'{len(captures):04d}.png';reply=api.call('screenshot',{'path':str(path),'format':'png'});assert 'error' not in reply
                captures.append(dict(file=path.name,wall_s=time.monotonic()-begin,logical_ms=s['result']['now_ms']));next_capture+=.25
            if s['eof']:break
            time.sleep(.025)
    assert s['eof'] and s['result']['samples']==511 and s['result']['sequence']==511
    actual=[json.loads(x) for x in (ROOT/'.run/live-events.jsonl').read_text().splitlines()]
    expected=[json.loads(x) for x in (OUT/'role-output.jsonl').read_text().splitlines()]
    assert len(actual)==len(expected)==655
    for a,e in zip(actual,expected):
        assert a['result']==e['result'],(a,e)
        assert (a['role'],a['stationary'],a['observations'])==(e['role'],e['stationary'],e['observations']),(a,e)
    (OUT/'native-events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in actual))
    # Pause/redraw must not create new samples or role observations.
    command('pause');before=state()
    for _ in range(3):command('draw')
    after=state();assert before['result']==after['result'] and before['role']==after['role']
    command('replay');command('advance 69000')
    replay=[json.loads(x) for x in (ROOT/'.run/live-events.jsonl').read_text().splitlines()]
    assert len(replay)==655
    for a,e in zip(replay,expected):assert a['result']==e['result'] and a['role']==e['role']
    report=dict(source='recorded',events=655,samples=511,device_core_mismatches=0,native_core_mismatches=0,native_role_mode_mismatches=0,logical_end_ms=s['result']['now_ms'],wall_s=time.monotonic()-begin,original_successful_capture_span_s=65.074,pause_redraw_pure=True,replay_consistent=True,hold_observed=any(x['role']=='HOLD' for x in actual),note='Unlabelled scene. No fresh quiet interval meets production HOLD threshold; do not infer physical stillness. Encoded4fps is screenshot sampling, not screen FPS.')
    for name,value in [('native-report.json',report),('native-captures.json',captures),('native-states.json',states)]: (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    subprocess.run(['ffmpeg','-v','error','-y','-framerate','4','-i',str(FRAMES/'%04d.png'),'-frames:v',str(len(captures)),'-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'recorded-native.mp4')],check=True)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
