# Review response — phase 2

Baseline: `60d57542e4f044392160a91c47ea11841dbf9e1e`. Input ZIP and all 51 supplied file hashes are retained in `evidence/phase2/input-provenance.json`; full external review input stays ignored under `review-inputs/`.

## Core/replay fixes (first commit)

- R1: `peek_submit` and `peek_fault` now apply aging after event processing in the production core. STALE takes precedence over INVALID when a previously valid capture has reached `stale_ms`; if no valid capture has ever existed, a fault is INVALID. A delayed accepted capture may update the last-valid sample but cannot expose a target already beyond `hold_ms`. Same-time tick is idempotent. Defaults are unchanged. `test_event_aging` pins delayed frames at capture 0/125/250 and receive 600/725/850, and invalid/fault/future-frame events at expiry. `data/aging.peek` goes through direct CLI, `peek_replay_until` and the real native pump for equivalence checks.
- R2: unsigned fields are parsed as complete decimal tokens with explicit `UINT64_MAX` / 0..1 overflow checks, rejecting signs, overflow and suffixes, preserving line-number diagnostics. Temperature tokens also require a delimiter. Original five datasets still pass and remain deterministic.
- GSP evidence gap: `draw` explicitly invalidates the native canvas without advancing logical time. The GSP test requests five redraws and requires `draws` to increase at least five while the full detection result remains unchanged. The image checker uses only five retained key PNGs and compares the actual cross center with the C centroid (within one display pixel), so it works from the review archive without movie intermediates.
- Mailbox policy: retain the existing latest-only low-latency queue. A failure can be overwritten by a later success before the consumer sees it; therefore **not every individual acquisition error is guaranteed to be visible**. A consumed error immediately invalidates the detector; sustained absence always ages it. No error-latching message framework is added for this role. The device never resubmits retained temperatures on failure.

The role stage will address R3/R4 with distinct observation-held/stationary semantics and sample-time decisions, R5 with actual array-to-C-to-role replay, and R6 with real native closed-eye/cropping pixels, rather than copying the Gemini defects.

## Shared role / native dragon (second commit)

- R3/R4: `dragon.c` uses only adjacent fresh capture timestamps for speed and stillness. Held breaks quiet evidence once, does not force HOLD, and repeated draws cannot create observations. A fixed300ms quiet-evidence deadline also handles a stream that stops entirely. Production8Hz tests compare decisions at30/60/120Hz; the300/301ms boundary is pinned.
- R5: `data/dragon.peek` and `idle.peek` provide actual Celsius arrays. Native replay calls production detection and shared behavior before painting; no Gemini approximated replay was imported. Original recorded timings/provenance remain unchanged.
- R6: complete blink explicitly hides eye content. Actual GSP closed/extreme/reopen pixels, full-frame C raster parity and an independently sampled Bézier aperture check establish closure/cropping. The idle observation lasts61.07 real seconds; the live full target flow lasts30.51 seconds. Movies are live API samples encoded8fps, with separate real-time metrics.
- New lifetime coverage: actual UI test now exercises eye registration failure, retained renderer on failed stop and release after successful detach; device failure release remains after successful flush. Firmware provides a diagnostic startup Kconfig option.
- ~30Hz was a goal, not achieved: native callback throughput is about14.1–14.5Hz during capture. The attempted tested dirty union did not materially improve this bridge's full-surface draw behavior. Retained images match the full raster exactly; performance remains an explicit limitation.
