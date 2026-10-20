# mosaico-peek — phase 1

One shared C hot-target detector, native 480×480 GSP diagnostics, temperature-array replay and review evidence. No character artwork or identity recognition. No hardware firmware was written.

## Dependencies

Use the sibling `esp-mosaico-vibe` workspace and existing `.toolchains/`; no shared checkout is upgraded. All exact revisions and driver source hashes are in [dependencies.json](dependencies.json), resolved ESP-IDF components in [dependencies.lock](projects/peek/dependencies.lock).

| Dependency | Verified version / revision |
| --- | --- |
| ESP-IDF / target | `7b9cc1ac79f865983f59bb8ff3ff43eb74ff1dbe` / `esp32s31` |
| IDF version reporting | CMake `6.2.0` satisfies `>=6.2`; git reports `v6.1-dev-7333-g7b9cc1ac79f` (development checkout, not a stable release) |
| Vibe / utils | `95469e63…` / `fc63d43f…` |
| BSP | `a2c985ad…` (retained display/module-manager APIs) |
| Thermal public driver | official BSP `5f88b91e…`, component `0.1.0`, unmodified C; dependency path relocated |
| ESP-GSP / GSPC / simulator | `1.5.1` (`472207a3…`) / `0.6.1` / `1.5.1` |
| RISC-V compiler | `riscv32-esp-elf-gcc 16.1.0`, `esp-16.1.0_20260609` |
| Native tools | GCC 11.4.0, CMake 3.22.1, Python 3.10.14; FFmpeg for review video only |

Layout: `projects/peek/` is the official `mosaico.py project init peek` app scaffold; `src/` is shared production C; `tests/` tests it; `data/` contains inputs/provenance; `evidence/` contains actual outputs. `deps/` and build directories are local, excluded from review archives. See [THIRD_PARTY.md](THIRD_PARTY.md) for source/licensing and offline dependency reuse.

## Run locally

From this directory, with the verified sibling dependencies available:

```sh
python3 tools/bootstrap.py
cmake -S . -B build-host
cmake --build build-host
ctest --test-dir build-host --output-on-failure
python3 tests/test_replay.py
./build-host/peek_replay data/motion.peek
python3 tools/preview.py
```

The last command builds the native backend and prints/opens the actual official GSP URL. It starts on the motion case, **paused**. CASE cycles empty → motion → multi → gaps → recorded. PLAY/PAUSE freezes/resumes the injected replay clock; REPLAY resets file, time and detector, preserving play/pause. Case selection resets and pauses. EOF pauses. The simulator is not an MLX90640 physical simulation: this project reads arrays and calls the production detector.

For automation, keep `python3 tools/preview.py --headless` running, then:

```sh
python3 tests/test_gsp.py
python3 tools/control.py case 3
python3 tools/control.py advance 6000
python3 tools/control.py status
python3 tools/stop_preview.py
```

`advance` is a Host diagnostic operation that pauses and advances virtual milliseconds through every intervening input event. It never substitutes expected coordinates. Default GSP runner ports were occupied in this environment; `preview.py` uses the official simulator/native bridge with loopback temporary listeners. In restricted sandboxes, socket permission is required. No other simulator or Gateway is stopped. Only one Peek preview per working directory is supported.

To override downloaded GSP locations set `ESP_GSP_COMPONENT_DIR`, `GSPC_EXECUTABLE`, `GSP_SIM_EXECUTABLE` to the pinned 1.5.1/0.6.1 tools. `python3 tools/build_idf.py` verifies the exact SDK commit, runs doctor and builds `projects/peek/build/peek.bin` and its GSP resource image. Set `IDF_PATH` only to that revision. It performs **no flash/update**. Full raw build logs live under `projects/peek/.codex-runs/idf-low-noise-build/`; selected logs are retained in `evidence/`.

## Interface and parameters

`peek_frame_t` contains `sequence`, `captured_ms`, `complete`, `c[768]` and `valid[768]`. Temperatures are °C, `c[y*32+x]`; origin top left, x right, y down. All 768 pixels must be valid, finite and in [-40,300] °C. The BSP owns calibration, temperature calculation, bad-pixel correction and both-subpage assembly. The live adapter preserves native sensor orientation; physical mounting-to-screen direction remains unverified. Recorded replay uses its recorded rotation (already applied in `temperatures`).

`peek_submit(detector, frame, now_ms)` accepts each strictly increasing sequence/capture timestamp once. `now_ms` and capture time share one injected monotonic epoch. Duplicate/older sequences never count or refresh last valid time, but elapsed time still ages the result. Future/non-increasing capture timestamps or invalid arrays are rejected. `peek_tick` only ages state; clock rollback returns false without changing state. Source restart/replay must call `peek_reset`. Every event API returns an already aged result; same-time `peek_tick` is idempotent. Expired previously valid data is STALE even when the new event is invalid/fault; before any valid capture a fault is INVALID. `peek_fault` marks acquisition failure without creating a sample or changing sequence/time-of-last-valid. The device calls it for consumed read-error messages; retained driver output is never resubmitted. The latest-only mailbox can overwrite a short failure with a later success before consumption, so individual failures are not all guaranteed visible; this low-latency policy is intentional.

`peek_result_t` exposes `has_target`, smoothed sensor-coordinate `x/y`, selected `area`, qualifying `candidates`, `data`, `has_valid`, `last_valid_ms`, `last_seen_ms`, sequence and sample count. `has_valid` disambiguates timestamp zero from “never received.” `WAITING` means no input; `VALID` includes a valid empty scene; `INVALID` means acquisition/input failure; `STALE` means the last valid capture has reached expiry. Without a target x/y are -1. The most recent valid heatmap stays visible as history during invalid/stale data; the white cross is removed. Labels show current time, last valid capture time and age. Callers must use the state/target flags, not historic pixels alone.

All defaults are centralized in `peek_default_config()`; callers can pass a validated `peek_config_t` to `peek_init`. Changing detection policy requires rerunning replay verification.

| Parameter | Default and meaning |
| --- | --- |
| Background | spatial median of current complete frame (no temporal adaptation) |
| `enter_delta_c` / `keep_delta_c` | 3 / 2 °C above background; lower threshold while tracking |
| `min_area` / `max_area` | 6 / 300 four-connected sensor pixels |
| `acquire_frames` / `release_frames` | 3 consistent new frames / 2 valid absent frames |
| `max_distance` | 5 sensor pixels for association and entry continuity |
| `smoothing` | 0.5 per accepted tracked frame |
| `continuity_ms` | 300 ms; larger input gaps reset acquisition confirmation |
| `hold_ms` / `stale_ms` | 500 / 750 ms from last sighting / last valid capture |

While tracked, the nearest qualifying region within the gate wins even if another source becomes hotter. Untracked selection maximizes summed temperature excess; ties use row-major discovery order. Distant replacements require release and fresh confirmations. This preserves stationary targets and limits source switching. Broad hot backgrounds, targets merging/crossing, or covering much of the image can defeat this simple approach; it is not person identification, classification or distance measurement.

## Replay and evidence

`python3 tools/generate_data.py` reproducibly regenerates `.peek` inputs from seed 90640 and the archived recorded JSONL. `.peek` contains `F now_ms sequence captured_ms complete` plus 768 Celsius values, or `P now_ms` to advance time without a new sample. Parser errors are reported with line numbers. `data/manifest.json` describes expected scenarios; `evidence/*-output.jsonl` are **actual C results**. `data/recorded-source.json` retains source hash, capture configuration and limitations. Thirty-two real temperature snapshots are reused, with original inter-frame gaps; no ground truth labels exist and their sparse timing cannot validate tracking continuity.

[Handoff](docs/HANDOFF.md) records passed/failed/unverified items. [GSP video](evidence/gsp-motion.mp4) shows the real native simulator rendering 80 input frames at 8 fps, including entry, movement, stationary hold and exit. It is assembled from simulator API captures at exact 125 ms replay steps, not a real-time screen recording or hardware capture. `evidence/gsp/checks.json`, captures, process logs and test scripts make the run reproducible. Optional `python3 tools/verify_pixels.py` checks the captured cross against native state (Pillow; already available in this environment).

Create a small review archive after committing with `python3 tools/package_review.py`. It includes tracked source, dependency manifests, replay inputs/results and evidence; excludes `.git`, build/cache files, raw 80-frame intermediates and reacquirable dependency copies.
