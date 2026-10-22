# Three additional eye UIs — native integration

Mechanical was replaced by the user-selected C globe/central shutter on2026-10-22.
See [current mechanical contract](MECHANICAL_C.md); the original mechanical
fixed-lid/neutral details below describe the prior version. Owl/sea are unchanged.

Appended `night_owl`, `deep_sea`, `mechanical`; `dragon` and `diagnostic` remain.
Started from reviewed9a25653 on an independent local branch. The initial review
was followed by a user-authorized installation of the exact reviewed artifact;
see [device evidence](../evidence/eye-ui/device-install/README.md). No remote
writes, shared SDK changes or detector/dragon-art changes.

## Start / select / replay

```sh
cmake -S . -B build-host
cmake --build build-host -j4
ctest --test-dir build-host --output-on-failure
python3 tools/preview.py --view night_owl
python3 tools/control.py view deep_sea
python3 tools/control.py view mechanical
python3 tools/control.py view dragon
python3 tools/control.py view diagnostic
python3 tools/control.py case dragon
python3 tools/control.py play
python3 tools/control.py pause
python3 tools/control.py replay
python3 tools/control.py case sleep
python3 tools/control.py play
python3 tools/control.py case live
python3 tools/control.py play
```

One preview per working directory. Selection controls are the external Host CLI,
not embedded in the480 artwork. `--sample-step` still controls only dragon;
new eyes always render all480×480 output pixels. Both flips are now disabled after the user confirmed both axes were reversed;
arrays and detector coordinates stay unmodified.
Selecting a character/diagnostic does not reset the input epoch, controller,
phase, seed or mapping. Replay/case selection resets all source/model time and
identity together, preserving selection and mapping. Pause freezes logical time.
No browser animation is used by the native preview.

Firmware uses the same `eye_pack.c`, `peek_ui.c`, `dragon.c`, `peek.c`.
`python3 tools/build_idf.py` builds isolated `build/sdkconfig.eye-motion`, version
`1.0.7-peek-mechanical`, default dragon, `CONFIG_PEEK_CHARACTER=0`. Values1/2/3 select
night owl/deep sea/mechanical at startup using Kconfig. The baseline
`sdkconfig.dragon240-sleep` is separate. The wrapper asserts the default-dragon
review configuration; a deliberately configured alternative needs its own
explicit config assertion. All three renderers/resources are linked in this
review firmware. Installed1.0.4 adds [touch/AI switching](CHARACTER_SWITCHING.md).
The user reports slow new-art rendering; actual mechanical timing and the installed
1.0.5 optimization are recorded in [performance work](EYE_PERFORMANCE.md).
No physical panel FPS or sustained multi-theme memory-peak claim is made.

## Retained sources / reproducibility

`assets/eye-pack/` retains the original PNGs, closed-eye AI design sources,
processed transparent layers, original manifest, provenance/license statements,
JS model/renderer/offline reference and rebuild tools byte-for-byte. Source ZIP
SHA256 is in `evidence/eye-ui/input-archive.sha256`. The original CHECKSUMS file
is unchanged. Its `evidence/` entries refer to the supplied Canvas-only evidence,
kept locally in ignored `review-inputs/eye-ui-v1/evidence/`; these bulky,
reproducible reference captures are excluded from the production source subset
and review archive. New native evidence is separately under `evidence/eye-ui/`.
Supplied source tools retain their original dependency instructions; they are
reference tools, not the production build. Main native drawing requires only
existing C tools, Pillow10.4.0 and zlib1.2.13. Verification used Python3.10,
NumPy2.1.1, CMake3.22.1, Host GCC11.4.0 and FFmpeg4.4.2. Target/toolchain
revisions remain exactly pinned in dependencies.json and dependencies.lock. The pack's browser reference can
still be opened at `assets/eye-pack/preview/index.html` without installation.

Ordinary CMake generation validates every retained non-evidence CHECKSUMS entry,
decodes PNGs without resizing or palette reduction, and writes zlib-compressed
RGBA8888 streams only under each build's `eye-generated/`. No source-update path
exists in this adapter. Original dragon assets and generator are unchanged.

```sh
python3 tools/bake_eye_pack.py --output build-host/eye-generated/eye_pack.inc
python3 tests/test_eye_asset_build.py
python3 tests/test_eye_pixels.py
```

Compressed sources are byte-lossless. Host uses the existing system zlib;
ESP32-S31 uses the pinned SDK's ROM `tinfl_decompress` with an explicit PSRAM
workspace. No new target library, dependency upgrade or shared checkout edit.
Missing/corrupt input and allocation/decode errors propagate. Draw never decodes,
allocates, changes pose or submits a detector observation.

## Geometry / layers / motion

480×480 black canvas; origin top-left, +x right, +y down. PNG alpha is straight.
Draw sphere-rotated eye → weighted premultiplied adjacent lids → fixed frame.
RGB565 rounding occurs only at output; no palette or downsampling. Bilinear
sampling interpolates premultiplied colors/alpha; lids mix once before
source-over, avoiding the dark overlap of two independent source-over draws.

| Theme | Derived eye | Each original lid / origin | Center | Pure-axis center travel |
| --- | --- | --- | --- | --- |
| night_owl |480×480 at(0,0)|489×272 /(-7,113)|(240,250)|±120 / ±80px|
| deep_sea |480×480 at(0,0)|507×269 /(-13,123)|(240,250)|±120 / ±80px|
| mechanical |480×480 at(0,0)|485×271 /(1,109)|(240,245)|±120 / ±80px|

Frame is480×480 at(0,0), always last. Original negative lid origins remain;
clip only at output. The radius233 globe uses inverse yaw/pitch rotation and
bilinear texture sampling. Newly exposed hidden regions are derived from visible
iris sectors at matching radius; original visible neutral pixels are restored
exactly. This intentional motion extension is separate from immutable supplied
PNG sources. [Recipe, limits and exact-neutral tests](EYE_MOTION.md).

Production `dragon.c` remains the shared behavior controller for all characters.
The existing pose's bounded gaze ±0.78/±0.58 is normalized to each theme's full
sphere angle; `blink` in[0,1] selects/interpolates lid00..08. Other dragon
shader parameters (`squint`, pupil width, tension) do not deform the new bitmap
art. This is an explicit native adaptation of the reference, not a claim to port
its separate JS behavior model or re-use dragon's procedural shapes.

All time is injected monotonic **milliseconds**. Confirmed production targets
only: candidate/fault/duplicate/redraw never creates NOTICE or wake. NOTICE320ms,
fresh quiet observations900ms below0.8 sensor pixel/s establish HOLD; held data
is not stillness. LEAVE returns over1200ms. Each IDLE entry calmly animates10s,
closes450ms and stays asleep. An acquired hot target opens150ms. Ordinary blinks
140ms close/40ms shut/230ms open, seeded irregular repeats while awake. Movement,
stillness, leaving and unavailable input use the unchanged detector's continuity,
hold and stale semantics (README). Loops use the existing seed/time rules;
there is no second character detector, timer task or sensor coordinate flip.
Selecting a different artwork shows the current phase immediately; hidden artwork
is not rendered. This shares the current global behavior while only the active artwork keeps its large renderer buffers. Dragon↔bitmap
switches release the old renderer before allocating the new one. Diagnostics
retain the last renderer. Allocation failures return a sticky display error;
they do not promise a working old-picture rollback.

## Verification / evidence

Commands (native checks require the running preview):

```sh
python3 tests/test_replay.py
python3 tests/test_real_replay.py
python3 tests/test_eye_gsp.py
python3 tests/test_eye_recorded_gsp.py
python3 tools/benchmark_eye_ui.py
PEEK_EVIDENCE_DIR=evidence/eye-ui/baseline-native python3 tests/test_gsp.py
PEEK_EVIDENCE_DIR=evidence/eye-ui/dragon-regression python3 tests/test_dragon_gsp.py --skip-live
python3 tools/build_idf.py
python3 tools/report_eye_budget.py
python3 tools/package_review.py --eye-ui
```

See `evidence/eye-ui/README.md` for actual run results. Tests include full480
independent float64 PNG composition vs production float32 C, odd tile origins,
padded strides, clipping/finite/range checks, read-only build/source hashes and
view lifecycle. Independent float rounding is bounded to one RGB565 channel
code at rounding boundaries; native captures match the C raster in every565
channel. Temperature arrays, not precomputed centroids, drive all acceptance.

Six synthetic native movies separately cover movement/HOLD/loss/faults and
sleep/wake for each theme. A separate recorded-scene movie switches views during
all511 real arrays/655 events. All movies use original screenshot wall intervals;
ffprobe duration is checked. Sampling may miss a short150ms wake; controlled
native checkpoints cover it. No video encoding rate is a physical FPS claim.

`resource-budget.json` contains exact target ABI allocations, image/ELF/map
hashes and effective memory selectors. `host-performance.md` separates active
and sleeping normal preview callbacks, equivalent full Canvas pixels and Host
GSP committed frames. Device1.0.5 executed ROM decode and all three new views; mechanical timing is
recorded in EYE_PERFORMANCE.md. Heap peaks/largest block, PSRAM bandwidth and
physical panel FPS remain unmeasured. Current motion/physical-direction
acceptance is tracked separately in EYE_MOTION.md.
Existing factory-capacity warning is retained: the normal app belongs in ota_0;
partition layout is unchanged. No additional visual reduction is authorized here.
