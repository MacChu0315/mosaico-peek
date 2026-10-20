# Complete real thermal input — 2026-10-20

Recorded from physical MLX90640 through the unchanged Peek detector and real diagnostic UI. Device `4553502d49524953010030eda0f452a0` / hardware MAC `30:ed:a0:f4:52:a0`, USB `/dev/ttyACM1`; Boot ID `2187646616958253656`. Firmware `1.0.0-peek-diag`, source `1dd860d52ab3e5dff0f60bf6125f0f11745191dc`, exact normal-app ELF SHA-256 `f80b7d6f47b5ddad9dc7576fcfd2324a54c86eede2e69147821ddcf16c02dbab`. Main algorithm source is byte-identical to reviewed `463a3588` and includes the existing event-aging fix. No candidate A/B is present.

- 512 acquisition records: **511 complete 32×24 float32 temperature arrays** and one initialization wait/error (`ESP_ERR_TIMEOUT`, sequence0; no retained pixels resubmitted).
- Successful capture times3022..68096 ms: **65.074 s**, measured **7.837 complete frames/s**. Median interval130 ms; min119/max190 ms.
- All511 successful captures were submitted to the actual C detector. 655 consecutive detector events include511 submits, one consumed fault and143 ticks. No missing input or event IDs; recorder contention drops0.
- Shared C replay: **655 events, 511 accepted samples, zero missing inputs, zero result mismatches, position difference0**. No recorded position is fed into detection.
- Temperatures24.1800..36.4772 °C as calculated by the pinned driver. All392,448 successful-frame values are finite and within the core input range. This is not an external temperature calibration.
- Capture-completion to C-processing delay: median55 ms, maximum105 ms. This excludes physical response and final display/presenter latency.

The buffer was frozen before downloading; the physical sensor, detector and screen continued. Acquisition attempts increased527→1839 during the ~167.2s download, with no additional reported acquisition fault. The same Boot ID remained healthy. The final real screenshot is at sequence2398, well after the retained recording window. This records a complete bounded window; it is not an indefinite log of all later user observations.

`captures.bin` and `events.bin` are the complete input and actual-C event streams. See [wire format and commands](../../../docs/LIVE_DIAGNOSTICS.md). `metadata.json` retains actual configuration; `summary.json` includes counts/file hashes; `analysis.json` describes data/timing; `observations.jsonl` is a readable index of actual C states and coordinates; `c-replay-verification.json` is the recomputation result.

```sh
./build-host/peek_live_replay data/live/20261020-complete-window/captures.bin data/live/20261020-complete-window/events.bin
```

The scene was not labelled and no object/motion ground truth was supplied. Do not infer identity, target-position accuracy, mounting orientation or candidate improvement from replay parity. Reuse the exact stored temperature arrays, processing times, sequence and fault/tick events for future comparisons; do not feed a candidate extra raw captures or replace fault events with invalid synthetic samples. Neither the diagnostic installation nor this dataset is acceptance of the dragon eye on physical hardware.
