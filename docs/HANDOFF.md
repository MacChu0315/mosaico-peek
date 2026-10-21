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
