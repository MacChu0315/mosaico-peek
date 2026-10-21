#!/usr/bin/env python3
"""Actual native C/GSP; synthetic Celsius arrays, never target injection."""
import io,json,subprocess,sys,time,hashlib,os
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'evidence/eye-ui/native'));OUT.mkdir(parents=True,exist_ok=True)
THEMES=['night_owl','deep_sea','mechanical']
def main():
    ready=json.loads((ROOT/'.run/ready.json').read_text());checks=[];movies=[]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'build-sim/peek_backend',ROOT/'build-sim/peek_backend_assets/app.gspb',ROOT/'build-sim/peek_backend_assets/bundle_gsp.api.json'] if p.exists()}
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def call(m,p=None):
            r=api.call(m,p);assert 'result' in r,r;return r['result']
        def advance(at):
            delta=at-state()['result']['now_ms'];assert delta>=0;command(f'advance {delta}')
        def capture(theme,name):
            call('wait',{'frames':2});path=OUT/f'{theme}-{name}.png';call('screenshot',dict(path=str(path),format='png'));s=state();assert not s['error'];pose=s['role']['pose']
            ppm=subprocess.check_output([str(ROOT/'build-host/eye_snapshot'),str(THEMES.index(theme)),str(pose['gaze_x']),str(pose['gaze_y']),str(pose['blink'])])
            # Compare RGB565 codes; simulator expands 565 to 8-bit with its own
            # integer convention, so normalize both to the original565 values.
            def code(im):
                return [((r*31+127)//255,(g*63+127)//255,(b*31+127)//255) for r,g,b in im.convert('RGB').getdata()]
            assert code(Image.open(io.BytesIO(ppm)))==code(Image.open(path)),(theme,name)
            checks.append(dict(theme=theme,name=name,state=s,pixel_sha256=hashlib.sha256(path.read_bytes()).hexdigest()));return s
        for theme in THEMES:
            command('view '+theme);command('case dragon')
            for at,name in [(0,'IDLE'),(2250,'NOTICE'),(3200,'left'),(4800,'right'),(6250,'up'),(8750,'down'),(10750,'HOLD'),(14875,'fresh-still'),(15000,'held'),(15250,'LEAVE'),(15750,'reappear'),(18125,'invalid'),(19875,'recovered'),(22750,'STALE')]:
                advance(at);s=capture(theme,name)
                if name=='NOTICE':assert s['role']['mode']=='NOTICE'
                if name in ('HOLD','fresh-still'):assert s['role']['mode']=='HOLD' and s['role']['stationary']
                if name=='held':assert s['result']['held'] and not s['role']['stationary']
                if name=='invalid':assert s['result']['data']=='INVALID'
                if name=='STALE':assert s['result']['data']=='STALE'
            first=state();command('draw');call('wait',{'frames':2});assert first['role']==state()['role'] and first['result']==state()['result']
            for other in ['diagnostic','dragon']+THEMES+[theme]:
                command('view '+other);assert first['result']==state()['result'] and first['role']==state()['role']
            command('replay');advance(22750);assert first['role']==state()['role'] and first['result']==state()['result']
            command('case sleep')
            for at,name in [(9950,'awake-idle'),(10225,'closing'),(10450,'sleeping'),(12000,'candidate'),(12250,'wake-start'),(12325,'waking'),(12400,'awake'),(30000,'asleep-again')]:
                advance(at);s=capture(theme,name)
                if name in ('sleeping','candidate','asleep-again'):assert s['role']['pose']['blink']==1 and not s['result']['target']
                if name=='wake-start':assert s['role']['waking'] and s['role']['pose']['blink']==1
                if name=='waking':assert s['role']['waking'] and 0<s['role']['pose']['blink']<1
            # Two real-time recordings per theme. Preserve API capture completion
            # timestamps and encode VFR; never compress a slow run into fake time.
            for case,duration in [('dragon',30.7),('sleep',34.7)]:
                command('case '+case);call('wait',{'frames':2});folder=ROOT/'.run'/f'eye-{theme}-{case}';folder.mkdir(exist_ok=True)
                command('play');start=time.monotonic();next_capture=start;records=[];captures=[]
                while time.monotonic()-start<duration:
                    s=state();assert not s['error'];records.append(dict(wall_s=time.monotonic()-start,**s))
                    if time.monotonic()>=next_capture:
                        file=folder/f'{len(captures):04d}.png';call('screenshot',dict(path=str(file),format='png'))
                        captures.append(dict(file=file.name,wall_s=time.monotonic()-start,logical_ms=s['result']['now_ms']));next_capture=time.monotonic()+.20
                    if s['eof']:break
                    time.sleep(.025)
                command('pause');elapsed=time.monotonic()-start;assert s['eof'],s
                if case=='dragon':
                    assert {'IDLE','NOTICE','TRACKING','HOLD','LEAVE'}<={s['role']['mode'] for s in records}
                    assert {'INVALID','STALE'}<={s['result']['data'] for s in records}
                else:assert any(s['role']['sleeping'] for s in records) and any(s['role']['waking'] for s in records)
                lines=['ffconcat version 1.0']
                for n,c in enumerate(captures):
                    end=captures[n+1]['wall_s'] if n+1<len(captures) else elapsed
                    # First sample holds from time0; subsequent timestamps stay exact.
                    begin=0 if n==0 else c['wall_s']
                    lines.extend(["file '"+str(folder/c['file'])+"'",'duration '+str(max(.001,end-begin))])
                lines.append("file '"+str(folder/captures[-1]['file'])+"'");concat=folder/'timeline.ffconcat';concat.write_text('\n'.join(lines)+'\n')
                movie=OUT/f'{theme}-{case}-realtime.mp4'
                subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
                length=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(movie)]));assert abs(length-elapsed)<.2,(length,elapsed)
                (OUT/f'{theme}-{case}-states.jsonl').write_text(''.join(json.dumps(s)+'\n' for s in records));(OUT/f'{theme}-{case}-captures.json').write_text(json.dumps(captures,indent=2)+'\n')
                movies.append(dict(theme=theme,case=case,wall_s=elapsed,movie_s=length,frames=len(captures),file=movie.name));print('LIVE',theme,case,round(elapsed,2),flush=True)
    (OUT/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');(OUT/'report.json').write_text(json.dumps(dict(checkpoints=len(checks),movies=movies,artifacts=hashes,physical_device_operated=False,note='Actual native C/GSP; all synthetic complete temperature arrays pass unchanged production detector. Screenshot sampling is not display FPS.'),indent=2)+'\n');print('PASS native trio',len(checks),'pixel checkpoints and six realtime runs',flush=True)
if __name__=='__main__':main()
