#!/usr/bin/env python3
"""Convert retained PKF1/PKE1 input to replay text without retiming or detection."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    folder=ROOT/'data/live/20261020-complete-window'
    raw=(folder/'captures.bin').read_bytes();events=(folder/'events.bin').read_bytes()
    assert len(raw)%3112==0 and len(events)%88==0
    index={}
    for offset in range(0,len(raw),3112):
        r=raw[offset:offset+3112];ident=struct.unpack_from('<I',r,4)[0]
        assert r[:4]==b'PKF1' and ident not in index
        index[ident]=r
    lines=['# RECORDED complete window: exact PKE1 receive times, PKF1 float32 arrays. F=submit E=fault P=tick. No resampling.\n']
    used=[];previous=0;timeline=[]
    for offset in range(0,len(events),88):
        e=events[offset:offset+88];ident,cid,op=struct.unpack_from('<III',e,4);now=struct.unpack_from('<Q',e,20)[0]
        assert e[:4]==b'PKE1' and ident==offset//88+1 and now>=previous and op in (0,1,2)
        previous=now;capture=index.get(cid)
        event=dict(event=ident,capture_id=cid,operation=op,received_ms=now)
        if op in (0,2):
            assert capture is not None
            error=struct.unpack_from('<i',capture,32)[0]
            event.update(read_begin_us=struct.unpack_from('<Q',capture,16)[0],captured_ms=struct.unpack_from('<Q',capture,24)[0],error=error)
            assert (error==0)==(op==0)
        if op==0:
            sequence=struct.unpack_from('<Q',capture,8)[0];values=struct.unpack_from('<768f',capture,40)
            tokens=[format(v,'.9g') for v in values]
            assert struct.pack('<768f',*map(float,tokens))==capture[40:]
            lines.append(f"F {now} {sequence} {event['captured_ms']} 1 "+' '.join(tokens)+'\n');used.append(cid)
        else:lines.append(f'{"P" if op==1 else "E"} {now}\n')
        timeline.append(event)
    assert len(used)==len(set(used))==511 and len(timeline)==655
    output=ROOT/'data/live.peek';output.write_text(''.join(lines))
    report=dict(source_commit='63c0799',diagnostic_firmware_commit='1dd860d52ab3e5dff0f60bf6125f0f11745191dc',kind='recorded',resampled=False,temperature_frames=len(used),events=len(timeline),timeline=timeline,files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (folder/'captures.bin',folder/'events.bin',output)})
    (ROOT/'evidence/real-input/input-timeline.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS import: 511 exact float32 arrays / 655 original events; no resampling')
if __name__=='__main__':main()
