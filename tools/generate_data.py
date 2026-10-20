#!/usr/bin/env python3
"""Deterministic synthetic Celsius arrays and loss events; no detector outputs as inputs."""
import json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=['empty','motion','multi','gaps','recorded']
def write(name,events):
    p=ROOT/'data'/f'{name}.peek'
    with p.open('w') as f:
        f.write('# PEEK1 Celsius row-major 32x24; F now_ms sequence captured_ms complete 768 values; P now_ms\n')
        for e in events:f.write(e+'\n')
def generate():
    for case in CASES[:-1]:
        rng=random.Random(90640);events=[];seq=0;previous=None
        for k in range(80):
            now=k*125
            if case=='gaps' and (k in (16,17) or k>=40):events.append(f'P {now}');continue
            if case=='gaps' and k==20:events.append(f'F {now} '+previous);continue
            pixels=[round(22+rng.uniform(-.12,.12),4) for _ in range(768)]
            def hot(x,y,w=4,h=4,c=30):
                for j in range(y,y+h):
                    for i in range(x,x+w):pixels[j*32+i]=round(c+rng.uniform(-.08,.08),4)
            if case=='motion' and 8<=k<56:hot(min(18,2+max(0,k-8)),8)
            if case=='multi':
                if k<48:hot(3,5)
                if k>=16:hot(24,15,5,5,40)
            if case=='gaps':hot(12,10)
            seq+=1;complete=0 if case=='gaps' and k==28 else 1
            previous=f'{seq} {now} {complete} '+' '.join(map(str,pixels))
            events.append(f'F {now} '+previous)
        write(case,events)
    rows=[json.loads(l) for l in (ROOT/'data/recorded.jsonl').open()]
    origin=rows[0]['acquisition_end_us']//1000;events=[];clock=0
    for row in rows:
        now=row['acquisition_end_us']//1000-origin
        while clock<now:events.append(f'P {clock}');clock+=125
        events.append(f'F {now} {row["sequence"]} {now} 1 '+' '.join(format(x,'.9g') for x in row['temperatures']))
        clock=now+125
    events.append(f'P {clock+1000}');write('recorded',events)
    metadata={'format':'PEEK1','cases':{
        'empty':{'kind':'synthetic','expected':'VALID with no target throughout'},
        'motion':{'kind':'synthetic','expected':'empty 0..875ms; acquire by 1250ms; move then stationary at x=19.5,y=9.5 through 6875ms; release by 7125ms'},
        'multi':{'kind':'synthetic','expected':'acquire left; retain left when a hotter right source appears at 2000ms; left leaves at 6000ms; reacquire right after release and 3 confirmations'},
        'gaps':{'kind':'synthetic','expected':'2 missing samples; duplicate at 2500ms; invalid complete flag at 3500ms; recover with 3 samples; continuous outage from 5000ms -> STALE at 5625ms'},
        'recorded':{'kind':'recorded','expected':'no labelled target ground truth; preserve sparse capture gaps, stale between snapshots; continuous tracking is not validated'}},'synthetic':{'seed':90640,'generator':'tools/generate_data.py','full_frame_interval_ms':125,'background_c':22,'noise_c':0.12}}
    (ROOT/'data/manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
if __name__=='__main__':generate()
