# Automatic eye orientation — integration handoff

## Scope and status

Local implementation on `feat/auto-orientation` in `mosaico-peek-orientation`,
originally based on `b53d861`, now integrating main UI commit`5e30025`. Four cardinal placements keep artwork upright after settling.
Flat, moving, ambiguous and failed IMU samples retain the last orientation.
No continuous-angle stabilization or compensation for changed thermal field of
view. Existing characters use the common layer; new artwork must use that same
layer to inherit orientation.

The main `mosaico-peek` source worktree continues independently; its committed
mechanical C artwork is included here. Its tracked source, branch and previews
were not changed. Explicitly approved device updates used its existing Gateway.
No dependency upgrade, remote write or change to the main worktree branch.
**1.0.9 is installed and the user confirmed upright, clockwise90, inverted and
counterclockwise90 artwork orientation and hand following in the dragon view.**
Version1.0.8 failed all four placements; the initial positive answer was explicitly
withdrawn. Do not cite it as acceptance. Corrected1.0.9 uses measured XY axes.
[Installation, physical evidence and limits](../evidence/auto-orientation/README.md).


## Implemented

- `src/peek_orientation.c`: screen gravity-down input; acceleration magnitude
  0.85..1.15g, angular speed at most12dps, screen-plane gravity at least0.5g,
  dominant-axis ratio at least1.4. First-order smoothing0.25 per sample;
  candidate must remain valid400ms. A sample gap over100ms or invalid sample
  clears pending evidence. Duplicate/backward timestamps cannot add evidence.
- `device_orientation.c`: sole BMI270 owner, nominal20ms sampling, locked small
  status snapshot. GSP only reads the snapshot, never performs sensor I2C.
  Failed initialization is reported without taking the eye down; read errors
  freeze orientation and are visible through telemetry. No automatic reinit.
- `peek_ui.c`: clockwise artwork direction0/90/180/270, inverse normalized gaze
  at preparation, inverse pointer coordinates and transformed dirty rectangles.
  Only512B embedded scratch is added for tiled rotation; no new framebuffer or
  artwork cache. Draw still consumes prepared geometry. Quarter-turn CPU cost
  has not been measured on hardware.
- All source gaze (including idle and leave) uses one physical coordinate
  convention. Idle scan directions consequently follow that frame; the artwork
  remains upright. Do not conditionally transform gaze on target acquisition:
  doing so jumps the pupil at IDLE→NOTICE and LEAVE→IDLE even with a continuous
  source spring. Pixel regression tests cover both boundaries.
- Raw768 temperatures, native detector coordinates, source role/seed/timestamps,
  sleep/wake and thermal mounting flips remain unchanged. Theme switches and
  replay preserve display direction. Orientation changes cancel an in-progress
  swipe so release cannot switch characters accidentally.

## Configuration and diagnostics

- `CONFIG_PEEK_AUTO_ORIENTATION=y`: automatic mode (default).
- `CONFIG_PEEK_FIXED_ORIENTATION=0..3`: startup/fallback direction, multiplied by90
  degrees clockwise. Disable automatic mode to lock this direction without IMU.
- `CONFIG_PEEK_IMU_MOUNT_QUARTERS=0..3`: sensor-to-screen mounting quarter-turns.
  Default0 now uses measured screen gravity-down `(-ax,+ay,-az)`. The original
  quarter-turn-only mapping was wrong: screen and sensor XY handedness differ.
  Upright measured approximately(+0.053,+0.913,+0.385)g; clockwise90 measured
  (-0.451,+0.234,+0.863)g. Both are user-labelled, with raw RPC evidence retained.
  Additional quarter-turns apply only after this axis conversion. An IMU does not identify
  which side of a flat screen the viewer occupies; flat placement holds direction.
- Device RPC0x504c/1 adds `orientation`, `orientation_auto`, `imu_error`, `imu_ms`
  and `imu_accel`. `imu_ms` is the last sampling attempt; raw acceleration retains
  the last finite successful reading on failure. Existing fields are unchanged.
- Native preview: `python3 tools/control.py orientation 90` (also0,180,270).
  This is a manual diagnostic input, not simulated hardware proof. `status.json`
  exposes `orientation`. Controls/diagnostic screen remain in their native frame.

## Validation

- `cmake -S . -B build-host && cmake --build build-host -j 4 && ctest --test-dir build-host --output-on-failure`:
  Integrated/calibrated source28/28 pass, including real artwork pixels at all rotations, full480 and the
  approved dragon2x2 sampling, source state invariance, touch rotation, canceled
  gestures, classifier uncertainty/time, IMU startup cleanup and fixed mode.
- `python3 tests/test_replay.py`: original5 cases, deterministic replay and
  malformed input checks pass.
- With this worktree's official GSP1.5.1/native preview running:
  Before mechanical C integration, `python3 tests/test_orientation_gsp.py`:32 full-frame comparisons against
  native raster with independent inverse-gaze/quarter-turn calculation pass;
  idle/target source state and replay direction remain unchanged. PNGs are local
  under `.run/orientation/`.
- `PEEK_EVIDENCE_DIR=.run/gsp-regression-final python3 tests/test_gsp.py`:
  existing100-check interaction/detection suite passes on the final source.
- `python3 tools/bootstrap.py`: pinned dependencies verified and prepared only
  in this worktree. `python3 tools/build_idf.py`: doctor and ESP32-S31 build pass
  on pinned ESP-IDF `7b9cc1a`. Current app6,681,344B fits unchanged ota_0 (0xcf0000).
  The existing retained factory capacity warning remains: app is too large for
  factory0x1c0000. Never use the generated whole-flash command for installation.
- Independent read-only review found the role-transition gaze jump; a failing
  pixel regression reproduced it before the common-frame fix. That regression
  now passes. Initial GSP startup was blocked by sandbox socket permissions;
  approved local-only execution ran the actual checks, without changing ports
  or processes belonging to the main thread.

## Integration and hardware acceptance

Keep the main thread's current `eye_pack.c/.h`, assets, recipes, eye pack CMake,
firmware version and build settings. This branch deliberately does not edit them.
Likely merge overlaps are root/main/PC source lists and shared `peek_ui.c/.h`;
combine source lists and retain both feature changes. Re-run Host/GSP tests and
build against the integrated artwork before any device update. Corrected candidate uses distinct1.0.9-peek-orient identity and sdkconfig.orientation-calibrated. Host28/28 and pinned-IDF build pass. The merge preserved immutable source CSV CRLF and license whitespace despite git diff --check warnings on those imported files; feature-owned source checks are clean.

The user completed the four-direction dragon check. Remaining acceptance for other artwork and controlled performance:

1. Log raw IMU readings upright, left/right side and upside-down; adjust the
   mounting quarter-turn setting if required. Check sign/axis correctness first.
2. In every direction move a real heat source left/right/up/down, verify gaze
   and visible swipe directions, and switch through every integrated character.
3. Rock near diagonal thresholds, pick up/shake, place flat, start while flat,
   and simulate IMU faults. Hold the last direction without chatter or UI failure.
4. Measure active-open draw/submit timing, not sleeping frames, against the same
   scene before/after rotation. Host checks do not establish panel FPS.

Implementation checklist: classifier, shared renderer, IMU adapter/configuration,
telemetry, native controls and local build checks complete. Physical mounting and four-direction dragon interaction are now accepted. Other
artwork-specific physical checks, controlled performance/long-term stability and
merging this branch back into the main UI worktree remain outstanding.

## Physical finding and correction

Official1.0.8 operation862149bf-00bf-4d2a-ace8-1d55d7ed0578 succeeded,
healthy/validated, Boot1100252626072364809. No Recovery replacement, partition
layout change or bootloader write. IMU/thermal/runtime errors stayed0 in the
recorded window; this did not prove orientation correctness.

User-labelled upright produced orientation270 and a counterclockwise90 eye.
After physically rotating clockwise90, the device produced orientation0 and a
clockwise90 eye. Therefore the failure is both the original mounting assumption
and XY handedness, not a single constant rotation offset. Real raw vectors now
form the device adapter regression fixtures. They failed before the correction.
Tests also cover the opposing cardinal vectors, but those tests do not replace
physical four-way acceptance. The follow-up1.0.9 update and user retest passed;1.0.8 remains a rejected firmware.
The first1.0.9 update attempt was outcome_unknown after Recovery reset; a read-only
reconciliation, absent old job and explicit approval preceded one successful retry.
Final observation ended on USB endpoint loss after138s; a later power-on boot
reported expected1.0.9/ELF, crash_count0, application/IMU error0 and VALID fresh
thermal frames. The new boot had2 cumulative thermal faults; cause unverified.
Do not claim uninterrupted operation or zero total post-reboot capture faults.
