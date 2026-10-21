#!/usr/bin/env python3
"""Validate authored eye surfaces and render labelled material-test previews."""
import argparse,hashlib,json,math,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import reference_renderer as renderer
ROOT=Path(__file__).resolve().parent
THEMES=['night_owl','deep_sea','mechanical']
def image_for(theme,gx,gy,blink):
    codes=renderer.oracle(theme,gx,gy,blink)
    return Image.fromarray(np.rint(codes/np.array([31,63,31])*255).astype('uint8'),'RGB')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True,help='directory containing theme/eye_surface.png')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--theme',choices=THEMES,action='append',help='repeat to select themes; default all three')
    parser.add_argument('--animate',action='store_true',help='8-second synthetic material test, requires ffmpeg')
    args=parser.parse_args();args.input=args.input.resolve();args.output=args.output.resolve()
    if args.output==ROOT or args.output==args.input or ROOT/'reference' in args.output.parents or args.output==ROOT/'reference':parser.error('Output must be a separate proof directory, not input/reference')
    references=json.loads((ROOT/'reference_checksums.json').read_text())
    for name,digest in references.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('Read-only reference changed: '+name)
    args.output.mkdir(parents=True,exist_ok=True);renderer.GENERATED=args.input
    manifest=json.loads((ROOT/'reference/source_pack/assets/manifest.json').read_text());themes=[t for t in manifest['themes'] if t['id'] in (args.theme or THEMES)]
    checks=[]
    for t in themes:
        name=t['id'];path=args.input/name/'eye_surface.png'
        if not path.is_file():raise ValueError(f'Missing {path}; create authored surfaces first, or use --input rejected for the rejected technical example.')
        with Image.open(path) as im:
            if im.mode!='RGBA' or im.size!=(480,480):raise ValueError(f'{name}: expected RGBA8 480x480')
            pixels=np.asarray(im)
        if not (pixels[:,:,3]==255).all():raise ValueError(name+': eye surface must be fully opaque')
        locked=np.asarray(Image.open(ROOT/'guides'/name/'locked_mask.png'))>0
        neutral=np.asarray(Image.open(ROOT/'reference/source_pack/assets/processed'/name/'neutral.png').convert('RGBA'))
        count=int(np.any(pixels[locked]!=neutral[locked],axis=1).sum())
        if count:raise ValueError(f'{name}: {count} locked pixels changed')
        folder=args.output/name;folder.mkdir(exist_ok=True)
        sheet=Image.new('RGB',(1440,1512),'#151515');draw=ImageDraw.Draw(sheet)
        for row,gy in enumerate([-.58,0,.58]):
            for col,gx in enumerate([-.78,0,.78]):
                im=image_for(t,gx,gy,0);label=f'x{col-1:+d}_y{row-1:+d}'
                im.save(folder/(label+'.png'));sheet.paste(im,(480*col,504*row));draw.text((480*col+8,504*row+482),label+' | synthetic pose',fill='white')
        sheet.save(folder/'contact-sheet.png')
        for blink in [.5,1.0]:image_for(t,.78,.58,blink).save(folder/f'blink-{blink}.png')
        if args.animate:
            fps=12;duration=8;movie=folder/'synthetic-material-check.mp4'
            process=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','480x504','-framerate',str(fps),'-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],stdin=subprocess.PIPE)
            try:
                for n in range(fps*duration):
                    sec=n/fps
                    # Continuous center -> right -> down -> left -> up -> diagonals -> center, then blink.
                    stops=[(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(0,0),(0,0)]
                    segment=min(7,int(sec));fraction=sec-segment;blend=fraction*fraction*(3-2*fraction)
                    x=stops[segment][0]*(1-blend)+stops[segment+1][0]*blend;y=stops[segment][1]*(1-blend)+stops[segment+1][1]*blend
                    blink=math.sin(math.pi*(sec-7))**2 if sec>=7 else 0
                    frame=Image.new('RGB',(480,504),'#151515');frame.paste(image_for(t,x*.78,y*.58,blink));ImageDraw.Draw(frame).text((8,484),f'SYNTHETIC MATERIAL TEST | {sec:.2f}s | not device FPS',fill='white')
                    process.stdin.write(frame.tobytes())
                process.stdin.close()
                if process.wait()!=0:raise RuntimeError('ffmpeg failed')
            finally:
                if process.poll() is None:process.terminate();process.wait()
        checks.append(dict(theme=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),locked_pixels=int(locked.sum()),locked_changed=0,fully_opaque=True,visual_approved=False))
    report=dict(technical_checks='passed',visual_approved=False,reference_only=True,input=str(args.input),themes=checks,note='Synthetic pose material reference only; no thermal detector, native GSP, device performance or visual approval claim.')
    (args.output/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
