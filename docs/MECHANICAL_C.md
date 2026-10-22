# Mechanical C — rotating central shutter

The user approved continuing with the supplied C artwork after the source review
on2026-10-22. This deliberately replaces the old mechanical-eye appearance and
fixed eyelids. Dragon/night_owl/deep_sea artwork and paths remain unchanged;
confirmed physical mapping stays flip_x=false, flip_y=false. No detector or
behavior deadline changes. Default startup remains dragon; select mechanical
through the existing tap/left-swipe/AI single click cycle, or right swipe back.

## Sources and native adaptation

`assets/mechanical-c/` retains the complete supplied source/reference package,
including original PNG, editable PSD/ORA/SVG, generation records, provenance,
checksums and labelled simulated evidence. ZIP SHA256 is retained under
`evidence/mechanical-c/input-archive.sha256`. Original CHECKSUMS84 entries are
validated on every build. Builds only write generated streams in build folders;
they do not run source-rewriting scripts. Prior eye-pack remains immutable.

Use the original480×480 opaque eye,480×480 fixed mount, and nine240×240 RGBA
shutters at texture origin(120,125). Center(240,245), radius233; existing gaze
bounds±0.78/±0.58 and pure-axis center travel±120/±80px are unchanged.
`closure=pose.blink`; nearest shutter index=floor(8*closure+0.5). No crossfade or
extra NOTICE/HOLD closure is added. Shared sleep/wake timings remain authoritative.

`src/eye_pack.c` adds an explicit rotating-shutter descriptor, leaving other
characters on the existing fixed-lid path. Prepare decodes only when the shutter
index changes, then composes a floating RGB240×240 tile from immutable base eye
and shutter. No intermediate8-bit rounding: preserve high-dynamic-range values
until final RGB565 conversion. Draw inverse-projects and bilinearly samples this
composite tile plus the untouched surrounding eye, then overlays fixed mount.
The shutter therefore moves with the eyeball. Draw never decodes, allocates,
updates material or submits temperature samples. Theme changes invalidate the
shutter index; reopening always recomposes from immutable base, preventing trails.

The two existing lid allocations together provide1103232B. Mechanical C uses
691200B float RGB plus230400B decoder output, leaving181632B unused. Eye/frame,
sphere depth cache and inflater allocations are unchanged: explicit bitmap
PSRAM total3418224B; internal renderer2004B on target ABI. No nine-full-frame
cache or new PSRAM allocation. Device framebuffer/SDK/XIP reservations and heap
peaks are additional. This storage policy remains compatible with current active-
renderer ownership; replacement allocation failure still enters display error.

## Verification and commands

```
cmake -S . -B build-host
cmake --build build-host -j4
ctest --test-dir build-host --output-on-failure
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release -j4
ctest --test-dir build-release --output-on-failure
python3 tests/test_eye_pixels.py
python3 tools/preview.py --headless --view mechanical
PEEK_EVIDENCE_DIR=evidence/mechanical-c/native-switch python3 tests/test_switch_gsp.py
PEEK_EVIDENCE_DIR=evidence/mechanical-c/native python3 tests/test_eye_gsp.py
PEEK_EVIDENCE_DIR=evidence/mechanical-c/recorded python3 tests/test_eye_recorded_gsp.py
python3 tools/build_idf.py
python3 tools/report_eye_budget.py --output-dir evidence/mechanical-c
```

Native controls: `python3 tools/control.py view mechanical`, `case dragon`,
`case sleep`, `case live`, `play`, `pause`, `replay`. Do not pass flip flags.
New build selector`sdkconfig.mechanical-c`, version1.0.7-peek-mechanical;
known1.0.6 restore remains separately retained. Installation and device evidence
must be recorded separately; build success alone does not claim installation.

Debug/Release25/25 pass. The new Python reference test first failed against the
old mechanical artwork; after adaptation81 direction/stage combinations and16
nearest-index boundaries pass. Independent reference tolerates at most one
RGB565 channel code at floating rounding boundaries, fewer than500 differing
channels/frame. The original package renderer supplies this independent oracle.
384 complete frames remain bit-identical to the adapted scalar C compositor.
Open-close-open in both orders, cross-theme return and draw/base immutability
are checked in production-code fixtures; existing allocation-failure tests stay.
The old1.0.6 art-handoff checker only compares unchanged owl/sea with the current
renderer; the old mechanical material contract does not apply to this new design.
The legacy exporter refuses to combine new C artwork with old-frame reference.

Full native motion and complete recorded input evidence belong under
`evidence/mechanical-c/`; actual results are reported in HANDOFF. Exported
movies retain capture wall-time intervals; their encoded FPS is not device FPS.

## Visual and performance boundaries

The supplied art still stretches/softens metal texture at extreme diagonals.
No smaller gaze range, added occlusion, downsampling or palette is used to hide
this. Nine discrete shutter states can be skipped if render cadence is slow;
no altered behavioral timing hides missed frames.

The new clear mount exposes154781 output pixels to sphere sampling versus
75876 previously (about2.04x). Closing the central shutter still renders the
sphere, so it cannot reuse the former cheap fixed closed-lid path. Old1.0.6
mechanical7.095 active-open engine Hz does not establish new performance.
Measure actual active and closed/static state separately, with preparation,
raster, submission, Canvas tile callbacks and full GSP frames distinguished.
Physical panel FPS, peak/largest allocations and visual acceptance require their
own evidence. Source PNGs total1328296B; zlib RGBA streams1566577B before linked
metadata/code/alignment. Actual final ELF/app/resource budget is recorded after
building the exact source commit.
