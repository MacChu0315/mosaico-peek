#!/usr/bin/env python3
"""Target ABI plus built ELF/images. No device connection or installation."""
import argparse,hashlib,json,re,shlex,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'projects/peek/build';OUT=ROOT/'evidence/eye-ui'
def run(args,**kw):return subprocess.check_output(list(map(str,args)),text=True,**kw)
def fp(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path,default=OUT);args=parser.parse_args();OUT=args.output_dir;OUT.mkdir(parents=True,exist_ok=True)
    db=json.loads((BUILD/'compile_commands.json').read_text());entry=next(e for e in db if e['file'].endswith('/src/eye_pack.c'));cmd=shlex.split(entry['command']);compiler=Path(cmd[0]);obj=BUILD/'eye-memory.o';binary=BUILD/'eye-memory.bin'
    for key in ['-o','-MF','-MT']:
        if key in cmd:
            n=cmd.index(key);cmd[n+1]=str(obj if key!='-MF' else obj.with_suffix('.d'))
    cmd[-1]=str(ROOT/'tools/eye_memory_layout.c');subprocess.run(cmd,cwd=entry['directory'],check=True)
    subprocess.run([str(compiler).replace('-gcc','-objcopy'),'--dump-section','.rodata.eye_budget='+str(binary),str(obj)],check=True)
    names=['renderer_internal_struct','ROM_inflater_explicit_PSRAM','frame_RGBA_explicit_PSRAM','eye_plus_two_lids_capacity_explicit_PSRAM','shared_UI_struct','texture_descriptors_RODATA'];sizes=dict(zip(names,struct.unpack('<6I',binary.read_bytes())))
    symbols=run([str(compiler).replace('-gcc','-nm'),'-S','--size-sort',BUILD/'peek.elf']);assets=[dict(symbol=m[4],bytes=int(m[2],16)) for l in symbols.splitlines() if (m:=re.fullmatch(r'([0-9a-f]+)\s+([0-9a-f]+)\s+([rRdD])\s+(eye_\w+)',l))]
    sections=run([str(compiler).replace('-gcc','-readelf'),'-W','-S',BUILD/'peek.elf']);(OUT/'idf-sections.txt').write_text(sections)
    description=json.loads((BUILD/'project_description.json').read_text());cfg=Path(description['config_file']).read_text().splitlines();config=[l for l in cfg if re.match(r'(CONFIG_(PEEK_|SPIRAM_|APP_PROJECT_VER|ESP_MAIN_TASK_STACK_SIZE)|# CONFIG_PEEK_)',l)]
    images={n:fp(BUILD/n) for n in ['peek.bin','ui_apps.bin','peek.elf','peek.map']};assert images['peek.bin']['bytes']<0xcf0000 and images['ui_apps.bin']['bytes']<=0x100000
    revision=re.search(r'PEEK_SOURCE_REVISION \"([0-9a-f]{40})\"',(BUILD/'peek_build_revision.h').read_text())[1]
    report=dict(source_revision=revision,version=description['project_version'],sdkconfig=Path(description['config_file']).name,flash=dict(images=images,ota_0_bytes=0xcf0000,ota_0_free_bytes=0xcf0000-images['peek.bin']['bytes'],retained_factory_bytes=0x1c0000,fits_retained_factory=False,ui_partition_bytes=0x100000,linked_eye_RODATA_symbols=assets,linked_eye_RODATA_bytes=sum(a['bytes'] for a in assets),lossless_streams=json.loads((BUILD/'eye-generated/eye_pack.json').read_text()),partition_changed=False),ram=dict(target_abi='ESP32-S31 GCC16.1.0, actual source/compile command; compile only',sizes=sizes,shared_UI_growth_from_9a25653_bytes=sizes['shared_UI_struct']-9712,new_renderer_explicit_PSRAM=sizes['ROM_inflater_explicit_PSRAM']+sizes['frame_RGBA_explicit_PSRAM']+sizes['eye_plus_two_lids_capacity_explicit_PSRAM'],dragon_renderer_retained_if_selected_bytes=3929120,framebuffer_RGB565_one_plane=460800,notes=['Only current theme frame/eye/two lids are decoded; all three themes compressed in app RODATA.','Existing XIP_FROM_PSRAM includes Flash text/RODATA mapping/copy budget; decoded renderer PSRAM is additional. See ELF sections and actual sdkconfig.','Renderer allocations use explicit SPIRAM without internal fallback. C state uses internal calloc.','Dragon renderer is lazy and retained after first dragon selection; switching back does not allocate it again. Both renderers may coexist.','GSP scene/framebuffers, SDK stacks/heaps/queue and switching allocation peaks are additional; no device allocator/free/largest-block or peak-runtime measurement.','Full480 eye shader and two-layer premultiplied lid blend; no new detail reduction.']),config=config,physical_runtime_measured=False)
    (OUT/'resource-budget.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(app_bytes=images['peek.bin']['bytes'],eye_RODATA_bytes=report['flash']['linked_eye_RODATA_bytes'],new_renderer_explicit_PSRAM=report['ram']['new_renderer_explicit_PSRAM'],internal_renderer_bytes=sizes['renderer_internal_struct']),indent=2))
if __name__=='__main__':main()
