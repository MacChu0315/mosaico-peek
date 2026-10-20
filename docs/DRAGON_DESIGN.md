# Approved dragon integration

The only visual baseline is the supplied `approved-dragon`: a single large yellow/green/gold iris, black slit pupil, purple-black scaled hide, heavy textured eyelids. Input/reference hashes are retained; Gemini is read-only motion organization reference, never runtime data or a replacement renderer.

Pipeline: new complete Celsius array → production `peek.c` → aged result → `dragon.c` observation/behavior/pose → prepared `dragon_render.c` → native GSP RGB565 Canvas. The original diagnosis scene remains a separate startup mode. The dragon screen contains only artwork; Host controls/status remain outside the 480×480 image.

`dragon_update` consumes observations identified by the accepted sample count and capture time. Speed is sensor-pixel displacement divided by adjacent capture-time delta; HOLD requires at least 900 ms of fresh stationary observations below 0.8 sensor pixel/s, and gaps over 300 ms break this evidence. `observation_held` is reported independently, breaks stationary evidence, and never manufactures an observation. State deadlines and seeded blink scheduling use the same injected clock; drawing never calls update or detection.

A new target triggers one 320 ms NOTICE. Continuous samples do not retrigger it. LEAVE lasts 1200 ms while gaze returns through the same critically damped spring. A target reappearing during LEAVE gets one light NOTICE, preserving current gaze and spring velocity; replay alone resets all state and the seed. WAITING/INVALID/STALE never supply old coordinates to the role. The low-latency latest-only device mailbox policy remains explicit in REVIEW_RESPONSE.md.

Sensor coordinates refer to pixel centers: normalize as `2*(x+0.5)/32-1`, `2*(y+0.5)/24-1`, so `(15.5,11.5)` is center and the outer edges `[-0.5,31.5]×[-0.5,23.5]` span [-1,1]. A centralized rotation/flip mapping precedes bounded gaze amplitudes 0.78/0.58. Native right/down is positive; physical left/right and mounting calibration remain unverified.

Rendering uses the approved source textures with actual quantization/asset costs reported separately from the 1 MiB GSP resource partition. The original offline Node renderer is a reference, not the runtime or a performance claim. A small precomputed sphere/pupil lookup and per-pose Bézier boundaries replace heavy per-pixel transcendental functions. Prepare freezes a pose; partitioned draw reads it. Full closure explicitly hides every iris/pupil pixel at blink=1, including extreme gaze.

Implementation/check order: first independently commit core/replay repairs and native redraw proof; then build/test the shared role and renderer, integrate both Host and ESP-IDF GSP sources, run controlled replay and at least 60 seconds real-time native idle observation, capture actual closed/extreme/reopen pixels, build firmware, measure native time/memory and encoded `ui_apps.bin`, package the two-stage review. No firmware writes or adjacent changes are authorized.
