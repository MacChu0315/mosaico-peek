#!/usr/bin/env python3
"""Validate the actual Peek0.2 update, configuration, resources and partitions offline."""
import argparse,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    if not __debug__:raise SystemExit('Run validation without Python -O')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--build-dir',type=Path,default=ROOT/'projects/peek/build')
    p.add_argument('--output',type=Path)
    p.add_argument('--require-clean-source',action='store_true')
    args=p.parse_args();build=args.build_dir.resolve()
    utils=ROOT.parent/'esp-mosaico-vibe-iris02/submodule/esp-mosaico-utils'
    pin=json.loads((ROOT/'dependencies.json').read_text())['utils']['commit']
    assert subprocess.check_output(['git','-C',str(utils),'rev-parse','HEAD'],text=True).strip()==pin
    sys.path.insert(0,str(utils/'ESP-Iris/components/esp_iris/tools'))
    from iris_gateway.system_update import load_system_update_bundle
    from iris_gateway.firmware import inspect_firmware_image
    bundle=load_system_update_bundle(args.bundle)
    assert bundle.manifest['schema']=='esp-iris-system-update/0.2'
    assert bundle.chip_id==32 and bundle.flash_size==0x1000000
    assert not bundle.signature and not bundle.key_id
    assert bundle.manifest['minimum_recovery_version']=='0.2.0'
    desc=json.loads((build/'project_description.json').read_text())
    config=Path(desc['config_file']).read_text().splitlines()
    for setting in ('CONFIG_ESP_IRIS_PRODUCT_CONTRACT="esp-mosaico/v2"',
                    'CONFIG_ESP_IRIS_LAYOUT_ID="mosaico-retained-test-2m-v2"',
                    'CONFIG_ESP_IRIS_RECOVERY_ABI=2','CONFIG_TINYUSB_CDC_COUNT=2',
                    'CONFIG_ESP_IRIS_FIRMWARE_ROLE=1','CONFIG_ESP_IRIS_OTA_DEFAULT_VIA_RECOVERY=y',
                    '# CONFIG_ESP_IRIS_OTA is not set','CONFIG_ESPTOOLPY_FLASHMODE_QIO=y',
                    'CONFIG_PEEK_CHARACTER=0','CONFIG_PEEK_EYE_SAMPLE_STEP=2',
                    'CONFIG_PEEK_GAZE_FLIP_X=y','CONFIG_PEEK_GAZE_FLIP_Y=y',
                    'CONFIG_PEEK_AUTO_ORIENTATION=y','CONFIG_PEEK_IMU_MOUNT_QUARTERS=0'):
        assert setting in config,setting
    version=next(s.split('=',1)[1].strip('"') for s in config if s.startswith('CONFIG_APP_PROJECT_VER='))
    assert version==desc['project_version']==bundle.manifest['release']=='1.2.0'
    components={c.kind.name.lower():c for c in bundle.components}
    assert len(bundle.components)==3 and set(components)=={'partition_table','application','data'}
    for kind,offset,name in [('partition_table',0x8000,'partition_table/partition-table.bin'),
                             ('application',0x210000,'peek.bin'),('data',0xf00000,'ui_apps.bin')]:
        c=components[kind];raw=(build/name).read_bytes()
        if kind=='partition_table':assert len(raw)==3072;raw=raw.ljust(4096,b'\xff')
        assert c.flags==0 and c.target_offset==offset and c.data==raw,name
    assert components['partition_table'].sha256.hex()==bundle.target_layout_sha256
    table={};raw=(build/'partition_table/partition-table.bin').read_bytes()
    for at in range(0,len(raw)-31,32):
        magic,kind,subtype,offset,size,label,flags=struct.unpack_from('<HBBII16sI',raw,at)
        if magic!=0x50aa:break
        table[label.rstrip(b'\0').decode()]=[kind,subtype,offset,size,flags]
    assert 'factory' not in table and 'ota_0' not in table
    for name,row in {'vibe_mode':[0,0x20,0x20000,0x1c0000,0],
                     'main_app':[0,0x10,0x210000,0xcf0000,0],
                     'nvs':[1,2,0x200000,0x10000,0],
                     'sysmeta':[1,2,0xc000,0x14000,0],
                     'coredump':[1,3,0x1e0000,0x20000,0],
                     'ui_apps':[1,0x40,0xf00000,0x100000,0]}.items():assert table[name]==row,name
    assert components['application'].size<=table['main_app'][3]
    assert components['data'].size<=table['ui_apps'][3]
    firmware=inspect_firmware_image(components['application'].data)
    assert firmware.project_name=='peek' and firmware.version==version
    assert hashlib.sha256((build/'peek.elf').read_bytes()).hexdigest()==firmware.elf_sha256
    assert b'night_owl' not in components['application'].data
    assert hashlib.sha256((build/'ui_apps.bin').read_bytes()).hexdigest()=='97d48a61cfbe44182b6794e6d0a74dc6a8a5406e0f8670dbd58c081cab6bc8e7'
    expected=json.loads((ROOT/'evidence/render-v111/firmware/resource-budget.json').read_text())['flash']['lossless_streams']
    assert json.loads((build/'eye-generated/eye_pack.json').read_text())==expected
    source=re.search(r'PEEK_SOURCE_REVISION "([0-9a-f]{40})"',(build/'peek_build_revision.h').read_text())[1]
    assert source.encode() in components['application'].data
    assert source==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','src','projects/peek','assets','cmake','tools','dependencies.json','.mosaico.json'],cwd=ROOT,text=True).strip()
    if args.require_clean_source:assert not dirty,'Commit source/configuration before delivery rebuild'
    report=dict(passed=True,release=version,schema=bundle.manifest['schema'],minimum_recovery_version='0.2.0',
                source_revision=source,source_matches_HEAD=True,source_worktree_clean=not bool(dirty),ELF_sha256=firmware.elf_sha256,bundle_sha256=hashlib.sha256(args.bundle.read_bytes()).hexdigest(),
                bundle_bytes=args.bundle.stat().st_size,partitions=table,
                components=[dict(kind=k,bytes=c.size,offset=c.target_offset,sha256=c.sha256.hex()) for k,c in components.items()],
                visual_resources_identical_to_1_1_1=True,
                scope='Official0.2 parser, actual images/config/layout/resources; no device or server acceptance claimed')
    text=json.dumps(report,indent=2)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    print(text)
if __name__=='__main__':main()
