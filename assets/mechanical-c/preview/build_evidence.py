#!/usr/bin/env python3
"""Rebuild simulated C reference evidence from the packaged layers and timeline."""
from pathlib import Path
import csv, json, math, subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reference_render import Renderer,timeline_sample,ROOT

OUT=ROOT/'evidence'
OUT.mkdir(exist_ok=True)
def font(size):
    try:return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',size)
    except OSError:return ImageFont.load_default(size=size)
F12,F16,F24=font(12),font(16),font(24)
R=Renderer()

def save(im,path):
    tmp=path.with_suffix('.tmp.png');im.save(tmp,compress_level=8)
    with Image.open(tmp) as check:check.verify()
    tmp.replace(path)

def caption_frame(im,first,second=''):
    out=Image.new('RGB',(480,520),(13,16,19));out.paste(im,(0,0))
    d=ImageDraw.Draw(out);d.text((10,484),first,fill=(229,233,236),font=F12)
    d.text((10,502),second,fill=(155,169,181),font=F12)
    return out

def make_video(name,samples,rate=12):
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
         '-video_size','480x520','-framerate',str(rate),'-i','-',
         '-an','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p',
         '-movflags','+faststart',str(OUT/(name+'.mp4'))]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for s in samples:
            im=R.render(s['gaze_x'],s['gaze_y'],s['shutter'],s.get('active',True))
            first=f"SIMULATED REFERENCE   {s['t_ms']/1000:05.2f}s   {s['state']}"
            second=f"gaze {s['gaze_x']:+.2f},{s['gaze_y']:+.2f}  close {s['shutter']:.2f}  valid {int(s.get('valid',True))}  confirmed {int(s.get('confirmed',False))}"
            p.stdin.write(caption_frame(im,first,second).tobytes())
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('ffmpeg export failed')
    finally:
        if p.poll() is None:p.kill()
    fields=['t_ms','state','active','valid','confirmed','candidate','gaze_x','gaze_y','shutter']
    csv_name='input-timeline.csv' if name=='scenario-reference' else name+'-inputs.csv'
    with (OUT/csv_name).open('w',newline='') as f:
        w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader()
        for s in samples:w.writerow({k:s.get(k,'') for k in fields})
    return {'file':name+'.mp4','frames':len(samples),'encoded_fps':rate,
            'duration_seconds':len(samples)/rate,'dimensions':[480,520],
            'character_region':[0,0,480,480],'input_csv':csv_name,
            'source':'Python simulated reference; not device or C/GSP recording'}

def main():
    overview=Image.new('RGB',(1440,576),(13,16,19));d=ImageDraw.Draw(overview)
    d.text((20,12),'C  /  OPTICAL SHUTTER  /  REFERENCE RENDER',font=F24,fill=(235,237,239))
    for i,(label,c) in enumerate([('OPEN  /  00',0),('CONTRACTED  /  04',.5),('SLEEP  /  08',1)]):
        im=R.render(0,0,c);overview.paste(im,(480*i,52))
        d.text((480*i+20,542),label,font=F16,fill=(223,178,92))
        if i:save(im,OUT/('contracted.png' if i==1 else 'closed.png'))
    save(overview,OUT/'overview.png')
    poses=[(-1,-1,'left-up'),(0,-1,'up'),(1,-1,'right-up'),(-1,0,'left'),(0,0,'center'),(1,0,'right'),(-1,1,'left-down'),(0,1,'down'),(1,1,'right-down')]
    for state,c in [('open',0),('closed',1)]:
        board=Image.new('RGB',(960,1100),(13,16,19));d=ImageDraw.Draw(board)
        d.text((16,10),f'C / NINE DIRECTIONS / {state.upper()} / SIMULATED',font=F24,fill=(232,235,238))
        for i,(x,y,name) in enumerate(poses):
            im=R.render(x*.78,y*.58,c)
            if state=='open':save(im,OUT/f'gaze-{name}.png')
            px=(i%3)*320;py=44+(i//3)*352
            board.paste(im.resize((320,320),Image.Resampling.LANCZOS),(px,py))
            d.text((px+12,py+326),f'{name}: {x*.78:+.2f}, {y*.58:+.2f}',font=F16,fill=(175,188,200))
        save(board,OUT/f'all-angles-{state}.png')
    # All nine aperture stages, fixed gaze; only the center changes.
    board=Image.new('RGB',(720,816),(13,16,19));d=ImageDraw.Draw(board)
    for i in range(9):
        px=(i%3)*240;py=(i//3)*272
        board.paste(R.render(0,0,i/8).resize((240,240),Image.Resampling.LANCZOS),(px,py))
        d.text((px+12,py+246),f'{i:02}  /  closure={i/8:.3f}',font=F12,fill=(192,201,209))
    save(board,OUT/'shutter-stages.png')

    videos=[];fps=12
    timeline=json.loads((ROOT/'preview/timeline.json').read_text())
    samples=[timeline_sample(timeline,i*1000/fps) for i in range(round(timeline['duration_ms']/1000*fps))]
    videos.append(make_video('scenario-reference',samples,fps))
    # Short inspection: center -> axes/diagonals around the preserved gaze range.
    path=[(0,0),(.78,0),(.78,.58),(0,.58),(-.78,.58),(-.78,0),(-.78,-.58),(0,-.58),(.78,-.58),(0,0)]
    samples=[]
    for i in range(96):
        u=i/95*(len(path)-1);j=min(int(u),len(path)-2);f=u-j;f=f*f*(3-2*f)
        a,b=path[j],path[j+1]
        samples.append(dict(t_ms=i*1000/fps,state='ANGLE_SWEEP',active=True,valid=True,confirmed=True,candidate=False,
                            gaze_x=a[0]+(b[0]-a[0])*f,gaze_y=a[1]+(b[1]-a[1])*f,shutter=0))
    videos.append(make_video('rotation-reference',samples,fps))
    samples=[]
    for i in range(48):
        t=i/fps
        if t<.75:c=0
        elif t<1.75:c=(t-.75)
        elif t<2.5:c=1
        elif t<3.5:c=1-(t-2.5)
        else:c=0
        samples.append(dict(t_ms=i*1000/fps,state='APERTURE_CYCLE',active=True,valid=True,confirmed=True,candidate=False,gaze_x=0,gaze_y=0,shutter=c))
    videos.append(make_video('aperture-cycle',samples,fps))
    (OUT/'video-metadata.json').write_text(json.dumps(videos,indent=2)+'\n')
    print(json.dumps({'images':'written','videos':videos},indent=2))

if __name__=='__main__':main()
