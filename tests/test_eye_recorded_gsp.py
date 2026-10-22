#!/usr/bin/env python3
"""Complete recorded arrays through native detector while switching views."""
import json,sys,time,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'evidence/eye-ui/recorded'));OUT.mkdir(parents=True,exist_ok=True)
def main():
    expected=list(map(json.loads,subprocess.check_output([str(ROOT/'build-host/peek_role_replay'),str(ROOT/'data/live.peek')],text=True).splitlines()))
    def verify():
        actual=list(map(json.loads,(ROOT/'.run/live-events.jsonl').read_text().splitlines()));assert len(actual)==655
        for a,e in zip(actual,expected):
            assert a['result']==e['result']
            assert (a['role'],a['stationary'],a['observations'])==(e['role'],e['stationary'],e['observations'])
        return actual
    # Every theme must consume all original events through the production path.
    for theme in ['dragon','night_owl','deep_sea','mechanical']:
        command('view '+theme);command('case live');command('advance 69000');verify();s=state();assert s['result']['samples']==511
        command('replay');command('advance 69000');verify();assert s['role']==state()['role'] and s['result']==state()['result']
    command('view night_owl');command('case live');command('play');start=time.monotonic();next_capture=start;records=[];captures=[];switches=[];folder=ROOT/'.run/eye-recorded';folder.mkdir(exist_ok=True)
    ready=json.loads((ROOT/'.run/ready.json').read_text())
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        while time.monotonic()-start<75:
            elapsed=time.monotonic()-start;s=state();assert not s['error'];records.append(dict(wall_s=elapsed,**s))
            for at,view in [(8,'diagnostic'),(9,'night_owl'),(22,'deep_sea'),(40,'mechanical'),(55,'dragon'),(58,'mechanical')]:
                if elapsed>=at and at not in [x['at'] for x in switches]:
                    before=s;after=command('view '+view);assert after['result']['samples']>=before['result']['samples'];assert after['result']['now_ms']>=before['result']['now_ms'];switches.append(dict(at=at,view=view,before=before,after=after))
            if time.monotonic()>=next_capture:
                file=folder/f'{len(captures):04d}.png';r=api.call('screenshot',dict(path=str(file),format='png'));assert 'result' in r
                captures.append(dict(file=file.name,wall_s=time.monotonic()-start,logical_ms=s['result']['now_ms']));next_capture=time.monotonic()+.25
            if s['eof']:break
            time.sleep(.025)
    assert s['eof'] and s['result']['samples']==511;actual=verify();command('pause');before=state()
    for _ in range(3):command('draw')
    assert before['role']==state()['role'] and before['result']==state()['result']
    elapsed=time.monotonic()-start;lines=['ffconcat version 1.0']
    for i,c in enumerate(captures):
        end=captures[i+1]['wall_s'] if i+1<len(captures) else elapsed;begin=c['wall_s'] if i else 0
        lines.extend(["file '"+str(folder/c['file'])+"'",'duration '+str(max(.001,end-begin))])
    lines.append("file '"+str(folder/captures[-1]['file'])+"'");concat=folder/'timeline.ffconcat';concat.write_text('\n'.join(lines)+'\n');movie=OUT/'recorded-switches-realtime.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
    length=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(movie)]));assert abs(length-elapsed)<.2
    report=dict(events=655,samples=511,all_three_theme_replays=True,zero_core_role_mode_mismatches=True,switches=len(switches),wall_s=elapsed,movie_s=length,frames=len(captures),hold_observed=any(x['role']=='HOLD' for x in actual),note='Recorded unlabelled thermal scene, original capture/receive/fault events unchanged. All arrays pass production C detector. Six live view switches preserve epoch; no physical device operation. Video retains capture wall times and is not screen FPS.')
    for name,value in [('report.json',report),('captures.json',captures),('switches.json',switches)]: (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    for name,rows in [('events.jsonl',actual),('states.jsonl',records)]: (OUT/name).write_text(''.join(json.dumps(r)+'\n' for r in rows))
    print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
