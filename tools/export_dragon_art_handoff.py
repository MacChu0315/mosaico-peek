#!/usr/bin/env python3
"""Export original dragon sources and an isolated sclera artwork reference."""
import argparse, hashlib, io, json, shutil, subprocess, sys, zipfile
from pathlib import Path
import PIL
from PIL import Image, ImageChops, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def copy(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
def package(out):
    validation=json.loads((out/'VALIDATION.json').read_text())
    assert validation['production_C_baseline_frames_exact']==11
    for name,value in json.loads((out/'REFERENCE_CHECKSUMS.json').read_text()).items():assert digest(out/name)==value,name
    files=sorted(s for s in out.rglob('*') if s.is_file() and 'build' not in s.relative_to(out).parts and '__pycache__' not in s.parts and s.name!='CHECKSUMS.sha256')
    (out/'CHECKSUMS.sha256').write_text(''.join(digest(s)+'  '+str(s.relative_to(out))+'\n' for s in files));files.append(out/'CHECKSUMS.sha256')
    archive=out.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for s in files:z.write(s,out.name+'/'+str(s.relative_to(out)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for s in files:assert hashlib.sha256(z.read(out.name+'/'+str(s.relative_to(out)))).hexdigest()==digest(s)
    archive.with_suffix('.zip.sha256').write_text(digest(archive)+'  '+archive.name+'\n')
    print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,sha256=digest(archive),files=len(files),baseline_exact=11,candidate_only_sclera=True),indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'review/dragon-sclera-art-handoff-v1');p.add_argument('--package-existing',action='store_true');a=p.parse_args();out=a.output.resolve()
    if ROOT/'review' not in out.parents:p.error('Output must be inside this project review/')
    if a.package_existing:package(out);return
    if 'c = sclera(lx,ly);' in (ROOT/'src/dragon_render.c').read_text():
        p.error('Legacy procedural-sclera exporter requires the retained pre-integration source; existing v1 ZIP remains valid')
    if out.exists():p.error('Refusing to overwrite existing handoff')
    original=ROOT/'review-inputs/peek-phase2-inputs/approved-dragon'
    if not original.is_dir():p.error('Original approved-dragon input package is missing; do not invent originals')
    sources=list((ROOT/'assets/dragon').glob('*'))+list(original.rglob('*'))
    sources=[s for s in sources if s.is_file()]
    before={str(s):(digest(s),s.stat().st_mtime_ns) for s in sources}
    out.mkdir(parents=True)
    copy(ROOT/'LICENSE',out/'LICENSE')
    for name in ('README.md','preview.py'):copy(ROOT/'tools/dragon_art_handoff'/name,out/name)
    for s in original.rglob('*'):
        if s.is_file():copy(s,out/'original-reference'/s.relative_to(original))
    for s in (ROOT/'assets/dragon').iterdir():copy(s,out/'source/assets/dragon'/s.name)
    for name in ('dragon_render.c','dragon_render.h','dragon_pose.h'):copy(ROOT/'src'/name,out/'source/src'/name)
    copy(ROOT/'tools/bake_dragon.py',out/'source/tools/bake_dragon.py')
    metadata=json.loads((out/'source/assets/dragon/metadata.json').read_text())
    for name in ('skin','iris'):
        assert digest(out/'original-reference/assets'/(name+'.png'))==metadata['textures'][name]['approved_source']['sha256']
        assert digest(out/'source/assets/dragon'/(name+'.png'))==metadata['textures'][name]['preprocessed']['sha256']
    subprocess.run([sys.executable,str(out/'preview.py'),'--output',str(out/'reference'),'--movie'],check=True)
    template=out/'template';template.mkdir()
    raw=subprocess.check_output([str(out/'build/snapshot'),'--template']);im=Image.open(io.BytesIO(raw)).convert('RGB');im.save(template/'current-procedural-sclera.png')
    radius=233*26870/32768
    mask=Image.new('L',(480,480));mask.putdata([255 if radius**2<=(x-240)**2+(y-240)**2<233**2 else 0 for y in range(480) for x in range(480)]);mask.save(template/'sclera-editable-mask.png')
    guide=im.copy();d=ImageDraw.Draw(guide);d.ellipse((7,7,473,473),outline='red',width=2);d.ellipse((240-radius,240-radius,240+radius,240+radius),outline='yellow',width=2);d.line((230,240,250,240),fill='white');d.line((240,230,240,250),fill='white');guide.save(template/'sclera-guide.png')
    # The unmodified default path must match the production scalar raster,
    # followed by precisely the device-approved2x2 sample replication.
    poses=json.loads((out/'reference/render.json').read_text())['poses']
    for name,gx,gy,blink in poses:
        raw=subprocess.check_output([str(ROOT/'build-host/dragon_snapshot'),str(gx),str(gy),str(blink),'.69','.072','.16'])
        expected=Image.open(io.BytesIO(raw)).convert('RGB').resize((240,240),Image.Resampling.NEAREST).resize((480,480),Image.Resampling.NEAREST)
        assert ImageChops.difference(expected,Image.open(out/'reference'/(name+'.png'))).getbbox() is None,name
    # Exercise actual optional-surface CLI; only eye-white pixels may change.
    black=out/'build/candidate-black.png';Image.new('RGB',(480,480)).save(black)
    subprocess.run([sys.executable,str(out/'preview.py'),'--surface',str(black),'--output',str(out/'build/candidate-proof')],check=True)
    changed={}
    for name,*_ in poses:
        old=Image.open(out/'reference'/(name+'.png'));new=Image.open(out/'build/candidate-proof'/(name+'.png'))
        diff=ImageChops.difference(old,new);channels=diff.split();maskdiff=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]).point(lambda v:255 if v else 0)
        allowed=Image.open(out/'reference'/(name+'-sclera-mask.png'))
        assert ImageChops.multiply(maskdiff,ImageChops.invert(allowed)).getbbox() is None,name
        changed[name]=sum(v!=0 for v in maskdiff.getdata())
    assert changed['closed']==0 and changed['left']>0 and changed['right']>0
    invalid=[]
    for name,size,alpha in [('wrong-size',(240,240),255),('transparent',(480,480),0)]:
        path=out/'build'/(name+'.png');Image.new('RGBA',size,(0,0,0,alpha)).save(path)
        r=subprocess.run([sys.executable,str(out/'preview.py'),'--surface',str(path),'--output',str(out/'build'/name)],capture_output=True,text=True)
        assert r.returncode==2 and not (out/'build'/name).exists();invalid.append(name)
    assert before=={str(s):(digest(s),s.stat().st_mtime_ns) for s in sources}
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate','-of','json',str(out/'reference/motion.mp4')],text=True))
    assert float(probe['format']['duration'])==8 and probe['streams'][0]['r_frame_rate']=='25/1'
    validation=dict(source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),Pillow=PIL.__version__,compiler=subprocess.check_output(['cc','--version'],text=True).splitlines()[0],ffmpeg=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],production_C_baseline_frames_exact=len(poses),candidate_changes_only_sclera=changed,invalid_inputs_rejected=invalid,original_and_production_sources_hashes_and_mtimes_unchanged=True,movie=probe,physical_or_native_GSP_validation=False,note='Art preparation only; no new design or firmware implementation. Candidate sampler is reference-only; preset poses are not thermal inputs.')
    (out/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
    refs={str(s.relative_to(out)):digest(s) for folder in ('source','original-reference') for s in (out/folder).rglob('*') if s.is_file() and '__pycache__' not in s.parts}
    (out/'REFERENCE_CHECKSUMS.json').write_text(json.dumps(refs,indent=2)+'\n')
    package(out)

if __name__=='__main__':main()
