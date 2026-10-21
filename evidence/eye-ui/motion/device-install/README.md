# Installed direction/motion correction —1.0.6-peek-motion

Official System Update succeeded on the first operation in this version:
`b5fe1381-1fc4-4bee-912d-a43dbbe8a099`, healthy/validated, commit response.
Standing user authorization applies only to MAC30:ed:a0:f4:52:a0 /
Device ID4553502d49524953010030eda0f452a0. No ROM recover, erase,
shared dependency changes or remote writes.

- Source`fd637cc133b132fe2a3f81661a577377beba57ed`.
- Bundle SHA256`aa41815c833b745fdb6158196557be85093799cc87102336a3ade7eef0abc78c`.
- ELF SHA256`543337f9a5fab62621b94c5ee01d443e8af582543e7558a20ac24d3ab5e6084b`.
- New Boot ID`11818992348187344414`.
- Post-install: normal firmware, crash_count0, runtime error0, live complete
  thermal samples, both flip_x and flip_y false, default dragon.
- Bootloader/partition-table hashes unchanged; UI resource image unchanged.
  target_recovery=null. The official workflow preserved a pre-existing retained
  core dump in its external session directory; no raw dump is added here and
  no current-app crash is inferred from that retained artifact.
- Before runtime screenshots: internal free237235B, PSRAM free4562148B.
  These readings are default-dragon free space, not bitmap workload peaks.

Preflight initially compared the raw3072-byte partition-table hash against the
packaged4096-byte hash. It failed locally before any device write. Rechecking the
official0xff padding established exact unchanged payload; see preflight.json.
No payload was modified to bypass the check.

The earlier1.0.5 Recovery watchdog/unknown first outcome remains recorded in
../../performance/device-install/; it did not recur in this1.0.6 operation.
Known1.0.5 restore bundle:../../performance/device-install/eye-fast.irisfw.

Exact reproduction (after build and official package preparation/inspection):

```
python3 ../esp-mosaico-vibe/mosaico.py iris system-update --workspace . --device-id 4553502d49524953010030eda0f452a0 --bundle evidence/eye-ui/motion/device-install/eye-motion.irisfw --json
```

Do not combine`--bundle` with`--project`. This is an installation command;
read-only verification uses`iris device-status`, application RPC20556/1 and
`tools/benchmark_device_eye.py`. The user confirmed BOTH physical directions correct on1.0.6. The user accepted the wider range but rejected the newly exposed synthesized
surface. Replacement artwork is the next step; no visual approval is claimed.
