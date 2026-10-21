# Eye surface artwork replacement handoff

User feedback after installed1.0.6:

- Original dragon horizontal/vertical physical tracking: accepted.
- New-eye wider120/80px motion range: accepted; preserve it.
- Newly exposed automatically synthesized surface (called “eye white” by the
  user): rejected as visually ugly. Technical checks do not imply visual approval.

The next task is authored eye-surface replacement, not another mapping/range or
performance change. No additional firmware installation was performed after this
feedback. The device remains1.0.6 for reference; the existing source/derived
backing is preserved and labelled rejected, not presented as final artwork.

## Standalone handoff

Export tool:`tools/export_eye_art_handoff.py`.
Source brief/checker:`tools/eye_art_handoff/README.md` and`check_preview.py`.
Delivery:`review/eye-surface-art-handoff-v1.zip` with SHA256 companion.
The ZIP contains no device credentials, SDK dependencies, build caches or firmware.

It includes immutable original selected PNGs,480 neutral images, frame/lids and
provenance; exact locked/editable/priority-paint masks; rejected backing and
production C screenshots; sphere geometry contract; a self-contained Python
reference preview/checker; and explicitly labelled synthetic rejected-example
previews. It is a material-production task, not a generic character importer.
The masks preserve every originally visible pixel; source frame/lids remain fixed.

A producing agent should read the included Chinese README and return one opaque
480×480 RGBA8`submission/<theme>/eye_surface.png` per theme, editable originals,
source/model/license/process records, corner/diagonal/eyelid previews and hashes.
The three themes can be assigned separately. No shared detector/role code or
hardware access is needed. Main project will add an explicit authored-surface
adapter and perform C/GSP/native/device validation only after receiving artwork.

## Reproduce/check/package

```
python3 tools/export_eye_art_handoff.py
python3 review/eye-surface-art-handoff-v1/check_preview.py --input review/eye-surface-art-handoff-v1/rejected --output review/eye-surface-art-handoff-v1/rejected-proof --animate
python3 tests/test_eye_art_handoff.py
python3 tools/export_eye_art_handoff.py --package-existing
```

Export refuses to overwrite an existing directory. Use`--output review/ANOTHER_NAME`
for a new independent export and pass that path to the checks. Packaging verifies
immutable reference hashes and the rejected-example technical report, then writes
per-file hashes and tests the ZIP. It does not approve the example art.

The27 direction reference renders match current C within the established one
RGB565-channel rounding allowance. Checker rejection paths cover wrong dimensions,
transparent pixels and any locked-pixel edit. Three8-second synthetic videos
retain their stated design duration; they are not real input, native rendering,
device recordings or measured FPS. Pixel-precise native comparison and physical
appearance/performance remain main-project responsibilities after adaptation.
