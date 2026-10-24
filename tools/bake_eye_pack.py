#!/usr/bin/env python3
"""Validate immutable handoff; losslessly encode RGBA into build-local streams."""
import argparse,hashlib,json,zlib,math
from pathlib import Path
from PIL import Image,ImageFilter
import PIL
ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'assets/eye-pack'
MOTION=ROOT/'assets/eye_motion.json'
MECHANICAL=ROOT/'assets/mechanical-c'
ADAPTATION=ROOT/'assets/mechanical-c-adaptation.json'
DEEP=ROOT/'assets/deep-sea-r2'
DEEP_ADAPTATION=ROOT/'assets/deep-sea-adaptation.json'
OWL=ROOT/'assets/night-owl-r2'
OWL_ADAPTATION=ROOT/'assets/night-owl-adaptation.json'
def expanded_eye(theme,recipe):
    folder=PACK/'assets/processed'/theme['id']
    neutral=Image.open(folder/'neutral.png').convert('RGBA')
    mask=Image.open(folder/'aperture_mask.png').getchannel('A')
    if neutral.size!=(480,480) or mask.size!=(480,480):raise ValueError('Expected480 source/mask')
    if neutral.getchannel('A').getextrema()!=(255,255):raise ValueError('Neutral must be opaque')
    alpha=mask.tobytes();original=neutral.tobytes();data=bytearray(original);cx,cy=theme['eye_center'];radius=recipe['sphere_radius_px']
    def valid(x,y):return 0<=x<480 and 0<=y<480 and alpha[y*480+x]>0
    # Available angular sectors on each half of each visible iris radius.
    tables=[]
    for side in (-1,1):
        maximum=max(r for r in range(radius+1) if valid(round(cx+side*r),cy))-3
        table=[]
        for r in range(radius+1):
            rr=min(r,maximum);limits=[]
            for vertical in (-1,1):
                last=0.0
                for degree in range(1,91):
                    angle=math.radians(degree)
                    if not valid(round(cx+side*rr*math.cos(angle)),round(cy+vertical*rr*math.sin(angle))):break
                    last=angle
                limits.append(last*.8)
            table.append((rr,*limits))
        tables.append(table)
    for y in range(480):
        for x in range(480):
            index=y*480+x
            if alpha[index]:continue
            dx,dy=x-cx,y-cy;r=math.hypot(dx,dy);radial=min(radius,round(r));colors=[]
            for side,table in zip((-1,1),tables):
                rr,top,bottom=table[radial];angle=(top if dy<0 else bottom)*abs(dy)/max(1,r)
                sx=round(cx+side*rr*math.cos(angle));sy=round(cy+(-1 if dy<0 else 1)*rr*math.sin(angle))
                if not valid(sx,sy):sx=round(cx+side*rr);sy=cy
                colors.append(original[(sy*480+sx)*4:(sy*480+sx)*4+3])
            weight=(dx/max(1,r)+1)/2
            for channel in range(3):data[index*4+channel]=round(colors[0][channel]*(1-weight)+colors[1][channel]*weight)
            data[index*4+3]=255
    backing=Image.frombytes('RGBA',(480,480),bytes(data)).filter(ImageFilter.GaussianBlur(recipe['guard_blur_radius_px']))
    backing.paste(neutral,(0,0),mask.point(lambda value:255 if value else 0))
    return backing,(0,0)

def bake(output):
    for line in (PACK/'CHECKSUMS.sha256').read_text().splitlines():
        digest,name=line.split(None,1);name=name.lstrip('* ')
        if name.startswith('evidence/'):continue
        p=PACK/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('Source checksum mismatch: '+name)
    for line in (MECHANICAL/'CHECKSUMS.sha256').read_text().splitlines():
        digest,name=line.split(None,1);name=name.lstrip('* ')
        if hashlib.sha256((MECHANICAL/name).read_bytes()).hexdigest()!=digest:raise ValueError('Mechanical source checksum mismatch: '+name)
    for organic,recipe_path in ((DEEP,DEEP_ADAPTATION),(OWL,OWL_ADAPTATION)):
        for line in (organic/'CHECKSUMS.sha256').read_text().splitlines():
            digest,name=line.split(None,1);name=name.lstrip('* ')
            if hashlib.sha256((organic/name).read_bytes()).hexdigest()!=digest:raise ValueError('Organic R2 source checksum mismatch: '+str(organic/name))
        selected=json.loads(recipe_path.read_text())
        if hashlib.sha256((organic/selected['surface']).read_bytes()).hexdigest()!=selected['surface_sha256']:raise ValueError('Selected organic R2 surface mismatch')
        if selected['sprite_origin']!=[0,128] or selected['sprite_size']!=[480,240] or selected['membrane_ms']!=[100,20,120] or selected['sleep_close_ms']!=450 or selected['wake_ms']!=150:raise ValueError('Unsupported organic presentation contract')
    if ROOT==output.resolve() or ROOT not in output.resolve().parents:raise ValueError('Output must be inside a project build directory')
    rel=output.resolve().relative_to(ROOT)
    if not rel.parts[0].startswith('build') and not (rel.parts[0]=='projects' and 'build' in rel.parts):raise ValueError('Generated output belongs in a build directory')
    adaptation=json.loads(ADAPTATION.read_text());frame_source=(ROOT/adaptation['fixed_frame_source']).resolve()
    if ROOT/'assets' not in frame_source.parents or hashlib.sha256(frame_source.read_bytes()).hexdigest()!=adaptation['sha256']:raise ValueError('Mechanical fixed frame source mismatch')
    recipe=json.loads(MOTION.read_text());amp=recipe['max_translation_px'];guard=recipe['guard_extra_px']
    if len(amp)!=2 or any(type(v) is not int or not 0<v<=160 for v in amp) or guard!=2 or recipe.get('guard_blur_radius_px')!=2 or recipe.get('sphere_radius_px')!=233:raise ValueError('Unsupported motion recipe')
    manifest=json.loads((PACK/'assets/manifest.json').read_text());chunks=['/* Generated lossless RGBA streams; do not edit. */'];themes=[];report=[]
    for theme in manifest['themes']:
        entries=[];sizes=[];rotating=theme['id']=='mechanical';dual=theme['id'] in ('night_owl','deep_sea');organic=OWL if theme['id']=='night_owl' else DEEP
        if rotating:backing,eye_origin=Image.open(MECHANICAL/'assets/processed/eye_surface.png').convert('RGBA'),(0,0)
        elif dual:backing,eye_origin=Image.open(organic/'processed/eye_surface.png').convert('RGBA'),(0,0)
        else:backing,eye_origin=expanded_eye(theme,recipe)
        output.parent.mkdir(parents=True,exist_ok=True);backing.save(output.parent/(theme['id']+'-wide-eye.png'))
        names=['frame','eye']+([f'membrane_{i:02}' for i in range(9)] if dual else [])+[f'lid_{i:02}' for i in range(9)]
        for name in names:
            path=PACK/'assets/processed'/theme['id']/(name+'.png')
            if rotating:path=MECHANICAL/'assets/processed'/('eye_surface.png' if name=='eye' else ('shutter/shutter_'+name[4:]+'.png' if name.startswith('lid_') else 'frame.png'))
            if rotating and name=='frame':path=frame_source
            if dual:path=organic/'processed'/('eye_surface.png' if name=='eye' else ('membrane/'+name+'.png' if name.startswith('membrane_') else ('lids/'+name+'.png' if name.startswith('lid_') else 'frame.png')))
            with Image.open(path) as im:
                if im.mode!='RGBA':raise ValueError(str(path)+' must be RGBA')
                if name=='eye':im=backing
                if dual and im.size!=((480,480) if name in ('frame','eye') else (480,240)):raise ValueError('Organic R2 layer size')
                if dual and name=='eye' and im.getchannel('A').getextrema()!=(255,255):raise ValueError('Organic R2 eye must be opaque')
                if rotating and im.size!=((240,240) if name.startswith('lid_') else (480,480)):raise ValueError('Mechanical C layer size')
                if rotating and name=='eye' and im.getchannel('A').getextrema()!=(255,255):raise ValueError('Mechanical C eye must be opaque')
                if dual:
                    # RGB under exactly-zero alpha has no contribution to any
                    # compositor. Normalize only those bytes in build output;
                    # preserve every source PNG and every visible color/alpha.
                    im=im.copy();im.paste((0,0,0,0),mask=im.getchannel('A').point(lambda a:255 if a==0 else 0))
                raw=im.tobytes();w,h=im.size
            blob=zlib.compress(raw,9);symbol='eye_'+theme['id']+'_'+name
            chunks.append('static const unsigned char '+symbol+'[] = {\n'+ '\n'.join(','.join(str(b) for b in blob[i:i+32])+',' for i in range(0,len(blob),32))+'\n};')
            entries.append('{'+symbol+f',sizeof({symbol}),{w},{h}'+'}');sizes.append(len(blob))
        origin=[0,128] if dual else [120,125] if rotating else theme['lid_origin']
        if theme['eye_origin']!=theme['lid_origin']:raise ValueError('This adapter requires shared eye/lid origins')
        if theme['layer_bbox']['w']>507 or theme['layer_bbox']['h']>272:raise ValueError('Layer exceeds renderer capacity')
        themes.append('{"'+theme['id']+'",'+','.join(map(str,origin+amp+list(eye_origin)+theme['eye_center']+[2 if dual else int(rotating)]))+',{'+','.join(entries)+'}}')
        report.append(dict(theme=theme['id'],eye_origin=list(eye_origin),lid_origin=origin,eye_size=list(backing.size),max_gaze_translation_px=amp,eye_center=theme['eye_center'],sphere_radius_px=recipe['sphere_radius_px'],fixed_frame_source=(str((organic/'processed/frame.png').relative_to(ROOT)) if dual else adaptation['fixed_frame_source'] if rotating else str((PACK/'assets/processed'/theme['id']/'frame.png').relative_to(ROOT))),rotating_shutter=rotating,dual_layers=dual,transparent_RGB_normalized=dual,layer_count=len(names),layer_size=([480,240] if dual else [240,240] if rotating else [theme['layer_bbox']['w'],theme['layer_bbox']['h']]),derived_eye_bytes=backing.width*backing.height*4,compressed_bytes=sum(sizes),png_bytes=(sum(p.stat().st_size for p in (organic/'processed').rglob('*.png') if p.name!='rim_restore_disabled.png') if dual else sum(p.stat().st_size for p in (MECHANICAL/'assets/processed').rglob('*.png'))-(MECHANICAL/'assets/processed/frame.png').stat().st_size+frame_source.stat().st_size if rotating else sum((PACK/'assets/processed'/theme['id']/(n+'.png')).stat().st_size for n in ['frame','eye']+[f'lid_{i:02}' for i in range(9)])),max_resident_rgba=(None if rotating else 480*480*4+backing.width*backing.height*4+2*(480*240 if dual else theme['layer_bbox']['w']*theme['layer_bbox']['h'])*4),shutter_float_RGB_bytes=(240*240*3*4 if rotating else 0),shutter_RGBA_decode_bytes=(240*240*4 if rotating else 0),shared_two_layer_capacity_bytes=2*507*272*4))
    chunks.insert(0,'#define EYE_PACK_EYE_BYTES '+str(max(t['derived_eye_bytes'] for t in report)))
    chunks.append('static const eye_theme_t eye_themes[] = {\n'+',\n'.join(themes)+'\n};')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text('\n'.join(chunks)+'\n')
    output.with_suffix('.json').write_text(json.dumps(dict(pillow=PIL.__version__,zlib=zlib.ZLIB_RUNTIME_VERSION,format='zlib RGBA8888; sources immutable; organic alpha0 RGB normalized in build output; no visible color/alpha loss, resizing or palette',motion_recipe=recipe,themes=report,total_compressed_bytes=sum(t['compressed_bytes'] for t in report)),indent=2)+'\n')
    print('Eye pack lossless streams:',sum(t['compressed_bytes'] for t in report),'bytes')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();bake(a.output)
