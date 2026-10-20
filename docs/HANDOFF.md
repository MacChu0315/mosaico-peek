# Phase2 handoff — approved dragon / native GSP

Baseline `60d57542e4f044392160a91c47ea11841dbf9e1e`. Work branch `feat/dragon-gsp`; first commit `adec718` independently fixes core/replay/evidence issues. The second commit adds only the approved single dragon, shared C behavior/rendering, native integration and acceptance material. Its exact hash is in Git and the archive's REVIEW_MANIFEST. Stop here for ChatGPT review; no hardware installation or remote write was performed.

## Delivered

- Aged event results are consistent across direct CLI, `peek_replay_until` and native pump. Invalid/expired precedence and same-time tick are explicit. Strict unsigned token parsing rejects negative, overflow and suffix inputs. Original five datasets retain deterministic results.
- Actual redraw requests increase draw count without altering input identity/timestamps/sample count/result. Offline diagnostic pixel checking now uses five retained PNGs and checks cross position.
- `dragon.c` is shared by Host and ESP-IDF: sample-time velocity/stationary evidence; held distinct from stillness; IDLE/NOTICE/TRACKING/HOLD/LEAVE; seeded blinks; smooth reappearance without resetting gaze/velocity. New-sample gaps over300ms break stillness even before the detector's500ms hold expiry.
- `dragon_render.c` is the same prepared-pose rasterizer on both platforms. It preserves the supplied scales/iris, sphere rotation, slit pupil, stretched textured hood and complete eyelid closure. Palette/RGB565/resampling/approximate shadow differ slightly from the approved offline reference; the retained comparison image makes this visible. Gemini contributes no runtime JS, approximate coordinates or replacement art.
- The 480×480 dragon view has no telemetry/buttons. Original diagnosis is a separate Host startup/view option; firmware offers `CONFIG_PEEK_DIAGNOSTIC_VIEW` (default n). Latest-only mailbox remains low latency; a transient error can be overwritten before delivery, so not every read failure is guaranteed visible.

## Actual verification

| Command / check | Actual result |
| --- | --- |
| `cmake -S . -B build-host`, build, `ctest --test-dir build-host --output-on-failure` | 6/6 pass: detector, actual device-adapter scheduling/cleanup, actual UI lifecycle including new eye registration failures, event aging, behavior, raster pixels |
| Release configure/build + CTest | 6/6 pass; assertions explicitly retained |
| `python3 tests/test_replay.py` | Original five cases deterministic; aging CLI/replay_until equality; malformed integer cases rejected |
| `python3 tests/test_gsp.py` | 100 checkpoint records, including80 motion samples (not100 independent scenarios), actual pointer controls, five redraws, native aging equivalence |
| `python3 tests/test_dragon_gsp.py` | 27 controlled native checkpoints pass; >4s fresh HOLD, reappearance, INVALID/STALE/recovery, pause/step/replay purity, closed/extreme/reopen captures; additionally61.07s real-time idle and30.51s full-flow observation pass |
| `python3 tools/verify_pixels.py` | Five retained diagnostic PNGs: cross presence and position agree |
| `python3 tools/verify_dragon_pixels.py` | 19 retained actual GSP PNGs: all230400 RGB565 pixels per frame match full C raster of exported exact pose; independent aperture mask finds0 bright iris pixels outside; closed frames have0 bright iris pixels |
| Shared behavior timing test | Same production8Hz input gives identical observation-time decisions at30/60/120Hz animation advancement; held, timeout, replay/seed and mapping tests pass |
| Asset/data regeneration | Byte-identical; asset rebuild also passes without original review-inputs, using retained PNGs and metadata |
| `python3 tools/build_idf.py` | Doctor verifies pinned SDK/target; ESP32-S31 firmware build succeeds. Final raw/result/summary retained in phase2 evidence |
| Python compileall and sanitizer | Syntax pass; renderer ASan+UBSan passed independently with leak checking disabled due environment ptrace limitation; no device runtime claim |

Additional independent review reproduced the stale stationary-evidence boundary, which was fixed and pinned at300/301ms. Review also prompted firmware diagnosis selection and tests for partial eye registration/renderer cleanup. No remaining high-impact correctness defect was identified in that read-only review; this is not a substitute for the requested next ChatGPT review.

## Runtime evidence and performance

`evidence/phase2/dragon/{idle,dragon}-live.mp4` consists of **actual live GSP API screenshots** sampled on wall clock and encoded at8fps. The source capture timestamps are retained in `*-captures.json`; these are not direct screen recordings. The encoded rate does not prove30Hz animation or device FPS. `*-live.jsonl`, `live-metrics.json`, controlled `frames.json` and `checks.json` preserve actual source sequence, capture/update times, role decisions/pose and canvas counters.

During capture, the final native program delivered about **14.15 callbacks/s in idle and14.45/s in the flow**, averaging **12.65/12.40ms** per C draw callback; maximum session draw was30.349ms. The ~30Hz Host goal was **not reached**. Open-eye dirty updates preserve pixel parity, but this pinned native bridge still supplied full480×480 draw surfaces and the observed throughput gain was negligible. The remaining combined bridge/render/scheduling overhead is not isolated here; no device-rate conclusion follows.

Measured native process memory: backend RSS/HWM3860kB; simulator RSS about100600kB, HWM102400kB. These are different processes/runtime from ESP-IDF and are not device RAM measurements.

## Flash and RAM

Actual final images and SHA-256 are in `evidence/phase2/resource-budget.json`:

- `ui_apps.bin`: **94,480 B /1,048,576 B**, free954,096 B.
- `peek.bin`: **1,985,248 B**, includes **651,780 B** indexed textures/palettes/LUTs. The texture cost is not hidden by leaving the GSP partition small.
- The app fits the unchanged `ota_0` capacity13,565,952 B. IDF emits a warning because the retained `factory` slot is only1,835,008 B. That slot contains retained Vibe Mode; the official `prepare_system_update.py` targets `ota_0` and direct IDF flashing is blocked by the application contract. No partition was enlarged or modified. No installation was performed.
- Cross-compiler ABI sizing of actual structs: renderer12,308 B; device app13,560 B; each capture message3,104 B. App + three message buffers + renderer is35,180 B, plus8,192 B sensor-task stack and uncounted RTOS metadata. No additional app full-screen buffer or runtime texture decoding is used.
- A480×480 RGB565 plane is460,800 B. Eye + diagnostic Canvas planes, if both cached, total681,984 B. GSP caches/scratch, font/scene allocations, presenter/DMA/framebuffer count and SDK heaps/stacks require separate accounting. **The device peak RAM is not measured**; the known allocations are not a claimed peak bound.

Configuration also exposes upstream SDK CMake private-include warnings (esp_wifi/wpa_supplicant and lwIP), preserved in the initial phase2 build raw log. They were not patched in adjacent SDK sources. The final low-noise build's counted warning is the retained-factory size warning above.

## Review material / remaining work

Start with `README.md`, `docs/REVIEW_RESPONSE.md`, `docs/DRAGON_DESIGN.md`, `src/peek.c`, `src/dragon.c`, `src/dragon_render.c`, `src/peek_ui.c` and `projects/peek/main/device_thermal.c`. Approved-source and generated-asset hashes: `assets/dragon/metadata.json` and `evidence/phase2/input-provenance.json`. Dynamic/keyframe comparison and pixel report are under `evidence/phase2/dragon/`. The ZIP includes retained source assets, replay data/results and evidence, but not original large input videos, generated include files, dependencies, `.git`, build caches or intermediate live capture PNGs.

No on-device acceptance: physical sensor-to-eye orientation, actual read rate, continuous target quality, FOV/distance, hand/warm-cup range, latency, device FPS/RAM/power, hotplug and long-term stability remain unverified. The32 existing recorded snapshots keep their original sparse ~254s span and inferred configuration provenance; they do not validate continuous8Hz tracking or labelled target accuracy. Palette/lighting differences and the unmet Host30Hz goal are explicit review items. The next step is review of this package, then a separately authorized hardware phase.
