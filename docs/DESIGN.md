# Phase 1 design and review boundary

Scope: one ESP-Mosaico (ESP32-S31, 480×480), one MLX90640. Shared significant-hot-target detection only. Roles and final character artwork are deferred.

Data flow: BSP public `mosaico_thermal_read` succeeds → `peek_frame_t` → `peek_submit` → `peek_result_t` → shared native `peek_ui.c` → GSP canvas and labels. Host `.peek` replay enters the very same detector and UI. Replay coordinates are never an input. A driver failure calls `peek_fault`; it does not resubmit its retained array.

The sensor task owns acquisition. A latest-only FreeRTOS queue copies completed frames/errors to the render-task timer. Only the render task owns the detector/UI; GSP timers, pointer events and canvas callbacks share that task context. Host sim_bridge callbacks similarly have one owner. No drawing callback changes detection state.

Detection uses the spatial median of the current 768 temperatures as background, temperature excess and four-connected component area. Entry requires three spatially consistent *new* complete frames. Existing tracks use a lower contrast threshold and retain the nearest qualifying component within five sensor pixels, regardless of a hotter remote source. When untracked, choose maximum summed positive temperature excess; equal scores resolve by row-major component discovery order. This is deliberately explainable and does not learn a stationary target into background. Release after two valid absent frames, an acquisition error, or finite hold/expiry time. Position uses an exponential smoother.

The injected clock and capture timestamps use one monotonically increasing millisecond epoch. A replay pause freezes the replay clock; resume adds only subsequent wall-time deltas. Replay resets detector, file cursor, sequence identity and clock together, preserving paused/running mode. Case selection resets and pauses. Missing data events advance time without samples. Real acquisition has no pause: its clock always advances. Hardware reboot/source epoch changes require a detector reset.

The native diagnostic UI has a 384×288 nearest-neighbor heatmap, white selected-centroid cross, source classification, data/target status, sensor frame sequence, logical current time, last valid capture time and age. Fixed 20–40 °C visualization does not alter detection thresholds. Invalid/stale data retains the last heatmap only as historical context; status invalidates the cross immediately. Host controls cycle cases, pause/resume and replay. Device controls are labelled SENSOR/LIVE/-- and do not pause the live clock.

Validation boundary: C tests and native GSP runs establish algorithm/replay/UI behavior. Firmware compilation establishes build/API compatibility. Neither establishes sensor accuracy, FOV, distance, physical orientation, detection reliability in real scenes or on-device timing. No firmware was installed in this phase.
