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

## Built and installed candidate

Sourceeffb682e2a35a6b6a4e862f990d6eb5219831a9d, firmware1.1.1.
ELFfad83dba1a8e4628b70dd82efbd4520d63b11006bdf12f70bd2b780442d5e33b.
Official update58511ef0-5c8a-4065-a38b-3cf3c1439577 succeeded first attempt;
boot11328770680449269444, normal mode, VALID, runtime/IMU error0, crash_count0,
both flips enabled, orientation270. Frozen v1.1.0 tag/bundle verified unchanged.

App7219760B (+1152), UI94480B unchanged. Bitmap linked RODATA4496919B and all31
streams unchanged. UI struct10336B (+24); renderer struct2004B and explicit
bitmap PSRAM3418224B unchanged. No extra framebuffer/cache allocation. Existing
SDK component-include and undersized factory partition warnings remain; ota_0 fits.

Native dynamic previews: evidence/render-v111/dynamic/*.mp4, each about8s,
synthetic complete-array timeline9400ms onward (sleep/wake/motion), orientation270.
VFR timestamps retain actual capture intervals within0.2s of video duration;
encoding/capture rate is not device throughput. Existing ffmpeg rejects-fps_mode;
re-export with its supported-vsync vfr succeeds, no dependency upgrade.
Reproduce with a running native preview and:
python3 tools/capture_render_trial.py --output <new-output-directory>

Host sampler A/B uses identical-O2/-ffp-contract=off and generated assets, with
baseline source read from v1.1.0 into a temporary directory; exact probe source
is evidence/render-v111/host-sampler-probe.c. Compile with cc plus-I<source-dir>
-Isrc -Iprojects/peek/build/eye-generated -lz -lm. Results are microbenchmarks,
not GSP throughput or PSRAM/device timings. Off-center timing is noisy; no
percentage improvement is inferred. Device post-install results follow below.

## Actual1.1.1 device observations

Same authorized device/boot/ELF above,270deg, no screenshots inside performance
windows (RPC polling remains). Deep-sea active-open45 frames/6.82s =6.598Hz,
108.752ms raster +32.789ms submit. Baseline1.1.0 active-open24 frames/4.16s =
5.769Hz,130.670ms raster +33.652ms submit. This is an observed improvement across
different hand-played short scenes, not a controlled percentage speedup.

Deep-sea fully closed24.55s:0 new frames,0 raster/submit work,193 new temperature
samples and0 faults;615 prepares continue (~0.016ms each). Three stable readings
bracket a screenshot whose RGB565 pixels exactly equal the approved C rendering.
The image is retained, not black/frozen acquisition; new target wake is separately
covered by production-input native tests. Four ordinary membrane engine frames
were observed in the mixed window, all full stage8; this does not prove every
pulse was visible. The original240ms timing and visibility limit remain.

Mechanical270deg active-open4.737Hz (see raw window lengths/phases). Fully closed
16.74s:0 new frames/raster/submit,131 new samples,0 faults. Render gaze remains
(0,0), source gaze remains independent; three stable readings and actual screen
RGB565 match C exactly. No same-angle v1.1.0 mechanical baseline was captured;
historical1.0.11 at0deg is not a valid speedup comparison. Mechanical active
raster remains expensive. Current-version dragon active throughput was not
remeasured; its rotated pixel/behavior regressions pass. Static picture keys are
conservative: unchanged output is reused when the declared visible dependencies
match; no approximate pose merging or future frame prediction.

Post-sea free internal243799B/free PSRAM4536896B,1152B less PSRAM than same-role
baseline as expected from code/XIP growth; minima are lifetime values, not a peak
allocation attribution. No reboot/crash/runtime/IMU errors in the measured windows.
Physical panel FPS, maximum fragmentation, input-to-screen latency and long-term
reliability remain unmeasured. No15Hz/30Hz claim or quality reduction.

## Review and restore

Local source commit: effb682 (perf: reuse exact eye pictures and streamline
rotated rendering). Follow-up receipt-only commit records these actual outcomes;
it does not change the installed source identity. No remote write.

Compact delta ZIP: review/mosaico-peek-render-v1.1.1.zip, against the full local
v1.1.0 checkout plus fa34821 receipt. It includes changed source/tests/docs,
current evidence and exact official update bundle, without.git/build/dependency
copies or unchanged original artwork. It is not a standalone rebuild kit.
Startup: python3 tools/preview.py --view deep_sea --flip-x --flip-y
Switch: python3 tools/control.py next / previous
Replay: python3 tools/control.py case sleep; python3 tools/control.py play
Explicit reset: python3 tools/control.py replay
Device restore remains releases/v1.1.0/mosaico-peek-v1.1.0.irisfw through the
official same-device System Update workflow. Do not move/overwrite its tag/bundle.
