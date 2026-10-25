#!/usr/bin/env python3
"""Compiled assets must exclude the retired owl, not merely hide its selector."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BUILD=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build-host'
report=json.loads((BUILD/'eye-generated/eye_pack.json').read_text())
assert [t['theme'] for t in report['themes']]==['deep_sea','mechanical'], 'retired owl remains in generated inventory'
assert [t['theme_index'] for t in report['themes']]==[1,2]
assert 'eye_night_owl' not in (BUILD/'eye-generated/eye_pack.inc').read_text()
print('PASS generated inventory contains only sea/mechanical; stable indices1/2, no owl texture arrays')
