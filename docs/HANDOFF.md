# Peek handoff — socket A and centered mechanical sleep (2026-10-22)

Current source targets1.0.11-peek-direction, combining calibrated orientation
(fca4114/installed source74a0f44) with frame A and centered sleep. The standalone
1.0.8 center bundle was NEVER installed: preflight found the newer orientation
firmware and stopped. User then authorized this integration after releasing the device. User selected A, restoring the original
fixed metal socket around the new C globe/central shutter. On sleep closure,
only the mechanical display pose smoothly returns to center; the final closed
shutter frame stays exactly still. Wake resumes existing follow. Ordinary
blinks, other characters, detector/source state, timing, physical mapping and
full480 rendering remain unchanged. [Details and commands](MECHANICAL_C.md).

The raw shared controller intentionally retains its previous idle behavior;
Host render_pose and device render_gaze_x/y describe the mechanical display.
Do not center by writing back into the source; thermal mounting signs are a separate calibration.
A selection is recorded in assets/mechanical-c-adaptation.json. B remains a
retained unselected image-generation candidate. The supplied C package is intact.

## Current device versus candidate

Installed1.0.10-peek-integrated, source7d897f6,
ELF3dc84c29223f08681d8472ad3601d8e053b0e991de9c55a9875a9e7bb28b955f,
Boot13998171743381255122. Official update retry succeeded as operation
7e9e5d4b-bc8d-40e3-8a04-4c25cb99692f. The first update outcome remained unknown
following a Recovery writer reset; read-only reconciliation, a new healthy idle
Recovery boot, empty queue and absent job preceded the same-bundle retry.
Evidence: evidence/mechanical-c/integrated/device-install/.

Latest user feedback rejects BOTH tracking axes in mechanical AND dragon in
unchanged placement. Device reports orientation0, flipsfalse/false. Both actual
C rasterers independently move positive gaze right/down. This points to shared
thermal mounting signs, not an artwork-only shader or IMU rotation correction.
Earlier1.0.6 and1.0.9 physical acceptance remains historical; why those reports
contradict the latest observation has not been established. Do not claim it was
caused by this merge: shared source mapping and IMU code were retained exactly.

Current candidate1.0.11-peek-direction enables BOTH existing source mapping flips
using isolated sdkconfig.integrated-direction. Raw768 arrays, detector results,
IMU gravity(-ax,+ay), mount quarters0, centering and renderers remain unchanged.
Device-equivalent preview requires --flip-x --flip-y. Physical retest is pending.
The failed-before/passing-after config regression prevents silent restoration of
old defaults; adapter tests cover both configurations and mailbox inheritance.
New evidence: evidence/mechanical-c/direction/; failed1.0.10 direction feedback:
evidence/mechanical-c/integrated/direction-feedback/.

Integrated1.0.10 had29/29 Debug/Release and40 native four-way pixel checks.
A/centering had11 native close/wake checks and a real-time close clip. These are
software parity evidence, not proof of physical heat-direction correctness.
The1.0.11 checks are recorded separately; no physical direction pass yet.

## Performance and known limits

Historical1.0.7 thin-mount measurements:3.935 active-open complete GSP frames/s,
3.879 sleeping frames/s; raster212..214ms, submit32ms.74.41s mechanical segments,
583 fresh thermal samples, zero faults. This was slower than1.0.6's7.095Hz.
Frame A reduces visible sphere area to the original socket's footprint; new
integrated performance must be measured, not inferred. Physical panel FPS, touch
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

Start: python3 tools/preview.py --view mechanical --flip-x --flip-y.
Select/replay: tools/control.py view mechanical; case sleep/live/dragon;
play/pause/replay. Product taps/left swipes/AI single clicks advance, right swipes
return. Package: python3 tools/package_review.py --mechanical-c, after clean commit.
