# Device rendering and acceptance

The real-device target is MAC `30:ed:a0:f4:52:a0`. Device measurements are independent of Host30Hz, which remains unmet and is not investigated in this continuation.

The first dragon build `d27bc7f` rendered about1.66 non-idle GSP frames/s, with tiled Canvas callbacks about17.64/s; average full-frame raster about557ms plus32ms submit. Its detector incorrectly processed only1.66 samples/s because input was behind the latest-only render mailbox. The corrected acquisition-side owner in `9389137` restores about7.84 accepted samples/s (sequence equals accepted count at every observed snapshot), without detector/role parameter changes. It deliberately does not claim to fix drawing throughput.

After that corrected install the user reported: “太卡太卡了。看不出来”. The120s physical observation captured NOTICE/TRACKING/HOLD/LEAVE and changing sensor coordinates, but the user could not judge visual follow/direction. Do **not** describe that run as accepted. No IDLE was captured after leaving in that particular unlabelled scene; persistent other hot sources are not excluded.

The user suggested consulting sibling Echoy. Its performance work at5c9ae92f showed analogous invisible-geometry/repeated-work costs and exact-pixel checks. Only read-only investigation occurred; no code/dependency/configuration copied. MIT provenance is in THIRD_PARTY and `render-cost-notes.json`.

The Peek renderer's highlighter evaluated four software64-bit ellipse divisions across the entire eye even outside the small highlight's support. Changes use conservative exact support bounds; uint32 numerators are proven below2^32; sphere normalization cancels common scale factors; texture normalization products remain within signed32-bit iris bounds. Circle-highlight scaling uses an exact quotient/remainder decomposition. Zero/full-alpha and integer-coordinate texture cases return the exact old value. No fast-math, texture/geometry/color reduction, renderer downsampling, dependency change or changed detection threshold.

Verification:

- All230400 screen coordinates ×3 channel inputs compare actual production highlights against the retained original expression, plus alpha endpoints and exact normalization.
-43 full-frame poses (seeded random, extreme, open/closed) contain9,907,200 identical RGB565 pixels versus the pre-optimization executable. Hashes/poses are retained;19 prior actual GSP frames also match the new full raster and independent aperture mask.
- Debug/Release CTest10/10 includes the slow-render ownership and exact arithmetic checks. Complete655-event/511-array recorded replay remains unchanged. Final native dynamic replay is retained separately.
- Target relocation sites for `__divdi3` fall from6 to1. This is static code inspection, not a runtime operation count or a measured speedup.

Final installed source/ELF, physical timing/RAM and remaining acceptance gaps are recorded in HANDOFF and `evidence/device-dragon/` after actual installation. GSP engine-render rates, tiled draw callbacks and physical screen FPS remain different quantities. Neither movie encoding nor a callback counter proves panel-visible FPS.

## Fixed-pixel cache follow-up

The first exact-arithmetic install (`6e968b1`) reached only about2.33 GSP rendered
frames/s; it remains an insufficient result, not accepted smoothness. The user
requested investigating Echoy, whose invariant/raster reuse technique is also
applicable here.

The next renderer allocates an immutable fixed-pixel table containing sphere
normals/light/vignette and exact terminal body/open-hood RGB565 values. Device
allocation uses `MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT` explicitly and never falls back
to internal RAM. Renderer creation propagates either allocation failure. It
allocates no buffers during draw. Conservative exact geometry predicates reuse
terminal background colors only where no eye/lip/shadow/stroke contributes;
all other pixels retain the original compositing order. Dynamic gaze, pupil,
lid contours, blinks and texture sampling are not quantized or downsampled.
The final remaining iris64-bit division is replaced by an exact reciprocal
estimate bounded low by at most1 and a single exact correction.

The table is3,225,600 bytes on the target; renderer workspace + table are
3,237,912 bytes. This is an explicit additional PSRAM cost, replacing repeated
calculations. The observed pre-cache role firmware had about13.2MB free PSRAM;
final actual free/minimum values must be measured after installation. Static
budget totals do not replace that measurement.

All43 retained old full frames still match byte for byte. An additional32-pose
cached-vs-uncached full-frame regression verifies both allocations, cleanup and
cache immutability. Host Debug/Release now have11 tests. Native/runtime results
are recorded separately before declaring this follow-up accepted.

Cache lifetime also passes ASan+UBSan with leak checking disabled because of the
retained environment's ptrace limitation; explicit allocation counters cover
both failure points and matching frees. The previous final6e968b1 low-noise
client remained in ep_poll after its child build completed and was interrupted
only after its exact PID/cwd/no-children state was verified. The independent
standalone cache low-noise build succeeded; original failure/result and
`build-process-note.json` remain retained. No device or shared process was
stopped to resolve this local build client.

## Owner placement and compiler boundary

The cache-only install (`e89cf73`) measured about2.665 engine frames/s and7.854
accepted samples/s, with9,919,632 bytes free PSRAM. It is still visibly slow;
cache-only performance is not declared accepted.

Draw and engine timers are elapsed wall times, including preemption; they do
not isolate shader CPU usage. The pinned SDK enables two HP cores and may make
floating-point tasks core-affine. Baseline core placement was not recorded,
so no same-core root-cause claim is made from those timings. Application startup
now observes GSP's first completed timer callback, waits at most1000ms for its
actual core, and creates the acquisition/detector/role task on the other core.
Unknown core or task creation failure fails initialization and follows the
existing detach/flush cleanup; single-core fallback remains the old path.
Read-only RPC records both actual core IDs for verification. Host fixtures
exercise both core selections and bounded unknown-core failure.

The target object also showed an out-of-line12-byte color result for palette
sampling. The shared sampler is explicitly inlined for GCC-compatible compilers
with a standard-inline fallback. This preserves the same arithmetic/pixels and
lets caller constants remove redundant coordinate and structure-return work.
No SDK/library code or global RTOS scheduling policy is changed. Final device
measurements cover both changes together and must not be attributed to either
one alone.

## Approved240 detail and physical mount

The user accepted2x2 replication after rejecting the previous frame rate.
Shared C/native/device startup selects sample_step2 while the additive renderer
API still defaults to the retained480 reference. No further detail reduction.
See SAMPLING240.md for exact pixels/odd tile edges and policy evidence.
Final source ba98632 with both user-requested gaze flips measured7.546 engine
frames/s,77.684 tiled Canvas callbacks/s and7.829 accepted samples/s over24.78s.
Mean engine121.86ms, raster90.98ms, submit30.76ms; GSP1/sensor0. The preceding
480 source49a7c57 measured2.693 engine frames/s in a different scene.
Internal free237,955B/min196,784B; PSRAM free/min9,918,228B before screenshots.
Panel-visible FPS and post-flip physical acceptance remain unmeasured/pending.
No30Hz or smoothness-pass claim. Exact runtime and recovery evidence: HANDOFF.

## Sleep/geometry-cache stopping point

Sourcef8845c5 adds the requested10s IDLE/450ms close/150ms wake and exact240
prepared-geometry reuse. Active-open device counters classify the completed
previous generation, excluding sleeping/partial blink frames. Host fixture
checks the transition accounting.94.74s observation measured10.336 active-open
engine frames/s over898 frames/86.882s, including misses; raster53.19ms and
submit31.32ms per active-open frame. Global engine9.975Hz, tiled callbacks
103.072Hz, samples7.843Hz; no panel-visible FPS claim. Cache-ready states53/87;
TRACKING/HOLD geometry changes reduce reuse. Internal free237,891B/min196,720B;
PSRAM free/min9,211,008B before screenshots. User said “可以，就先这样吧”;
stop at this version.15Hz remains unmet. Uninstalled packed-color/O3 WIPa6a0fb1
is separate, with no hardware speed claim. Exact current source/ELF/recovery and
physical sleep/wake observation gap: HANDOFF.
