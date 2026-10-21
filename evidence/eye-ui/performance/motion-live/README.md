# Installed1.0.6 sphere-motion observation

Sourcefd637cc; ELF/Boot and raw counters in summary.json/samples.jsonl. User confirmed both physical dragon directions correct and mechanical selected. No screenshots during window; all themes visited manually. Rates count complete GSP engine frames, not physical panel FPS.

| Theme | Seconds | Engine Hz, mixed | Active-open Hz | Raster ms/frame | Fresh samples | Faults |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dragon | 2.23 | 7.623 | 7.650 | 90.51 | 17 | 0 |
| night_owl | 8.61 | 7.317 | 7.440 | 90.74 | 68 | 0 |
| deep_sea | 9.70 | 7.216 | 7.426 | 89.17 | 76 | 0 |
| mechanical | 40.99 | 6.904 | 7.095 | 98.53 | 322 | 0 |

Mechanical has40.99s of same-view intervals; other views are brief and not sustained performance acceptance. Overall Canvas tile callbacks103.37/s are not full-frame Hz. Mechanical active-open7.095Hz is lower than prior1.0.5 small-translation8.333Hz; new sphere motion costs more, while the original1.0.4 was2.009Hz. Live scenes differ; no controlled percentage comparison.

Before final screenshot: internal free247763B/min196064B, PSRAM free5116384B/min4562148B. Largest blocks/complete workload peaks are unknown. This window covers all three bitmaps after active-only cache changes, but does not prove indefinite switching stability.

HOLD and active movement are separated in by-role.json; no physical sleeping interval was observed. Native closed-eye timing and sleep correctness are separate evidence under ../../motion/. Video export rate is not device throughput.
