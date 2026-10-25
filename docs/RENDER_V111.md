# v1.1.1 exact-output rendering optimization

User approved the three optimization directions after the v1.1.0 audit.
Frozen tag082c783 and releases/v1.1.0 remain unchanged. Work branch:
perf/three-eye-render. Do not change artwork, source detector/controller,
physical mapping, membrane/sleep timing, full480 bitmap quality or dependencies.

## Changes and acceptance

1. Resolve quarter-turn tile traversal once; integer index increments replace
   per-pixel orientation calls. Preserve odd offsets/edge tiles and padded stride.
2. Neutral projection integer texel coordinates use exact(1,0,0,0) bilinear weights directly;
   preserve source alpha and HDR shutter channels until RGB565 output.
3. Prepare/read source on every tick, but request a new picture only when its
   exact render dependencies change. Do not quantize gaze. Bitmap keys use their
   existing nearest9 selection. A decoded opaque outer lid plus fixed frame
   can make gaze/membrane irrelevant; derive coverage from actual alpha bytes,
   never infer coverage from a stage number or artwork name. Theme/orientation,
   re-entry/reset and allocation/prepare errors invalidate or reject reuse.

No new framebuffer or bulk allocation. Static retention intentionally lowers
completed-frame counters: this is reduced redundant work, not a claimed active
FPS increase. Wake and source processing remain live through the33ms timer.
Existing GSP completed-generation counters remain distinct from Canvas tiles
and physical panel FPS. Compare active open states separately from closed ones.

Validation: extend UI invalidation/rotation and renderer scalar/occlusion tests;
run Debug/Release suites and native GSP replay/rotation/switch/sleep/wake checks.
Build using tools/build_idf.py (isolated sdkconfig.v1.1.1), verify target ABI/map
budgets and exact art streams. Install only on the standing-authorized device,
then measure before/after under the same orientation and labelled activity.
Full outcomes and limits will be filled after validation; this document alone
is not a claim of hardware speedup.

## Local validation before installation

- New identical-picture assertion fails on baseline1.1.0; passes on candidate.
- Debug/Release ctest37/37 pass, including288 full480 scalar pixel comparisons,
  neutral nine-stage shutters, decoded coverage gap rejection, four rotations
  with odd23x19 offset tiles/padded stride, and zero-completion telemetry.
- Native GSP16 pointer checks,44 orientation images and17 sea phase checkpoints
  pass; detector/role/time and pause/replay invariants preserved.
- Read-only review found no required implementation fix; both requested test
  gaps (horizontal odd edge tiles, zero-completion status) were added and passed.
- Baseline1.1.0 deep-sea270deg: short4.16s active-open window5.769Hz; fully closed
 24.93s window7.461Hz,90.335ms raster and33.931ms submit. Real hand-played inputs
  are not a controlled percentage-speedup benchmark. Original receipts retained.

- Native retained-picture checks pass: no new Canvas draw with8 new complete
  temperature samples while closed; paused redraw preserves source; genuine
  complete-array target acquisition wakes; repeated checkpoints match replay.
  Full recorded replay655 events/511 arrays retains detector/role results.
- The first native counter test sampled status before pending Canvas work was
  published. A following acknowledged callback fixes the measurement boundary;
  source/role did not differ. This was not handled by relaxing the assertion.
