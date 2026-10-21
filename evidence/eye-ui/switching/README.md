# Input switching acceptance — candidate1.0.4-peek-switch

No physical device operation this turn. Installed1.0.3 and its previous evidence
remain unchanged. This candidate is prepared for a separately authorized update.

- Host Debug/Release CTest20/20: retained18 tests plus gesture boundary cases and
  actual BSP adapter callback/count tests. UI lifetime fixture also exercises
  pointer registration failure/failed detach retry, cancelled touches, cycling
  and byte-identical detector/role state. AI atomic handoff concurrently delivers
  all10000 fixture callbacks; only BSP SINGLE_CLICK is registered, with cleanup
  failure preserving its handle and preventing duplicate startup.
- `tests/test_switch_gsp.py`:16 actual native input checks pass. Official
  `feed_pointer` down/move/up drives shared C; no role-coordinate injection.
  Four PNG captures match each565 output channel of the C artwork raster.
  Tap/left-next/right-previous and both wraps work; duplicate release, long hold,
  vertical and drag-return gestures do not switch. View changes cancel old
  touches, queued diagnostic input does not reset the thermal source. Sleep
  remains asleep when changing art. Detector/result/role/mapping/time stay equal.
- `tests/test_gsp.py` with isolated evidence directory:100 original diagnostic
  controls/pause/replay/real native detection checks pass.
- Fixed ESP-IDF doctor/build passes; effective version1.0.4-peek-switch,
  sdkconfig.eye-switch, character0, sample-step2 for dragon, both gaze flips.
  Factory-capacity warning is retained; application fits unchangedota_0.
- Actual app/UI/ELF/map hashes and target ABI resource values are in the new
  scoped resource-budget.json. Original eye-UI budget remains the installed1.0.3
  record. The new reporter reads active config from project_description.json
  instead of guessing a previous sdkconfig path.
- Independent read-only review found no Critical/Important issues. It verified
  actual BSP button classification and the GSP device touch adapter's preserved
  release coordinates. No new SDK/library or neighboring checkout modifications.

The first compile used a mistaken result.now_ms member; current logic uses the
actual detector.now_ms. The first native input script used convenience `tap`,
which did not notify the registered pointer observer; failure is preserved in
first-native-input-error.log. Explicit feed_pointer samples exercise the real
observer route successfully. The firmware/browser route was not replaced with
simulated role movement to hide this test-path difference.

No device touch/AI latency, physical switch behavior, ROM bitmap decoding or
runtime heap under all four characters has yet been measured. BSP single click
waits for its click-sequence decision; rapid double click and long press do not
switch. Multi-contact gestures are not an application feature. Lifecycle cancel
means a view/epoch change or outside input; the observer API has no separate
hardware touch-cancel event. No physical FPS claim is made.

Final candidate is built from committed sourcef77ccb2. `candidate.json` and
`bundle-inspect.json` identify `eye-switch.irisfw`, version1.0.4-peek-switch,
unchanged partition layout and matching app/UI image hashes. It has not been
submitted to a device. The source commit includes tests/evidence; the following
delivery commit only updates exact committed-build/package records.
