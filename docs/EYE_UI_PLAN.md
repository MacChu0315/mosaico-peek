# Three eye UI integration

Scope: append night_owl, deep_sea and mechanical to dragon/diagnostic native
views. Supplied pack is immutable in assets/eye-pack; CHECKSUMS.sha256 and the
input ZIP hash identify the reviewed reference. Do not change detector, dragon
behavior, physical mapping or approved dragon renderer.

- [x] Validate pack checksums, bake lossless RGBA zlib streams in build trees.
  Host uses system zlib; ESP32-S31 uses existing ROM tinfl. No new target dependency.
- [x] Add shared C layer compositor: black, translated eye, premultiplied blend
  of adjacent lids, fixed frame; 480 output, full-resolution source sampling.
  Keep only frame/eye/two lids decoded in explicit device PSRAM. Negative origins
  and guard pixels remain unchanged. Do not apply dragon's240 sampling to new art.
- [x] Reuse dragon.c's source-owned observation/state/time as the behavior
  source, map gaze to each artwork's documented amplitude. Selecting a view
  preserves detector, epoch, pose and logical time. Add Host --view/control view,
  firmware startup selector. No new physical gesture behavior in this task.
- [x] Test independent pixel oracle, tiles/stride, clipping, invalid parameters,
  source build immutability, switch/pause/replay and original regression suite.
- [x] Build pinned native GSP and firmware; retain native PNGs and wall-time
  movies, active/static callback vs commit throughput and allocation/image budget.
  Physical FPS/runtime memory remain unmeasured without device operation.
- [x] Update current handoff, local commit and compact review archive, no device
  operations, dependency upgrades, remote writes or default-branch integration.
