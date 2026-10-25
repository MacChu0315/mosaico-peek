# Peek handoff — night owl removal (2026-10-25)

The user explicitly rejected night owl and requested removal from firmware.
Candidate1.0.15-peek-three has only dragon, deep_sea and mechanical. UI IDs0/2/3
remain stable; ID1 is invalid. Three-entry cycling is shared by touch/swipe/AI.
Host selectors reject owl, and no owl texture is generated. Source artwork and
historical evidence are archived, not deleted or linked into current firmware.
[Details and commands](OWL_REMOVAL.md).

Host/Release37 tests pass. Retained31 bitmap streams and detector/controller,
dragon renderer and calibrated orientation files are unchanged. Native and final
firmware/install checks are being completed. Device is still1.0.14 until the
new official update is confirmed below.

## Current installed device

Installed1.0.14-peek-organic, source735fbe7,
ELF391287d2cb275c6d2726e4fe45059678cded097e58c38fe91c4cb3772d7805fb,
Boot934720684676756858. Official update succeeded on its first attempt; actual
ELF/version verified, VALID input, runtime/IMU error0, crash_count0, both flips
true and calibrated auto orientation retained. Default startup remains dragon;
next view is the new night owl. Physical owl visual/performance checks pending: latest read-only observation
remained on dragon, so no other-view counters are presented as owl measurements.
Evidence: evidence/night-owl-r2/device-install/.

Previous1.0.13-peek-deepsea, sourcea5ef0ce, is the exact restore at
evidence/deep-sea-r2/device-install/deep-sea-r2.irisfw. User accepted its look,
with intermittent incomplete visible240ms membrane motion at low frame rate.
Keep approved timing without silent stretching; membrane counters now count
ordinary frames from whichever organic view is active. Deep-sea was preserved
in this update, not restyled.

The retained dragon C texture replaces only procedural eye-white coloring. Shared
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

Current1.0.14 app9509712B (+778112B), UI94480B unchanged; linked bitmap
resources6788133B. Explicit bitmap PSRAM3418224B/internal renderer2004B unchanged.
Initial dragon free internal233271B/free PSRAM1693128B; actual owl-state memory,
active/closed rates and physical acceptance remain to be measured. Other-artwork
native44 frames and deep-sea/mechanical31 compressed streams are unchanged.

Historical1.0.13 figures below are not1.0.14 measurements.

Historical1.0.13 app8731600B (+1025856B from1.0.12), UI94480B unchanged. Bitmap
resources6010037B linked; explicit renderer PSRAM3418224B and internal struct
2004B unchanged. Only deep-sea transparent RGB was normalized in build streams.
Device deep-sea free internal243799B/free PSRAM3025464B; lifetime minima
192100B/2467060B after the closed check (not attributed allocator peaks/largest-block measurements).

Measured54.94 device seconds at270deg,431 fresh thermal samples,0 faults:
active-open5.751 complete GSP frames/s, overall5.679; raster132.044ms/frame,
submit33.535ms/frame, prepare1.501ms/prepare. Canvas callbacks85.184/s are tiles.
Nine completed ordinary-membrane frames, including three full-coverage frames,
were observed. At roughly174ms per active frame, a240ms pulse is represented
by only1–2 frames; the nearest-stage8 coverage window is about53ms. This supports
the user's report that some phases are not fully seen. No guarantee of every
membrane phase or physical panel FPS. Current logic/time is retained, limitation
unresolved; different scenes/orientations are not a controlled speed comparison.
A separate18.95s closed window at270deg completed141 frames (7.441Hz),
148 new samples and0 faults; raster90.297ms, submit34.095ms, prepare0.027ms.
Stable closed-device pixels exactly match production C. Native closed pixels
and all four rotations also passed. Full four-placement physical tracking retest,
largest memory block and end-to-end touch/visual latency remain unmeasured.

Historical preceding version measurements follow; do not cite them as1.0.13.

Historical1.0.12 app7705744B (+689408B from1.0.11), GSP94480B unchanged. Exact
sclera RGB888691200B; linked dragon texture/LUT total1340932B (unused old sine
2048B removed by linker). Same dragon renderer allocation3929120B and shared
UI10312B. No new dynamic decode/cache; XIP/RODATA-to-PSRAM is enabled. Post-boot
free internal233271B unchanged, free PSRAM3497828B versus prior4186436B in dragon.
Full peak/largest-block and physical panel FPS remain unmeasured.
Historical1.0.12 measured54.04 device seconds,424 new thermal samples,0 faults.
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
Historical1.0.11 mechanical: active-open6.124 complete GSP frames/s, sleeping6.617;
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

Start: python3 tools/preview.py --view deep_sea --flip-x --flip-y.
Select/replay: tools/control.py view night_owl; case sleep/live/dragon;
play/pause/replay. Product taps/left swipes/AI single clicks advance, right swipes
return. Current compact delta review: python3 tools/package_review.py --night-owl-r2, after clean commit.
