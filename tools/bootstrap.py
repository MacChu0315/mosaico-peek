#!/usr/bin/env python3
"""Resolve pinned local dependencies without changing adjacent worktrees."""
import hashlib,io,json,os,shutil,subprocess,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VIBE=(ROOT.parent/'esp-mosaico-vibe').resolve()
PINS={'iris':'fc63d43f3ac72aa54e701b07b07fbed07a16b3ca','vibe':'95469e63b621fc6ece3b0e313af8c1ba59dcd066','bsp':'a2c985ad698b3f04a21c63e006b43e7e948bc1d7','utils':'fc63d43f3ac72aa54e701b07b07fbed07a16b3ca'}
def commit(p):return subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
def main():
    paths={'iris':VIBE/'submodule/esp-mosaico-utils/ESP-Iris','vibe':VIBE,'bsp':VIBE/'submodule/esp-mosaico-bsp','utils':VIBE/'submodule/esp-mosaico-utils'}
    for key,path in paths.items():
        if commit(path)!=PINS[key]:raise RuntimeError(f'{key}: expected {PINS[key]} at {path}; no shared checkout was changed')
    source=Path(os.environ.get('PEEK_THERMAL_SOURCE',ROOT.parent/'Mondrian/components/mosaico_module_thermal'))
    manifest=json.loads((ROOT/'dependencies.json').read_text())['thermal']
    if not source.exists():
        # Public read, exact upstream commit; extracted paths are an explicit allowlist.
        url='https://codeload.github.com/esp-mosaico/esp-mosaico-bsp/zip/'+manifest['commit']
        print('Retrieving pinned thermal driver:',url)
        archive=zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url,timeout=60).read()))
        source=ROOT/'deps/thermal-source';prefix='esp-mosaico-bsp-'+manifest['commit']+'/components/mosaico_module_thermal/'
        for name in manifest['files_sha256']:
            raw=archive.read(prefix+name)
            if hashlib.sha256(raw).hexdigest()!=manifest['files_sha256'][name]:raise RuntimeError('Downloaded thermal hash mismatch: '+name)
            dst=source/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
    target=ROOT/'deps/mosaico_module_thermal'
    # A fresh official BSP checkout at this commit also provides this directory.
    for name,digest in manifest['files_sha256'].items():
        raw=(source/name).read_bytes()
        if name=='idf_component.yml':continue # owning workspace path is relocated below
        if hashlib.sha256(raw).hexdigest()!=digest:raise RuntimeError(f'thermal source mismatch: {name}')
    target.mkdir(parents=True,exist_ok=True)
    for name in manifest['files_sha256']:
        dst=target/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/name,dst)
    (target/'idf_component.yml').write_text('version: "0.1.0"\ndescription: ESP-Mosaico MLX90640 thermal imaging module\nlicense: Apache-2.0\ndependencies:\n  esp-mosaico-bsp:\n    public: true\n    version: "*"\n    override_path: '+json.dumps('../../../esp-mosaico-vibe/submodule/esp-mosaico-bsp/components/esp-mosaico-bsp')+'\n')
    (ROOT/'deps/paths.json').write_text(json.dumps({k:str(v) for k,v in paths.items()},indent=2)+'\n')
    print('Pinned dependencies verified; thermal public driver prepared in deps/.')
if __name__=='__main__':main()
