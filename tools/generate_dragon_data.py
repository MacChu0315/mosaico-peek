#!/usr/bin/env python3
"""Reproducible synthetic arrays; actual detector computes all target positions."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def write(name,seconds,scenario):
    rows=['# synthetic PEEK1; 8Hz complete arrays; no precomputed detector coordinates']
    seq=0
    for k in range(seconds*8+1):
        t=k*125;target,invalid= scenario(t)
        if invalid=='missing':rows.append(f'P {t}');continue
        seq+=1;pixels=[22]*768
        if target:
            x,y=target
            for j in range(y,y+4):
                for i in range(x,x+4):pixels[j*32+i]=30
        rows.append(f'F {t} {seq} {t} {0 if invalid else 1} '+' '.join(map(str,pixels)))
    (ROOT/'data'/f'{name}.peek').write_text('\n'.join(rows)+'\n')
def scenario(t):
    if t<2000:return None,False
    if t<3500:return (2+int((t-2000)*14/1500),10),False
    if t<5000:return (16+int((t-3500)*12/1500),10),False
    if t<7000:return (28,10-int((t-5000)*10/2000)),False
    if t<9000:return (28,int((t-7000)*20/2000)),False
    if t<15000:return (28,20),False
    if t<15500:return None,False
    if t<17000:return (28,20),False
    if t<18000:return (28-int((t-17000)*7/1000),20),False
    if t<19000:return (21,14),True
    if t<22000:return (21,14),False
    if t<24000:return None,'missing'
    if t<27000:return (18-int((t-24000)*3/3000),12),False
    return None,False
if __name__=='__main__':
    write('dragon',30,scenario);write('idle',70,lambda t:(None,False))
    write('sleep',34,lambda t:((2+min(18,(t-12000)//250),8) if 12000<=t<18000 else None,False))
    manifest=ROOT/'data/manifest.json';data=json.loads(manifest.read_text())
    data['cases'].update({
        'aging':{'kind':'synthetic','expected':'delayed 600ms captures; expired target never exposed; CLI/replay_until/native pump equivalent'},
        'dragon':{'kind':'synthetic','generator':'tools/generate_dragon_data.py','expected':'30s idle, enter, x/y movement, >=4s still, leave/reappear, INVALID, recover, outage, recover and leave'},
        'sleep':{'kind':'synthetic','generator':'tools/generate_dragon_data.py','expected':'10s idle then450ms close, fresh acquired target at12.25s starts150ms wake, motion/hold, leave and repeat idle sleep'},
        'idle':{'kind':'synthetic','generator':'tools/generate_dragon_data.py','expected':'70s uniform22C complete8Hz inputs; no target; calm idle/blinks for10s,450ms close then sleep'}})
    manifest.write_text(json.dumps(data,indent=2)+'\n')
    print('Generated synthetic dragon 30s / idle 70s arrays at 8Hz')
