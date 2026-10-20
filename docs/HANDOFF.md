# Phase 1 handoff

Completed locally: shared Host/ESP-IDF hot-target detector, native GSP diagnostic UI, project-owned array replay, successful ESP32-S31 firmware build, deterministic synthetic cases, reuse of 32 real snapshots, reproducible checks and review material. Stop here for ChatGPT review; official character scenes/animations are not part of this phase.

## Verified

- `cmake -S . -B build-host`, `cmake --build build-host`, `ctest --test-dir build-host --output-on-failure`: detector, device-adapter scheduling/cleanup stubs, and actual UI partial-registration cleanup tests pass (3/3).
- `cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release`, build and CTest: 3/3 pass with assertions explicitly retained, avoiding a false PASS under `NDEBUG`.
- `python3 tests/test_replay.py`: five cases run through production C; two runs of each are byte-identical. Empty, entering/moving/stationary/leaving, multi-source lock/reselection, duplicate input, short missing frames, invalid input, continuing outage and timeout assertions pass. Malformed files are rejected with line-number errors.
- `python3 tools/generate_data.py`: all five `.peek` SHA-256 values remain unchanged; recorded input keeps the original sparse timestamp gaps. `data-regeneration.json` and `replay-verification.json` contain hashes/results.
- `python3 tools/preview.py --headless` plus `python3 tests/test_gsp.py`: 96 native checks pass, including actual GSP pointer taps on CASE/PLAY/REPLAY, paused clock preservation, replay equality and detector state unchanged during repeated render frames. Tests use official simulator 1.5.1 plus C backend, not scene-only mode.
- `python3 tools/build_idf.py`: doctor verifies the exact SDK revision and `>=6.2` constraint; low-noise ESP-IDF build succeeds for `esp32s31`. Actual compiler and versions are in `evidence/environment.json`; artifacts include `projects/peek/build/peek.bin` and `ui_apps.bin`. `evidence/idf-build-summary.log` and retained raw log/result document this build.
- `python3 -m compileall -q tools tests`: Python syntax check passes. ASan/UBSan detector check passes with `ASAN_OPTIONS=detect_leaks=0`; LeakSanitizer cannot run under this environment's ptrace wrapper, so no leak-sanitizer claim is made.

The independent code review found a queue/clock ordering race and asynchronous callback cleanup lifetime defects in the initial device adapter. Both were fixed and re-reviewed. The clock race was reproduced against the original source (`evidence/device-regression-before.log`); actual adapter and actual UI cleanup now have Host regression coverage. These stubs prove the selected order/error behavior, not physical hardware operation.

## Review material

- Start with `README.md`, `src/peek.h`, `src/peek.c`, `src/peek_ui.c`, `projects/peek/main/device_thermal.c`, `docs/DESIGN.md`.
- Inputs/provenance: `data/manifest.json`, `recorded-source.json`, `recorded.jsonl` and five `.peek` files. Actual detector outputs: `evidence/*-output.jsonl`. No precomputed centroid feeds the detector.
- Dynamic evidence: `evidence/gsp-motion.mp4`, a 10-second sequence of **actual GSP API screenshots** stepped at exact 125 ms replay times and encoded at 8 fps. This is controlled replay video, not real-time performance evidence. Selected PNGs and `evidence/gsp/checks.json` show other states.
- `evidence/gsp-host.log`, `gsp-backend.log`, `gsp-build.log`, `gsp-test.log` retain process/build/test evidence. The package's `REVIEW_MANIFEST.json` records its exact local commit and per-file SHA-256; `.git`, cached dependencies/builds and intermediate movie frames are excluded.

## Failures encountered and disposition

- Sandboxed startup initially failed to bind loopback listeners (reported as occupied default ports). Running local GSP with socket permission and temporary listen addresses succeeded. Other running GSP/Gateway processes were preserved. Reproduce the intended startup with `python3 tools/preview.py`; if a sandbox blocks sockets it needs local listener permission.
- First firmware attempts could not resolve GSPC / component registry under restricted network access. The explicit local pinned GSPC and registry read permission resolved them. Final component versions equal those in the previously validated Mondrian app (`evidence/dependency-versions.json`). No shared SDK/BSP/toolchain upgrade occurred.
- LeakSanitizer reports “does not work under ptrace.” Address/undefined checks were rerun with leak detection disabled; ordinary debug and Release behavior tests pass.

- Final shutdown inspection exposed the pinned sim_bridge select/EINTR behavior: direct external SIGTERM marked a healthy session failed. The project launcher now sends a local `quit` command; the native callback requests stop at a poll boundary, leaving the official host alive for cleanup. The original error log is retained as `evidence/gsp-signal-shutdown-before.log`; bounded shutdown smoke and final process log confirm clean cleanup. No dependency source was changed.

## Not verified / known limits

- **No hardware writes or real hardware acceptance.** No flash, recover, firmware upgrade or mode change was performed. New device adapter I²C acquisition, actual screen/rotation/touch/timing, read failures, hotplug/reconnection, power and long-duration stability still need on-device testing with separate authorization.
- Existing recorded temperatures are genuine but sparse, with no object/distance/scene ground truth. They validate import, orientation provenance and expiry, not continuous tracking or detection quality. Configuration is inferred from the archived source/defaults, not a per-frame configuration record.
- FOV, useful distance and physical mounting direction remain unknown. Native `(0,0)` is the sensor array's top-left; user-facing left/right is not yet calibrated.
- Spatial-median subtraction assumes a significant cooler background. Large hot coverage, weak contrast, reflective surfaces, changing ambient conditions and merging/crossing targets may fail or change associations. The selected target is a hot region, not a person or stable identity. Parameter defaults need real continuous labelled recordings.
- Sensor driver defaults stay at 400 kHz, address 0x33, emissivity 0.95, reflected offset 8 °C, 16 Hz **subpage** rate (~8 full frames/s nominal). Both slots share I²C; use only one thermal board. Actual delivered rate remains unmeasured here.
- The firmware intentionally labels replay controls SENSOR/LIVE/-- and keeps its acquisition clock advancing. Full replay/control testing is Host-side. On a rare failed teardown synchronization, contexts are retained until reboot to avoid dangling callbacks; repeated start is rejected.

Next handoff: have ChatGPT review this package and its evidence. Then arrange a separately approved device test and continuous recorded cases before connecting official character UI. This phase does not authorize those later steps.
