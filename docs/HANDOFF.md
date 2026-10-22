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

User visually accepted the installed1.0.11 mechanical result on2026-10-22:
“可以，感觉机械眼的效果还可以”. Treat the C globe/shutter with socket A,
current motion range and centered closure as the accepted mechanical baseline.
This acceptance does not expand rendering-detail authorization or imply the
unmeasured performance/physical-orientation checks below have passed.

Next art-only task: user requested the original dragon materials for sclera
improvement. [Standalone material handoff](DRAGON_ART_HANDOFF.md) includes
originals, procedural-sclera template and tested preview. No new dragon art is
selected or installed; current firmware and accepted mechanical remain intact.

## Current device versus candidate

Installed1.0.11-peek-direction, sourcee5d8629,
ELF7f6f4904a770952878e8cd4557341956154e0b8589a8d1f48fbd4f11b92d1aea,
Boot6092061336953637827. Official System Update succeeded on the first attempt:
40570b75-6459-4810-834c-cf6f4af53666. Post-boot runtime confirms both mounting
flips enabled, orientation0/autoenabled, VALID capture, application/IMU error0,
crash_count0. User now confirms BOTH axes correct for dragon AND mechanical in this placement.
Evidence: evidence/mechanical-c/direction/device-install/.

The previous integrated1.0.10 was source7d897f6. Its first update outcome remained
unknown following a Recovery writer reset; read-only reconciliation, new healthy
idle Recovery, empty queue and absent job preceded a successful same-bundle retry.
Exact evidence/restore: evidence/mechanical-c/integrated/device-install/.

Before the1.0.11 correction, user feedback rejected BOTH tracking axes in
mechanical AND dragon in unchanged placement. The1.0.10 device reported
orientation0, flipsfalse/false. Both actual
C rasterers independently move positive gaze right/down. This points to shared
thermal mounting signs, not an artwork-only shader or IMU rotation correction.
Earlier1.0.6 and1.0.9 physical acceptance remains historical; why those reports
contradict the latest observation has not been established. Do not claim it was
caused by this merge: shared source mapping and IMU code were retained exactly.

Installed1.0.11-peek-direction enables BOTH existing source mapping flips
using isolated sdkconfig.integrated-direction. Raw768 arrays, detector results,
IMU gravity(-ax,+ay), mount quarters0, centering and renderers remain unchanged.
Device-equivalent preview requires --flip-x --flip-y. User confirmed both axes
correct on dragon and mechanical after the update (observed orientation0).
Other physical rotations have not been re-tested with1.0.11.
The failed-before/passing-after config regression prevents silent restoration of
old defaults; adapter tests cover both configurations and mailbox inheritance.
New evidence: evidence/mechanical-c/direction/; failed1.0.10 direction feedback:
evidence/mechanical-c/integrated/direction-feedback/.

Integrated1.0.10 had29/29 Debug/Release and40 native four-way pixel checks.
A/centering had11 native close/wake checks and a real-time close clip. These are
software parity evidence, not proof of physical heat-direction correctness.
1.0.11: Debug/Release30/30 plus new mounted-adapter and affected IMU tests pass;
40 native orientation frames,11 native centered-sleep frames/real-time clip,
5 replay cases and511 real arrays/655 events pass. Pinning current mounting
defaults failed before the fix. IDF build and package/installed ELF checks pass.
Physical direction pass is user-confirmed for dragon/mechanical in the current
placement; other placements are native-tested only in this update.

## Performance and known limits

Historical1.0.7 thin-mount measurements:3.935 active-open complete GSP frames/s,
3.879 sleeping frames/s; raster212..214ms, submit32ms.74.41s mechanical segments,
583 fresh thermal samples, zero faults. This was slower than1.0.6's7.095Hz.
Frame A reduces visible sphere area to the original socket's footprint.
Current1.0.11 mechanical: active-open6.124 complete GSP frames/s, sleeping6.617;
canvas callback91.580Hz. The54.87s window accepted430 fresh thermal samples with
0 faults. Active/transition raster120.675ms, sleeping110.429ms; submit33.197/32.261ms.
These are different live scenes from1.0.7, not a controlled speedup percentage.
Device closed framebuffer exactly matches production C at centered(0,0), while
source gaze stays(-0.05,0.035). First60s centering probe ended before a stable
closed mechanical window; retained as NOT VERIFIED, followed by successful
post-measurement check. Evidence: direction/device-performance/mechanical-a/
and direction/device-center-confirmed/. The first1.0.11 observation stayed
on dragon for54.39 device seconds:426 fresh samples,0 faults, active-open9.483
complete GSP frames/s;93.308 canvas callbacks/s. This is not mechanical data. Physical panel FPS, touch
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

-1.0.10: evidence/mechanical-c/integrated/device-install/peek-integrated.irisfw.
-1.0.9: evidence/mechanical-c/integrated/restore-1.0.9/orientation-calibrated.irisfw.
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
