# Authorized installation —2026-10-21

The user explicitly authorized installation ("允许烧录") after reviewing the
three-theme delivery. Exactly one official application System Update was issued,
to MAC30:ed:a0:f4:52:a0 / Device ID4553502d49524953010030eda0f452a0.
No direct IDF/esptool flash, erase, `mosaico.py recover`, additional installation
or remote repository write. System Update performed its required Recovery-mode
transition and application reboot; the retained Recovery image was not replaced.

## Exact artifact / operation

- Version1.0.3-peek-eyes, source9da7987c7c39436402252b8cf6e3fd7e03fc883a.
- Installed ELF SHA256:`b46699a95d376eef4db145a33170d86598bed8a1aed076b48f34c152b755ef94`.
- Bundle:`eye-trio.irisfw`,5887193B; SHA256:`47cd717e4b2a4ba96c123e957d0fac706bcc4e7c59e3fba0ff6d1eaebe7ad420`.
- App6504384B; UI94480B. App/UI hashes equal the preceding reviewed budget.
- CONFIG_PEEK_CHARACTER=0, sample step2 for dragon, both physical gaze flips true.
- Official operation:`7e197546-0fab-4d38-9f77-15947a70594c`; succeeded, healthy, validated.
- Old Boot ID:3345998236476284272; new Boot ID:18113205708322532055.
- Existing bootloader and partition-table hashes match before/after; target
  Recovery is null. Resource components passed the official commit response.
- The old1.0.2-peek-sleep restore bundle remains at
  `evidence/sleep-performance/installed/dragon-sleep.irisfw`; official inspect
  confirmed it shares the same layout. No restore was performed.
- The official workflow automatically preserved an existing coredump in its
  private artifact store before writing. This is not a new application crash:
  pre/post live crash counters are0. No raw memory dump is included here.

The package was prepared from existing checked images with the official
`prepare_system_update.py` and `esp_iris.py bundle build/inspect`; no rebuild or
configuration substitution occurred. Full image/ELF/map backups are local under
ignored`firmware-local/eye-ui-9da7987/`, not bundled dependency/build copies.

## Executed checks / observations

```sh
python3 ../esp-mosaico-vibe/mosaico.py iris device-status --workspace . --project projects/peek --device-id 4553502d49524953010030eda0f452a0 --json
python3 ../esp-mosaico-vibe/mosaico.py iris system-update --workspace . --device-id 4553502d49524953010030eda0f452a0 --bundle evidence/eye-ui/device-install/eye-trio.irisfw --json
python3 ../esp-mosaico-vibe/mosaico.py iris rpc 20556 1 --workspace . --project projects/peek --device-id 4553502d49524953010030eda0f452a0 --json
python3 ../esp-mosaico-vibe/mosaico.py iris screenshot evidence/eye-ui/device-install/installed-screen.png --workspace . --project projects/peek --device-id 4553502d49524953010030eda0f452a0 --json
```

Device identity/current Boot/old ELF were rechecked immediately before writing.
The installation completed in about65.6s; operation identity/result, bundle
components and target/source inventories are retained in`install-result.json`.
No ambiguous result or write retry occurred. Initial sandbox restrictions on the
existing Gateway state lock were resolved with local tool permission, before
any device write; no account, credentials or remote access were changed.

Read-only RPCs over34.18s confirm version/source/ELF,
normal mode,0 errors/crashes, both gaze flips and continuous VALID MLX90640 input.
Capture and consumed sample rates both7.841/s; faults0.
Every observed sequence equals accepted samples. IDLE/TRACKING and sleeping were
observed; waking was not sampled. Actual device screenshot is`installed-screen.png`.

- Internal free:237499B; minimum:196328B.
- PSRAM free/min before screenshot:4699668B.
- Screenshot metadata subsequently reports a lower minimum PSRAM4228552B;
  screenshot capture affects minima. These are allocator values, not peak
  workload guarantees, largest blocks or complete memory accounting.
- Mixed-state engine frames:19.573/s; Canvas tile
  callbacks:293.154/s. Sleeping frames dominate this short
  window, so the mixed rate must not be presented as active-eye performance.
- Active-open counters covered only4 frames /
  570ms (7.018 engine frames/s).
  This short tail is insufficient for comparison to the prior sustained trial.
- Physical panel-visible FPS remains unmeasured.

## Remaining boundary

The installed reviewed configuration shows **dragon**. Night owl, deep sea and
mechanical resources are included, but physical touch/AI switching is not
implemented. Their ROM decompression, PSRAM use and actual on-device rendering
were not exercised and remain unverified. Installing another startup character
would be another device write, outside this completed single installation.
The prior Host/native evidence remains valid at its original scope.
