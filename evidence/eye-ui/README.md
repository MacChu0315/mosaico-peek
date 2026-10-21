# New three-theme native acceptance (2026-10-21)

This evidence belongs to the appended night owl/deep sea/mechanical views.
No device writes, restart, Recovery, remote writes or physical validation.
Current installed dragon trial is retained separately in docs/HANDOFF.md.

- Host Debug and Release CTest18/18. Logs: ctest-debug.log / ctest-release.log.
  Existing detector, timing, sleep, fixed/prepared cache and lifetime tests remain;
  new tests cover three-layer rendering and source-build immutability.
- `python3 tests/test_replay.py`:5 production-C cases, deterministic and malformed
  input checks pass. `python3 tests/test_real_replay.py`:511 exactfloat32 arrays /
  655 original events, zero stored-device/core field mismatches.
- Independent57 full480 PNG/compositor comparisons pass (`independent-pixels.json`).
  Python float64 vs C float32 permits one565 channel code only at rounding
  boundaries; no channel difference over1, fewer than500 differing channels/frame.
  Source RGBA remains lossless; no palette, image scaling or sample reduction.
- Native66 controlled checkpoints match **every565 output channel** against the
  full C raster. `native/checks.json` pairs poses/results with actual PNG hashes.
  Covers IDLE/NOTICE, four-way motion, fresh stillness/HOLD, held observation,
  LEAVE/reappearance, INVALID/STALE, candidates, closure/sleep/wake and recovery.
  Pause/redraw, replay and cross-view state preservation pass for every theme.
- Six native real-time movies: `native/<theme>-dragon-realtime.mp4` (about30s)
  and `<theme>-sleep-realtime.mp4` (about34s). Each uses original screenshot wall
  intervals; ffprobe duration differs from observation by less than0.2s.
  `*-captures.json` and `*-states.jsonl` retain wall/logical time and source type.
  Synthetic complete Celsius arrays enter the unchanged production C detector.
- Recorded input: `recorded/report.json`, events/states/switches and
  `recorded-switches-realtime.mp4`. Each theme consumes all655 events/511 arrays
  and repeats identically. The wall-time run switches among new views, dragon
  and diagnostics six times without epoch reset or detector/role-mode mismatch.
  The scene is unlabelled and does not establish a production HOLD interval.
- Original native diagnostics and dragon controlled regressions are recorded in
  `baseline-native/` and `dragon-regression/`, with separate final command logs.
  They exercise actual native rendering and original external controls; no new
  physical gesture behavior is claimed. Old historical evidence is not replaced.
- Pinned IDF doctor/build passes: current image/config hashes and target ABI
  allocations in `resource-budget.json`; exact logs retained. App6504384B at the
  initial final build fits unchangedota_0(13565952B). UI bundle counts separately.
  The retained factory partition is smaller and still generates its capacity
  warning; no partition or Recovery image change. Final source-commit rebuild
  can update image hashes/bytes in the budget without changing these boundaries.
- PSRAM renderer:2587440B bulk (921600 frame +1654848 eye/two-lid capacity +10992
  ROM inflate workspace) plus52B renderer state on target. All themes share this
  capacity. Dragon renderer3929120B is lazy/retained if selected, additional to
  the new renderer. RODATA/text PSRAM reservations, framebuffers, sensor state,
  SDK heaps/stacks/queue and overlap are additional. See exact ELF sections and
  whitelisted effective config, not Host sizeof, for target allocation values.
- Normal connected Chrome observations: `host-performance.md/json`.5s per scene/
  theme, no screenshots/status polls/builds inside each window. Active moving
  scene (including ordinary blinks) is separate from fully closed idle. Draw
  callbacks18.48–18.88/s active,18.77–19.19/s sleeping; each callback was full480
  in this Host run. Host GSP commit sequence18.78–19.18/s active. These are short
  observations, not physical or browser-visible FPS. No30Hz pass claim.

Failures retained rather than relabelled:

- First added Host adapter build needed CONFIG_PEEK_CHARACTER in the existing
  test stub; this fixture was updated, and full Debug/Release reruns passed.
- `idf-first-error.log`:new generated include directory did not exist at IDF
  configuration. CMake now creates its own build output directory before include
  registration; subsequent actual IDF builds pass. No dependency upgrade/fullclean.
- Restricted socket/proc visibility initially prevented local simulator control;
  loopback permission allowed identification/stopping of only this project's old
  preview and running the native checks. No device process was stopped.
- The budget reporter initially searched only nmR/r symbols; this SDK places
  XIP RODATA in a WA PSRAM-mapped section and nmd symbols. Counting was corrected
  to include the actual eye stream symbols; final report is not a zero-Flash claim.

Not verified: ESP32-S31 ROM decompression execution, device frame time/PSRAM
bandwidth, actual heap/free/largest-block or peak allocation, physical panel FPS,
new art and post-flip orientation on the physical screen, BSP touch/AI switching.
Screenshot sampling can miss a short150ms wake; exact controlled checkpoints
verify its intermediate pose. Video encoding rate is never a screen FPS metric.

Whitespace check: `git diff --cached --check -- . ':!assets/eye-pack'` passes.
The full imported-source check reports trailing whitespace in the supplied
FONT_LICENSE.txt and extra final blank lines in two supplied CJS tools. These
three source-package formatting warnings are intentionally retained byte-for-byte
so the original source/license checksums remain valid; they are not edited away.
