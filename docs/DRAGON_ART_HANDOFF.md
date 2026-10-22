# Dragon sclera artwork handoff

The user requested the original first dragon eye's materials to improve its
sclera on2026-10-22, after accepting the mechanical result. No new dragon art
has been approved or installed. Keep the current iris, pupil, skin, eyelids,
range, tracking map and behavior while the artist prepares the replacement.

Package: `review/dragon-sclera-art-handoff-v1.zip` (13.35MiB). Start at its
Chinese `README.md`; it defines editable scope, layers, geometry, provenance,
reference commands, required return files and the native/device validation gap.
The current sclera is procedural C, not an original PNG. The exported template
is explicitly a derived unlit reference; its preview sampler is art-only and
must not be presented as a production texture adapter.

The package retains original1254 skin/iris sources with alpha/provenance,
original offline design code/videos, current production textures/C raster,
an opaque480 sclera template/guide,11 current-pose images and affected-pixel
masks, an8-second preset reference video, and a standalone Python/C preview.
No SDK, firmware, build cache, device access or installed dependency copies.
Root Apache-2.0 license is retained without inventing additional image rights.

Reproduce in this checkout (original approved input directory must be present):

```sh
python3 tools/export_dragon_art_handoff.py --output review/dragon-sclera-ANOTHER_NAME
python3 tools/export_dragon_art_handoff.py --package-existing
```

Export refuses to overwrite existing handoff directories. Normal preview writes
only its build/output directories. Original reference assets and their mtimes
remain unchanged. Return `submission/sclera.png`, editable sources, provenance,
preview/checksums; the main thread will adapt resources and validate C/GSP/device.

Verified:11 baseline images match production scalar C plus approved2x2 sampling;
black candidate changes only measured sclera pixels, closed image unchanged;
wrong-size/transparent candidates rejected; MP4 is480×480,8s,25fps (not measured
runtime performance). ZIP CRC and every file hash pass. Extracted ZIP builds
and renders independently of the main project and SDK. No firmware rebuild or
installation is required for this material-only export.

## Returned selected C artwork

The user returned dragon-sclera-C-handoff-v1.zip and authorized production
integration. See DRAGON_SCLERA.md and current HANDOFF. Existing art-handoff-v1
remains historical; the legacy exporter now rejects current textured source.
