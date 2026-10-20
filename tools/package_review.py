#!/usr/bin/env python3
"""Archive committed review material with an exact source commit and file hashes."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main():
    if git('status','--porcelain'):raise RuntimeError('Commit reviewed task files before packaging; working tree must be clean')
    commit=git('rev-parse','HEAD');paths=git('ls-files','-z').strip('\0').split('\0')
    forbidden={'.git','deps','managed_components','__pycache__','.run','.codex-runs','review-inputs'}
    selected=[]
    for name in paths:
        parts=Path(name).parts
        if any(p in forbidden or p.startswith('build') for p in parts[:-1]):raise RuntimeError('Unexpected generated/dependency directory tracked: '+name)
        if name=='src/dragon_assets.inc':raise RuntimeError('Generated asset include must not be tracked')
        if name.startswith('evidence/gsp/motion/'):continue
        if name.endswith('.mp4') and not name.startswith('evidence/real-input/'):continue
        selected.append(name)
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in selected}
    manifest={'commit':commit,'branch':git('branch','--show-current'),'files_sha256':hashes,'evidence':'Live dragon: exact recorded-temperature native replay and separately retained physical-device acceptance; see docs/HANDOFF.md','excluded':['.git','build/cache','dependency copies','intermediate screenshots, old historical MP4s, ignored original review input and dependency caches, full local ELF/map/config backup']}
    output=ROOT/'review';output.mkdir(exist_ok=True);archive=output/f'mosaico-peek-live-dragon-{commit[:8]}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in selected:z.write(ROOT/name,'mosaico-peek/'+name)
        z.writestr('mosaico-peek/REVIEW_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,digest in hashes.items():assert hashlib.sha256(z.read('mosaico-peek/'+name)).hexdigest()==digest
    checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(checksum+'  '+archive.name+'\n')
    print(f'{archive}\n{archive.stat().st_size} bytes; {len(selected)} files; SHA256 {checksum}')
if __name__=='__main__':main()
