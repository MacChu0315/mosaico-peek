# Peek handoff — exact-output rendering1.1.1 (2026-10-25)

Installed1.1.1 on perf/three-eye-render contains dragon, deep_sea and mechanical.
Night owl stays retired. Frozen v1.1.0 source tag082c783 and exact bundle remain
unchanged; never move that tag or overwrite releases/v1.1.0.

## Installed identity

Sourceeffb682e2a35a6b6a4e862f990d6eb5219831a9d.
ELFfad83dba1a8e4628b70dd82efbd4520d63b11006bdf12f70bd2b780442d5e33b.
Boot11328770680449269444; official update58511ef0-5c8a-4065-a38b-3cf3c1439577
succeeded first attempt. Matching version/source/ELF, normal mode, VALID,
runtime/IMU error0 and crash_count0. Both flips enabled; orientation270 observed.
Only authorized MAC30:ed:a0:f4:52:a0 / Device ID4553502d49524953010030eda0f452a0
was updated. Restore: releases/v1.1.0/mosaico-peek-v1.1.0.irisfw.

## Rendering changes and validation

[RENDER_V111.md](RENDER_V111.md) records the three approved exact-output changes:
affine quarter-turn tile traversal; neutral exact texel sampling preserving HDR;
identical-picture retention while acquisition, source ticks and wake checks stay
live. Actual outer-lid/frame alpha establishes deep-sea occlusion. No gaze,
artwork, timing, source detector/controller, orientation or dependency change.

Debug/Release37/37;288 full480 scalar comparisons; four-angle odd tiles; static
invalidation/zero-completion status checks. Native16 pointer checks,44 orientation
images,17 sea phase checkpoints and retained-picture source/wake/replay checks
pass;511 recorded arrays/655 events preserve results. Three native8s movies use
actual capture intervals. No physical panel-FPS claim.

App7219760B (+1152 over1.1.0), UI94480B and all bitmap streams unchanged. Shared
UI10336B (+24), renderer internal2004B, explicit bitmap PSRAM3418224B unchanged.
No added framebuffer. Existing SDK include/factory-size warnings remain; ota_0 fits.
Measured270deg deep-sea active-open6.598Hz versus baseline5.769Hz, short different
hand-played windows (6.82s/4.16s), not controlled percentage speedup. Closed24.55s
has0 redraws with193 samples. Mechanical270deg active-open4.737Hz lacks a same-angle
baseline; closed16.74s has0 redraws with131 samples. Both stable closed device
RGB565 captures match C; mechanical stays centered.0 sample faults/runtime errors.
Current dragon activity, panel FPS and long-term runtime remain unmeasured.
See evidence/render-v111/device-after and RENDER_V111.md for limits. Review delta:
review/mosaico-peek-render-v1.1.1.zip (requires complete v1.1.0/fa34821 baseline).

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

## Inherited three-eye validation and resource result

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
python3 tools/build_idf.py now builds development1.1.1 with build/sdkconfig.v1.1.1.

Evidence: evidence/remove-owl/. Compact delta review uses
python3 tools/package_review.py --remove-owl (requires49648e4/1.0.14 baseline).
Exact historical1.0.14 restore: evidence/night-owl-r2/device-install/organic-r2.irisfw;
this archive still contains the rejected owl and must not be installed by default.
Earlier approved-only1.0.13 restore remains in evidence/deep-sea-r2/device-install/.
Local exact ELF/map/config backups remain in ignoredfirmware-local/.

Standing authorization covers official updates on this same device and required
reboots/retained-Recovery transitions. No ROM recover, full erase, dependency
upgrade, remote repository write or default-branch mutation occurred. Main work
branch isperf/three-eye-render. Historical docs/evidence do not override the
current three-role roster.
