# Peek1.2.0 — Iris/Vibe Mode0.2 migration

User explicitly requested a native uploadable .irisfw migration, not an ABI1 ZIP
workaround. Branchfeat/vibe-02-migration starts from14cf7f8. No platform upload,
remote push or device base write is implied by local bundle preparation.

## Contract and source

Independent read-only workspace ../esp-mosaico-vibe-iris02: Vibe849e3d04,
utils632adc76, BSP5f88b91e. IDF7b9cc1a, ESP-GSP1.5.1/GSPC0.6.1, LVGL9.5.0,
libpng1.6.58~2/zlib1.3.2~1 remain pinned. New official BMI270/BMM150 packages are
required by this BSP; acceleration(g), gyro(dps), XYZ order and default4g/2000dps/
100Hz are unchanged. Existing calibrated axes/flip settings stay untouched.

Workspace schema2; product esp-mosaico/v2, Recovery ABI2, layout
mosaico-retained-test-2m-v2; separate control/data CDC interfaces. Retained
factory/app-factory becomes vibe_mode/app-test; ota_0 becomes main_app/app-ota_0.
Offsets/capacities stay the same, including NVS/sysmeta/coredump and1MiB UI.
The ordinary app package contains exactly partition_table/application/data and
uses esp-iris-system-update/0.2, minimum Recovery0.2.0. It contains no bootloader,
Vibe Mode image, account credentials or platform identity. Historical skill text
that still names /v1 is superseded by the actual0.2 parser and migration contract.

Production detector/controller/rendering/source timing and approved assets are
unchanged. New BMI270 init may retain a cleanup-only handle on failure; its
adapter now attempts deinit after actual init errors while preserving the original
error. INVALID_STATE never tears down a preexisting owner. The regression covers
failed cleanup and all existing physical mounting fixtures.

Old generated build cache was moved to ignored build-before-iris02-20261026;
ABI2 uses a fresh build/ and sdkconfig. SDK/adjacent checkouts were not upgraded.
Build wrapper checks clean pinned Vibe/BSP/utils/IDF and uses their matching host
Python; tools/check_iris02_bundle.py compares actual images, partition bytes,
ELF/source identity, configuration and unchanged UI/art resources.

## Validation and current limits

Initial build was blocked by sandbox registry access; retry with official registry
access succeeded. Unrelated libpng/zlib resolver upgrades were pinned back before
delivery. Host37/37 and native44 orientation images,16 pointer cases,17 sea phases,
511 recorded arrays/655 events and retained-picture wake/replay checks pass.
Final committed-source rebuild and delivery hashes are recorded in evidence/iris02.

New BSP changes display SPI batching to8 lines and disables psram_dma_direct.
Do not reuse old device performance/RAM figures as new-version measurements.
Device startup, active drawing, switching, IMU orientations, memory and normal/
Vibe Mode transitions remain unverified until hardware migration and acceptance.
Local parsing does not prove platform upload/review acceptance.

## Device-base migration gate

The last verified device is still ABI1. The official0.2 guide requires ROM
Download Mode plus mosaico.py recover for an incompatible base; cross-generation
Iris update/relabeling is unsupported. Standing authorization only covered normal
System Updates and explicitly excluded ROM recover. Do not perform it silently.

Reviewed0.2.0 base images/hashes and intended offsets are inspected locally:
bootloader0x2000, partition table0x8000, otadata0x9000, vibe_mode0x20000. The official
flow preserves sysmeta/NVS/coredump and regions not declared for writing; no full
flash erase. The old1.1.1 app bundle cannot directly undo an ABI2 base migration.
Prepare the app, validate the base plan, then ask specifically about that same
MAC30:ed:a0:f4:52:a0 migration if device verification is to proceed. Only official
mosaico.py operations, ownership handoff and live identity checks are allowed.

## Commands

python3 tools/bootstrap.py
python3 tools/build_idf.py --bundle
# Run final check with the matching isolated Iris Python:
python tools/check_iris02_bundle.py --bundle projects/peek/build/peek-system-update.irisfw --require-clean-source --output evidence/iris02/bundle-check.json

This is the requested native .irisfw route. No legacy download ZIP is produced.

## Locally validated delivery artifact

Source commitb672117486d65ab76893fb833103594b019636f8 was rebuilt with clean source.
Exact file: releases/v1.2.0/mosaico-peek-v1.2.0.irisfw (6301404B).
SHA256b881507941bbbfffc7d1603ad4196db4f38e194e614e582c60e051f049068d59.
ELFd99572ee4ee4322d1575aa2ca16d1b2617aa470ae3f430a3f4162e3008c85d04.
App7258864B, UI94480B; explicit bitmap PSRAM3418224B unchanged. Actual free/peak
memory is not established until hardware validation. Official0.2 parser and
clean-source/config/image/partition checks pass; the old ABI1 bundle is rejected
by that parser as expected. No schema relabeling or legacy ZIP workaround.

Debug/Release37/37 and the native checks above pass. IMU error-cleanup regression
fails on the old adapter and passes after the migration fix. Official recover
--dry-run checked the reviewed base environment but reported no ROM Download Mode
interface; this is not successful device migration and no Flash writes occurred.
The user has been asked for specific base-migration authorization; no dependent
write may start before a reply. Candidate may be handed off for local review,
but server upload/review and physical behavior are still explicitly unverified.

## Current device gate

Both legacy and0.2 read-only identity checks failed to validate the selected
4553502d49524953010030eda0f452a0 device. USB descriptors currently belong to an
Echoy device, not the selected Peek identity; no substitute device was claimed
for writes. Reconnect the original Peek MAC30:ed:a0:f4:52:a0 before proceeding.
Specific ROM base-migration approval remains pending. No device writes, base
updates, website uploads or subsequent GitHub pushes occurred in this migration.
Final bundle validation was run at source commitb672117; receipt-only commits
may follow. To audit that exact artifact using --require-clean-source, check out
its recorded source commit; normal subsequent builds embed their own HEAD.
