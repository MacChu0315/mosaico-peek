#!/usr/bin/env python3
"""Read immutable supplied sclera; generate lossless RGB888 in the build tree."""
import argparse, hashlib, json
from pathlib import Path
from PIL import Image
from bake_dragon import c_array
ROOT=Path(__file__).resolve().parents[1]
def bake(output,check=False):
    output=output.resolve()
    if ROOT==output or ROOT not in output.parents:raise ValueError('Output must be inside a project build directory')
    rel=output.relative_to(ROOT)
    if not (len(rel.parts)>1 and (rel.parts[0]=='build' or rel.parts[0].startswith('build-'))) and not (len(rel.parts)>3 and rel.parts[0]=='projects' and rel.parts[2]=='build'):raise ValueError('Generated output belongs in a build directory')
    recipe=json.loads((ROOT/'assets/dragon-sclera-adaptation.json').read_text())
    pack=ROOT/recipe['source_package'];source=pack/recipe['source']
    for line in (pack/'CHECKSUMS.sha256').read_text().splitlines():
        expected,name=line.split(None,1);path=pack/name.lstrip('* ')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Immutable input checksum mismatch: '+str(path))
    if hashlib.sha256(source.read_bytes()).hexdigest()!=recipe['sha256']:raise ValueError('Selected sclera checksum mismatch')
    with Image.open(source) as im:
        if im.size!=(480,480) or im.mode!='RGB':raise ValueError('Expected retained480x480 RGB sclera')
        raw=im.tobytes()
    data=('/* Generated lossless selected sclera RGB888; do not edit. */\n#include <stdint.h>\n'+c_array('dragon_sclera_rgb','uint8_t',raw,24)).encode()
    report=dict(source=source.relative_to(ROOT).as_posix(),source_sha256=recipe['sha256'],raw_rgb_sha256=hashlib.sha256(raw).hexdigest(),width=480,height=480,format='RGB888',resource_bytes=len(raw),additional_dynamic_allocation_bytes=0,generated_include_sha256=hashlib.sha256(data).hexdigest(),note='Static app RODATA; existing XIP/RODATA-to-PSRAM configuration still incurs residency cost. No PNG decoder at runtime.')
    if check:
        if output.read_bytes()!=data:raise ValueError('Generated sclera differs')
        if json.loads(output.with_suffix('.json').read_text())!=report:raise ValueError('Generated sclera report differs')
    else:
        output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data);output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS lossless sclera:691200B app RODATA; source checksums preserved; no runtime decode/cache')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build-host/dragon-generated/dragon_sclera.inc');p.add_argument('--check',action='store_true');a=p.parse_args();bake(a.output,a.check)
