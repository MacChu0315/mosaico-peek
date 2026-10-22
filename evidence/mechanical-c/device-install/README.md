# Mechanical C installation —1.0.7-peek-mechanical

Authorized target: MAC30:ed:a0:f4:52:a0, Device ID4553502d49524953010030eda0f452a0.
Standing user authorization covers same-project subsequent official System Updates,
including required update reboots; no ROM recover, whole erase or other targets.

- Source df6f6da63613656204ccee052f637494433da2b8.
- Bundle SHA256 d0050fb8c6226af9ec57027859ce2f34725f3c24fdb5c6c980964dd33ba75d23.
- ELF SHA256 97d859cb847b3ceeff6956477098a28210dc90ebe50a3f3e6dfdc5f5ac010d2e.
- Successful operation44a14d33-a875-4164-99ef-3f5e9dcfcb2f.
- Healthy/validated, exact ELF, Boot1088401539410791703.
- After.json/runtime.json: normal firmware, crash_count0, error0, both flips false,
  live thermal samples with zero faults; default dragon. This does not by itself
  validate mechanical appearance or sustained performance.
- Bootloader/partition-table hashes unchanged; UI image unchanged; target Recovery
  null. Shared SDK/BSP untouched. Exact known local ELF/map/config retained in
  ignoredfirmware-local/1.0.7-peek-mechanical/.

## First outcome and evidence-based retry

First operationeac7243a-89b3-4067-a22d-31058e02fdad returnedoutcome_unknown;
last reported bytes4096/6759504 at partition-table component. The failed writer
Boot12671832305804571837, app address0x20000 and ELF54f72372… identify retained
Recovery. Subsequent Recovery Boot1467388130633976323 reported reset_reason5.
The archived core has a different ELFb3640c8d… and decode_eligible=false;
its old panic text is not a confirmed diagnosis of this event. No raw core dump
is copied into the review repository.

Official operation-reconcile remainedoutcome_unknown with insufficient current
evidence; this is retained, not rewritten as success. Subsequent writer-status
confirmed the new Recovery boot healthy/idle with empty running/queued lists;
job1 was absent (device0x105). After these checks, one same-bundle official retry
completed successfully with commit response and application validation. No changed
bundle, timeout increase, Recovery replacement, erase or blind retry was used.

## Reproduction / restore

```
python3 ../esp-mosaico-vibe/mosaico.py iris system-update --workspace . --device-id 4553502d49524953010030eda0f452a0 --bundle evidence/mechanical-c/device-install/mechanical-c.irisfw --json
```

Do not combine --bundle with --project. Inspect identity, bundle and current state
first. Read-only status uses iris device-status; app telemetry is RPC20556/1.
Prior1.0.6 restore: evidence/eye-ui/motion/device-install/eye-motion.irisfw.
No restore was performed. Physical direction/range stays user-confirmed from1.0.6;
new mechanical appearance/performance needs the separately recorded observation.
