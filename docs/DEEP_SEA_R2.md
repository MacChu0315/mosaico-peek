# Approved deep-sea R2 integration

The user accepted the independent R2 appearance and requested a demo update
before revisiting owl. This changes only deep_sea artwork/presentation. Retain
the current owl, approved dragon sclera C, mechanical socket A/centered sleep,
both thermal mounting flips and calibrated IMU orientation.

## Source and native layers

`assets/deep-sea-r2/` retains the approved R2 inputs, processing scripts, recipe,
candidate PNGs and review evidence under a checksum manifest. The separate
`assets/deep-sea-adaptation.json` pins the selected eye surface and timing.
Original R1 and the independent R2 review directory remain unchanged.

The20 encoded layers are480×480 frame/opaque eye plus nine480×240 membrane and
nine480×240 outer-lid sprites, origin(0,128). Sphere center(240,250), radius233,
pure-axis travel120/80px and full480 bilinear rendering remain unchanged.
No rim_restore layer is encoded or rendered. Membrane/lid each select nearest9
frames; order is sphere eye -> membrane -> outer lid -> original fixed frame.

Two existing551616B buffers hold the selected460800B membrane/lid, with distinct
cache keys. Prepare decodes only changed indices; draw allocates/decodes nothing
and mutates no state. Theme selection clears both keys. No extra mutable texture
or geometry allocation is added. The fixed-frame fast path and opaque-lid early
exit remain exact relative to the independent scalar C compositor.

Only fully transparent RGB bytes are normalized to zero in generated deep-sea
streams. Source PNGs, all visible colors and every alpha byte remain unchanged.
This cuts deep-sea compressed resources from5121245B to2594691B, avoiding
2526554B of invisible data. Source checksums and native pixel checks remain
authoritative; no palette reduction, downsampling or new dependency.

## Shared source, separate presentation phases

`eye_layers.h` is a pure reader of the existing source-owned dragon snapshot.
No second detector, mutable scheduler, new timer, threshold or random seed.
Ordinary membrane movement begins at the existing next_blink_ms:100ms cover,
20ms hold,120ms retreat; outer lid stays open. The source's legacy410ms blink
continues unchanged for other views and its counters; deep-sea is visibly open
after240ms, even while the source raw blink remains nonzero.

IDLE still waits10s. Over the existing450ms close, membrane covers during100ms,
then outer lid closes during350ms. Full waking takes150ms: outer lid opens over
97.5ms, then membrane retreats. For interrupted partial closure, the initial
close time is recovered from the source's saved quintic wake_blink; outer-lid
opening duration scales by its initial coverage, and membrane uses the remainder
of150ms. This preserves visible start frames and avoids a spurious97.5ms pause
from numerical noise when an almost-open lid is interrupted. Tests cover all450
integer close times and99/100/101ms mid-wake boundaries.

Display switching, pause, redraw and replay keep source state/time intact. Replay
full-pose equality requires the same injected animation tick schedule: a single
large advance is not the same schedule as many intermediate NOTICE easing ticks.
The actual detector, source controller, acquisition adapter and IMU files remain
byte-identical to the1.0.12 baseline.

## Observability and checks

Host adds render_layers.membrane/lid. Device RPC adds render_membrane/render_lid
and completed membrane/full-membrane frame counters. Existing raw blink and gaze
fields retain their meanings. Completed-frame classification uses the previous
prepared generation and excludes diagnostic/sleep/wake frames from ordinary
membrane counters. A240ms logical pulse does not guarantee every sprite or the
full-coverage stage is physically displayed at the device's measured frame rate.

Executed validation and firmware/install/performance status are in HANDOFF and
`evidence/deep-sea-r2/`. Approved seven static cases match C exactly; randomized
independent scalar C checks include separate membrane/lid parameters. Native
pixel oracles use render_layers, not raw blink. Real thermal recordings continue
through the unchanged detector before artwork presentation.

```sh
cmake -S . -B build-host && cmake --build build-host -j4
ctest --test-dir build-host --output-on-failure
python3 tools/rebuild_deep_sea.py --output build-host/deep-sea-reproduce
python3 tools/preview.py --view deep_sea --flip-x --flip-y
python3 tools/control.py case sleep
python3 tools/control.py play
python3 tools/control.py replay
python3 tools/build_idf.py
```

Standalone art reproduction copies retained scripts/inputs into the requested
new build directory. Never run the retained reconstruction scripts in-place in
assets/. Existing timing/appearance acceptance is distinct from final physical
demo acceptance. Owl reconstruction remains deferred until user confirmation.

## Installed result and observed limit

1.0.13, sourcea5ef0ce, installed successfully on the first official update. User
accepted its appearance, but sometimes cannot see the entire membrane motion.
At270deg,54.94s observation gave431 new samples/0 faults, active-open5.751
complete GSP frames/s. Nine ordinary membrane frames reached the engine, three
at full stage8. The240ms pulse can only occupy1–2 frames at this rate; stage8
has about53ms of logical visibility. The physical panel scan rate is unmeasured.
Do not report every pulse fully presented, or silently stretch the approved
timing. The observation is a performance limitation, not an appearance rejection.

App8731600B, UI94480B; linked bitmap assets6010037B. Explicit bitmap PSRAM
3418224B/internal renderer2004B unchanged; global XIP/RODATA residency grows.
Observed free internal243799B/free PSRAM3025464B, lifetime minima192100B/2471228B.
Preserved1.0.12 restore and exact local ELF/map/config remain separate. See
HANDOFF for final closed-state/device acceptance and review archive status.

Closed-state device follow-up:18.95s at270deg,141 completed frames=7.441Hz,
148 fresh samples,0 faults. Raster90.297ms, submit34.095ms, prepare0.027ms.
Three stable closed readings bracketed a screenshot; all RGB565 pixels match
production C. Final lifetime min PSRAM2467060B. No device restart/errors during
these measurements. User can resume normal operation. Fast-membrane visibility
remains a known frame-rate limitation; no duration change was installed.
