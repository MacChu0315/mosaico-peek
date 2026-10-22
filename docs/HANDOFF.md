# Peek handoff — socket A and centered mechanical sleep (2026-10-22)

Current source targets1.0.8-peek-center. User selected A, restoring the original
fixed metal socket around the new C globe/central shutter. On sleep closure,
only the mechanical display pose smoothly returns to center; the final closed
shutter frame stays exactly still. Wake resumes existing follow. Ordinary
blinks, other characters, detector/source state, timing, physical mapping and
full480 rendering remain unchanged. [Details and commands](MECHANICAL_C.md).

The raw shared controller intentionally retains its previous idle behavior;
Host render_pose and device render_gaze_x/y describe the mechanical display.
Do not “fix” this by writing centered gaze into the source or by flipping axes.
A selection is recorded in assets/mechanical-c-adaptation.json. B remains a
retained unselected image-generation candidate. The supplied C package is intact.

## Current device versus candidate

Device currently runs verified1.0.7-peek-mechanical, sourcedf6f6da,
ELF97d859cb847b3ceeff6956477098a28210dc90ebe50a3f3e6dfdc5f5ac010d2e,
Boot1088401539410791703. Final1.0.8 build/install verification is in progress;
do not infer that source changes are already installed.

26/26 Debug and Release tests pass for A/centering. Independent81 mechanical
pose/stage images and16 stage boundaries pass; full480 scalar parity preserved.
Native A:11 centered-close/wake pixel checkpoints and a real-time close clip,
16 pointer checks/four artwork captures,22 mechanical motion/sleep checkpoints
and two full wall-time movies pass. Source role/detector survive switches/replay.
Final evidence belongs under evidence/mechanical-c/a-centered/; old1.0.7 evidence
is retained separately. Native dynamic evidence is not physical FPS acceptance.

## Performance and known limits

Historical1.0.7 thin-mount measurements:3.935 active-open complete GSP frames/s,
3.879 sleeping frames/s; raster212..214ms, submit32ms.74.41s mechanical segments,
583 fresh thermal samples, zero faults. This was slower than1.0.6's7.095Hz.
Frame A reduces visible sphere area to the original socket's footprint; new
1.0.8 performance must be measured, not inferred. Physical panel FPS, touch
latency, largest allocator block and complete memory peaks remain unmeasured.
Extreme-direction peripheral texture stretching still exists in the supplied
surface. No smaller gaze range, downsampling or palette was added to hide it.

## Authorized hardware scope and update history

Only MAC30:ed:a0:f4:52:a0 / Device ID4553502d49524953010030eda0f452a0.
Standing user permission covers subsequent official System Update installations
and their required reboots/retained-Recovery transitions. Recheck identity and
exact artifact/layout each time; reconcile uncertain outcomes before another
write. No ROM recover, whole erase, shared SDK/BSP upgrade or remote write.

The first1.0.7 operation remainedoutcome_unknown after a retained Recovery
writer reset. Read-only reconciliation, new healthy idle Recovery, empty queue
and absent old job preceded one same-bundle retry, which succeeded. The old
core dump ELF did not match the failed writer; it is not a source diagnosis.
[Exact history](../evidence/mechanical-c/device-install/README.md). A similar
1.0.5 incident is retained under eye-ui/performance/device-install/.

## Retained restore and review material

-1.0.7: evidence/mechanical-c/device-install/mechanical-c.irisfw (sourcedf6f6da).
-1.0.6: evidence/eye-ui/motion/device-install/eye-motion.irisfw (sourcefd637cc).
-Earlier1.0.5/1.0.4/1.0.3/1.0.2 packages and detailed original dragon records
 remain in their evidence directories and docs/DEVICE_DRAGON.md. No restore was
 performed. wip/dragon-packed-color remains an unverified alternative, not baseline.
-Exact local ELF/map/config backups: ignoredfirmware-local/. No full-flash
 readback backup claim. Local branchfeat/eye-ui-trio; no remote configured/written.

Start: python3 tools/preview.py --view mechanical (no flip flags).
Select/replay: tools/control.py view mechanical; case sleep/live/dragon;
play/pause/replay. Product taps/left swipes/AI single clicks advance, right swipes
return. Package: python3 tools/package_review.py --mechanical-c, after clean commit.
