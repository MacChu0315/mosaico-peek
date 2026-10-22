# Selected dragon sclera C

The user supplied dragon-sclera-C-handoff-v1.zip and authorized integration.
Only the original dragon's procedural sclera branch is replaced by its selected
dark-green fiber texture. Iris, pupil, skin, eyelids, geometry, lighting, gloss,
mapping, controller and other characters remain unchanged. Current runtime
mounting flips remain true/true; IMU calibration remains(-ax,+ay).

## Retained source and sampling

`assets/dragon-sclera-c/` preserves all76 supplied files, including the75-entry
checksum list,480 RGB submission,1254 editable PSD/ORA/layers, generation prompt,
provenance and offline reference evidence. Input ZIP SHA256:
6ee74e0e373e7748aef0634128a7ba5bc2fa532abd9a16e23b4c4f68184ff782.
Submission SHA256:
5775c62ce834c1e3573148241f2589e434d0226a9cea4d88ad78348d2c4c9887.
Existing `assets/dragon/` sources/provenance stay intact. The separate adaptation
recipe pins the selected submission and documents scope.

`tools/bake_dragon_sclera.py` verifies immutable inputs and emits build-local
RGB888 bytes, without palette reduction, resizing or runtime PNG decoding.
Sampling exactly matches the art reference: Q15 local sphere coordinates become
Q16 texture coordinates u=240*65536+lx*466,v=240*65536+ly*466, clamped0..479.
Four raw RGB texels interpolate with the original integer blend convention.
Only the existing radial region outside the iris calls this sampler. All
subsequent lighting, eyelid shadow/gloss and RGB565 packing remain shared C.

No new mutable cache or allocation; existing prepared/fixed-cache paths use the
same sampler. Full480 scalar rendering remains the reference; the installed
dragon's previously approved step2 remains unchanged. Other artwork stays480.

## Resources and lifecycle

PNG382300B; RGB888691200B additional app RODATA. Existing assets declare651780B,
giving1342980B total declared dragon resources. The now-unused legacy2048B sine
table remains in the immutable old generated include and can be discarded by
the optimized linker; the final ELF report is authoritative. No new per-instance
heap is needed, but existing XIP/RODATA-to-PSRAM configuration adds residency
for the new constant texture. Do not describe this as zero PSRAM cost.

Original scalar/fixed/prepared cache tests, tiled draws, allocation failures and
pose invalidation continue to apply. Display still reads source snapshots;
neither the renderer nor the new asset generator submits temperature samples.

## Validation and reproduction

```sh
cmake -S . -B build-host && cmake --build build-host -j 4
ctest --test-dir build-host --output-on-failure
python3 tools/preview.py --view dragon --flip-x --flip-y
PEEK_EYE_THEMES=dragon PEEK_EVIDENCE_DIR=evidence/dragon-sclera/native-motion python3 tests/test_eye_gsp.py
python3 tools/control.py case live
python3 tools/control.py play
python3 tools/build_idf.py
```

Before implementation, the supplied-reference regression failed on center;
after implementation all11 poses match exactly, no changes lie outside the
supplied sclera masks, and the fully closed frame is unchanged. Debug/Release
33/33 pass. Generator checks cover deterministic/read-only outputs, corrupt
source rejection and disallowed output paths. Original5 replay cases and511
recorded arrays/655 events pass. Native/device checks and resource measurements
belong in `evidence/dragon-sclera/`; see HANDOFF for current installation status.
Offline supplied movies are not native GSP/device evidence or measured FPS.

The old procedural art exporter now refuses to generate a misleading legacy
handoff from the new renderer. Its existing v1 ZIP remains unchanged and valid.
