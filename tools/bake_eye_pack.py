#!/usr/bin/env python3
"""Validate immutable handoff; losslessly encode RGBA into build-local streams."""
import argparse,hashlib,json,zlib
from pathlib import Path
from PIL import Image
import PIL
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'assets/eye-pack'
def bake(output):
    for line in (PACK/'CHECKSUMS.sha256').read_text().splitlines():
        digest,name=line.split(None,1);name=name.lstrip('* ')
        if name.startswith('evidence/'):continue
        p=PACK/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Source checksum mismatch: '+name)
    if ROOT==output.resolve() or ROOT not in output.resolve().parents:raise ValueError('Output must be inside a project build directory')
    rel=output.resolve().relative_to(ROOT)
    if not rel.parts[0].startswith('build') and not (rel.parts[0]=='projects' and 'build' in rel.parts):raise ValueError('Generated output belongs in a build directory')
    manifest=json.loads((PACK/'assets/manifest.json').read_text());chunks=['/* Generated lossless RGBA streams; do not edit. */'];themes=[];report=[]
    for theme in manifest['themes']:
        entries=[];sizes=[]
        for name in ['frame','eye']+[f'lid_{i:02}' for i in range(9)]:
            path=PACK/'assets/processed'/theme['id']/(name+'.png')
            with Image.open(path) as im:
                if im.mode!='RGBA':raise ValueError(str(path)+' must be RGBA')
                raw=im.tobytes();w,h=im.size
            blob=zlib.compress(raw,9);symbol='eye_'+theme['id']+'_'+name
            chunks.append('static const unsigned char '+symbol+'[] = {\n'+ '\n'.join(','.join(str(b) for b in blob[i:i+32])+',' for i in range(0,len(blob),32))+'\n};')
            entries.append('{'+symbol+f',sizeof({symbol}),{w},{h}'+'}');sizes.append(len(blob))
        origin=theme['eye_origin'];amp=theme['max_gaze_translation_px']
        if origin!=theme['lid_origin']:raise ValueError('This adapter requires shared eye/lid origins')
        if theme['layer_bbox']['w']>507 or theme['layer_bbox']['h']>272:raise ValueError('Layer exceeds renderer capacity')
        themes.append('{"'+theme['id']+'",'+','.join(map(str,origin+amp))+',{'+','.join(entries)+'}}')
        report.append(dict(theme=theme['id'],compressed_bytes=sum(sizes),png_bytes=sum((PACK/'assets/processed'/theme['id']/(n+'.png')).stat().st_size for n in ['frame','eye']+[f'lid_{i:02}' for i in range(9)]),max_resident_rgba=480*480*4+3*theme['layer_bbox']['w']*theme['layer_bbox']['h']*4))
    chunks.append('static const eye_theme_t eye_themes[] = {\n'+',\n'.join(themes)+'\n};')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text('\n'.join(chunks)+'\n')
    output.with_suffix('.json').write_text(json.dumps(dict(pillow=PIL.__version__,zlib=zlib.ZLIB_RUNTIME_VERSION,format='zlib RGBA8888 lossless; no resizing or palette',themes=report,total_compressed_bytes=sum(t['compressed_bytes'] for t in report)),indent=2)+'\n')
    print('Eye pack lossless streams:',sum(t['compressed_bytes'] for t in report),'bytes')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();bake(a.output)
