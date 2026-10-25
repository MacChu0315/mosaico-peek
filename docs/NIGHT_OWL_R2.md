> RETIRED2026-10-25: user rejected night owl. This document is historical; current firmware excludes it. See OWL_REMOVAL.md.

# Night owl R2 demo update

The user requested the same R2 optimization for owl after accepting the installed
deep-sea demo. Keep deep-sea, dragon sclera C and mechanical socket A unchanged.
Installed1.0.14-peek-organic; installed identity/physical acceptance are
tracked in HANDOFF.

## Artwork and scope

`assets/night-owl-r2/` is a newly reconstructed package, not recovery of lost v2.
The original circular pupil region9841px and original highlight region1780px
remain exactly equal to the accepted480 source raster. The surrounding iris is
brightness-matched and smoothly joined to the full surface, without an aperture-
shaped patch. A pupil-preserving coordinate warp aligns the two original
catchlights; minimum sampled Jacobian0.4091298878 prevents folding. All recipe
values and scripts are retained, not inferred to be original design parameters.

No returning rim is encoded. Frame and18 membrane/lid PNGs are byte-identical to
R1. Membrane RGB comes only from the independent RGBA material, using the same
0.68 RGB gain and0.50 opacity as the reviewed reconstruction. It is deliberately
translucent; a deployed membrane is not an opaque closed eyelid. The outer lid
provides full closure. Source images remain unchanged/checksummed.

## Runtime

Both organic characters now use the existing dual-layer renderer and the same
pure shared-source timing helper. The only runtime routing extension is allowing
UI character1 as well as2. Ordinary membrane:100ms cover,20ms hold,120ms retreat;
10s IDLE,450ms sleep closure and150ms waking remain. Ordinary outer lids remain
open; sleep closes them after the membrane. No detector, source clock, seed,
mapping, IMU calibration, gesture or renderer arithmetic change.

Frame/eye are480×480, membrane/lid480×240@(0,128). Sphere center(240,250),R233,
120/80px pure-axis travel and full480 detail remain. Existing two551616B layer
buffers are reused; zero-alpha RGB normalization only affects build streams,
not source files or visible RGBA. No extra mutable texture buffer or dependency.
Membrane counters now cover whichever organic view was actually rendered;
diagnostic/sleep/wake frames remain excluded from ordinary membrane counters.

## Verification and use

- Host37/37, including pupil/highlight preservation and seven candidate images
  exactly matching production C. Release suite and actual results retained in
  evidence/night-owl-r2/verification.
- Deep-sea/mechanical31 compressed streams unchanged; core detector/controller,
  original dragon renderer, source adapter and IMU unchanged.
- Native17 phase checkpoints,64 orientation images,16 pointer checks,22 motion/
  sleep checks, two wall-time native videos;511 recorded arrays/655 events and
  six live view switches pass.44 other-artwork native images match1.0.13.
- Independent read-only review found no critical/important defect. Remaining
  appearance/texture joins require physical user acceptance; numerical tests do
  not grant visual approval.

```sh
python3 tools/rebuild_deep_sea.py --theme night_owl --output build-host/night-owl-reproduce
python3 tools/preview.py --view night_owl --flip-x --flip-y
python3 tools/control.py case sleep
python3 tools/control.py play
python3 tools/control.py replay
python3 tools/build_idf.py
```

Run retained art scripts only after copying into a build directory, never in
assets/. Frame-rate limits from deep-sea still apply:240ms does not guarantee
all intermediate or maximum-coverage frames appear at low device FPS. This
update does not silently lengthen the approved timing to mask that limitation.

## Installation/resource checkpoint

Official1.0.14 installed on first attempt. Source735fbe7 and ELF391287d2...
match device identity. App9509712B, UI94480B unchanged, linked bitmap resources
6788133B. Existing renderer buffers3418224B PSRAM and2004B internal struct stay
unchanged; XIP/RODATA residency increases. Initial dragon free internal233271B,
free PSRAM1693128B. Physical owl review/performance are pending in HANDOFF.

The review ZIP is a compact delta over30a2d64/installed1.0.13: changed source,
new owl materials and current evidence. It requires the baseline checkout and
is not a standalone clone. Existing unchanged artwork/SDK are not duplicated.
