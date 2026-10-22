#!/usr/bin/env python3
"""Pin the latest physical feedback, separately from synthetic raster parity."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config = {}
for name in ('sdkconfig.defaults', 'sdkconfig.application.defaults', 'sdkconfig.eyes.defaults'):
    for line in (ROOT / 'projects/peek' / name).read_text().splitlines():
        if line.startswith('CONFIG_') and '=' in line:
            key, value = line.split('=', 1)
            config[key] = value
        elif line.startswith('# CONFIG_') and line.endswith(' is not set'):
            config[line[2:-11]] = 'n'

# 2026-10-22: installed1.0.10, orientation0, both flipsfalse; user observed
# BOTH dragon and mechanical reversed on BOTH axes in the same placement.
# Renderers independently move positive gaze right/down. Correct the shared
# mounting map, not a character shader, IMU calibration or raw thermal array.
for axis in ('X', 'Y'):
    assert config['CONFIG_PEEK_GAZE_FLIP_' + axis] == 'y', axis + ' mounting sign contradicts current physical feedback'
assert config['CONFIG_PEEK_IMU_MOUNT_QUARTERS'] == '0'
assert config['CONFIG_PEEK_AUTO_ORIENTATION'] == 'y'
print('PASS current device mounting defaults; physical retest remains required')
