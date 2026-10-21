# Full480 bitmap renderer performance

The user reported severe stutter in all three added characters after installing
1.0.4-peek-switch. On the physical device, mechanical measured2.0 complete GSP
engine frames/s over35.04s, with452.34ms raster,34.32ms submission per frame and
4.93ms preparation average. Acquisition remained7.82 samples/s, zero faults.
So the first optimization targets raster work, not detector deadlines or rates.

Read-only local skills were confirmed identical to remote HEAD
c5ab8a45fdbd41cb841caef1331e11af2f7d197c of
https://github.com/MacChu0315/mosaico-dev-skills . Applied:
`.agents/skills/mosaico-runtime-performance/SKILL.md`, its
`references/rendering.md`, and `mosaico-gsp-parity/SKILL.md`.
No skill checkout, SDK/BSP dependency, thermal settings or device layout changed.

## Exact-output optimization

- Convert opaque fixed foreground pixels to final RGB565 once after decoding,
  within the existing frame allocation. Preserve alpha and partial-alpha RGBA.
- Prepare480 exact X and480 exact Y source coordinates per frame. Keep each
  coordinate's original float subtraction/rounding; one shared fractional
  coordinate would be numerically different near larger integer positions.
- Sample fully opaque eye neighbors with the same float products and addition
  order, avoiding redundant alpha multiplication and loop/stack work. Retain
  the original scalar sampler for boundary/partial-alpha cases.
- Skip transparent eyelids when blink=0 and invisible eye samples beneath fully
  opaque eyelid pixels. Decode only layers actually needed for a weighted blend;
  open and exact integer-lid states do not require an unused next layer.
- Replace per-pixel clamp/floor library calls with the same multiply/divide/add
  expression followed by an unsigned cast. Convex sampling/composition keeps
  channels in0..255 (float roundoff below.001), and rounding remains within the
  5/6-bit range. No fast-math, FMA contraction or changed operation order.

All480 pixels and original source RGBA/alpha/detail remain. No palette,
downsampling, gaze quantization, role timing or detector change. Draw is read-only;
prepare owns mutable maps/decoded layers. Switching re-decodes a fresh foreground,
so the in-place opaque representation cannot be converted twice.

Coordinates add5,760B within the renderer structure; target allocation is counted
by the actual ABI reporter. With current ALWAYSINTERNAL=16384 this small calloc
normally uses internal RAM. Large RGBA storage and ROM inflate workspace remain
explicit PSRAM. No additional large pixel/texture cache or internal fallback.

## Verification

`tests/reference/eye_pack_v104.c` is a byte-identical frozen copy of the renderer
from6eff674, compiled only for Host tests with isolated symbols. Production code
is never linked against it.

- `test_eye_exact`:384 complete480 frames bit-identical across themes, extreme
  and fractional gaze, all integer/intermediate lids, closed/open transitions,
  odd tile origins and padded strides.
- Debug/Release CTest21/21; independent57 PNG composition comparisons pass.
- ASan/UBSan exact-frame and allocation-failure tests pass with leak sanitizer
  disabled under the existing ptrace restriction; explicit ownership counts run.
- Host Release draw CPU for the same384 poses: reference1.838s / optimized0.464s.
  This supports reduced Host work only, not a device performance claim.
- Official native GSP input/pixel regression and exact versioned IDF build are
  retained under evidence/eye-ui/performance/ before installation.

Build candidate1.0.5-peek-fast with `python3 tools/build_idf.py`, using isolated
sdkconfig.eye-fast. Preserve1.0.4 and1.0.3 bundles. The user's standing same-device
installation permission applies; verify artifact/identity before each update.
Physical before/after measurements must distinguish active-open, closed/static,
Canvas tile callbacks, completed engine frames and physical panel FPS. Different
live hand-played scenes do not support a controlled percentage-speedup claim.
