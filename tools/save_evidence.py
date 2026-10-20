#!/usr/bin/env python3
"""Retain complete final local build and GSP logs for review."""
from pathlib import Path
import json,shutil
r=Path(__file__).resolve().parents[1]
summary=(r/'evidence/idf-build-summary.log').read_text();line=next(l for l in summary.splitlines() if l.startswith('result: '));result=Path(line[8:]);raw=result.parent/'raw.log'
shutil.copy2(result,r/'evidence/idf-build-result.json');shutil.copy2(raw,r/'evidence/idf-build-raw.log')
for name in ['host','backend']:shutil.copy2(r/f'.run/{name}.log',r/f'evidence/gsp-{name}.log')
