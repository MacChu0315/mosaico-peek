# Peek handoff — approved deep-sea R2 (2026-10-24)

Current source targets1.0.13-peek-deepsea, combining calibrated orientation
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

Completed task: integrate the returned selected dragon sclera C under explicit
user authorization. Installed1.0.12-peek-sclera replaces only procedural sclera
with exact RGB888 sampling; original iris/lids/lighting and accepted mechanical
remain intact. [Integration](DRAGON_SCLERA.md). The official update and post-boot checks below are complete.

The user selected reconstruction, then accepted deep-sea R2 and requested this
integration before revisiting owl. Candidate1.0.13 uses the exact accepted eye
surface, no rim layer,240ms independent membrane and existing450/150ms sleep/
wake rules. Ordinary blink cadence comes from the unchanged shared controller.
Owl remains on its existing runtime; no new owl artwork is installed.
[Deep-sea implementation and commands](DEEP_SEA_R2.md).

Current verification: Debug/Release36/36; seven approved R2 snapshots exact,
384 full-frame scalar C comparisons,57 independent PNG comparisons,17 native
phase checkpoints,52 orientation pixel checks,16 switch checks,22 native motion/
sleep pixel checks and two real-time movies. Recorded511 arrays/655 events and
six live view switches pass.32 non-sea native frames and22 owl/mechanical
compressed streams are byte-identical to baseline. Renderer buffers unchanged.
Initial failed test comparisons and clean preview interruption remain in
verification/; corrected same-tick replay and bounded native runs passed.
Device update/physical R2 acceptance are still pending below.

## Current installed device

Installed1.0.12-peek-sclera, sourced7f5af5,
ELFdbfbf90c05fb944db80ec0714dbf7f3016d10e8d3dd23e64df722fb13d7edbe5,
Boot5484327898152195899. Official update226bfcca-bf7e-47fc-aead-57dd4b3aaf36
succeeded on its first attempt. Post-boot identity/hash match, VALID capture,
application/IMU error0, crash_count0; both mounting flipstrue, autoenabled.
The user observed the new sclera during movement and answered “符合预期”.
Evidence: evidence/dragon-sclera/device-install/ and user-acceptance.json.

The current C texture replaces only procedural eye-white coloring. Shared
controller/detector, physical map, calibrated IMU, original iris/skin/eyelids,
other artwork, mechanical socket A and its centering are byte-identical to the
prior source. Native before/after40 controller/detector checkpoints and32
other-artwork screenshots are identical. All75 supplied checksums are retained.

Validation: Debug/Release33/33;11 supplied C pose references pixel-exact and
sclera-only, unchanged full closure; generator deterministic/read-only and rejects
corruption/non-build output; native40 orientation comparisons,22 motion/sleep
pixel checks,30.16s/34.16s real-time native clips;511 recorded arrays/655 events
match production replay, four artwork replay checks and six live switches with
68.4s real-time recording. Videos are native screenshot evidence, not panel FPS.

Current physical map: keep both flips enabled. On1.0.10 the user reported BOTH
dragon and mechanical reversed in unchanged placement with orientation0 and
flipsfalse/false. After1.0.11 the user confirmed both axes correct in both views.
Earlier1.0.6/1.0.9 acceptance remains historical; the conflicting reports' cause
was not established. This texture update changes no mapping or IMU code.
Device-equivalent preview uses --flip-x --flip-y. Runtime observed0/270deg and the270deg closed framebuffer matched C. Complete
four-placement physical tracking acceptance has not been repeated in1.0.12;
native four-way checks pass separately.

## Performance and known limits

Current1.0.12 app7705744B (+689408B from1.0.11), GSP94480B unchanged. Exact
sclera RGB888691200B; linked dragon texture/LUT total1340932B (unused old sine
2048B removed by linker). Same dragon renderer allocation3929120B and shared
UI10312B. No new dynamic decode/cache; XIP/RODATA-to-PSRAM is enabled. Post-boot
free internal233271B unchanged, free PSRAM3497828B versus prior4186436B in dragon.
Full peak/largest-block and physical panel FPS remain unmeasured.
Current1.0.12 measured54.04 device seconds,424 new thermal samples,0 faults.
Orientation0 active-open9.627 complete GSP frames/s (49 frames/5.09s);270 active-
open7.510 (136/18.11s). Rotation-changed intervals are excluded from groups.
Orientation0 sleeping19.818 frames/s (short4.39s segment). Canvas callbacks
102.794/s are tile callbacks, not full frames or physical panel FPS. Active/
transition raster/submit:0deg62.430/31.555ms per frame;270deg96.208/29.924ms;
0deg sleeping11.311/31.833ms. Different real scenes, no controlled speedup claim.
A separate stable closed-device screenshot at270deg matches C RGB565 exactly.
No device runtime/IMU errors or reboot during these checks. See
evidence/dragon-sclera/device-performance/dragon-active-closed/ and device-closed/.

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

-1.0.11: evidence/mechanical-c/direction/device-install/peek-direction.irisfw.
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
return. Current review: python3 tools/package_review.py --dragon-sclera, after clean commit.
