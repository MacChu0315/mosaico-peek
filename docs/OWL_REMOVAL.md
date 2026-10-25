# Night owl retired from firmware

On2026-10-25 the user rejected night owl and requested its removal from firmware.
Installed1.0.15-peek-three retains only dragon, deep_sea and mechanical.
Owl original sources and historical evidence remain archived, not built into the
application. This is removal of runtime resources and selection, not secure erase
of historical backups or the entire device flash.

## Behavior and compatibility

Tap/left swipe/AI single click: dragon -> deep_sea -> mechanical -> dragon.
Right swipe goes backward through the same three entries. Batched AI presses
use the same three-entry count. Gesture cancellation/deduplication is unchanged.
Startup remains dragon. Deep-sea fast membrane, mechanical centered closure,
dragon detail, detector, mapping and calibrated IMU remain unchanged.

Stable UI IDs0/2/3 and bitmap indices1/2 are retained; retired UI1/bitmap0 are
rejected before mutating the active renderer or source. No renumbering or saved
data migration. Kconfig startup1 is invalid and produces a build error. Host
preview/control no longer offer owl. Raw unknown Host commands retain the
existing explicit INVALID_ARG behavior; the CLI rejects them before sending.

## Resource exclusion

`bake_eye_pack.py` skips owl entirely and produces only sea/mechanical streams.
The unused index0 descriptor is zero-initialized for stable indexing; it has no
name, texture pointer or texture bytes. `eye_pack_select` rejects it. No current
build dependency references the retired R2 package. The original immutable
eye-pack is still validated as a source package, but its owl files are not encoded.

Generated inventory and final ELF symbol/strings checks establish exclusion.
The remaining31 bitmap streams must match1.0.14 exactly. Retired art reproduction
and historical tests are retained for audit but are not active firmware/preview
entry points; the owl renderer test is replaced by the removal inventory test.

## Checks and commands

Host/Release CMake/ctest covers removed ID rejection, remaining image parity,
three-entry wrapping, batch AI count and existing time/input guarantees. Native
tests cover real pointer switching, four orientations of all retained artworks,
511 recorded temperature arrays/655 events, and backend/CLI retired-name rejection.
The final negative raw command is intentionally last because the existing Host
protocol records INVALID_ARG as a sticky error. It does not alter source state.

```sh
python3 tools/preview.py --view deep_sea --flip-x --flip-y
python3 tools/control.py next
python3 tools/control.py previous
python3 tools/control.py case live
python3 tools/control.py play
python3 tools/build_idf.py
```

See HANDOFF and evidence/remove-owl for final identity, resource deltas and
installation. Existing exact1.0.14 restore is retained; no ROM recover, erase,
shared dependency upgrade or remote write is authorized by this removal.

## Installed outcome

Official update completed on first attempt, source db16ee0, matching actual ELF,
normal/VALID/error0/IMU0/crash0. App7218608B (2291104B smaller), UI94480B
unchanged. Final ELF/application contain no owl resources/name. Initial free
PSRAM3984068B versus1693128B in the prior dragon startup observation. Hardware
button sequence was not separately exercised; production/native routing checks
passed. No physical FPS improvement is claimed from resource removal alone.
