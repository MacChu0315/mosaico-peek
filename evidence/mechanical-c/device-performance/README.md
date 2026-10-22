# Mechanical C physical counters

Installed1.0.7 sourcedf6f6da, ELF97d859cb…; Boot1088401539410791703. User confirmed mechanical selection and exercised movement/absence. Raw samples preserve actual views and states. No screenshots during either measurement window.

| Window / condition | Same-view seconds | Complete engine Hz | Active-open Hz | Raster ms/frame | Submit ms/frame | Prepare ms/step |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| live / active-or-transition | 14.59 | 3.907 | 3.937 | 212.40 | 32.13 | 3.280 |
| mechanical / active-or-transition | 12.38 | 3.877 | 3.932 | 211.50 | 32.29 | 6.349 |
| mechanical / sleeping | 47.44 | 3.879 | — | 213.52 | 32.51 | 0.019 |

Across mechanical-only segments: 74.41s, 583 fresh samples, 0 faults. Active-open 73 frames/18.55s = 3.935Hz. These are short observational segments, not controlled same-scene statistics.

Focused Canvas tile callbacks 58.175/s;15 callbacks per complete480 frame. Neither this nor movie export FPS is physical panel-visible FPS.

Prior1.0.6 mechanical active-open was7.095Hz. The new full globe exposes154781 vs75876 pixels to sphere sampling. Current raster212..214ms dominates; submission32ms is similar. The new artwork is slower. No fast-math, range reduction, downsampling, palette or timing change hides this regression. Performance has NOT been accepted as fluid or restored to the old rate.

Closed-state47.44s was observed and afterwardsTRACKING returned. The short150ms waking intermediate was not caught by RPC sampling; no physical wake-duration claim. Native deterministic wake checkpoints passed.

Before final screenshot: internal free247763B/min196064B; PSRAM free5096896B/min4542336B. These allocator values are not peak/largest-block measurements. Error0, no new crashes, same Boot/ELF across the windows.

Remaining: physical panel FPS, input-to-screen latency, long-run switching peaks and user visual acceptance. Further performance work must target raster cost and preserve accepted full480/detail/range.
