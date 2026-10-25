#!/usr/bin/env python3
"""Source hashes and mtimes cannot change in ordinary eye builds."""
import importlib.util,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bake',ROOT/'tools/bake_eye_pack.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def fingerprint():return {str(p):(p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).digest()) for root in [b.PACK,b.MECHANICAL,b.DEEP] for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
deep_adaptation=b.DEEP_ADAPTATION.read_bytes();before=fingerprint();adaptation=(b.ADAPTATION.stat().st_mtime_ns,b.ADAPTATION.read_bytes());recipe=(b.MOTION.stat().st_mtime_ns,b.MOTION.read_bytes());output=ROOT/'build-host/eye-readonly/eye_pack.inc';b.bake(output);first=output.read_bytes();b.bake(output);assert first==output.read_bytes();assert before==fingerprint();assert adaptation==(b.ADAPTATION.stat().st_mtime_ns,b.ADAPTATION.read_bytes());assert recipe==(b.MOTION.stat().st_mtime_ns,b.MOTION.read_bytes())
try:b.bake(ROOT/'src/forbidden.inc')
except ValueError:pass
else:raise AssertionError('source output path accepted')
assert not (ROOT/'src/forbidden.inc').exists();assert b.DEEP_ADAPTATION.read_bytes()==deep_adaptation
print('PASS eye pack: repeated byte identity, source hashes/mtimes unchanged, source-output rejected')
