# Automatic eye orientation — integration handoff

## Scope and status

Local implementation on `feat/auto-orientation` in `mosaico-peek-orientation`,
based on `b53d861`. Four cardinal placements keep artwork upright after settling.
Flat, moving, ambiguous and failed IMU samples retain the last orientation.
No continuous-angle stabilization or compensation for changed thermal field of
view. Existing characters use the common layer; new artwork must use that same
layer to inherit orientation.

The main `mosaico-peek` worktree has concurrent mechanical artwork work. None of
its files, branches, running previews or devices were modified by this task.
No device installation, dependency upgrade, remote write or main-branch merge.
**Hardware acceptance remains pending.** Do not treat the built firmware as a
physically validated replacement for the main thread's current firmware.

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
  Default1 uses screen gravity-down `(ay,-ax,-az)`. Existing Mosaico IMU app code
  describes90-degree mounting, but this exact screen/sign relationship is
  **provisional until verified on the physical board**. An IMU does not identify
  which side of a flat screen the viewer occupies; flat placement holds direction.
- Device RPC0x504c/1 adds `orientation`, `orientation_auto`, `imu_error`, `imu_ms`
  and `imu_accel`. `imu_ms` is the last sampling attempt; raw acceleration retains
  the last finite successful reading on failure. Existing fields are unchanged.
- Native preview: `python3 tools/control.py orientation 90` (also0,180,270).
  This is a manual diagnostic input, not simulated hardware proof. `status.json`
  exposes `orientation`. Controls/diagnostic screen remain in their native frame.

## Validation

- `cmake -S . -B build-host && cmake --build build-host -j 4 && ctest --test-dir build-host --output-on-failure`:
  26/26 pass, including real artwork pixels at all rotations, full480 and the
  approved dragon2x2 sampling, source state invariance, touch rotation, canceled
  gestures, classifier uncertainty/time, IMU startup cleanup and fixed mode.
- `python3 tests/test_replay.py`: original5 cases, deterministic replay and
  malformed input checks pass.
- With this worktree's official GSP1.5.1/native preview running:
  `python3 tests/test_orientation_gsp.py`:32 full-frame comparisons against
  native raster with independent inverse-gaze/quarter-turn calculation pass;
  idle/target source state and replay direction remain unchanged. PNGs are local
  under `.run/orientation/`.
- `PEEK_EVIDENCE_DIR=.run/gsp-regression-final python3 tests/test_gsp.py`:
  existing100-check interaction/detection suite passes on the final source.
- `python3 tools/bootstrap.py`: pinned dependencies verified and prepared only
  in this worktree. `python3 tools/build_idf.py`: doctor and ESP32-S31 build pass
  on pinned ESP-IDF `7b9cc1a`. App6,662,368B fits unchanged ota_0 (0xcf0000).
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
build against the integrated artwork before any device update. This isolated
build still uses the baseline1.0.6 version identity, so integration must assign
its own release version rather than confusing it with installed1.0.6.

After the main thread releases the test device, verify:

1. Log raw IMU readings upright, left/right side and upside-down; adjust the
   mounting quarter-turn setting if required. Check sign/axis correctness first.
2. In every direction move a real heat source left/right/up/down, verify gaze
   and visible swipe directions, and switch through every integrated character.
3. Rock near diagonal thresholds, pick up/shake, place flat, start while flat,
   and simulate IMU faults. Hold the last direction without chatter or UI failure.
4. Measure active-open draw/submit timing, not sleeping frames, against the same
   scene before/after rotation. Host checks do not establish panel FPS.

Implementation checklist: classifier, shared renderer, IMU adapter/configuration,
telemetry, native controls and local build checks complete. Physical mounting,
real interaction/performance acceptance and integration remain outstanding.
