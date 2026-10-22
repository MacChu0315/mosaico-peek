#!/usr/bin/env python3
"""Verify source-readonly generation, determinism and fail-closed integrity."""
import contextlib, io, json, shutil, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import bake_dragon_sclera as baker
with tempfile.TemporaryDirectory(prefix='peek-sclera-build-') as temporary:
    root=Path(temporary);(root/'assets').mkdir()
    shutil.copytree(ROOT/'assets/dragon-sclera-c',root/'assets/dragon-sclera-c')
    shutil.copyfile(ROOT/'assets/dragon-sclera-adaptation.json',root/'assets/dragon-sclera-adaptation.json')
    baker.ROOT=root
    def sources():return {str(p.relative_to(root)):(p.read_bytes(),p.stat().st_mtime_ns) for p in (root/'assets').rglob('*') if p.is_file()}
    before=sources();output=root/'build/dragon_sclera.inc'
    with contextlib.redirect_stdout(io.StringIO()):baker.bake(output);baker.bake(output,True)
    generated=output.read_bytes();assert sources()==before
    report=json.loads(output.with_suffix('.json').read_text());assert report['resource_bytes']==691200 and report['additional_dynamic_allocation_bytes']==0
    with contextlib.redirect_stdout(io.StringIO()):baker.bake(output)
    assert output.read_bytes()==generated and sources()==before
    for path in (root/'assets/forbidden.inc',root/'src/forbidden.inc',root/'forbidden.inc',root/'build.inc',root.parent/'outside.inc'):
        try:baker.bake(path)
        except ValueError as e:assert 'build directory' in str(e)
        else:raise AssertionError('non-build output must be rejected')
        assert not path.exists()
    source=root/'assets/dragon-sclera-c/submission/sclera.png';source.write_bytes(source.read_bytes()+b'corruption')
    try:baker.bake(output)
    except ValueError as e:assert 'checksum mismatch' in str(e)
    else:raise AssertionError('tampered source accepted')
    assert output.read_bytes()==generated
print('PASS sclera generation/check are deterministic and source-readonly; source outputs and corrupt input rejected before replacing generated data')
