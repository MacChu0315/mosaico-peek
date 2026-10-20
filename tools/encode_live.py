#!/usr/bin/env python3
"""Encode live GSP API screenshot samples; metadata retains true wall timestamps."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'evidence/phase2/dragon'
    for case in ['idle','dragon']:
        captures=json.loads((out/f'{case}-captures.json').read_text());movie=out/f'{case}-live.mp4'
        command=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','8','-i',str(ROOT/'.run'/('live-'+case)/'%04d.png'),'-frames:v',str(len(captures)),'-c:v','libx264','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
        subprocess.run(command,check=True)
        info=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,duration','-of','json',str(movie)],text=True)
        (out/f'{case}-video-info.json').write_text(info)
        print(case,len(captures),'live API screenshot samples; encoded8fps; see captures.json for wall timestamps')
if __name__=='__main__':main()
