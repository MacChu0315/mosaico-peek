#!/usr/bin/env python3
"""Export a self-contained art-only handoff; never change retained source assets."""
import argparse,hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review/eye-surface-art-handoff-v1'
PACK=ROOT/'assets/eye-pack';GEN=ROOT/'build-host/eye-generated'
def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--package-existing',action='store_true',help='verify and ZIP an exported, preview-checked handoff')
    args=parser.parse_args();OUT=args.output.resolve()
    if ROOT/'review' not in OUT.parents:parser.error('Export belongs below this project review/ directory')
    if args.package_existing:
        refs=json.loads((OUT/'reference_checksums.json').read_text())
        for name,digest in refs.items():assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==digest,name
        result=json.loads((OUT/'rejected-proof/verification.json').read_text())
        assert result['technical_checks']=='passed' and result['visual_approved'] is False
        metadata=json.loads((OUT/'HANDOFF_MANIFEST.json').read_text())
        metadata['export_source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        (OUT/'HANDOFF_MANIFEST.json').write_text(json.dumps(metadata,indent=2)+'\n')
        paths=sorted(p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='CHECKSUMS.sha256')
        (OUT/'CHECKSUMS.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(OUT))+'\n' for p in paths))
        paths.append(OUT/'CHECKSUMS.sha256');archive=OUT.with_suffix('.zip')
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for path in paths:z.write(path,OUT.name+'/'+str(path.relative_to(OUT)))
        with zipfile.ZipFile(archive) as z:assert z.testzip() is None
        digest=hashlib.sha256(archive.read_bytes()).hexdigest();archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n')
        print(f'{archive}\n{archive.stat().st_size} bytes; SHA256 {digest}');return
    geometry=json.loads((GEN/'eye_pack.json').read_text())
    if any(t.get('rotating_shutter') for t in geometry['themes']):raise RuntimeError('Legacy1.0.6 handoff export requires its retained build; current mechanical C is a different artwork contract. Existing ZIP remains valid.')
    if OUT.exists():raise RuntimeError(f'Refusing to overwrite existing handoff: {OUT}')
    OUT.mkdir(parents=True)
    for name in ['README.md','check_preview.py']:copy(ROOT/'tools/eye_art_handoff'/name,OUT/name)
    # Freeze the already independently checked reference compositor; no detector is copied.
    source=(ROOT/'tests/test_eye_pixels.py').read_text().split('def main():')[0]
    source=source.replace('ROOT=Path(__file__).resolve().parents[1]', 'ROOT=Path(__file__).resolve().parent')
    source=source.replace("PACK=ROOT/'assets/eye-pack';OUT=ROOT/'evidence/eye-ui/motion';GENERATED=ROOT/'build-host/eye-generated'", "PACK=ROOT/'reference/source_pack';OUT=ROOT/'proof';GENERATED=ROOT/'submission'")
    source=source.replace("GENERATED/(theme['id']+'-wide-eye.png')", "GENERATED/theme['id']/'eye_surface.png'")
    source=source.replace("GENERATED/'eye_pack.json'", "ROOT/'reference/runtime_geometry.json'")
    assert 'build-host' not in source
    (OUT/'reference_renderer.py').write_text(source)
    copy(GEN/'eye_pack.json',OUT/'reference/runtime_geometry.json')
    copy(ROOT/'src/eye_projection.h',OUT/'reference/eye_projection.h')
    for name in ['assets/manifest.json','assets/SOURCES_AND_LICENSES.md','assets/GENERATION.md','LICENSE']:
        copy(PACK/name,OUT/'reference/source_pack'/name)
    themes=json.loads((PACK/'assets/manifest.json').read_text())['themes']
    x,y=np.meshgrid(np.arange(480),np.arange(480))
    for t in themes:
        name=t['id'];folder=PACK/'assets/processed'/name
        for file in folder.glob('*.png'):copy(file,OUT/'reference/source_pack/assets/processed'/name/file.name)
        copy(PACK/'assets/originals'/(name+'.png'),OUT/'reference/source_pack/assets/originals'/(name+'.png'))
        copy(GEN/(name+'-wide-eye.png'),OUT/'rejected'/name/'eye_surface.png')
        for direction in ['neutral','right','left','up','down','diagonal']:
            copy(ROOT/'evidence/eye-ui/motion'/f'{name}-{direction}.png',OUT/'rejected-native'/f'{name}-{direction}.png')
        guides=OUT/'guides'/name;guides.mkdir(parents=True)
        locked=np.asarray(Image.open(folder/'aperture_mask.png').getchannel('A'))>0
        Image.fromarray((locked*255).astype('uint8'),'L').save(guides/'locked_mask.png')
        Image.fromarray((~locked*255).astype('uint8'),'L').save(guides/'editable_mask.png')
        frame=np.asarray(Image.open(folder/'frame.png'));yy,xx=np.nonzero(frame[:,:,3]<255);cx,cy=t['eye_center']
        nx=(xx-cx)/233;ny=(yy-cy)/233;nz=np.sqrt(np.maximum(0,1-nx*nx-ny*ny));sampled=np.zeros((480,480),dtype=bool)
        for gx in np.linspace(-1,1,17):
            for gy in np.linspace(-1,1,17):
                yaw=gx*np.arcsin(120/233);pitch=gy*np.arcsin(80/233)
                lx=np.cos(yaw)*nx-np.sin(yaw)*nz;az=np.sin(yaw)*nx+np.cos(yaw)*nz;ly=np.cos(pitch)*ny-np.sin(pitch)*az
                u=np.floor(cx+233*lx).astype(int);v=np.floor(cy+233*ly).astype(int)
                for dx in [0,1]:
                    for dy in [0,1]:sampled[np.clip(v+dy,0,479),np.clip(u+dx,0,479)]=True
        expanded=np.asarray(Image.fromarray((sampled*255).astype('uint8'),'L').filter(ImageFilter.MaxFilter(5)))>0
        priority=expanded&~locked
        Image.fromarray((priority*255).astype('uint8'),'L').save(guides/'priority_paint_mask.png')
        neutral=Image.open(folder/'neutral.png').convert('RGB');orange=Image.new('RGB',(480,480),(255,125,0));mask=Image.fromarray((priority*130).astype('uint8'),'L');Image.composite(orange,neutral,mask).save(guides/'overlay.png')
    (OUT/'submission').mkdir();(OUT/'submission/README.txt').write_text('Place authored <theme>/eye_surface.png here. No approved replacement artwork is supplied.\n')
    refs={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for base in ['reference','guides'] for p in (OUT/base).rglob('*') if p.is_file()}
    (OUT/'reference_checksums.json').write_text(json.dumps(refs,indent=2)+'\n')
    manifest=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),installed_source='fd637cc133b132fe2a3f81661a577377beba57ed',source_zip_sha256=(ROOT/'evidence/eye-ui/input-archive.sha256').read_text().strip(),user_acceptance=dict(both_dragon_axes='accepted on1.0.6',motion_range='accepted',generated_hidden_surface='rejected: visually ugly'),not_included='Original closed-eye design-reference and JS evidence are outside this eye-surface-only task; original frame/lids are included unchanged.',purpose='Artwork handoff only. No production integration or visual approval claim.')
    (OUT/'HANDOFF_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(OUT)
if __name__=='__main__':main()
