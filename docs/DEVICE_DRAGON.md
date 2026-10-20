# Live dragon integration

Scope: mainline `feat/dragon-gsp` from `f278cfd`; diagnostic handoff `63c0799` is read-only. No algorithm candidate, dependency upgrade, partition change or remote write.

## Replay and compatibility

`src/peek.c`/`peek.h` are byte-identical in both worktrees. The mainline role keeps the reviewed previous-evidence expiry fix from `99c2b97`. Driver uses the same public BSP interface, native32×24 orientation,400kHz,16Hz subpages (~8 complete frames/s),0.95 emissivity and8°C reflected offset. Only successful new complete frames create samples.

The complete recorded PKF1/PKE1 data is retained under `data/live/20261020-complete-window/`. `python3 tools/import_live.py` converts every original event to `data/live.peek`, preserving all655 processing times,511 capture timestamps/sequences and float32 arrays (9-digit roundtrip verified). `E now` is an additive fault opcode calling production `peek_fault`; `P` remains a tick, `F` a complete frame. No retiming/interpolation or prefilled detector coordinates. Read-beginµs/fault times remain in original binaries and `evidence/real-input/input-timeline.json`. Old replay files retain their meaning.

Run `python3 tests/test_real_replay.py` after Host build. Start `python3 tools/preview.py`, then `python3 tools/control.py case live` and `python3 tools/control.py play`. `python3 tools/validate_real_gsp.py` performs the complete wall-clock run with actual native screenshots, event/core/role comparison and replay checks. Screenshot movies are encoded4fps, not a measured screen rate. Recorded scene has no labels; unchanged production quietness threshold does not trigger HOLD in this window.

## Firmware and read-only observations

`python3 tools/build_idf.py` selects a separate build-tree `sdkconfig.dragon`, version `1.0.0-peek-dragon`, dragon view and2048-byte RPC body. The default detector/art/33ms timer remain unchanged. No full-temperature recorder is allocated in this role firmware.

Read-only RPC service `0x504c`, method1, empty request returns source commit/version, capture/fault counters, consumed samples, core/role/gaze, timer callback count, canvas draws/pixels/times and official GSP render/raster/submit counters. GSP task alone reads mutable UI; it publishes a fixed snapshot under a short cross-core lock, RPC copies then formats outside the lock. Sensor counters are atomic. Counters do not create samples. A callback/surface can be a tile, and an engine-render count is not a physical panel scan count. No panel-visible FPS claim without separate measurement. On this retained firmware, `iris memory` returns HTTP501 (task memory observation unavailable); live `iris device-status` still supplies free/minimum internal RAM and PSRAM.

## Slow-device-render isolation

The first physical build (`d27bc7f`) exposed a scheduling defect:18s observation measured7.923 complete captures/s but1.664 detector samples/s and render callbacks/s. Full GSP frames take about588ms (about557ms raster +32ms submit). Rendering supplied tiled canvas callbacks (~17.64/s), which are not full frames. The latest-only mailbox used to discard complete frames **before** detection; the resulting600ms sample intervals exceed the unchanged300ms continuity requirement.

`src/peek_live.c` now owns acquisition-side detector + role observations. `device_thermal.c` processes every successful complete frame/fault before the latest-only display mailbox. Whole independent state copies cross that mailbox; rendering ages/animates its own copy and never writes history back. No detector parameter/art/render algorithm change. A Host regression renders only every750ms while8Hz samples still acquire and remain HOLD; copy aging cannot mutate source state. Original recorded events also traverse this exact portable wrapper in `peek_role_replay`. No physical FPS improvement is claimed from this scheduling fix.

## Target and recovery

Only MAC `30:ed:a0:f4:52:a0`, Device ID `4553502d49524953010030eda0f452a0`. Recheck live identity before writes. Previous app `1.0.0-peek-diag`, ELF SHA `f80b7d6f47b5ddad9dc7576fcfd2324a54c86eede2e69147821ddcf16c02dbab` was verified healthy before installation.

Full known diagnostic BIN/ELF/map/sdkconfig/resources/update bundle are preserved locally in `firmware-local/diagnostic-f80b7d6f47b5ddad/`, verified against the diagnostic handoff manifest. Small review package includes the exact restore bundle under `evidence/device-dragon/restore/diagnostic.irisfw`, configuration excerpt and original manifest. No device readback/full-flash backup claim.

Restore only when intentional, from this project directory, through the same official application update path:

```sh
python3 ../esp-mosaico-vibe/mosaico.py iris device-status --workspace . --project projects/peek --device-id 4553502d49524953010030eda0f452a0 --json
python3 ../esp-mosaico-vibe/mosaico.py iris system-update --workspace . --device-id 4553502d49524953010030eda0f452a0 --bundle evidence/device-dragon/restore/diagnostic.irisfw --json
```

This retains the existing `ota_0`/immutable prefix/Vibe Mode contract. Never use direct IDF/esptool writes, whole-flash erase or change partitions to accommodate the factory-size warning. After restore verify the same Device ID, a new Boot ID, expected diagnostic ELF/version, healthy normal mode and live MLX90640. If update fails, inspect its original operation; do not start a competing write. ROM/base-firmware recovery is outside this task's authorization.

Runtime results and remaining limits are recorded in `docs/HANDOFF.md` and `evidence/device-dragon/` after actual installation.
