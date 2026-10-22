# Executed checks

- cmake -S . -B build-host; cmake --build build-host -j4; ctest --test-dir build-host --output-on-failure:33/33.
- Release configure/build/ctest:33/33.
- python3 tests/test_dragon_sclera.py:11 pixel-exact supplied frames; no changes outside masks; closed unchanged;75 checksums.
- python3 tests/test_dragon_sclera_build.py:read-only deterministic output, integrity and build-directory guards.
- python3 tests/test_replay.py:5 cases; python3 tests/test_real_replay.py:511 arrays/655 events.
- Native tests/test_orientation_gsp.py:40 exact images across four orientations/artworks.
- PEEK_EYE_THEMES=dragon tests/test_eye_gsp.py:22 exact images and two real-time movies, all behavior/fault/sleep/pause/replay checks.
- tests/test_eye_recorded_gsp.py:four artwork replays,511 arrays/655 events, six live switches and68.4s real-time movie.
- python3 tools/build_idf.py:pinned SDK build passes, actual1.0.12 config verified.
- tools/report_budget.py,report_eye_budget.py,report_firmware.py:actual target sizes and linked resource/config reports.
- Official bundle inspection,preflight,System Update and post-boot ELF verification:pass first attempt.
- tools/benchmark_device_eye.py --seconds 55 --expected-version 1.0.12-peek-sclera:424 fresh samples,0 faults; separate0/270deg frame counters.
- tools/verify_dragon_sclera_device.py:stable actual270deg closed RGB565 pixels exactly match C.

The initial new test failed against old code as intended. Initial implementation
build caught an unused sine function (removed); the test initially used a wrong
mask filename suffix (fixed). Supplied CSV CRLF bytes are preserved via exact
.gitattributes entries, not rewritten to silence whitespace checks. SDK component
include warnings and retained factory-capacity warning remain in raw build log;
normal app fits the authorized ota_0 System Update layout. No native movie rate
is asserted as physical FPS. Original closed/reference scene is preserved.
