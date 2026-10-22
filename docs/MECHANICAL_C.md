# Mechanical C — rotating central shutter

Current1.0.10 integrated source combines user-selected fixed metal socket A with the new C
eye/shutter, and centers the mechanical presentation during sleep closure.
[A/B comparison and exact sources](../evidence/mechanical-c/frame-candidates/comparison.png).
The original thin round mount remains in the immutable input package, but is
not selected by the current adapter. See assets/mechanical-c-adaptation.json.

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

Use the supplied480×480 opaque eye, selected480×480 fixed socket A, and nine240×240 RGBA
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
Current build selector`sdkconfig.integrated`, version1.0.10-peek-integrated;
known1.0.6 restore remains separately retained. Installed sourcedf6f6da is confirmed in
[device evidence](../evidence/mechanical-c/device-install/README.md). Installation
used an identical-bundle retry after read-only reconciliation of a retained
Recovery writer reset; the first operation remains outcome_unknown.

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

## Historical1.0.7 installation

Version1.0.7-peek-mechanical, sourcedf6f6da, exact ELF97d859cb847b3ceeff6956477098a28210dc90ebe50a3f3e6dfdc5f5ac010d2e.
Healthy/validated, crash0/runtime error0, both physical flips false. Bootloader,
partition table and UI resource image unchanged; Recovery not replaced.
Physical performance and appearance are separate from native/source verification.
Review archive: `python3 tools/package_review.py --mechanical-c`; retains current
source/asset checksums/current evidence and prior1.0.6 restore, omitting build
caches/dependencies and unrelated historical evidence. Original84-file mechanical
source completeness is also checked inside the ZIP.

## Historical1.0.7 thin-mount performance limitation

[Actual device windows](../evidence/mechanical-c/device-performance/README.md)
measure about3.93 active-open complete GSP frames/s and3.88 sleeping frames/s.
Raster is212..214ms/frame; submit about32ms. Thermal acquisition remains about
7.8 fresh samples/s with zero faults. Prior1.0.6 mechanical was7.095Hz active-open;
new full-globe artwork is slower, and this regression is not resolved or called
fluid. Physical panel-visible FPS remains unmeasured. Closed state and later
TRACKING were observed; no exact physical wake-duration claim.

Memory before screenshot: internal free247763B, PSRAM free5096896B. Peak/largest
blocks and input-to-screen latency are not established. The next performance
step is raster profiling/optimization under the same full480 and gaze bounds;
do not silently reduce quality, change shared behavior or inflate FPS with cheap
states. Visual acceptance of the new installed artwork remains pending.

## Mechanical sleep centering and frame A

The user reported that the closed mechanical eye still wandered, and selected
A after comparing both old/new sockets with the same production C globe and
poses. Source frame is the original mechanical frame.png (480RGBA), verified
by SHA256 in assets/mechanical-c-adaptation.json. No source image is overwritten;
new B original/prompt/provenance remains in assets/mechanical-candidates/ only.
The reference compositor now explicitly overlays selected A for parity checks.

src/eye_character_pose.h is a pure display transform of shared dragon_t: only
character3 with sleeping or waking applies a follow weight
max(0,1-blink/(7.5/8)) to gaze. The existing nearest9-stage policy is visually
fully closed at7.5/8, so gaze is exactly(0,0) from that point onward. This means
the established front-facing eye center(240,245), not the screen origin.
The450ms close/150ms wake, detection and raw controller motion remain unchanged.
Ordinary blinks retain gaze. Partial-close interruption keeps the same
presentation pose at acquisition and returns to unmodified follow at wake end.

Both peek_ui_set_view and refresh prepare from the copied artwork pose. Host
status adds render_pose; device telemetry adds render_gaze_x/y while preserving
existing raw gaze_x/y. These are additive fields and do not modify source state
or count new samples. CTest includes all449 interior close milliseconds, same-
time idempotence, wake completion, source immutability, last-frame centering,
ordinary blinks and other-character behavior. Actual native screenshots verify
that all closed poses are identical while the raw controller continues moving.

Standalone1.0.8 native/build results (NEVER installed) are recorded under
`evidence/mechanical-c/a-centered/`; historical1.0.7 evidence stays separate.
Candidate source preparation: cmake --build build-host --target frame_candidate_snapshot;
python3 tools/preview_mechanical_frames.py. The frame preview executable uses
production eye_pack.c with review-only fixed-frame substitution; it is never
linked into firmware. B was generated with built-in image_gen, retains original
1254RGBA, and is resized only in the build folder for comparison.

## Integration with accepted auto orientation

Before standalone1.0.8 installation, a read-only identity check found that the
completed orientation task had installed1.0.9-peek-orient. No1.0.8 write occurred.
The user released the device and authorized integration. The local merge retains
fca4114 (installed calibrated source74a0f44) without modifying its worktree.
Calibrated gravity(-ax,+ay), automatic orientation and mount quarters0 are retained.

Presentation order is mechanical centering -> inverse orientation gaze -> globe
and fixed socket drawing -> complete-canvas quarter-turn. Host render_pose and
device render_gaze_x/y are canonical artwork coordinates before canvas rotation;
raw gaze_x/y retain source physical-coordinate semantics. Center stays zero in
all four directions, including wake and theme/rotation changes. Target input is
not rotated or re-fed. New CTest total29; native40 four-way pixel comparisons
cover all four artworks plus mechanical centered sleep and partial wake.

Latest evidence belongs under evidence/mechanical-c/integrated/. Exact1.0.9
restore is retained there. The earlier standalone1.0.8 candidate is only a local
uninstalled backup; never install it over the integrated/orientation versions.

## Latest physical direction feedback

Integrated1.0.10 was installed. User then reported both mechanical and dragon
following in the opposite direction on both axes in unchanged placement.
Runtime orientation0 and both gaze flipsfalse were recorded. Current1.0.11
candidate enables both shared mounting flips; it does not change artwork, IMU,
raw temperature coordinates, detector timing or centering. Previous physical
acceptance is historical and conflicts with this observation; cause of that
conflict remains unknown. See HANDOFF for physical retest and installed identity.
Device-equivalent native startup now adds --flip-x --flip-y.
