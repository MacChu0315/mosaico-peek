# mosaico-peek

- Phase 2 adds only the approved single dragon eye to the shared thermal/GSP/replay foundation; Gemini is motion reference only. Hardware writes require explicit task authorization.
- `src/peek.c` is the single Host/ESP-IDF detector implementation. Rendering must never submit samples. Sensor reads create samples only on successful **complete** frames; consumed errors use `peek_fault`. The latest-only mailbox may overwrite transient errors; do not claim every failure is delivered. Core event exits must already be aged and same-time tick idempotent.
- Keep injected monotonic time, sequence identity and replay epoch semantics in `README.md`. Reset all three on replay/source restart. Synthetic and recorded data must remain labelled and traceable.
- Use the pinned dependencies in `dependencies.json`, the project lock and the official Hello World application/retained Vibe Mode contract. Do not upgrade or edit adjacent checkouts. `deps/`, build output and `.run/` are local only.
- Tests: `cmake -S . -B build-host && cmake --build build-host && ctest --test-dir build-host --output-on-failure`; `python3 tests/test_replay.py`; with preview running, `python3 tests/test_gsp.py`.
- Project status/handoff: `docs/HANDOFF.md`. GSP results and hardware validation must be reported separately.
