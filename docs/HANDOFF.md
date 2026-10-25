> Release labeling in progress: user froze this unchanged three-eye baseline as v1.1.0. The following installed1.0.15 identity is the pre-release baseline until the release receipt is added. See docs/releases/v1.1.0.md.

# Peek handoff — three retained eyes (2026-10-25)

User explicitly rejected night owl and requested removal from firmware. Installed
1.0.15-peek-three contains only dragon, deep_sea and mechanical. Owl original
sources, standalone reconstruction and old firmware remain historical archives;
they are not encoded, selectable or restored automatically. [Removal details](OWL_REMOVAL.md).

## Installed identity

Source db16ee02fc2642f30f12982e1f34b8f9502f02ae.
ELF930c78593c4e1690a1f34890523099916c754398faf1b88733bdc071ff04275e.
Boot372463084054451689; official updatefe74ffdd-6eb8-4f7c-83fb-a94b0b6242c0
succeeded on first attempt. Matching version/ELF, normal mode, VALID thermal
samples, runtime/IMU error0, crash_count0. Startup viewdragon; auto orientation
and both gaze flips remain enabled. Only authorized MAC30:ed:a0:f4:52:a0 /
Device ID4553502d49524953010030eda0f452a0 was updated.

## Active behavior

Tap/left swipe/AI:dragon -> deep_sea -> mechanical -> dragon; right swipe reverses.
Stable UI IDs0/2/3, bitmap indices1/2 retained; retired IDs1/0 reject before state
mutation. No configuration migration. Kconfig startup1 explicitly fails compilation.
Host preview/control reject night_owl. Negative raw Host commands retain existing
sticky INVALID_ARG258 behavior; the normal CLI rejects before sending.

Dragon retains selected sclera C and approved240 sampling. Deep-sea retains R2
surface with no rim fade,240ms ordinary membrane and450/150ms sleep/wake. Its
appearance was accepted in1.0.13, with incomplete visible membrane motion at low
FPS noted by the user. This removal does not change that timing or promise higher
frame rate. Mechanical retains socket A and centered closure. No detector,
controller, sampling cadence, physical coordinate mapping or IMU change.

Keep both gaze flips enabled: the user confirmed both axes correct in dragon
and mechanical after1.0.11. Earlier contradictory1.0.6/1.0.9 acceptance stays
historical. IMU screen gravity remains(-ax,+ay). Do not flip source arrays or
reintroduce a removed role based on older archive instructions.

## Validation and resource result

Debug/Release ctest37/37. Generated inventory has only sea/mechanical streams;
final application/ELF contains no owl runtime name or eye_night_owl symbol.
Remaining31 bitmap streams and core/controller/dragon/IMU source are unchanged.
256 full C/scalar frames and38 independent PNG checks pass. Native16 pointer
checks,44 orientation images (all identical to1.0.14 retained views), three-role
wrap/backward cycles, retired-name rejection,511 recorded arrays/655 events and
six live switches pass. Recorded replay movie retains wall-clock intervals.

App7218608B, down2291104B (~2.18MiB) from1.0.14. UI94480B unchanged; bitmap
RODATA4496919B. Explicit bitmap PSRAM3418224B/internal renderer2004B unchanged.
Post-update dragon free internal233271B/free PSRAM3984068B (prior1693128B).
Physical button cycling was not repeated on hardware; production pointer/AI
adapter logic and native inputs were checked. No new physical FPS, largest-block,
latency or allocator-peak claim. No remeasurement needed to claim the unchanged
artwork, but earlier rates must remain labelled by their original versions.

## Commands, evidence and restore

python3 tools/preview.py --view deep_sea --flip-x --flip-y
python3 tools/control.py next / previous
python3 tools/control.py case live; python3 tools/control.py play / pause / replay
python3 tools/build_idf.py uses build/sdkconfig.three-eyes.

Evidence: evidence/remove-owl/. Compact delta review uses
python3 tools/package_review.py --remove-owl (requires49648e4/1.0.14 baseline).
Exact historical1.0.14 restore: evidence/night-owl-r2/device-install/organic-r2.irisfw;
this archive still contains the rejected owl and must not be installed by default.
Earlier approved-only1.0.13 restore remains in evidence/deep-sea-r2/device-install/.
Local exact ELF/map/config backups remain in ignoredfirmware-local/.

Standing authorization covers official updates on this same device and required
reboots/retained-Recovery transitions. No ROM recover, full erase, dependency
upgrade, remote repository write or default-branch mutation occurred. Main work
branch remainsfeat/eye-ui-trio. Historical docs/evidence do not override the
current three-role roster.
