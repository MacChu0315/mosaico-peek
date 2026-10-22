#!/usr/bin/env python3
"""Read-only centered-sleep check, including oriented physical-device framebuffer."""
import argparse,io,json,subprocess,time,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from probe_device import command,payload
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--expected-version',default='1.0.11-peek-direction');a=p.parse_args()
 if not 5<=a.seconds<=120:p.error('seconds must be5..120')
 a.output.mkdir(parents=True,exist_ok=False);initial=command(['device-status']);d=initial['device'];assert d['hardware_mac']=='30:ed:a0:f4:52:a0' and d['app_version']==a.expected_version and d['firmware_mode']=='normal' and not d['stale'];boot=initial['boot_id'];(a.output/'before.json').write_text(json.dumps(initial,indent=2)+'\n')
 def eligible(s):return s['view']=='mechanical' and s['sleeping'] and s['blink']>=7.5/8
 start=time.monotonic();rows=[];stable=0;previous=None;passed=False;capture_number=0
 with (a.output/'samples.jsonl').open('w') as log:
  while time.monotonic()-start<a.seconds:
   s=json.loads(payload(command(['rpc','20556','1'])));assert s['error']==0
   row=dict(wall_s=time.monotonic()-start,state=s);rows.append(row);log.write(json.dumps(row)+'\n');log.flush()
   if eligible(s):
    assert s['render_gaze_x']==s['render_gaze_y']==0,('closed gaze drift',s)
    stable=stable+1 if previous is not None and previous['orientation']==s['orientation'] else 1
   else:stable=0
   previous=s
   if stable>=3:
    file=a.output/f'capture-{capture_number:02}.png';capture_number+=1;screen=command(['screenshot',str(file)]);assert screen['boot_id']==boot
    after=json.loads(payload(command(['rpc','20556','1'])));(a.output/f'capture-{capture_number-1:02}-state.json').write_text(json.dumps(dict(before=s,after=after,capture=screen),indent=2)+'\n')
    if not eligible(after) or after['orientation']!=s['orientation']:
     stable=0 # Observed state changed during capture; keep evidence and await a stable window.
     time.sleep(.5);continue
    assert after['render_gaze_x']==after['render_gaze_y']==0
    raw=subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),'2','0','0','1']);expected=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'));expected=np.rot90(expected,-s['orientation']//90)
    actual=np.asarray(Image.open(file).convert('RGB'));codes=lambda x:np.rint(x.astype(float)/255*np.array([31,63,31])).astype(int)
    diff=np.abs(codes(expected)-codes(actual));assert diff.max()==0,('device framebuffer differs',int(diff.max()),int((diff>0).sum()))
    shutil.copyfile(file,a.output/'closed.png')
    final=command(['device-status']);assert final['boot_id']==boot and final['device']['crash_count']==d['crash_count'];(a.output/'after.json').write_text(json.dumps(final,indent=2)+'\n')
    report=dict(version=d['app_version'],boot_id=str(boot),ELF=d['firmware_sha256'],orientation=s['orientation'],closed_render_gaze=[0,0],source_gaze=[s['gaze_x'],s['gaze_y']],RGB565_pixels_exact=True,observations=len(rows),wall_s=time.monotonic()-start,note='Actual device framebuffer, stable closed state before/after capture. Same production C globe/shutter/frame with independent quarter-turn. Not physical panel FPS or calibrated latency.')
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));passed=True;break
   time.sleep(.5)
 if not passed:
  (a.output/'not-observed.json').write_text(json.dumps(dict(reason='No stable mechanical closed window within deadline; no centering/device-pixel pass claimed',samples=len(rows)),indent=2)+'\n');raise SystemExit('NOT VERIFIED: no stable closed mechanical state observed')
if __name__=='__main__':main()
