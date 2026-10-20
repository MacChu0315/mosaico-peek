#!/usr/bin/env python3
"""Behavior assertions against the production C executable, including deterministic reruns."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE=ROOT/'build-host/peek_replay'
def run(case):
    out=subprocess.check_output([str(EXE),str(ROOT/'data'/f'{case}.peek')])
    assert out==subprocess.check_output([str(EXE),str(ROOT/'data'/f'{case}.peek')]),case+' replay differs'
    (ROOT/'evidence'/f'{case}-output.jsonl').write_bytes(out)
    return [json.loads(l) for l in out.splitlines()],hashlib.sha256(out).hexdigest()
def main():
    report={}
    for case in ['empty','motion','multi','gaps','recorded']:
        rows,digest=run(case);report[case]={'rows':len(rows),'sha256':digest,'deterministic':True,'last':rows[-1]}
        if case=='empty':assert all(r['data']=='VALID' and not r['target'] for r in rows)
        if case=='motion':
            assert all(not r['target'] for r in rows[:10])
            assert all(r['target'] for r in rows[10:56])
            assert all(abs(r['x']-19.5)<.1 for r in rows[40:56])
            assert not rows[57]['target']
        if case=='multi':
            assert all(r['target'] and r['x']<8 for r in rows[2:48])
            assert all(r['target'] and r['x']>20 for r in rows[51:])
        if case=='gaps':
            assert rows[16]['target'] and rows[17]['target']
            assert rows[20]['samples']==rows[19]['samples'] and rows[20]['last_valid_ms']==rows[19]['last_valid_ms']
            assert rows[28]['data']=='INVALID' and not rows[28]['target']
            assert all(r['target'] for r in rows[31:43])
            assert rows[45]['data']=='STALE' and not rows[45]['target']
            assert all(r['data']=='STALE' and not r['target'] for r in rows[45:])
        if case=='recorded':assert any(r['data']=='STALE' for r in rows) and rows[-1]['samples']==32
    # Reject malformed packets rather than silently truncate the array.
    for text in ['F 0 1 0 1 22\n','F 0 1 0 1 '+'22 '*768+'extra\n','P 100\nP 99\n']:
        with tempfile.NamedTemporaryFile(mode='w',suffix='.peek') as f:
            f.write(text);f.flush();p=subprocess.run([str(EXE),f.name],capture_output=True)
            assert p.returncode!=0 and b'line' in p.stderr
    (ROOT/'evidence/replay-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS replay: 5 production-C cases, deterministic reruns, malformed input rejected')
if __name__=='__main__':main()
