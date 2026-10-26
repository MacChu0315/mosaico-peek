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

## Validation and installation result

Clean sourceb672117486d65ab76893fb833103594b019636f8 was rebuilt and checked with
the official0.2 parser. Exact native attachment:
releases/v1.2.0/mosaico-peek-v1.2.0.irisfw,6301404B,
SHA256b881507941bbbfffc7d1603ad4196db4f38e194e614e582c60e051f049068d59,
ELFd99572ee4ee4322d1575aa2ca16d1b2617aa470ae3f430a3f4162e3008c85d04.
App7258864B, UI94480B, explicit bitmap PSRAM3418224B. UI/art streams equal1.1.1.
Debug/Release37/37 and native44 image/16 pointer/17 phase/511-array replay checks
pass. The failed-init cleanup regression fails on the former adapter, passes now.
Initial sandbox registry access failed; authorized official registry resolution
succeeded. Unrelated libpng/zlib updates were pinned back before delivery.

The first device inspection found another device and did not write it. User then
reconnected the original Peek and explicitly requested actual flashing/test after
the concrete ROM migration question. This authorizes this one same-device base
migration, not other hardware or future whole-flash erase. Legacy identity was
verified and existing crash evidence preserved. Old owner had already exited;
release reported owner=none, verified by passive status (not forced takeover).

The official recover request found no ROM interface. User performed the documented
Boot+power-on entry. Reviewed0.2.0 base operation
c6878691-daa8-418a-a741-8f328154f521 succeeded onMAC30:ed:a0:f4:52:a0, with four
base images at0x2000/0x8000/0x9000/0x20000. No full erase or unlisted partition
write. Exact ABI1 bundles are retained but cannot provide ordinary ABI2 rollback.

The first app operation13638cfa-4966-47f1-8c42-dc1c7b2af377 failed at plan
validation before transfer: independent data link absent. Keeping an official
iris run client and inspecting both same-ID/same-Boot links established readiness.
The explicit data-endpoint claim itself reported a selector error because the
active primary endpoint was control; subsequent aggregate state, not that error,
proved both links ready. The terminal failed operation and empty queue were
checked before the same-package retry. Retry140379a2-5291-4058-80fd-2fbcaab75883
succeeded. No host dependency was edited to bypass checks.

Actual smoke:74.97s,588 accepted temperature samples,0 faults/runtime/IMU errors,
all three characters,0/270deg and sleeping observed. User confirmed clicking,
left/right swipes,AI key,gaze direction and reopening. The brief waking flag was
not sampled; its physical acceptance is the user's observation. Closed dragon
and deep-sea screenshots match C RGB565. Software maintenance roundtrip passed
normal1.2.0 -> VibeMode0.2.0 -> normal1.2.0 with distinct BootIDs and the same
DeviceID. Final Boot3927091703191660807, VALID, error0/crash0.

## Measured boundaries

New BSP display batches8 lines and disables psram_dma_direct; old resource/FPS
claims were not assumed. In mixed manual270deg windows, active GSP rates were
7.246Hz dragon,6.600Hz sea,4.738Hz mechanical; not controlled improvement or
physical panel FPS. Smoke-end free internal171155B/free PSRAM4480380B; lifetime
minima119456B/3458840B. The task-memory query returned HTTP501 not_supported;
BootID/health stayed unchanged, and status heap values remained available.
No new90/180deg physical acceptance, prolonged soak, allocator fragmentation,
forced-crash recovery or physical AI-held power-on maintenance test is claimed.
Website submission/review and a new remote Git push remain unperformed.

## Reproduce and update

python3 tools/bootstrap.py
python3 tools/build_idf.py --bundle
# With the matching isolated Iris Python, at the recorded source commit:
python tools/check_iris02_bundle.py --bundle releases/v1.2.0/mosaico-peek-v1.2.0.irisfw --require-clean-source

The source guard compares current HEAD; receipt-only documentation commits do not
change the already verified firmware identity. Fresh builds embed their own HEAD.
For installation use only the matching0.2 mosaico.py, keep the project client alive
and verify independently connected control/data links before system-update.
No legacy ZIP workaround or schema relabeling was used. Evidence and current
acceptance summary: evidence/iris02/DEVICE_ACCEPTANCE.json.
