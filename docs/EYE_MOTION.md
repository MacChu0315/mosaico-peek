# Direction and wider motion —1.0.6-peek-motion

The user confirmed that both physical directions were reversed in1.0.5 and
that the new eyes moved much less than dragon. Current build disables both
source mapping flips and widens new-eye motion. No raw temperature rearrangement,
detector parameter, role timing, dragon art/shader or approved240 sampling change.
Physical direction/range acceptance remains separate from software verification.

## Motion and immutable sources

The old new-eye range was owl18/12px, deep sea20/12px, mechanical10/8px.
All three now rotate a radius233 sphere, with pure-axis projected pupil-center
travel±120 horizontal/±80 vertical pixels. Dragon's approximate corresponding
travel is139/93px; the artwork geometry and visible aperture still differ.
Gaze inputs remain bounded±0.78/±0.58, positive right/down. Yaw is
`gx/0.78 * asin(120/233)`; pitch is`gy/0.58 * asin(80/233)` in radians.
Combined diagonals couple through sphere rotation, rather than independent flat
translation. Fixed eyelids/frame occlude the eye; extreme gaze may hide much of
the pupil. Ordinary C role blending, milliseconds, sleep/wake and replay remain
as described in EYE_UI.md. The enlargement is positional; no new detector,
speed boost or shortened smoothing deadline is used.

`assets/eye_motion.json` records the recipe separately from immutable
`assets/eye-pack/`. Build-local full480 opaque backing fills formerly hidden
sphere areas with visible iris sectors at matching radius, blending left/right
and smoothing only new hidden content. Original visible neutral pixels are then
restored exactly. This is derived texture, not newly supplied original artwork;
extreme rotation can expose mirrored/repeated/soft texture. Fixed frame and nine
lid sources retain their original resolution, transparency, crop and origin.
No source PNG is overwritten. New art still draws full480; no palette reduction.

`src/eye_projection.h` contains shared Q15 inverse rotation; per-column/row
normals and an immutable per-theme depth table avoid per-pixel square roots.
The exact-neutral branch preserves original pixels. `eye_pack.c` retains1.0.5's
opaque foreground/eye and skipped invisible-layer fast paths. Draw does not
allocate, decode or feed detector samples. Prepare owns mutable state.

## Resources and failure behavior

Target ABI report: [resource-budget.json](../evidence/eye-ui/motion/resource-budget.json).
Application6641952B, linked eye RODATA4634724B; fits unchanged ota_0.
Decoded bitmap PSRAM3418224B includes frame921600, sphere921600, two-lid
capacity1103232, sphere depth460800 and ROM inflater10992B. Renderer C state
is2004B internal RAM. GSP buffers, stacks, SDK reservations and XIP_FROM_PSRAM
Flash-code/data backing are additional; these are not total runtime peaks.

Only the active artwork retains large caches: dragon3929120B or bitmap3418224B.
The UI owner releases an inactive renderer before allocating its replacement;
this avoids retaining both in PSRAM. Diagnostics retain the last artwork.
A cross-family switch performs allocation/preparation and can briefly pause
presentation. Failure propagates to the sticky display error; there is no
promise to roll back to the old renderer. Sensor acquisition stays independent.

## Reproduce and verification

```
cmake -S . -B build-host
cmake --build build-host -j4
ctest --test-dir build-host --output-on-failure
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release -j4
ctest --test-dir build-release --output-on-failure
python3 tests/test_eye_pixels.py
python3 tools/preview.py --headless --view night_owl
PEEK_EVIDENCE_DIR=evidence/eye-ui/motion/native-switch python3 tests/test_switch_gsp.py
python3 tests/test_eye_mapping_evidence.py
PEEK_EVIDENCE_DIR=evidence/eye-ui/motion/native python3 tests/test_eye_gsp.py
python3 tools/build_idf.py
python3 tools/report_eye_budget.py --output-dir evidence/eye-ui/motion
```

Do not pass`--flip-x --flip-y` for the corrected physical mapping. Preview controls
remain outside artwork; `control.py view dragon/night_owl/deep_sea/mechanical`,
`case dragon`, `case live`, `case sleep`, `play`, `pause`, `replay` select and replay.

Debug/Release23/23 and independent57 full480 pixel comparisons pass.384 complete
frames exactly match adapted scalar color composition (`eye_pack_scalar.c`) with
current geometry. Frozen original`eye_pack_v104.c` remains unchanged; off-center
motion intentionally no longer equals1.0.5. Three neutral images match retained
actual1.0.5 C output byte-for-byte.27 aperture/direction bounds and pure-axis
center displacement checks pass. ASan/UBSan exact384-frame/allocation/projection
checks pass; leak sanitizer is disabled for the existing ptrace limitation,
while explicit allocation/free counts cover partial failures.

Native16 input checks and four pixel captures pass. Same87-temperature-sample
checkpoint preserves detector result/phase/other pose channels, while both gaze
signs change from negative to positive. This checks software mapping, not the
physical mount. Complete motion/sleep native run results and real-time movies
are under`evidence/eye-ui/motion/native/`; original screenshot intervals are
retained and encoded duration checked. Movie FPS is not physical panel FPS.

IDF build passes pinned7b9cc1a / ESP32-S31, no SDK change. The existing retained-
factory capacity warning remains; application belongs in ota_0. Actual1.0.6
installation and hardware measurements will be recorded in the handoff and
motion device-install directory. Earlier1.0.5 measurements do not establish
current sphere-rendering cost. Physical direction, appearance and maximum
range still require observation; device panel FPS/largest blocks remain unknown.
