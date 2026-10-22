| Theme | State | Canvas callbacks/s | GSP commit seq/s | C draw ms | Prepare ms |
| --- | --- | ---: | ---: | ---: | ---: |
| night_owl | active | 19.93 | 20.18 | 1.70 | 0.192 |
| night_owl | sleeping | 19.93 | 20.18 | 0.66 | 0.001 |
| deep_sea | active | 19.93 | 20.18 | 1.53 | 0.143 |
| deep_sea | sleeping | 19.93 | 20.18 | 0.63 | 0.001 |
| mechanical | active | 19.81 | 19.98 | 3.57 | 0.073 |
| mechanical | sleeping | 19.93 | 20.18 | 3.20 | 0.001 |

One native GSP API connection; browser presence is not asserted.5s per theme/state; no screenshots, status polls, browser automation or builds inside windows. Boundary frame_info and cumulative counters retained. Active window contains moving gaze/blinks; closed idle separate. One short observation per condition, not statistical device acceptance.

Callbacks were full480x480 in this Host run. On device a callback may be a tile; callback rate is not engine full-frame rate or physical screen FPS. GSP commit sequence is the Host complete-frame counter; browser-visible and physical panel FPS are unmeasured. Video sampling/encoding FPS is not throughput.
