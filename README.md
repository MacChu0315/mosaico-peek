# mosaico-peek — thermal eye characters

Shared C thermal detection → shared C behavior/pose → native 480×480 GSP artwork.

New native views: **night_owl / deep_sea / mechanical**, alongside the retained
dragon and diagnostics. [Current three-theme integration, commands and limits](docs/EYE_UI.md).
Use `python3 tools/control.py view night_owl` (or deep_sea/mechanical/dragon);
`python3 tools/preview.py --view night_owl` starts directly.
New art remains full480 with lossless RGBA sources and blended lids. Current
build is1.0.7-peek-mechanical (`sdkconfig.mechanical-c`): both gaze flips disabled per
latest user feedback, new eyes use sphere rotation with120/80px pure-axis center
travel. [Motion change and validation](docs/EYE_MOTION.md).
The user accepted direction/range. Mechanical now uses the supplied C artwork
with a rotating central shutter; owl/sea remain unchanged.
[Mechanical C adaptation and verification](docs/MECHANICAL_C.md).
[Original artwork handoff](docs/EYE_ART_HANDOFF.md) remains historical.
Installed1.0.6-peek-motion corrects mapping and motion. The prior1.0.5 improved
observed mechanical active-open engine rate
from2.009 to8.333Hz in separate live scenes; current installation status is in
[handoff](docs/HANDOFF.md). Physical panel FPS is not measured.

 Phase2 keeps the approved purple-black scales, yellow/green/gold iris, vertical slit and heavy textured eyelids. Gemini is motion reference only. The live-dragon continuation reuses the diagnostic recording and targets only MAC `30:ed:a0:f4:52:a0`; [installation/recovery and telemetry](docs/DEVICE_DRAGON.md). Historical phase2/follow-up evidence remains separate.

[Tap/swipe/AI switching and verification](docs/CHARACTER_SWITCHING.md): tap or left
swipe advances, right swipe goes back, AI single click advances. Switching is installed in1.0.4. [Full480 rendering optimization](docs/EYE_PERFORMANCE.md)
was installed as1.0.5; subsequent same-device firmware updates are authorized.

## Start

From this directory, with the existing sibling dependencies and pinned tools:

```sh
python3 tools/bootstrap.py
python3 tools/preview.py --sample-step 2
```

This opens/prints the official native GSP URL, starting on the synthetic dragon case, paused. Controls stay **outside** the artwork:

```sh
python3 tools/control.py play
python3 tools/control.py pause
python3 tools/control.py step
python3 tools/control.py replay
python3 tools/control.py case idle
python3 tools/control.py case dragon
python3 tools/control.py view diagnostic
python3 tools/control.py status
python3 tools/stop_preview.py
```

`python3 tools/preview.py --view diagnostic` starts the original heatmap/buttons. Cases: empty, motion, multi, gaps, recorded, aging, dragon, idle, live, sleep (or indexes0..9). CASE resets and pauses; REPLAY resets source/time/identity/detector/role/random seed while preserving play/pause; STEP pauses and processes the next input event. `advance MS` is a controlled replay operation. EOF pauses. Real acquisition continues monotonic time; firmware defaults to dragon and offers `CONFIG_PEEK_DIAGNOSTIC_VIEW` under “Peek diagnostics” in menuconfig for a diagnostic build. No touchscreen input represents a thermal target.

Only one preview per working directory is supported. Loopback socket permission is necessary in restricted sandboxes. The launcher uses temporary local listeners and a callback-boundary quit; it never stops another simulator/Gateway. GSP does not physically simulate MLX90640: this project's `.peek` arrays enter the real detector.

## Approved240 sampling

The user accepted the displayed240-vs480 detail tradeoff on2026-10-21. Device and native startup use `sample_step=2`: evaluate the same C shader at `(x|1,y|1)` and replicate globally aligned2x2 cells into the unchanged480×480 RGB565 Canvas. Sensor32×24 input, detector/role parameters, texture PNGs and geometry remain unchanged. Odd tile origins, padded strides and edge pixels are covered by `render_sampling`; the scalar renderer still defaults to lossless step1 for references. `python3 tools/preview.py --sample-step 1` retains the old native quality. Neither mode changes detector counts.

Retained installed baseline firmware version is `1.0.2-peek-sleep`; its build uses isolated `build/sdkconfig.dragon240-sleep` with `CONFIG_PEEK_EYE_SAMPLE_STEP=2`. Read-only RPC/status records the actual step. The fixed-pixel cache remains full-sized; reducing shader work does not claim reduced cache RAM. Retained480 firmware: `evidence/sampling240/restore-480/dragon480.irisfw`; diagnostic restore remains separately retained. Install only through the official workflow and the authorized MAC.

## Complete recorded input / live dragon

`python3 tools/control.py case live` then `python3 tools/control.py play` runs all511 recorded temperature arrays and655 original submit/fault/tick events through the production C detector and role. `data/live/20261020-complete-window/` is copied unchanged from diagnostic handoff63c0799; successful-frame span65.074s, unlabelled scene. Processing/capture/fault times are preserved, no interpolation or prefilled focus. `python3 tools/import_live.py` regenerates `data/live.peek`; `E now` is an additive fault event, not a sample. `python3 tests/test_real_replay.py` checks every recorded C result and deterministic role output. `python3 tools/validate_real_gsp.py` records the wall-clock native run; [actual native movie](evidence/real-input/recorded-native.mp4). No HOLD is triggered by this recorded scene under the unchanged quietness threshold.

The renderer retains its full invariant cache of3,225,600 bytes for invariant geometry/static colors in explicit device PSRAM; its workspace plus both caches total3,929,120 bytes is reported separately from textures and framebuffer memory. [Device rendering investigation](docs/DEVICE_PERFORMANCE.md) retains exact pixel/ownership evidence and actual runtime rates.

The retained installed dragon build selected `build/sdkconfig.dragon240-sleep`, version `1.0.2-peek-sleep`, approved art and existing detector, with a small read-only acceptance RPC instead of the diagnostic full-array recorder. See [target, telemetry, installation and exact diagnostic restore bundle](docs/DEVICE_DRAGON.md). Host30Hz remains unmet and is not investigated further here. Real replay and physical acceptance are reported separately in [handoff](docs/HANDOFF.md).

## Build / verify

```sh
cmake -S . -B build-host
cmake --build build-host
ctest --test-dir build-host --output-on-failure
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release
ctest --test-dir build-release --output-on-failure
python3 tests/test_replay.py
python3 tools/build_idf.py
```

With preview running, `python3 tests/test_gsp.py` verifies original diagnostics and core/native equivalence. `python3 tests/test_dragon_gsp.py` performs controlled native checks plus61s idle and30.5s live full-flow observation. `tools/verify_pixels.py` checks five retained diagnostic PNGs and actual cross coordinates; `tools/verify_dragon_pixels.py` checks retained dragon PNGs against a full C raster and independent Bézier aperture geometry. Both work from the ZIP after Host build, without excluded intermediate movie frames. `tools/encode_live.py` recreates movies only when live screenshot intermediates are available in `.run/`.

Dependencies are unchanged: ESP-IDF commit `7b9cc1ac79f865983f59bb8ff3ff43eb74ff1dbe`, target `esp32s31`; CMake version6.2.0 satisfies >=6.2 while git describes this development SDK as `v6.1-dev-7333-g7b9cc1ac79f`. ESP-GSP1.5.1 (`472207a3…`), GSPC0.6.1, simulator1.5.1, RISC-V GCC16.1.0, BSP `a2c985ad…`, utils `fc63d43f…`, Vibe `95469e63…`. The separately pinned official thermal driver is BSP `5f88b91e…`, unmodified C. Exact source hashes and versions: `dependencies.json` and `projects/peek/dependencies.lock`; [source/licensing](THIRD_PARTY.md).

Asset generation requires **Pillow10.4.0** for byte-identical output; this was already available in the Host Python. CMake only reads/verifies retained assets and provenance, and writes the include plus generation information inside each build tree. Source PNG/metadata updates require explicit `python3 tools/bake_dragon.py --update-assets`; ordinary builds never rescale source art or rewrite its Pillow provenance. The build wrapper supplies that existing interpreter separately from ESP-IDF Python, without installing into/upgrading the shared SDK environment. `python3 tools/bake_dragon.py --check --output build-host/dragon-generated/dragon_assets.inc` verifies it. Retained source PNGs + provenance reproduce the assets even without `review-inputs/`. GSP tool paths can be overridden with `ESP_GSP_COMPONENT_DIR`, `GSPC_EXECUTABLE`, `GSP_SIM_EXECUTABLE`; the SDK revision remains checked.

## Interface / behavior

`peek_frame_t` has sequence, capture timestamp in injected monotonic **milliseconds**, complete flag, Celsius `c[768]` and per-pixel validity. Row-major `c[y*32+x]`, origin top-left, x right/y down. Every pixel must be valid, finite, within [-40,300]°C. Driver calibration, two-subpage assembly, bad-pixel correction and temperature calculation stay behind the BSP public API. Read failures never resubmit retained temperatures. The acquisition task runs shared `peek_live_event` on each complete frame or fault before publishing a latest-only display snapshot. A slow display cannot discard samples before detection. The render task owns its copied state and ages/animates that copy; it never feeds it back into acquisition. Every read fault enters `peek_fault`, but a short error state can be overwritten before display.

`peek_submit`, `peek_fault` and `peek_tick` return an already aged state: same-time tick is idempotent. Expired previously valid data is STALE even if the incoming event is invalid/fault; before any valid capture a fault is INVALID. Duplicate/older sequence never counts/refreshes last-valid time. Capture timestamps must strictly increase and not be in the future; clock rollback is rejected unchanged. Reset the detector and role on source epoch change. `peek_result_t` exposes data state WAITING/VALID/INVALID/STALE, target/held, x/y (-1 without target), area/candidates, last-valid/last-seen times, sequence and sample count. `has_valid` disambiguates timestamp zero from “never”.

Defaults stay centralized in `peek_default_config`: spatial-median background; enter/keep contrast3/2°C; four-connected area6..300; acquisition3 new consistent frames; release2 valid absent frames; association5 pixels; smoothing0.5; continuity300ms; target hold500ms; data stale750ms. While tracked, nearest qualifying region in the gate wins even over a hotter distant source. Untracked selection maximizes summed temperature excess; ties follow row-major discovery. No identity recognition/classification/distance claim.

`dragon.c` consumes the core result at the same injected time. It distinguishes observation-held from stationary, estimates speed only between fresh capture timestamps, and requires900ms of fresh quiet observations below0.8 sensor pixel/s for HOLD. Gaps beyond300ms break stillness before the core's finite target hold ends. Repeated rendering never adds observations. NOTICE is a single320ms response; LEAVE returns gaze over1200ms. A reappearing target gets one light NOTICE without resetting gaze/velocity. IDLE retains the approved calm holds and seeded irregular blinks for10s after entry, then closes over450ms and stays shut. A newly acquired production target wakes it over150ms; faults or pending candidates do not wake it. Ordinary blinks resume after waking (140ms close,40ms shut,230ms reopen). Mapping uses pixel centers: `2*(x+.5)/32-1`, `2*(y+.5)/24-1`, then centralized rotation/flips and bounded eye amplitudes0.78/0.58. Latest user feedback confirmed both axes reversed with both flips enabled;1.0.6 disables both. The user confirmed both physical directions correct on1.0.6.

Draw reads a prepared pose only. Open-eye dirty updates request the tested `(16,80)..(464,416)` union; blink transitions request the full textured hood. Native GSP currently still supplies full draw surfaces, so this request produced no substantial measured throughput gain. The full-frame parity test prevents stale pixels from being hidden by partial updates.

## Evidence / limits

The original eight cases are labelled synthetic except the32 retained sparse recorded snapshots. The ninth case, `live`, is the separate511-array complete recorded window described above. Original recorded capture gaps (roughly254s total) are preserved; there is no scene/target ground truth or continuous8Hz recording. `tools/generate_data.py` and `tools/generate_dragon_data.py` reproduce the inputs. `.peek`: `F now sequence captured complete` +768 Celsius tokens, or `P now` (tick), `E now` (fault). Unsigned fields strictly reject signs, overflow and suffixes; malformed input reports line number. Actual C output is retained separately; no prefilled centroid drives the role.

[Handoff](docs/HANDOFF.md), [review response](docs/REVIEW_RESPONSE.md), [resource budget](evidence/phase2/resource-budget.json), [native artwork comparison](evidence/phase2/dragon/approved-vs-native.png), [live idle movie](evidence/phase2/dragon/idle-live.mp4), [live target-flow movie](evidence/phase2/dragon/dragon-live.mp4).

The phase2 movies sample actual official GSP API pixels during wall-clock runs and encode at8fps; encoded rate does not establish runtime/browser/device FPS. The follow-up [A/B table](evidence/followup/performance/AB_COMPARISON.md) now separates normal connected preview (idle14.955Hz / flow14.914Hz draw callbacks) from screenshot/poll conditions (14.384 /14.122Hz). Host commit-sequence rates are separate; none are browser-visible FPS. The approximately30Hz goal remains unmet. Those archived phase2 results preceded hardware installation. Current real-input installation, engine timing and available heap measurements are in the live-dragon handoff; physical screen FPS, post-flip physical direction acceptance, labelled accuracy, distance/FOV and long-term reliability remain separate acceptance gaps. No remote write occurred.

The review manifest may map byte-identical repeated native PNG captures to the retained phase2 golden PNG; their state logs and SHA256 provenance remain present. Source, temperature input and installed/restore firmware are retained directly.

Create the review archive after commit with `python3 tools/package_review.py`; it retains exact commit/file hashes and excludes original large input movies, `.git`, dependencies, generated includes, build caches and intermediate captures.

## Follow-up timing/build/performance checks

The previous quiet-observation deadline is now evaluated **before** new capture evidence replaces it, then the new evidence is aged again. Eight latency/boundary/held/stop scenarios at30/60/120Hz pin this behavior. `python3 tests/test_asset_build.py` verifies10 ordinary-build/source-update cases, including source hashes and mtimes. That archived follow-up had8 CTests; the current live-dragon branch has11.

After starting preview and opening its browser URL, keep the same browser tab connected and avoid builds during windows:

```sh
python3 tools/benchmark_host.py --seconds 30 --repeats 2
python3 tools/analyze_host_benchmark.py
```

A performs no screenshot/status sampling inside each window; B follows the API screenshot/15ms-loop-sleep method. Results retain actual read rates, wall/logical times, timer/prepare/draw counters and times, interval histograms, surfaces, process CPU/load and boundary `frame_info`. The public API does not isolate upload/present duration. No public dependency or texture was changed to chase30Hz. [Follow-up response](docs/FOLLOWUP_RESPONSE.md) records the scope and report-recovery detail.

`python3 tools/report_budget.py --output evidence/followup/static-budget.json` refreshes target-ABI allocation estimates. `python3 tools/report_firmware.py --build-log evidence/followup/idf-build-raw.log --static-budget evidence/followup/static-budget.json` retains final image/ELF/map/config hashes, whitelisted config and section/symbol summaries. With XIP/RODATA-to-PSRAM enabled, linked read-only textures require PSRAM mapping/copy budget; no texture decoding does **not** mean zero runtime PSRAM. Device startup/residency/peak measurements belong to the separate hardware line and have not been performed by this mainline session.

Physical mount: the installed board uses `CONFIG_PEEK_GAZE_FLIP_X=y` and
`CONFIG_PEEK_GAZE_FLIP_Y=y`, based on the user's2026-10-21 motion observation.
Only `dragon_map` transforms the target into gaze; thermal arrays/coordinates
remain native. Reproduce this mount with
`python3 tools/preview.py --sample-step 2 --flip-x --flip-y`.
Omit the two flags for the retained unmounted synthetic/reference convention.
Mapping is reapplied on every replay/source reset; pause never changes it.
Device RPC and Host status expose `flip_x`/`flip_y`.

If an existing incremental build rejects missing new Kconfig selectors, trigger
local CMake reconfiguration with `touch projects/peek/CMakeLists.txt`, then rerun
`python3 tools/build_idf.py`. This changes only the local file timestamp, does
not fullclean or upgrade dependencies, and leaves the config checks enabled.

The exact240 prepared-geometry cache adds691,200B explicit PSRAM. It is keyed
only by exact blink/squint/tension; moving gaze and pupil are always fresh.
Pixels near contours use the scalar compositor. Changing geometry invalidates
the cache; a repeated geometry builds it once in prepare. Draw remains read-only.
No additional downsampling or pose quantization. Run
`python3 tools/control.py case sleep` then `play` for the new synthetic scenario,
or `python3 tests/test_sleep_gsp.py` for actual native dynamic acceptance.

Current device trial: source f8845c5, version1.0.2-peek-sleep; active-open engine
rate10.336Hz. The roughly15Hz goal remains unmet; user chose to stop at this
version. See HANDOFF for hardware/native distinctions and exact restore bundle.
