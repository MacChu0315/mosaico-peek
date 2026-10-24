#!/usr/bin/env python3
"""Reproduce the approved R2 art in a separate build tree; never modify sources."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build-host/deep-sea-reproduce');a=p.parse_args();out=a.output.resolve()
    if ROOT not in out.parents:p.error('Use a project build directory')
    rel=out.relative_to(ROOT)
    if not (rel.parts[0]=='build' or rel.parts[0].startswith('build-')):p.error('Use a project build directory')
    if out.exists():p.error('Refusing to overwrite existing reproduction directory')
    source=ROOT/'assets/deep-sea-r2';out.mkdir(parents=True)
    for folder in ('input','scripts','reference'):shutil.copytree(source/folder,out/folder)
    for name in ('INPUTS.json','recipe.json'):shutil.copyfile(source/name,out/name)
    (out/'build').mkdir();(out/'review').mkdir()
    subprocess.run([sys.executable,'-B',str(out/'scripts/revise.py')],check=True)
    checked=[]
    for f in (source/'processed').rglob('*.png'):
        relative=f.relative_to(source/'processed');actual=out/'build/r2/deep_sea'/relative
        assert f.read_bytes()==actual.read_bytes(),relative;checked.append(str(relative))
    report=dict(approved_PNGs_byte_identical=len(checked),files=checked,source_unchanged=True,output=str(out))
    (out/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
