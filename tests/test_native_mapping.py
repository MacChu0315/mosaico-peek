#!/usr/bin/env python3
"""Native GSP mount comparison; baseline and flipped runs use identical arrays."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from control import command,state
OUT=ROOT/'evidence/orientation'
TIMES=[3200,4800,6250,8750,13000]
def collect():
    command('view dragon');command('case dragon');records=[]
    for at in TIMES:
        command(f'advance {at-state()["result"]["now_ms"]}')
        s=state();assert s['error']==0 and s['result']['target'];records.append(s)
    return records

def main():
    p=argparse.ArgumentParser();p.add_argument('--record-baseline',action='store_true');a=p.parse_args()
    records=collect()
    if a.record_baseline:
        assert all(not s['flip_x'] and not s['flip_y'] for s in records)
        (OUT/'native-unflipped.json').write_text(json.dumps(records,indent=2)+'\n');return
    baseline=json.loads((OUT/'native-unflipped.json').read_text());checks=[];directions=set()
    for native,physical in zip(baseline,records):
        assert physical['flip_x'] and physical['flip_y']
        assert native['result']==physical['result']
        for key in ['mode','observations','notices','stationary','speed_px_s','blinks']:
            assert native['role'][key]==physical['role'][key],key
        # Pose retains authored idle initial conditions and HOLD micro-motion;
        # those are intentionally not mirrored. Check direction for material
        # excursions, while the C test proves exact map reflection at all768
        # centers. Record residuals without claiming an exact mirrored pose.
        errors={k:abs(native['role']['pose'][k]+physical['role']['pose'][k]) for k in ['gaze_x','gaze_y']}
        for k in ['gaze_x','gaze_y']:
            original=native['role']['pose'][k];flipped=physical['role']['pose'][k]
            if abs(original)>.02:
                assert original*flipped<0,(k,original,flipped)
                directions.add(k)
        checks.append(dict(now_ms=physical['result']['now_ms'],reflection_residual=errors))
    assert directions=={'gaze_x','gaze_y'}
    final=records[-1];command('replay');command('advance 13000');again=state()
    assert again['flip_x'] and again['flip_y']
    assert again['result']==final['result'] and again['role']==final['role']
    command('pause');command('draw');paused=state()
    assert paused['role']==again['role'] and paused['result']==again['result']
    (OUT/'native-flipped.json').write_text(json.dumps(records,indent=2)+'\n')
    (OUT/'native-mapping-checks.json').write_text(json.dumps(dict(checks=checks,replay_mapping_preserved=True,pause_is_pure=True,detector_results_identical=True),indent=2)+'\n')
    print('PASS native mapping: identical detector/role decisions, both gaze axes reflected, mapping survives replay and pause')
if __name__=='__main__':main()
