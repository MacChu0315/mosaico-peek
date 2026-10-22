#!/usr/bin/env python3
"""Read-only checks for the frozen selected artwork and delivered pose evidence."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = '5775c62ce834c1e3573148241f2589e434d0226a9cea4d88ad78348d2c4c9887'

def changed_mask(before, after):
    channels = ImageChops.difference(before, after).split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    return maximum.point(lambda value: 255 if value else 0)

def main():
    surface = ROOT / 'submission/sclera.png'
    assert hashlib.sha256(surface.read_bytes()).hexdigest() == EXPECTED, 'Selected surface changed'
    with Image.open(surface) as im:
        assert im.size == (480, 480) and im.mode == 'RGB'
    pose_records = []
    rendered = json.loads((ROOT/'evidence/render.json').read_text())
    for name, *_ in rendered['poses']:
        with Image.open(ROOT/'evidence/baseline'/f'{name}.png') as im:
            before = im.convert('RGB')
        with Image.open(ROOT/'evidence/poses'/f'{name}.png') as im:
            after = im.convert('RGB')
        with Image.open(ROOT/'evidence/sclera-masks'/f'{name}.png') as im:
            mask = im.convert('L')
        changed = changed_mask(before, after)
        outside = ImageChops.multiply(changed, ImageChops.invert(mask))
        assert outside.getbbox() is None, f'{name}: change outside sclera'
        if name == 'closed': assert changed.getbbox() is None, 'Closed pose changed'
        pose_records.append({'pose': name, 'changed_pixels': changed.histogram()[255]})
    editable = json.loads((ROOT/'source/editable-checks.json').read_text())
    for name, record in editable['outputs'].items():
        assert hashlib.sha256((ROOT/'source'/name).read_bytes()).hexdigest() == record['sha256'], name
    checksums = ROOT/'CHECKSUMS.sha256'
    checked_files = 0
    if checksums.exists():
        for line in checksums.read_text().splitlines():
            digest, relative = line.split('  ', 1)
            assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
            checked_files += 1
    print(json.dumps({'selected_surface_unchanged': True,
                      'poses_checked': len(pose_records),
                      'changes_outside_sclera': 0,
                      'closed_pose_unchanged': True,
                      'editable_file_hashes': 'passed',
                      'package_files_hash_checked': checked_files,
                      'native_GSP_or_device_verified': False}, indent=2))

if __name__ == '__main__': main()
