| Theme | State | Canvas callbacks/s | GSP commit seq/s | C draw ms | Prepare ms |
| --- | --- | ---: | ---: | ---: | ---: |
| night_owl | active | 18.88 | 19.18 | 5.94 | 0.116 |
| night_owl | sleeping | 19.19 | 19.38 | 5.96 | 0.001 |
| deep_sea | active | 18.65 | 18.98 | 5.71 | 0.154 |
| deep_sea | sleeping | 18.77 | 18.98 | 6.20 | 0.001 |
| mechanical | active | 18.48 | 18.78 | 6.26 | 0.164 |
| mechanical | sleeping | 19.17 | 19.38 | 6.29 | 0.001 |

One connected Chrome native preview.5s per theme/state; no screenshots, status polls, browser automation or builds inside windows. Boundary frame_info and cumulative counters retained. Active window contains moving gaze/blinks; closed idle separate. One short observation per condition, not statistical device acceptance.

Callbacks were full480x480 in this Host run. On device a callback may be a tile; callback rate is not engine full-frame rate or physical screen FPS. GSP commit sequence is the Host complete-frame counter; browser-visible and physical panel FPS are unmeasured. Video sampling/encoding FPS is not throughput.
