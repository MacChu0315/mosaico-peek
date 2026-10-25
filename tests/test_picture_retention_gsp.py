#!/usr/bin/env python3
"""Native retained-picture checks; all target input uses complete temperature arrays."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
out=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'.run/picture-retention'))
out.mkdir(parents=True,exist_ok=True)
ready=json.loads((ROOT/'.run/ready.json').read_text());checks=[]
with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
    def call(name,args=None):
        reply=api.call(name,args);assert 'result' in reply,reply;return reply['result']
    def settle():
        # Published counters precede pending Canvas work within a backend tick.
        # After the engine wait, an acknowledged next callback publishes it.
        call('wait',{'frames':3});command('pause');return state()
    for theme in ('deep_sea','mechanical'):
        command('view '+theme);command('orientation 270');command('case sleep');command('advance 10500')
        before=settle();assert before['role']['sleeping']
        for _ in range(5):command('draw')
        paused=settle();(out/(theme+'-paused-debug.json')).write_text(json.dumps(dict(before=before,after=paused),indent=2)+'\n')
        assert paused['draws']==before['draws'] and paused['result']==before['result'] and paused['role']==before['role'], {k:(before[k],paused[k]) for k in ('draws','result','role') if before[k]!=paused[k]}
        command('advance 1000');after=settle()
        assert after['draws']==before['draws'] and after['result']['samples']==before['result']['samples']+8
        command('advance 750');waking=settle();assert waking['role']['waking'] and waking['result']['target']
        command('advance 75');middle=settle();assert middle['draws']>after['draws']
        command('advance 75');awake=settle();assert not awake['role']['sleeping'] and not awake['role']['waking'] and awake['role']['pose']['blink']==0
        checkpoints=(before,after,waking,middle,awake)
        for name in ('dragon','deep_sea','mechanical'):
            command('view '+name);assert state()['result']==awake['result'] and state()['role']==awake['role']
        command('view '+theme);command('replay')
        for point in checkpoints:
            command('advance '+str(point['result']['now_ms']-state()['result']['now_ms']))
            repeated=state();assert repeated['result']==point['result'] and repeated['role']==point['role']
        checks.append(dict(theme=theme,checkpoints=checkpoints,paused=paused))
    command('view deep_sea');command('case live');command('advance 70000');end=settle()
    assert end['eof'] and end['result']['samples']==511
    actual=[json.loads(x) for x in (ROOT/'.run/live-events.jsonl').read_text().splitlines()]
    expected=[json.loads(x) for x in (ROOT/'evidence/real-input/role-output.jsonl').read_text().splitlines()]
    assert len(actual)==len(expected)==655
    for a,e in zip(actual,expected):
        assert a['result']==e['result']
        assert (a['role'],a['stationary'],a['observations'])==(e['role'],e['stationary'],e['observations'])
    (out/'recorded-events.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in actual))
artifacts={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'build-sim/peek_backend',ROOT/'build-sim/peek_backend_assets/app.gspb')}
(out/'checks.json').write_text(json.dumps(dict(checks=checks,artifacts=artifacts,recorded_samples=511,recorded_events=655,note='Native pause/static-source/wake/replay checks; simulated complete-array sleep fixture and recorded event replay, not physical FPS.'),indent=2)+'\n')
print('PASS native retained pictures: zero closed redraws with8 new samples; paused purity, genuine array-driven wake and replay;511 recorded arrays/655 events')
