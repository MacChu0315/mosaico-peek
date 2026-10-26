#!/usr/bin/env python3
"""Capture a running native preview with actual wall-time movie intervals."""
import argparse,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--orientation',type=int,choices=[0,90,180,270],default=270);args=p.parse_args()
out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
ready=json.loads((ROOT/'.run/ready.json').read_text())
with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
    for theme in ('dragon','deep_sea','mechanical'):
        frames=ROOT/'.run/render-trial'/theme;frames.mkdir(parents=True,exist_ok=True)
        command('view '+theme);command('orientation '+str(args.orientation));command('case sleep');command('advance 9400');command('play')
        begin=time.monotonic();rows=[]
        while time.monotonic()-begin<8:
            path=frames/f'{len(rows):04d}.png';reply=api.call('screenshot',{'path':str(path),'format':'png'});assert 'result' in reply,reply
            rows.append(dict(file=str(path),wall_s=time.monotonic()-begin,state=state()));time.sleep(.06)
        command('pause')
        report=dict(source='SYNTHETIC complete temperature arrays through production detector/controller',orientation=args.orientation,logical_start_ms=9400,capture_wall_seconds=rows[-1]['wall_s']-rows[0]['wall_s'],timing='VFR durations from actual screenshot completion intervals; screenshot sampling is not device FPS',ffmpeg=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],frames=rows)
        (out/(theme+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        lines=[]
        for i,row in enumerate(rows):
            lines.append("file '"+row['file']+"'")
            if i+1<len(rows):lines.append('duration '+str(rows[i+1]['wall_s']-row['wall_s']))
        lines.append("file '"+rows[-1]['file']+"'")
        concat=frames/'frames.ffconcat';concat.write_text('\n'.join(lines)+'\n')
        # The pinned local ffmpeg predates -fps_mode; -vsync vfr preserves PTS.
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-c:v','libx264','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(out/(theme+'.mp4'))],check=True)
        print(theme,len(rows),report['capture_wall_seconds'],flush=True)
