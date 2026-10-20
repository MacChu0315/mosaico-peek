# Follow-up to review of463a3588

Scope: preserve approved visual art and existing core detector. No device operations, candidate-algorithm merge, tracking-worktree edits or shared dependency upgrade. Pre-existing root `.codex-runs/` diagnostic logs belong to other activity; left untouched and excluded from this review.

## Correctness / asset build stage

The supplied `repro/run.py` returned2 against463a3588, reproducing30Hz HOLD vs60/120Hz TRACKING at receive2200. `dragon_update` now expires the **previous** observation before new capture identity/evidence can overwrite it, and retains the post-event expiry check. All three rates return TRACKING, stationary=false, quiet_since=2000. Thresholds300/900ms, velocity, spring, held and detector policy stay unchanged.

`tests/test_dragon_timing.c` uses production Celsius arrays and detector with eight receive-delay/boundary/held scenarios at30/60/120Hz, fixed125ms delay, arrival at2175/2176, an over-aged new capture, stopped input and same-time idempotence. Existing behavior/raster tests remain in place.

Ordinary baking reads and validates retained PNG, pixel, quantization and include hashes without writing the source tree. Build-local generation JSON records the actual tool version independently of original provenance. `--check` is read-only; `--update-assets` is explicit, requires original art and the pinned Pillow version. Script and CMake read-only regressions include source content/mtime, tamper rejection and successful explicit updates in temporary copies. The651780-byte C asset payload and retained art are unchanged.

Performance measurements and current image/map/XIP budget follow in the second stage; normal/no-query preview and screenshot/poll conditions use the same version/scene/timer. Device diagnostic work is separate and is not evidence of mainline hardware acceptance.

## Host measurement stage

One connected Chrome native preview stayed open for the same binary/bundle/scenes and33ms target timer. Each idle/flow ×A/B condition ran twice for30s; repeat2 reversed A/B order. Formal windows had no builds or browser automation. A has zero screenshot/status reads **inside** the window (boundary counters and public frame_info only); B uses the prior8fps API screenshot target and15ms loop sleep, with actual observed status reads about9.4–9.6Hz. Preparation, callback body/status write, draw, interval histograms, surface bounds and process CPU/load snapshots are retained separately. Surface/prepare extrema labelled session are not window extrema.

The initial runner completed and flushed all8 raw window records, then its report assembly raised a NameError for `sources`. That report-only bug was fixed; a complete1s-per-condition tool check returned0. The formal report was reassembled from the original8 JSON records without changing values, verifying them byte-for-structure against each saved record, the same backend/simulator PIDs across boundaries, and final artifact hashes against a saved pre-window smoke report. The initial error is retained in `performance-ab.log` and recovery is recorded in `ab-results.json`. The first smoke run overlapped build work and is only a functional/version-hash check; no smoke rates contribute to the formal A/B table.

Normal-preview draw callbacks are14.955Hz idle /14.914Hz flow; screenshot/poll callbacks are14.384 /14.122Hz. Public frame commit-sequence rates are separately14.952 /14.919Hz in A and11.664 /11.428Hz in B. Neither is browser-visible FPS or device FPS. Pure C draw is about12.4–12.6ms, prepare about0.029ms, total timer callback including status publication about0.21–0.31ms. About54–58ms per draw cycle remains outside those measured backend sections; this residual is **not** assigned to a single bridge/transport/present component. Normal preview still misses the ~30Hz goal, so removing screenshots alone would not fix it.

No speculative runtime optimization, texture reduction, target-timer change or public dependency modification was made. A useful next trace is per-poll/upload-ack and host commit/present timestamps in an isolated vendor/debug build, while keeping this artwork and input sequence. The current public frame_info interface provides seq/damage, not the required internal durations.

Final SDK/map review confirms XIP, instruction fetch and rodata-to-PSRAM configuration. The651780-byte texture/LUT payload is included in both app Flash and the linked rodata copy/mapping budget; zero decoding allocation does not imply zero PSRAM residency. Whitelisted final config and section/symbol summaries, image/config/map/ELF hashes and actual build warnings are retained; startup residency/freeheap/peak and device FPS remain unmeasured. The independent hardware/algorithm line was not accessed or merged.
