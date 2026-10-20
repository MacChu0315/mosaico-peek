#!/usr/bin/env python3
"""Stop only the preview that owns this project's recorded GSP child PID."""
import json,os,signal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
pid=json.loads((ROOT/'.run/ready.json').read_text())['pid']
parent=int(next(l for l in Path(f'/proc/{pid}/status').read_text().splitlines() if l.startswith('PPid:')).split()[1])
command=Path(f'/proc/{parent}/cmdline').read_bytes().split(b'\0')
if b'tools/preview.py' not in command or Path(f'/proc/{parent}/cwd').resolve()!=ROOT:raise RuntimeError('Preview owner mismatch; no signal sent')
os.kill(parent,signal.SIGTERM)
