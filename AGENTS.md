# mosaico-peek

- Phase 1 is the shared thermal detector, native GSP diagnostics and temperature replay. Character UI is deferred. Hardware writes require explicit task authorization.
- `src/peek.c` is the single Host/ESP-IDF detector implementation. Rendering must never submit samples. Sensor reads create samples only on successful **complete** frames; errors use `peek_fault`.
- Keep injected monotonic time, sequence identity and replay epoch semantics in `README.md`. Reset all three on replay/source restart. Synthetic and recorded data must remain labelled and traceable.
- Use the pinned dependencies in `dependencies.json`, the project lock and the official Hello World application/retained Vibe Mode contract. Do not upgrade or edit adjacent checkouts. `deps/`, build output and `.run/` are local only.
- Tests: `cmake -S . -B build-host && cmake --build build-host && ctest --test-dir build-host --output-on-failure`; `python3 tests/test_replay.py`; with preview running, `python3 tests/test_gsp.py`.
- Project status/handoff: `docs/HANDOFF.md`. GSP results and hardware validation must be reported separately.
