#!/usr/bin/env python3
"""Curate current approved artwork for publicity preparation; no device access."""
import argparse,hashlib,html,io,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
LABELS={'dragon':'怪物眼','deep_sea':'深海眼','mechanical':'机械眼'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--native',type=Path,default=ROOT/'evidence/promo-assets-20261026/native')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    edit=out.with_name(out.name+'-editable');edit.mkdir(exist_ok=False)
    rows=[];editable=[]
    def copy(src,dst,kind,role=None,base=out):
        src=ROOT/src;target=base/dst;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
        assert sha(src)==sha(target)
        record=dict(file=dst,kind=kind,role=role,source=str(src.relative_to(ROOT)),sha256=sha(target),bytes=target.stat().st_size)
        if target.suffix.lower()=='.png':
            with Image.open(target) as im:
                record.update(width=im.width,height=im.height,mode=im.mode)
                if 'A' in im.getbands():record['alpha_extrema']=im.getchannel('A').getextrema()
        (rows if base==out else editable).append(record)
    # Runtime-selected layers only; copy original alpha/RGB bytes unchanged.
    for name in ('skin.png','iris.png'):
        copy('assets/dragon/'+name,'04_current_layers/dragon/'+name,'current texture','dragon')
        copy('review-inputs/peek-phase2-inputs/approved-dragon/assets/'+name,'05_high_res_sources/dragon/'+name,'original texture, not complete UI','dragon')
    copy('assets/dragon-sclera-c/submission/sclera.png','04_current_layers/dragon/sclera_C.png','current sclera texture','dragon')
    copy('assets/dragon-sclera-c/source/layers/01-ai-original.png','05_high_res_sources/dragon/sclera_C_original.png','original texture','dragon')
    for p in sorted((ROOT/'assets/deep-sea-r2/processed').rglob('*.png')):
        if p.name=='rim_restore_disabled.png':continue
        copy(str(p.relative_to(ROOT)),'04_current_layers/deep_sea/'+str(p.relative_to(ROOT/'assets/deep-sea-r2/processed')),'current layer','deep_sea')
    for p in sorted((ROOT/'assets/deep-sea-r2/masks').glob('*.png')):
        copy(str(p.relative_to(ROOT)),'04_current_layers/deep_sea/working_masks/'+p.name,'processing mask, not UI overlay','deep_sea')
    for p in sorted((ROOT/'assets/organic-eyes-source-recovery/assets/raw/deep_sea').glob('*.png')):
        copy(str(p.relative_to(ROOT)),'05_high_res_sources/deep_sea/'+p.name,'historical original input; prefer current R2 for UI','deep_sea')
    copy('assets/organic-eyes-source-recovery/reference/deep_sea/membrane_v3.png','05_high_res_sources/deep_sea/membrane_V3_reference_NOT_A_LAYER.png','approved direction reference, not membrane layer','deep_sea')
    copy('assets/eye-pack/assets/processed/mechanical/frame.png','04_current_layers/mechanical/frame_A.png','selected fixed socket A','mechanical')
    copy('assets/mechanical-c/assets/processed/eye_surface.png','04_current_layers/mechanical/eye_surface_C.png','current eye surface','mechanical')
    for p in sorted((ROOT/'assets/mechanical-c/assets/processed/shutter').glob('*.png')):
        copy(str(p.relative_to(ROOT)),'04_current_layers/mechanical/shutter/'+p.name,'current rotating shutter','mechanical')
    for name in ('concept-C-triptych.png','generated-metal-backing.png'):
        copy('assets/mechanical-c/assets/originals/'+name,'05_high_res_sources/mechanical/'+name,'concept/material original, not current full UI','mechanical')
    copy('assets/eye-pack/assets/originals/mechanical.png','05_high_res_sources/mechanical/original_socket_A_portrait.png','original socket context; old central eye is not current C','mechanical')
    provenance={
        'dragon/sclera_SOURCE.md':'assets/dragon-sclera-c/SOURCE.md',
        'dragon/original_textures_SOURCE.md':'review-inputs/peek-phase2-inputs/approved-dragon/SOURCE_README.md',
        'dragon/texture_metadata.json':'assets/dragon/metadata.json',
        'dragon/sclera_provenance.json':'assets/dragon-sclera-c/source/provenance.json',
        'dragon/sclera_generation_prompt.txt':'assets/dragon-sclera-c/source/imagegen-prompt.txt',
        'dragon/original_texture_prompts.json':'review-inputs/peek-phase2-inputs/approved-dragon/art-prompts.json',
        'dragon/current_adaptation.json':'assets/dragon-sclera-adaptation.json',
        'deep_sea/recovered_originals_SOURCE.md':'assets/organic-eyes-source-recovery/SOURCES.md',
        'deep_sea/R2_recipe.json':'assets/deep-sea-r2/recipe.json',
        'deep_sea/current_adaptation.json':'assets/deep-sea-adaptation.json',
        'mechanical/C_SOURCES.md':'assets/mechanical-c/SOURCES.md',
        'mechanical/selected_socket_A.json':'assets/mechanical-c-adaptation.json',
        'mechanical/generation_record.json':'assets/mechanical-c/source/generation-record.json',
        'mechanical/concept_prompt.txt':'assets/mechanical-c/source/concept-C-generation-prompt.txt',
        'mechanical/backing_prompt.txt':'assets/mechanical-c/source/backing-generation-prompt.txt',
        'original_pack_SOURCES_AND_LICENSES.md':'assets/eye-pack/assets/SOURCES_AND_LICENSES.md',
        'original_pack_software_LICENSE.txt':'assets/eye-pack/LICENSE',
    }
    for dst,src in provenance.items():copy(src,'06_provenance/'+dst,'retained provenance; historical statements may refer to old packages')
    # Keep old editable containers separate so their unselected mount is not used as hero art.
    for name in ('sclera-master.psd','sclera-master.ora'):
        copy('assets/dragon-sclera-c/source/'+name,'dragon_sclera_only/'+name,'sclera-only editable container','dragon',edit)
    for suffix in ('psd','ora'):
        copy('assets/mechanical-c/source/mechanical_c.'+suffix,'mechanical/ARCHIVED_C_WITH_UNSELECTED_MOUNT.'+suffix,'archived editable container; replace mount with selected A','mechanical',edit)
    for name in ('shutter-rig.svg','shutter-rig.json'):
        copy('assets/mechanical-c/source/shutter/'+name,'mechanical/'+name,'shutter reference (SVG embeds raster)','mechanical',edit)
    copy('assets/eye-pack/assets/processed/mechanical/frame.png','mechanical/CURRENT_frame_A.png','current selected replacement mount','mechanical',edit)
    copy('assets/mechanical-c/source/editable-source-notes.json','mechanical/original_editable_notes.json','original editable notes','mechanical',edit)
    copy('assets/dragon-sclera-c/source/README.md','dragon_sclera_only/original_README.md','original editable notes','dragon',edit)
    # Export fresh production-C pixels. Dragon uses the approved step2 path in C.
    work=ROOT/'build-host/promo-export';work.mkdir(exist_ok=True)
    source=(ROOT/'tools/dragon_snapshot.c').read_text()
    source=source.replace('!dragon_renderer_prepare(r,&p)','!dragon_renderer_set_sample_step(r,2)||!dragon_renderer_prepare(r,&p)')
    write(work/'dragon_snapshot240.c',source)
    subprocess.run(['cc','-O2','-ffp-contract=off','-I',str(ROOT/'src'),str(work/'dragon_snapshot240.c'),str(ROOT/'build-host/libdragon.a'),'-lm','-o',str(work/'dragon_snapshot240')],check=True)
    poses=[('center',0,0),('left',-.78,0),('right',.78,0),('up',0,-.58),('down',0,.58),('up_left',-.78,-.58),('up_right',.78,-.58),('down_left',-.78,.58),('down_right',.78,.58)]
    for role in LABELS:
        states=[(n,x,y,0,0,0) for n,x,y in poses]
        states += [('closed',0,0,1,1,1),('membrane_half' if role=='deep_sea' else 'closure_half',0,0,.5,.5,0)]
        for name,x,y,blink,membrane,lid in states:
            if role=='dragon':command=[str(work/'dragon_snapshot240'),str(x),str(y),str(blink),'.69','.072','.16']
            else:command=[str(ROOT/'build-host/eye_snapshot'),str({'deep_sea':1,'mechanical':2}[role]),str(x),str(y),str(blink)]
            if role=='deep_sea':command += [str(membrane),str(lid)]
            raw=subprocess.check_output(command);im=Image.open(io.BytesIO(raw));assert im.size==(480,480)
            rel=f'01_ready_to_use/{role}/{name}.png';path=out/rel;path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
            rows.append(dict(file=rel,kind='production C controlled-pose export, not device capture',role=role,width=480,height=480,mode='RGB',sha256=sha(path),bytes=path.stat().st_size,parameters=dict(gaze_x=x,gaze_y=y,blink=blink,membrane=membrane,lid=lid,orientation=0,dragon_sample_step=2 if role=='dragon' else None)))
        movie=args.native.resolve()/(role+'.mp4');meta=json.loads((args.native.resolve()/(role+'.json')).read_text());assert meta['orientation']==0
        copy(str(movie.relative_to(ROOT)),f'02_native_motion/{role}.mp4','native GSP; synthetic complete temperature arrays; not physical-device video',role)
        timeline=dict(source=meta['source'],orientation=0,logical_start_ms=meta['logical_start_ms'],capture_wall_seconds=meta['capture_wall_seconds'],timing=meta['timing'],frames=[dict(wall_s=f['wall_s'],logical_ms=f['state']['result']['now_ms'],mode=f['state']['role']['mode'],sleeping=f['state']['role']['sleeping'],waking=f['state']['role']['waking'],pose=f['state']['render_pose'],layers=f['state']['render_layers']) for f in meta['frames']])
        write(out/f'02_native_motion/{role}-timeline.json',json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
    for role,src,report in [
        ('dragon','evidence/dragon-sclera/device-closed/closed.png','evidence/dragon-sclera/device-closed/report.json'),
        ('deep_sea','evidence/render-v111/device-after/deepsea-closed-pixels/closed.png','evidence/render-v111/device-after/deepsea-closed-pixels/report.json'),
        ('mechanical','evidence/render-v111/device-after/mechanical-closed-pixels/closed.png','evidence/render-v111/device-after/mechanical-closed-pixels/report.json')]:
        copy(src,f'03_device_captures/{role}-closed.png','actual framebuffer capture, not camera photo',role)
        d=json.loads((ROOT/report).read_text());write(out/f'03_device_captures/{role}-metadata.json',json.dumps(dict(version=d['version'],orientation=d['orientation'],kind='actual device framebuffer; not physical photograph/video',historical=role=='dragon',appearance_matches_current=True,source=src),ensure_ascii=False,indent=2)+'\n')
    # Copy authoritative human-facing guidance from project docs, not old upstream READMEs.
    for name in ('START_HERE.md','AGENT_BRIEF.md','LAYER_GUIDE.md'):
        copy('docs/promo/'+name,name,'current package guidance')
    copy('docs/promo/EDITABLE_README.md','README.md','editable-package guidance',base=edit)
    for p in (out/'06_provenance').rglob('*'):
        if p.is_file():target=edit/'provenance'/p.relative_to(out/'06_provenance');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    cards=[]
    for role,label in LABELS.items():
        cards.append(f'<section><h2>{label}</h2><a href="01_ready_to_use/{role}/center.png"><img width="240" height="240" src="01_ready_to_use/{role}/center.png" alt="{label}正视"></a><p>生产 C 静态导出 · 480×480</p><video controls preload="metadata" width="320" src="02_native_motion/{role}.mp4"></video><p>原生 GSP／合成温度输入；不是实机录像。</p></section>')
    gallery=''.join(f'<figure><a href="{r["file"]}"><img loading="lazy" width="160" height="160" src="{r["file"]}" alt="{html.escape(r["file"])}"></a><figcaption>{html.escape(r["file"])}</figcaption></figure>' for r in rows if r['file'].startswith('01_ready_to_use/'))
    write(out/'index.html','<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Mosaico Peek 素材索引</title><style>body{font:16px system-ui;margin:32px;color:#20242b;background:#f4f5f7}h1{margin-bottom:8px}main,.grid{display:flex;flex-wrap:wrap;gap:24px}section,figure{background:white;padding:16px;border-radius:10px;margin:0}img,video{display:block;max-width:100%;object-fit:contain}figcaption{font-size:12px;max-width:180px;overflow-wrap:anywhere}a{color:#164b8c}</style><h1>Mosaico Peek · 当前三角色素材</h1><p>稳定版本1.1.1 · 2026-10-26 · 仅作宣传准备，未发布</p><p><a href="START_HERE.md">先读使用说明</a> · <a href="AGENT_BRIEF.md">给其他 agent 的任务说明</a> · <a href="LAYER_GUIDE.md">图层与来源</a></p><main>'+''.join(cards)+'</main><h2>静态姿态</h2><div class="grid">'+gallery+'</div></html>')
    write(out/'manifest.json',json.dumps(dict(version='1.1.1',firmware_source='effb682e2a35a6b6a4e862f990d6eb5219831a9d',repository_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),roles=list(LABELS),selection='dragon sclera C / deep-sea R2 / mechanical C + socket A',files=rows),ensure_ascii=False,indent=2)+'\n')
    write(edit/'manifest.json',json.dumps(dict(kind='optional archived editable source; read README before use',files=editable),ensure_ascii=False,indent=2)+'\n')
    for base in (out,edit):
        members=sorted(p for p in base.rglob('*') if p.is_file())
        write(base/'SHA256SUMS',''.join(sha(p)+'  '+p.relative_to(base).as_posix()+'\n' for p in members))
        zip_path=base.with_name(base.name+'.zip');assert not zip_path.exists()
        with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(base.rglob('*')):
                if p.is_file():z.write(p,base.name+'/'+p.relative_to(base).as_posix())
        with zipfile.ZipFile(zip_path) as z:
            assert z.testzip() is None
            for line in (base/'SHA256SUMS').read_text().splitlines():
                digest,name=line.split('  ',1);assert hashlib.sha256(z.read(base.name+'/'+name)).hexdigest()==digest
        write(zip_path.with_suffix('.zip.sha256'),sha(zip_path)+'  '+zip_path.name+'\n')
        print(json.dumps(dict(path=str(zip_path),bytes=zip_path.stat().st_size,sha256=sha(zip_path),files=len(members)+1),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
