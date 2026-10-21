# 1.0.6 direction and sphere-motion evidence

See ../../../docs/EYE_MOTION.md for full source/geometry, resources and limits.
Installed sourcefd637cc. User confirmed original dragon BOTH axes correct;
the wider range is user-accepted; the synthesized hidden surface is rejected.

- ctest-debug.log / ctest-release.log:23/23 each.
- asan-exact/alloc/projection.log:384-frame scalar parity, allocation cleanup,
  pure-axis projected120/80px centers. Leak sanitizer off for ptrace restriction.
- independent-pixels.json/log:57 full480 comparisons to independent composition.
- asset-checks.json:3 exact1.0.5 neutral images and27 aperture sampling bounds.
- native-switch/:16 real pointer checks, four exact565 pixel snapshots.
- native/:66 exact565 keyframes and six actual native real-time movies;
  raw logical/wall timestamps retained. No exported-FPS performance claim.
- preserved-source.json:dragon/controller/detector/input code unchanged from34ae08b.
- resource-budget.json:actual target ABI, image hashes and configuration.
- host-performance.*:active versus sleeping native Host timings, separate from
  ../performance/motion-live/ device counters.
- device-install/:exact bundle/identity/official successful operation and live
  mapping verification. Earlier1.0.5 failed first operation is separately retained.

Representative images at this directory root are production C raster snapshots
of explicit pose tests, not temperature detection evidence. Their direct poses
are labelled action tests; native/ uses synthetic full arrays through the real
production detector. Native images preserve the exact compositor output.
