#!/usr/bin/env python3
"""Native mechanical presentation centering; source detection/role remain intact."""
import io,json,os,subprocess,sys,time,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'evidence/mechanical-c/integrated/sleep-center'));OUT.mkdir(parents=True,exist_ok=True)
def main():
 checks=[];ready=json.loads((ROOT/'.run/ready.json').read_text())
 with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
  def call(m,p=None):
   r=api.call(m,p);assert 'result' in r,r;return r['result']
  def shot(name):
   call('wait',{'frames':3});s=state();p=s['render_pose'];assert s['error']==0
   ppm=subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),'2',str(p['gaze_x']),str(p['gaze_y']),str(p['blink'])]);expected=np.asarray(Image.open(io.BytesIO(ppm)))
   file=OUT/(name+'.png');call('screenshot',{'path':str(file),'format':'png'});actual=np.asarray(Image.open(file).convert('RGB'))
   code=lambda a:np.rint(a/255*np.array([31,63,31])).astype(int)
   assert np.array_equal(code(actual),code(expected)),name
   checks.append(dict(name=name,state=s,pixels_sha256=hashlib.sha256(actual.tobytes()).hexdigest()));return s,actual
  command('orientation 0');command('view mechanical');command('case sleep');command('advance 6180');s,_=shot('ordinary-blink')
  assert not s['role']['sleeping'] and s['render_pose']==s['role']['pose']
  command('replay');closed=None
  for at,name in [(9950,'before-close'),(10225,'closing-center'),(10400,'last-shutter-frame'),(10450,'closed'),(11400,'closed-later'),(11900,'closed-still'),(12250,'wake-start'),(12325,'waking'),(12400,'awake')]:
   command('advance '+str(at-state()['result']['now_ms']));s,im=shot(name);p=s['render_pose'];raw=s['role']['pose']
   if (s['role']['sleeping'] or s['role']['waking']) and raw['blink']>=7.5/8:
    assert p['gaze_x']==p['gaze_y']==0
    if closed is None:closed=im
    else:assert np.array_equal(im,closed),name
   elif name in ('before-close','awake'):assert p==raw
   else:
    for k in ['gaze_x','gaze_y']:assert abs(p[k]-raw[k]*max(0,1-raw['blink']/(7.5/8)))<1e-7
  command('replay');command('advance 11900');original=state()
  for theme in ['dragon','deep_sea','mechanical']:
   command('view '+theme);call('wait',{'frames':2});s=state();assert s['role']==original['role'] and s['result']==original['result']
   if theme!='mechanical':assert s['render_pose']==s['role']['pose']
   else:assert s['render_pose']['gaze_x']==s['render_pose']['gaze_y']==0
  command('draw');call('wait',{'frames':2});assert state()['role']==original['role'] and state()['result']==original['result']
  s,im=shot('sleep-reentry');assert np.array_equal(im,closed)
  command('case idle');command('advance 9800');command('play');start=time.monotonic();records=[];captures=[];folder=ROOT/'.run/center-sleep-frames';folder.mkdir(exist_ok=True)
  while time.monotonic()-start<4.3:
   s=state();assert not s['error'];records.append(dict(wall_s=time.monotonic()-start,state=s))
   if s['role']['sleeping'] and s['role']['pose']['blink']>=7.5/8:assert s['render_pose']['gaze_x']==s['render_pose']['gaze_y']==0
   path=folder/f'{len(captures):04}.png';call('screenshot',{'path':str(path),'format':'png'});captures.append(dict(file=str(path),wall_s=time.monotonic()-start));time.sleep(.1)
  command('pause');elapsed=time.monotonic()-start;assert any(r['state']['role']['sleeping'] for r in records)
  lines=['ffconcat version 1.0']
  for i,c in enumerate(captures):
   begin=0 if i==0 else c['wall_s'];end=captures[i+1]['wall_s'] if i+1<len(captures) else elapsed;lines += ["file '"+c['file']+"'",'duration '+str(max(.001,end-begin))]
  lines += ["file '"+captures[-1]['file']+"'"];concat=folder/'timeline.ffconcat';concat.write_text('\n'.join(lines)+'\n');movie=OUT/'center-sleep-realtime.mp4'
  subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-c:v','libx264','-crf','24','-pix_fmt','yuv420p',str(movie)],check=True)
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(movie)]));assert abs(duration-elapsed)<.2
  (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');(OUT/'live.json').write_text(json.dumps(records,indent=2)+'\n');(OUT/'report.json').write_text(json.dumps(dict(checkpoints=len(checks),wall_s=elapsed,movie_s=duration,source_unchanged_across_switch=True,closed_center_pixels_identical=True,note='Native C/GSP synthetic-temperature flow. Movie retains wall intervals; not device FPS. Role pose is distinct from mechanical render_pose.'),indent=2)+'\n')
 print('PASS native centered sleep, closing/waking, ordinary blink, source-preserving switch/replay;11 exact C screenshots and realtime evidence')
if __name__=='__main__':main()
