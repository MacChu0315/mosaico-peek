#!/usr/bin/env python3
"""Encode retained B-window API samples; use capture metadata for actual wall timing."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',default='ab-dragon-B-1');args=p.parse_args()
    out=ROOT/'evidence/followup/performance';captures=json.loads((out/(args.run+'-captures.json')).read_text())
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','8','-i',str(ROOT/'.run'/args.run/'%04d.png'),'-frames:v',str(len(captures)),'-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(out/(args.run+'.mp4'))],check=True)
    info=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,duration','-of','json',str(out/(args.run+'.mp4'))],text=True)
    (out/(args.run+'-video-info.json')).write_text(info)
    print(f'{len(captures)} actual API screenshot samples from {args.run}; encoded8fps, not proof of runtime/browser/device FPS')
if __name__=='__main__':main()
