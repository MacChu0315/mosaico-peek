# Executed validation

- Host/Release CMake build and ctest:36/36 each, including450 interrupted closes and99/100/101ms mid-wake regressions.
- tests/test_deep_sea_r2.py:seven accepted static cases bit-exact; tests/test_eye_exact:384 full frames/scalar and tile parity, independent membrane/lid phases.
- tests/test_eye_pixels.py:57 independent PNG comparisons; tests/test_eye_asset_build.py:source hashes/mtime unchanged, repeat output identical.
- tools/rebuild_deep_sea.py:21 approved PNGs reproduce byte-identically in isolated build directory.
- tests/test_replay.py:five production-C scenarios. tests/test_real_replay.py:511 recorded arrays/655 events exact.
- Native test_deep_sea_gsp.py:17 exact layer-time/pixel checks; paused redraw/theme switching and same-tick replay preserve source state.
- Native test_orientation_gsp.py:52 exact images across all orientations; test_switch_gsp.py:16 pointer checks/four captures.
- Native test_eye_gsp.py with deep_sea:22 pixel checks,two full wall-time movies; test_eye_recorded_gsp.py:four role replays and six live switches,511 arrays/655 events.
- Pinned tools/build_idf.py:1.0.13 actual config passes. Resource reports inspect final target ABI/ELF/map.
- Official bundle verification/System Update/post-boot ELF:pass first attempt. No ROM recover or remote writes.
- tools/benchmark_device_eye.py:55s active and20s closed observation with frames/callbacks separated; no screenshot inside measurement windows.
- tools/verify_deep_sea_device.py:actual270deg closed framebuffer bit-exact to production C.

Resolved failures retained separately: pre-integration neutral mismatch; mid-wake
boundary found by reviewer; UI test fixture clock mismatch; replay comparison
using unequal tick schedules; clean preview shutdown during the first sleep
movie. Bounded re-run completed both native movies plus recorded replay. Existing
SDK include-dependency/factory-capacity warnings are in raw build log; app fits
unchanged ota_0. No physical panel-FPS claim, no guarantee every240ms pulse has
all visible stages at the observed5.75Hz. No silent timing extension.
