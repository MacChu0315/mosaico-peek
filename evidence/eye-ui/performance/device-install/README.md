# Installed exact-pixel optimization —1.0.5-peek-fast

Standing user authorization covers subsequent updates for this project and only
MAC30:ed:a0:f4:52:a0 / Device ID4553502d49524953010030eda0f452a0.
The unchanged reviewed bundle was installed using official System Update;
no ROM recover, whole-flash erase, dependency upgrade or remote write.

- Source:34ae08b028dea84715a434494f82c7b07306a5c5.
- Bundle SHA256:c66b7d17b88d834237aa5623cce8b50b2dc57be335d6944f346be46f19786702.
- ELF SHA256:dfa99df79efdea11c49343870631809f7451f9d5d6948adcfb67351d4001f9d0.
- Successful operation:63c50b3a-7bc0-44ec-8573-9b461b945f9f.
- Boot ID:14769927073946096952.
- Healthy/validated and exact ELF match. Bootloader and partition-table hashes
  match before/after; target Recovery=null. UI image hash equals the reviewed
  switching image, since artwork and scene content did not change.

## First update and reconciliation

Operationaff0370b-2704-4e19-8a2b-953322a35032 returnedoutcome_unknown. Last reported
progress was4096B/6612352B (partition-table component), then the retained Recovery
writer rebooted with reset_reason5. Its failed Boot7494137676407733170 and failed
app address0x20000 identify the Recovery writer, not the candidate application.
The candidate had not started. The next Recovery Boot5988425410027701479 was
healthy/idle with no queued/running update; priorjob1 returned not-found0x105.

The original operation, status, crash metadata and official read-only operation
reconciliation are retained. Reconciliation reported insufficient evidence for
the exact write outcome; it is not relabelled succeeded. The retained core dump
ELF did not match the failed writer, so its old panic text is not a confirmed
source diagnosis of this incident. No raw dump is copied into this repository.

After preserving evidence and confirming the prior job no longer existed, the
same exact bundle was submitted once from the new idle Recovery boot under the
user's standing authorization. That second operation succeeded, with commit
response, application validation and unchanged bootloader/layout. No third write,
no altered timeout/dependency/Recovery image and no competing update was used.
The standard project Gateway expires after10 idle seconds; current addresses
were read from official CLI results instead of assuming an old port remained.

## Actual run after successful update

The user confirmed mechanical selection for the second observation. Over34.24s:
276 engine frames,268 fresh samples,0 faults; current runtime error0, normal
mode and0 crash count.227 active-open frames over27.24s =8.333Hz.
Mean raster75.66ms/frame; submit32.98ms/frame. See ../COMPARISON.md and ../optimized/.
The first runtime observation also showed deep_sea with valid live input/error0;
no separate sustained deep-sea/night-owl timing is claimed. The three themes
share optimized production code and all passed exact384-frame Host comparisons.

Current screenshot and status share the successful Boot/ELF. Internal free
231343B, PSRAM free2058212B before the final screenshot. Largest block, peak
all-character interaction workload and physical panel-visible FPS are unmeasured.
The physical observation is user-controlled, unlabelled and RPC-sampled; no
controlled percentage-speedup claim. Prior1.0.4 bundle is retained at
`evidence/eye-ui/switching/eye-switch.irisfw` for an intentional official restore.
