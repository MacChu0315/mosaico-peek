# Automatic orientation physical correction — 2026-10-22

Branch includes main UI commit5e30025 and retains mechanical C. Version1.0.8
installed successfully (operation862149bf-00bf-4d2a-ace8-1d55d7ed0578,
Boot1100252626072364809), but user corrected their response to ALL FOUR
orientations wrong. No physical acceptance. Labelled upright/+Y and clockwise90/-X
measurements expose an XY handedness error plus the provisional mounting angle.
Candidate1.0.9-peek-orient converts screen gravity to(-ax,+ay); real measurements
are regression fixtures. Build config:sdkconfig.orientation-calibrated.
Retest/install status is recorded in AUTO_ORIENTATION.md and device evidence.

---

# Mechanical C continuation (2026-10-22)

The user approved native adaptation of mechanical-c-assets-v1 after source
review. Candidate1.0.7-peek-mechanical replaces only mechanical art: opaque globe,
rotating central shutter and fixed round mount. Source/gaze range, both confirmed
false flip flags, shared detector/behavior/sleep timing and switching remain.
[Implementation, sources, resources and commands](MECHANICAL_C.md).

Installed1.0.7-peek-mechanical, sourcedf6f6da63613656204ccee052f637494433da2b8,
ELF97d859cb847b3ceeff6956477098a28210dc90ebe50a3f3e6dfdc5f5ac010d2e.
Official operation44a14d33-a875-4164-99ef-3f5e9dcfcb2f succeeded, healthy/validated;
Boot1088401539410791703. Runtime error0/crash0, both flips false, live input.
[Exact install and first-attempt reconciliation](../evidence/mechanical-c/device-install/README.md).

The first attempt eac7243a-89b3-4067-a22d-31058e02fdad remainedoutcome_unknown
following a retained Recovery writer reset. Its failed Boot/address/ELF identify
Recovery, not this candidate app; the retained core dump ELF does not match the
failed writer. After read-only reconciliation, a new healthy/idle Recovery boot,
empty queue and absent prior job, one identical-bundle retry succeeded. No ROM
recover, erase, Recovery replacement, shared SDK change or remote write.

Host Debug/Release25/25 pass;81 independent direction/shutter references and16
nearest-frame boundaries pass;384 full frames match scalar C. ASan/UBSan passes
with the established leak-sanitizer restriction. Native66 pixel checkpoints,
16 pointer checks, six wall-time movies and all511 real arrays/655 events pass.
New HDR composite reuses existing workspace; bitmap explicit PSRAM3418224B.
Final app6660928B fits unchangedota_0; the prior factory-size warning remains.
Device performance/visual acceptance is tracked separately from these checks.

Old1.0.6 direction/range acceptance remains valid. Mechanical C intentionally
changes the old neutral picture; the former fixed-lid/locked-mask policy does not
apply to its new artwork. The supplied extreme-diagonal texture stretch remains
a visual limit. Its larger visible sphere area needs actual device timing; prior
7.095Hz mechanical result is not a prediction for this new renderer.


## Current device performance limitation

[Actual device windows](../evidence/mechanical-c/device-performance/README.md)
measure about3.93 active-open complete GSP frames/s and3.88 sleeping frames/s.
Raster is212..214ms/frame; submit about32ms. Thermal acquisition remains about
7.8 fresh samples/s with zero faults. Prior1.0.6 mechanical was7.095Hz active-open;
new full-globe artwork is slower, and this regression is not resolved or called
fluid. Physical panel-visible FPS remains unmeasured. Closed state and later
TRACKING were observed; no exact physical wake-duration claim.

Memory before screenshot: internal free247763B, PSRAM free5096896B. Peak/largest
blocks and input-to-screen latency are not established. The next performance
step is raster profiling/optimization under the same full480 and gaze bounds;
do not silently reduce quality, change shared behavior or inflate FPS with cheap
states. Visual acceptance of the new installed artwork remains pending.

The following2026-10-21 history is retained for exact prior results/restores.

---

# Peek handoff — direction and motion correction (2026-10-21)

Current source targets1.0.6-peek-motion, default dragon. Latest user feedback
confirmed BOTH axes reversed with1.0.5's two flips enabled. Both flags are now
false, before source acquisition; raw arrays/detector coordinates are unchanged.
New eyes use full480 sphere rotation with pure-axis center travel±120/±80px,
replacing tiny±10..20/±8..12px translations. Neutral visible pixels match1.0.5
exactly; original handoff assets and dragon shader/behavior remain unchanged.
[Current correction and validation](EYE_MOTION.md).

Installed1.0.6-peek-motion, sourcefd637cc133b132fe2a3f81661a577377beba57ed,
ELF`543337f9a5fab62621b94c5ee01d443e8af582543e7558a20ac24d3ab5e6084b`.
Operation`b5fe1381-1fc4-4bee-912d-a43dbbe8a099` succeeded, healthy/validated,
new Boot11818992348187344414. Normal mode, crash_count0, runtime error0 and
both flip flags false were verified on the device. Default dragon.
[Exact installed package and checks](../evidence/eye-ui/motion/device-install/README.md).

Prior1.0.5 mechanical active-open engine rate8.333Hz versus1.0.4's2.009Hz;
live scenes differ, physical panel FPS unmeasured. These do not establish the
new sphere-rendering cost. [Earlier measurements](../evidence/eye-ui/performance/COMPARISON.md).
One earlier1.0.5 update outcome remained unknown after a retained Recovery writer
watchdog reset; reconciliation and an idle new Recovery boot preceded the
successful retry. It did not recur in1.0.6. [History](../evidence/eye-ui/performance/device-install/README.md).

Standing user authorization covers subsequent official System Updates only for
MAC30:ed:a0:f4:52:a0 / Device ID4553502d49524953010030eda0f452a0,
including required update reboots/retained-Recovery transitions. Recheck exact
artifact/layout/identity; reconcile uncertain outcomes before any further write.
No ROM recover, erase, shared dependency update or remote write is authorized.

Tap/left swipe/AI single click next; right swipe previous. Source detector/role,
time and mapping survive artwork switches. Only active large renderer caches
are retained. If replacement allocation fails, the display enters a reported
error; old-renderer rollback is not promised. Current1.0.6 installation is verified;
the user confirmed the original dragon now tracks correctly on BOTH physical
axes. The user accepted the wider range but rejected the synthesized hidden texture.
Artwork replacement is pending; see EYE_ART_HANDOFF.md.
Prior1.0.5/1.0.4/1.0.3/1.0.2 bundles remain retained separately. No use of
wip/dragon-packed-color as a verified baseline. Current work stays on the local
feat/eye-ui-trio branch; no remote is configured or written.


## Installed1.0.6 performance

[65s mixed-view observation](../evidence/eye-ui/performance/motion-live/README.md)
includes40.99s mechanical: mixed6.904 engine Hz, active-open7.095Hz,
raster98.53ms/frame, submit32.87ms/frame;322 fresh thermal samples, zero faults.
This costs more than1.0.5's small translation (8.333Hz active-open), while the
original1.0.4 was2.009Hz. Scenes differ; no controlled percentage claim.
Before screenshot, internal free247763B and PSRAM free5116384B. No panel FPS,
largest-block or complete peak-memory claim. Physical HOLD observed; no sustained
physical closed/sleep window. All three new views ran error-free in this window;
other per-theme timing segments are short. Native closed-eye timing is separate.

The following section preserves the prior installed-device handoff verbatim.

---

# Peek live dragon handoff — stopped at user-accepted trial (2026-10-21)

The user said “可以，就先这样吧”. Keep the current device running; stop further
optimization/installation and hand off. **The roughly15Hz doubling goal is not
achieved.** This is acceptance of the current stopping point, not a measured
15Hz pass or a specific physical closed/wake test result.

## Current device / source

- MAC `30:ed:a0:f4:52:a0`, Device ID `4553502d49524953010030eda0f452a0`.
- Version `1.0.2-peek-sleep`; source **f8845c5c03794b97bb6c146b87a36d8327092519**.
- ELF SHA `23bb5c540f2f480614a0771e939e4d30429bc1f74853a695f396d6543b34eebb`.
- Boot ID `3345998236476284272`; official operation
  `663a7636-cf9b-47c1-818a-79daa08f7741` succeeded, healthy/validated.
- Final official status/RPC/screenshot verify same MAC/Boot/ELF, normal mode,
  zero crash count, both gaze flips true and continuous live input. No reboot
  or install after the user's stop. Device remains running the dragon.

Only this board was operated. Existing ota_0, bootloader and partition layout
retained; target_recovery=null, so Vibe Mode was not overwritten. No algorithm
A/B, adjacent checkout modification, shared dependency upgrade or remote write.

## Implemented

Shared production C detection and source-owned role process every complete frame
before the latest-only display mailbox. No repeated old temperatures on read
failure; independent render snapshots cannot lose detection samples or change
acquisition history. Detector/header match read-only diagnostic63c0799 and
reviewed f278cfd; thresholds remain unchanged. Significant hot regions are
selected; cold objects do not compete. Current physical mount flips both target-
to-gaze axes, leaving native32x24 temperatures/detector coordinates unchanged.

User-approved240 odd-center sampling remains replicated2x2 into480 output.
Original textures/shape/color and scalar480 reference are retained. Prepared
exact-geometry reuse accelerates static eyelids and pure eye interiors while
boundary pixels retain the scalar compositor. Gaze/pupil remain dynamic; no
additional downsampling or pose quantization. See SLEEP_RENDER.md. Explicit
PSRAM caches: fixed3,225,600B plus prepared691,200B; target renderer total
**3,929,120B**, not a complete application peak. Allocation failures propagate.

IDLE now calmly looks for10s after entry, closes over450ms, stays closed, and
opens over150ms only when production detection confirms a target. Pending
candidates/faults do not wake it. LEAVE/reentry resets the10s clock. Seeded,
injected-time replay and same-time idempotence remain. Diagnostic RPC exposes
sleeping/waking/cache state and separate active-open render counters, without
creating observations. All animation behavior stays shared C.

## Actual results

Latest94.74s physical window:7.843 accepted samples/s, zero read faults, every
observed sequence equals sample count. All rendered states averaged9.975 engine
frames/s; **active, fully open target-follow averaged10.336 engine frames/s**
over86.882s/898 frames. Active-open mean84.62ms, raster53.19ms, submit31.32ms.
This includes cache misses and excludes closed-eye frames.53/87 sampled states
had reusable geometry; TRACKING/HOLD changes can invalidate it. Historical
ba98632 was about7.546 engine frames/s in a different scene. No controlled
same-scene percentage-speedup claim. **Physical panel-visible FPS is unmeasured**;
Canvas tiled callbacks103.072/s are not full screen frames. Host30Hz remains
unmet and was not a new investigation target.

Observed cores GSP1/sensor0. Internal free237,891B/min196,720B; PSRAM
free/min9,211,008B before screenshot. These are allocator readings, not largest
blocks or complete workload peaks; screenshots can lower later minima. Task
memory through iris memory remains unavailable (HTTP501); status heaps work.

The physical window showed TRACKING/HOLD, no IDLE/sleep/wake. Final read-only
state remained TRACKING. **Do not claim physical sleep/wake timing was observed**;
user chose to stop at the current experience. Software/native evidence confirms
the behavior; orientation after flip, labelled target accuracy, exact latency,
FOV/range/temperature calibration, panel FPS and long-term/hotplug remain gaps.

## Verification

- Debug and Release CTest **15/15**; final mainline checkout rebuilt/tested after
  preserving the uninstalled candidate. Original5 replay cases pass.
- All511 original float32 arrays/655 events from the65.074s successful capture
  window preserve capture/receive/fault timing. Production C results have zero
  mismatches. Latest native68.54s wall replay passes core/role-mode, pause and
  replay checks. This unlabelled recording does not trigger HOLD; synthetic
  cases cover it. No resampling or prefilled focus. Latest real movie is retained.
- Native GSP **27** original role checkpoints plus **10** sleep/wake checkpoints
  and34.05s wall run pass.29 actual PNGs match every RGB565 output pixel to the
  scalar shader/approved2x2 policy, including full closure and aperture checks.
  The sleep movie preserves original screenshot wall-time intervals. Movie
  sampling is dynamic evidence, not a runtime/physical FPS measurement.
-80 full sampled cache/scalar frames, dynamic gaze/pupil and all cache classes;
  all3 allocation failures;43 unchanged full480 reference frames; ASan/UBSan
  passes. Existing ptrace limitation keeps leak sanitizer off; explicit free
  counts run. Source sprite/provenance builds remain read-only.
- Actual firmware doctor/build passes pinned ESP-IDF7b9cc1a for ESP32-S31;
  app1,993,584B fits unchanged ota_0. One retained-factory capacity warning
  remains. No fullclean/dependency upgrade. Logs, exact manifest and install
  result are in evidence/sleep-performance/.
- A missing-key typo in the new budget reporter was fixed and rerun. Earlier
  screenshot ack/commit synchronization and old FFmpeg option failures are
  retained with successful reproductions; none is rewritten as a pass.

## Start / restore / review

`python3 tools/preview.py --sample-step 2 --flip-x --flip-y` starts native GSP.
Use `python3 tools/control.py case sleep` then `play` for the new synthetic
scenario, or `case live` for the complete real window. Host controls and build/
verify commands: README; exact role/cache details: SLEEP_RENDER.md.

Installed bundle: `evidence/sleep-performance/installed/dragon-sleep.irisfw`.
Exact prior flipped240: `evidence/orientation/installed/dragon240-flipped.irisfw`.
Prior240 and480 plus original diagnostic bundles remain retained. Full known
local BIN/ELF/map/config/resource backups are in firmware-local/ (excluded from
review ZIP); no device readback/full-flash backup claim. Restore through the
same official command in DEVICE_DRAGON.md, selecting the intended bundle and
exact Device ID; never combine --bundle with --project. No restore at handoff.

Uninstalled experimental work is preserved separately on local branch
`wip/dragon-packed-color`, **a6a0fb1**, explicitly WIP. It has Host15/15 but no
IDF build/install/device speed measurement. Current mainline/firmware do not
contain it. Its patch and exploratory compiler/Host logs are labelled under
packed/; concurrent exploratory timings are not controlled device comparisons.

`python3 tools/package_review.py` creates the clean-commit ZIP/hash under review/:
source, dependencies/provenance, full original temperature input, actual outputs,
latest native movie and installed/restore bundles. Excludes .git, build/cache,
retrievable dependency copies and full local ELF/config backups. Final delivery
commit may include documentation/evidence tools beyond installed sourcef8845c5.
