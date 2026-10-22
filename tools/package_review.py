#!/usr/bin/env python3
"""Archive committed review material with an exact source commit and file hashes."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--eye-ui",action="store_true",help="compact current eye-UI source and evidence, excluding historical firmware/movies")
    parser.add_argument("--mechanical-c",action="store_true",help="mechanical C source, current evidence and integrated/orientation restore bundles")
    parser.add_argument("--dragon-sclera",action="store_true",help="selected dragon sclera source, current native/device evidence and1.0.11 restore")
    args=parser.parse_args()
    if sum((args.eye_ui,args.mechanical_c,args.dragon_sclera))>1:parser.error("Choose one review scope")
    if git('status','--porcelain'):raise RuntimeError('Commit reviewed task files before packaging; working tree must be clean')
    commit=git('rev-parse','HEAD');paths=git('ls-files','-z').strip('\0').split('\0')
    forbidden={'.git','deps','managed_components','__pycache__','.run','.codex-runs','review-inputs'}
    selected=[];aliases={}
    # Byte-identical recaptures retain their provenance/state logs but share
    # the already retained golden PNG in the small review archive.
    golden={hashlib.sha256(p.read_bytes()).hexdigest():str(p.relative_to(ROOT))
            for p in (ROOT/'evidence/phase2/dragon').glob('*.png')}

    for name in paths:
        parts=Path(name).parts
        if any(p in forbidden or p.startswith('build') for p in parts[:-1]):raise RuntimeError('Unexpected generated/dependency directory tracked: '+name)
        if name=='src/dragon_assets.inc':raise RuntimeError('Generated asset include must not be tracked')
        if args.dragon_sclera and name.startswith('evidence/') and not name.startswith('evidence/dragon-sclera/') and name not in (
                'evidence/real-input/detector-output.jsonl','evidence/real-input/role-output.jsonl',
                'evidence/mechanical-c/direction/device-install/peek-direction.irisfw',
                'evidence/eye-ui/performance/native/native-checks.json','evidence/eye-ui/motion/native-switch/native-checks.json',
                'evidence/eye-ui/performance/motion-live/summary.json'):continue
        if args.mechanical_c and name.startswith('evidence/') and not name.startswith(('evidence/mechanical-c/','evidence/auto-orientation/')) and name not in ('evidence/real-input/detector-output.jsonl','evidence/real-input/role-output.jsonl','evidence/eye-ui/motion/device-install/eye-motion.irisfw','evidence/eye-ui/motion/device-install/README.md','evidence/eye-ui/performance/native/native-checks.json','evidence/eye-ui/motion/native-switch/native-checks.json','evidence/eye-ui/performance/motion-live/summary.json'):continue
        if args.mechanical_c and name.endswith('.irisfw') and name not in (
                'evidence/mechanical-c/direction/device-install/peek-direction.irisfw',
                'evidence/mechanical-c/integrated/device-install/peek-integrated.irisfw',
                'evidence/mechanical-c/integrated/restore-1.0.9/orientation-calibrated.irisfw'):continue
        if args.mechanical_c and name.startswith('evidence/') and name.endswith(('.png','.mp4')) and not (
                name.startswith('evidence/mechanical-c/direction/') or
                name=='evidence/mechanical-c/frame-candidates/comparison.png'):continue
        if args.eye_ui and name.startswith('evidence/') and not name.startswith('evidence/eye-ui/') and name not in ('evidence/real-input/detector-output.jsonl','evidence/real-input/role-output.jsonl'):continue
        if args.eye_ui and name.endswith('.irisfw') and name not in ('evidence/eye-ui/motion/device-install/eye-motion.irisfw','evidence/eye-ui/performance/device-install/eye-fast.irisfw'):continue
        if args.eye_ui and name.startswith('evidence/eye-ui/native/') and name.endswith('.mp4'):continue
        if name.startswith('evidence/gsp/motion/'):continue
        if name.startswith('evidence/') and name.endswith('.mp4') and not (name.startswith('evidence/dragon-sclera/') or name.startswith('evidence/mechanical-c/') or name.startswith('evidence/real-input/') or name=='evidence/sleep-performance/native/sleep-live.mp4' or name.startswith('evidence/eye-ui/')):continue
        if name.endswith('.png') and name.startswith(('evidence/real-input/synthetic-regression/','evidence/device-dragon/cache-native/')):
            digest=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
            if digest in golden:
                aliases[name]={'sha256':digest,'identical_to':golden[digest]}
                continue
        selected.append(name)
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in selected}
    manifest={'commit':commit,'branch':git('branch','--show-current'),'files_sha256':hashes,'identical_evidence_aliases':aliases,'evidence':('Mechanical C integration, native replay and device acceptance; see docs/MECHANICAL_C.md and HANDOFF' if args.mechanical_c else 'Three-theme shared-C/native-GSP motion correction and separately recorded authorized device installations/performance; physical acceptance limits are in docs/EYE_MOTION.md and docs/HANDOFF.md' if args.eye_ui else 'Live dragon: exact recorded-temperature native replay and separately retained physical-device acceptance; see docs/HANDOFF.md'),'excluded':['.git','build/cache','dependency copies','intermediate screenshots, old historical MP4s, ignored original review input and dependency caches, full local ELF/map/config backup']}
    if args.dragon_sclera:manifest['evidence']='Selected dragon sclera C; see docs/DRAGON_SCLERA.md and HANDOFF for exact native/device acceptance and limits'
    output=ROOT/'review';output.mkdir(exist_ok=True);archive=output/f'mosaico-peek-{"dragon-sclera" if args.dragon_sclera else "mechanical-c" if args.mechanical_c else "eye-ui" if args.eye_ui else "live-dragon"}-{commit[:8]}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in selected:z.write(ROOT/name,'mosaico-peek/'+name)
        if args.dragon_sclera:z.writestr('mosaico-peek/REVIEW_SCOPE.txt','Selected dragon sclera C, all retained build sources and current native/device evidence; previous installed1.0.11 restore included. Historical evidence links may require full checkout. No .git, dependencies, generated includes, build caches or full local ELF/map/config backups. See docs/DRAGON_SCLERA.md and HANDOFF.\n')
        if args.mechanical_c:z.writestr('mosaico-peek/REVIEW_SCOPE.txt','Integrated calibrated orientation, mechanical socket A and centered sleep; full retained sources/current verification. Current1.0.11 plus exact1.0.10/1.0.9 restore packages retained. Historical native PNG/MP4 and older firmware excluded from ZIP (kept in checkout); summaries and current real-time native movie retained. Standalone1.0.8 center candidate is excluded. Older evidence links may require the full checkout. Build: docs/MECHANICAL_C.md. No .git, dependencies, generated includes or build caches.\n')
        if args.eye_ui:z.writestr('mosaico-peek/REVIEW_SCOPE.txt','Current eye UI source, retained source PNG/provenance, data and new evidence. Historical firmware/verification binaries and movies are excluded; historical document links can refer to the full checkout. No generated includes, dependencies or build caches. Build instructions: docs/EYE_UI.md.\n')
        z.writestr('mosaico-peek/REVIEW_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        if args.mechanical_c:
            for line in z.read('mosaico-peek/assets/mechanical-c/CHECKSUMS.sha256').decode().splitlines():
                digest,name=line.split(None,1);assert hashlib.sha256(z.read('mosaico-peek/assets/mechanical-c/'+name.lstrip('* '))).hexdigest()==digest
        if args.dragon_sclera:
            for line in z.read('mosaico-peek/assets/dragon-sclera-c/CHECKSUMS.sha256').decode().splitlines():
                digest,name=line.split(None,1);assert hashlib.sha256(z.read('mosaico-peek/assets/dragon-sclera-c/'+name.lstrip('* '))).hexdigest()==digest
        for name,digest in hashes.items():assert hashlib.sha256(z.read('mosaico-peek/'+name)).hexdigest()==digest
    for name,alias in aliases.items():assert hashlib.sha256((ROOT/alias['identical_to']).read_bytes()).hexdigest()==alias['sha256']
    checksum=hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(checksum+'  '+archive.name+'\n')
    print(f'{archive}\n{archive.stat().st_size} bytes; {len(selected)} files; SHA256 {checksum}')
if __name__=='__main__':main()
