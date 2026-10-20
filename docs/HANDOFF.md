# Mainline follow-up handoff — review463a3588

Keep branch `feat/dragon-gsp`, approved single dragon art and production detector. Correctness/read-only-build fix is local commit `99c2b97`; the second stage contains Host observation, A/B measurement/reporting and this handoff (exact final commit in REVIEW_MANIFEST). No device operation, candidate-algorithm merge, adjacent tracking-worktree modification, public dependency upgrade or remote write occurred. Pre-existing root `.codex-runs/` diagnostic logs were preserved and excluded.

## Fixed and verified

- The supplied review probe returned2 on463a3588 and now returns0. At capture2000/receive2200,30/60/120Hz all return TRACKING, stationary=false, quiet_since=2000. Previous evidence is aged before new capture overwrite, with post-event aging and same-time idempotence retained. No300/900ms threshold, velocity/spring/held or detector-policy changes.
- `tests/test_dragon_timing.c` covers8 ordered latency/boundary/held scenarios ×30/60/120Hz, fixed125ms latency,2175/2176 arrival boundaries, over-aged captures, stopped input and repeated same-time updates.
- Ordinary asset build is read-only for retained PNG/provenance; it verifies all hashes and writes include/generation info only to build output. Explicit `--update-assets` requires original art and pinned Pillow.9 script regressions and an actual CMake asset-only build verify content and mtime preservation, tamper rejection, and explicit-update behavior. The C include hash and651780-byte payload are unchanged.
- Debug and Release configure/build/CTest:8/8 pass. Original5-case replay and malformed/core-equivalence tests pass. Native role check:27 controlled points pass.19 newly recaptured GSP PNGs and art/renderer/scene files are byte-identical to reviewed463a3588; every frame's230400 RGB565 pixels match the C raster and independent aperture/closure checks pass.
- Fixed ESP-IDF doctor/build succeeds for `esp32s31`; final raw/result/summary retained. Source asset hashes/mtime remain unchanged. Python compileall passes. Retained sanitizer limits from phase2 remain; no new device test is implied.

Actual commands/logs: `evidence/followup/{host-tests,release-tests,replay-tests,timing-review-after,native-role-validation,native-role-pixels,idf-build-summary}.log`; reproducible commands remain in README and tools.

## Host A/B result

Same running native backend/bundle and synthetic input, connected Chrome preview,33ms timer. Two30s windows per condition/scene, reversed order in repetition2. A: no screenshots/status sampling inside the window. B: API screenshot target8fps +15ms loop sleep (actual status reads about9.4–9.6Hz). No builds or browser automation during formal windows.

| Scene | A normal draw callbacks/s | B screenshot/poll draw callbacks/s | A commit seq/s | B commit seq/s |
| --- | ---: | ---: | ---: | ---: |
| idle | 14.955 | 14.384 | 14.952 | 11.664 |
| target-flow | 14.914 | 14.122 | 14.919 | 11.428 |

The ~30Hz goal remains unmet in normal preview. C draw averages12.4–12.6ms, prepare about0.029ms and full timer body/status write about0.21–0.31ms. The native interval is about67–71ms; the54–58ms residual outside the measured backend sections is not an isolated bridge/present measurement. The public frame_info interface reports commit seq/damage only. Browser-visible FPS is not measured. Surface requests remain actual480×480; session extrema are labelled as such.

`evidence/followup/performance/AB_COMPARISON.md`, `ab-summary.json`, all8 raw windows, clock/counter snapshots, interval histograms, CPU/load samples and artifact/source hashes are retained. No optimization was justified in the owned callback/prepare path; no texture,33ms target or public bridge was changed. Next step, if further performance work is requested, is an isolated per-poll/upload-ack/host-commit trace, not another blind art reduction.

The initial post-measurement summary NameError and exact report recovery are disclosed in FOLLOWUP_RESPONSE and `ab-results.json`; every original window remains intact and independently rechecked. A complete short tool rerun succeeds. Smoke runs are tool checks and excluded from the formal table. The B-flow MP4 samples actual GSP API pixels and encodes8fps, with captured wall timestamps; encoded rate is not runtime/browser/device FPS.

## Final Flash / PSRAM interpretation

`evidence/followup/firmware-budget.json`, `sdkconfig-memory.txt` and `map-summary.txt` retain final artifact hashes, whitelisted build configuration and actual ELF/map section/symbol sizes.

- `peek.bin` **1,985,504 B**, `ui_apps.bin` **94,480 B**, combined2,079,984 B. Texture/palette/LUT **651,780 B** is already included in app size; do not add it twice. UI fits1MiB; app fits the unchanged `ota_0` capacity13,565,952 B.
- Actual build has5 SDK private-include CMake warning lines plus the retained-factory size warning. App exceeds the retained factory capacity1,835,008 B by150,496 B; normal application integration targets `ota_0`. No partition was changed and no install was performed.
- `CONFIG_SPIRAM_XIP_FROM_PSRAM=y`, `CONFIG_SPIRAM_RODATA=y`, instruction fetch and flash-load-to-PSRAM are enabled. Seven dragon asset symbols are in linked `.flash.rodata`; that name does not prove flash-only runtime residency. Linker reserved spans are849,888 B rodata and1,025,120 B instructions, including their respective non-texture contents/reservations. These configuration/linker deductions require PSRAM mapping/copy budget but do not establish successful startup or measured heap occupancy.
- Updated target-ABI static estimate: app13,576 B +3×3,104 B messages +renderer12,308 B =35,196 B, plus8,192 B sensor task stack and additional RTOS/GSP/presenter/DMA/SDK allocations. One480×480 RGB565 plane is460,800 B; possible eye+diagnostic Canvas planes total681,984 B. None of these subtotals is a measured device peak.

## Handoff boundary

Artwork, source textures and core detector remain unchanged. Source/build fixes, original regression closure, normal-vs-observer Host comparison and local firmware build are reviewable. Device startup/residency/FPS/RAM, continuous thermal quality, physical mapping/FOV/distance, real interaction delay/power and long-term stability remain unverified by this mainline work. The other session's diagnostics do not certify this role firmware. Stop here for ChatGPT review; do not install, push or merge an algorithm candidate without a new scoped instruction.
