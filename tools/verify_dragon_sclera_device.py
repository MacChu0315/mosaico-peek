#!/usr/bin/env python3
"""Read-only stable closed-device check against the retained dragon C shape."""
import argparse, io, json, subprocess, time
from pathlib import Path
from PIL import Image, ImageChops
from probe_device import command,payload
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=float,default=30);a=p.parse_args()
    if not 5<=a.seconds<=60:p.error('seconds must be5..60')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    initial=command(['device-status']);d=initial['device'];assert d['hardware_mac']=='30:ed:a0:f4:52:a0' and d['app_version']=='1.0.12-peek-sclera' and d['firmware_mode']=='normal' and not d['stale'];boot=initial['boot_id']
    (out/'before.json').write_text(json.dumps(initial,indent=2)+'\n');start=time.monotonic();stable=0;previous=None;rows=[]
    def eligible(s):return s['view']=='dragon' and s['role']=='IDLE' and s['sleeping'] and s['blink']==1
    while time.monotonic()-start<a.seconds:
        s=json.loads(payload(command(['rpc','20556','1'])));rows.append(s);assert s['error']==s['imu_error']==0
        stable=stable+1 if eligible(s) and previous is not None and eligible(previous) and previous['orientation']==s['orientation'] else int(eligible(s));previous=s
        (out/'states.json').write_text(json.dumps(rows,indent=2)+'\n')
        if stable>=3:
            file=out/'closed.png';shot=command(['screenshot',str(file)]);assert shot['boot_id']==boot
            after=json.loads(payload(command(['rpc','20556','1'])));(out/'capture.json').write_text(json.dumps(dict(before=s,after=after,capture=shot),indent=2)+'\n')
            if not eligible(after) or after['orientation']!=s['orientation']:raise RuntimeError('State changed during capture; no pixel verification claimed')
            # Production IDLE converges for>10s before sleep; retained shape
            # parameters are.69/.072/.16. Full closure is independent of gaze.
            raw=subprocess.check_output([str(ROOT/'build-host/dragon_snapshot'),'0','0','1','.69','.072','.16'])
            expected=Image.open(io.BytesIO(raw)).convert('RGB')
            if s['sample_step']==2:expected=expected.resize((240,240),Image.Resampling.NEAREST).resize((480,480),Image.Resampling.NEAREST)
            angle=s['orientation']
            if angle:expected=expected.transpose({90:Image.Transpose.ROTATE_270,180:Image.Transpose.ROTATE_180,270:Image.Transpose.ROTATE_90}[angle])
            lut=[(i*m+127)//255 for m in (31,63,31) for i in range(256)]
            assert ImageChops.difference(expected.point(lut),Image.open(file).convert('RGB').point(lut)).getbbox() is None,'Closed device differs from retained C shape'
            final=command(['device-status']);assert final['boot_id']==boot and final['device']['crash_count']==d['crash_count'];(out/'after.json').write_text(json.dumps(final,indent=2)+'\n')
            report=dict(version=d['app_version'],boot_id=str(boot),ELF=d['firmware_sha256'],orientation=angle,closed_RGB565_exact=True,observations=len(rows),wall_s=time.monotonic()-start,note='Actual stable closed-device framebuffer equals production C retained eyelids. No physical screen FPS or moving-frame synchronization claim.')
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return
        time.sleep(.5)
    (out/'not-observed.json').write_text(json.dumps(dict(reason='No stable closed dragon window; not verified',observations=len(rows)),indent=2)+'\n');raise SystemExit('NOT VERIFIED: no stable closed dragon state observed')
if __name__=='__main__':main()
