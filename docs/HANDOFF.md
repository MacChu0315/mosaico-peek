# Peek mainline — live dragon handoff (2026-10-21)

Reviewed baseline `f278cfd`; branch `feat/dragon-gsp`. The device remains running
`1.0.1-peek-dragon240`, application source **ba98632f38233c2af20009a3a088b5328316f35d**,
ELF SHA `1b1f39a4176c2d4d2e1b15b6080180656ee2958d7a011b85c925b24c8d23ebbd`.
MAC `30:ed:a0:f4:52:a0`, Device ID `4553502d49524953010030eda0f452a0`,
Boot ID `408941243312734824`. Official update operation
`0dbfa8e7-686a-4b28-8eb0-a8e07da5c3fd` completed healthy/validated through
existing Vibe Mode; identical bootloader/layout, ota_0 retained, no recovery
firmware update. No other device, adjacent checkout modification, algorithm A/B,
dependency upgrade or remote write.

## Delivered behavior

- Acquisition processes every successful complete768-temperature frame/fault
  through production C detection and role before the latest-only display mailbox.
  Display owns an independent copy; a slow renderer cannot drop detector samples.
- User explicitly approved240 unique eye samples replicated2x2 into480 output.
  Source textures/shape/color and full fixed-pixel PSRAM cache remain retained.
  Step1 remains the pixel-equivalent480 reference. See SAMPLING240.md and
  DEVICE_PERFORMANCE.md for earlier rejected exact-output optimizations.
- User confirmed visible follow on c316843 but requested both axes reversed.
  Device source-owned mapping now flips x/y before target-to-gaze conversion;
  raw thermal arrays and detector coordinates remain native. Both runtime flags
  are confirmed true by read-only RPC. Host can reproduce the mount with
  `python3 tools/preview.py --sample-step 2 --flip-x --flip-y`.
  The two flags are reapplied on replay reset; pause never creates observations.
- Detector source/parameters and shared dragon behavior remain byte-identical to
  reviewed f278cfd. Detector/header also match read-only diagnostic63c0799.
  Area/contrast/continuity rules still track significant **hot** regions, not cold
  objects, identity, classification or distance. Existing targets retain priority
  within the association gate; initial selection uses summed temperature excess.
- IDLE retains authored calm10s gaze holds and seeded blinks, approximately4–8s
  apart. It does not increase blink frequency. LEAVE returns over1200ms once
  the core removes the target. Other persistent hot regions may prevent IDLE.

## Actual verification

- Debug and Release CTest **12/12**; original5 replay cases and complete real
  replay pass. Asset tests keep ordinary builds read-only and no longer make the
  missing-original assertion depend on the host Pillow version.
- New regression failed before the fix, then passed: both physical mapping flags
  are initialized in source and display owners and survive the display snapshot.
  Shared mapper checks exact reflection at all768 sensor centers.
- Native GSP compares identical inputs with and without mount flips: detector
  results and role decisions identical, material gaze excursions reverse on both
  axes, replay/pause pure. Authored idle offsets and HOLD micro-motion are not
  mirrored, so transient poses are intentionally not exact negative images.
  An initial test assumption of near-exact inverse transient poses failed;
  that failure and the corrected direction-focused checks are both retained.
- **27** actual native role checkpoints pass; **19** actual PNGs match every
  RGB565 output pixel to the approved2x2 policy, including closed-eye/aperture
  checks. Retained step1 reference parity evidence remains separate.
- Latest native wall run:68.53s, all511 original arrays/655 events from the
 65.074s successful capture window, original capture/receive/fault timeline,
  zero detector/role-mode mismatches. Latest movie uses both flips. No resampling
  or recorded focus drives detection. See evidence/real-input/ and
  evidence/orientation/. The unlabelled recording does not trigger HOLD;
  synthetic regression covers HOLD independently.
- Pinned IDF doctor/build passes for ESP32-S31. First incremental build retained
  old Kconfig; the wrapper rejected missing flip flags and it was **not installed**.
  Touching the project CMakeLists.txt forced local reconfiguration; the subsequent
  build passed all config assertions. Reproduction/error logs retained under
  evidence/orientation/. One existing retained-factory size warning remains;
  app1,990,480B fits unchanged ota_0. No fullclean/shared upgrade.
- Official device screenshot was inspected; approved single textured eye runs
  with continuous live sensor data. Healthy matching ELF and unchanged crash
  count were checked separately from simulator results.

## Measured device performance and remaining acceptance

Latest24.78s read-only steady window (before screenshot): **7.829 accepted
samples/s**, **7.546 GSP engine frames/s**, **77.684 tiled Canvas callbacks/s**.
Every observed sequence equals accepted sample count; zero read faults in that
window. GSP mean121.86ms/frame, raster90.98ms, submit30.76ms. Observed cores:
GSP1, capture/detector/role0. These are elapsed wall times, not CPU-only timings.
**Physical panel-visible FPS is not measured.** Historical49a7c57 engine rate
was2.693Hz; scenes differ, so this is not a controlled identical-pose speedup.
Host30Hz remains unmet and was not investigated further.

Internal free237,955B/min196,784B; PSRAM free/min9,918,228B in this window.
These allocator values are not a complete application peak/largest-block
measurement. Screenshot workload can lower subsequent boot-wide minimum. The separate59.54s
unlabelled observation afterwards stayed IDLE/VALID throughout, with7.423 engine
frames/s,7.843 samples/s and no faults; PSRAM minimum after screenshot was9,447,112B.
This proves a physical live IDLE state was observed, not that a labelled cup
removal caused it.
`iris memory` task observation remains unavailable (HTTP501); status heaps work.

User confirmed visible follow before the flip, then asked what IDLE looks like
rather than confirming the post-flip trial. **Post-flip physical direction,
stationary review/removal-to-IDLE and perceived smoothness remain unaccepted**;
software/native checks and runtime flags do not replace that observation.
Original pre-flip motion evidence and exact feedback are retained. FOV/range,
labelled accuracy/temperature calibration, panel FPS, long-term reliability and
hotplug remain unverified. No failed acceptance is rewritten as passed.

## Reproduce / restore / review

Build/test commands are in README. Use `tools/control.py case live` then `play`
for the full recording in the native preview. `tests/test_native_mapping.py`
requires an unflipped baseline run with `--record-baseline`, then a flipped run.
`tools/probe_device.py` is read-only and uses only the exact selected device.
Evidence directories distinguish historical480, approved240, and final flipped
runtime; telemetry summaries explicitly separate callback/engine/panel rates.

Current bundle: `evidence/orientation/installed/dragon240-flipped.irisfw`.
Previous240: `evidence/sampling240/installed/dragon240.irisfw`.
Previous480: `evidence/sampling240/restore-480/dragon480.irisfw`.
Exact diagnostic restore: `evidence/device-dragon/restore/diagnostic.irisfw`.
Restore through the official command documented in DEVICE_DRAGON.md, selecting
one intended bundle and the same Device ID; no restore is performed at handoff.
Full known local BIN/ELF/map/config/resource backups remain under firmware-local/
(excluded from the small review ZIP). No device readback/full-flash backup claim.

`python3 tools/package_review.py` produces the clean-commit review ZIP and hash
under review/, excluding .git, caches and retrievable dependency copies. Its
manifest retains source hashes and aliases only byte-identical duplicate PNGs.
The latest native movie is screenshot-sampled4fps; it is dynamic evidence, not a
screen-rate measurement. Device stays running the final dragon for user trial.
