#!/usr/bin/env python3
"""Verify the real event path against stored actual-device C output."""
import json,struct,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    subprocess.run(['python3',str(ROOT/'tools/import_live.py')],check=True)
    command=[str(ROOT/'build-host/peek_replay'),str(ROOT/'data/live.peek')]
    output=subprocess.check_output(command);assert output==subprocess.check_output(command)
    rows=[json.loads(x) for x in output.splitlines()]
    raw=(ROOT/'data/live/20261020-complete-window/events.bin').read_bytes();assert len(rows)==655
    names=['WAITING','VALID','INVALID','STALE']
    for i,r in enumerate(rows):
        e=raw[i*88:(i+1)*88];flags=struct.unpack_from('<I',e,32)[0]
        assert r['now_ms']==struct.unpack_from('<Q',e,20)[0]
        assert r['data']==names[struct.unpack_from('<I',e,28)[0]]
        assert (r['target'],r['held'],r['has_valid'])==tuple(bool(flags&b) for b in (1,2,4))
        assert all(abs(r[k]-struct.unpack_from('<f',e,off)[0])<=1e-4 for k,off in [('x',36),('y',40),('background_c',44)])
        assert all(r[k]==struct.unpack_from('<I',e,off)[0] for k,off in [('area',48),('candidates',52)])
        assert all(r[k]==struct.unpack_from('<Q',e,off)[0] for k,off in [('sequence',56),('last_valid_ms',64),('last_seen_ms',72),('samples',80)])
    assert rows[-1]['samples']==511
    assert rows[9]['data']=='INVALID' and rows[9]['samples']==0
    roles=subprocess.check_output([str(ROOT/'build-host/peek_role_replay'),str(ROOT/'data/live.peek')])
    assert roles==subprocess.check_output([str(ROOT/'build-host/peek_role_replay'),str(ROOT/'data/live.peek')])
    assert [r['result'] for r in map(json.loads,roles.splitlines())]==rows
    # An explicit fault must age a tracked target, never submit stale pixels.
    frame='F 0 1 0 1 '+'22 '*768+'\n'
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(frame+'E 100\nE 750\n');f.flush()
        p=subprocess.check_output([command[0],f.name]);states=list(map(json.loads,p.splitlines()))
        assert states[1]['data']=='INVALID' and states[2]['data']=='STALE'
        assert all(s['samples']==1 and s['last_valid_ms']==0 for s in states)
    (ROOT/'evidence/real-input/detector-output.jsonl').write_bytes(output)
    (ROOT/'evidence/real-input/role-output.jsonl').write_bytes(roles)
    print('PASS: 655 exact real events / 511 arrays; zero device/core field mismatches; deterministic role; explicit fault aging')
if __name__=='__main__':main()
