# Character switching —1.0.4-peek-switch (not installed)

Four artworks cycle in this order: dragon → night_owl → deep_sea → mechanical
→ dragon. The diagnostic screen is a development tool, outside this cycle.

| Input | Action |
| --- | --- |
| Tap on the eye artwork | Next character |
| Swipe left | Next character |
| Swipe right | Previous character |
| Mosaico AI key single click | Next character |

Touch emits only once, on release. No separate GSP click callback is attached to
the artwork, so releasing a recognized swipe cannot add a click. Built-in scene
swipe is disabled for the single-scene app. Touch does not switch from diagnostic
controls; an already queued diagnostic callback is ignored after leaving that
view. Explicit view/case changes cancel any ongoing touch sequence.

The shared C gesture recognizer uses mapped display coordinates480×480 (+x
right,+y down), and injected monotonic wall milliseconds independent of thermal
replay time. Tap: <=600ms with maximum excursion<=16px on each axis. Horizontal
swipe: final displacement>=48px, with|dx|>=2|dy|. Intermediate move events never
switch. Vertical/dead-zone drags, out-of-bounds sequences, drag-return-to-origin,
long holds, duplicate releases and cancelled sequences do not become taps.

AI uses the actual pinned BSP `BSP_BUTTON_AI` and button driver's
`BUTTON_SINGLE_CLICK`. The driver waits for its multi-click decision; a rapid
double click produces DOUBLE_CLICK and is not a single click here. Long press
has no character action. No invented GPIO number or private BSP API is used.
The callback only increments an atomic unsigned counter. The GSP owner drains
that counter in its existing timer and applies the net steps modulo4; multiple
pending presses preserve their final selection without repeated decoding in one
render step. No UI/sensor calls, allocation or blocking in the button callback.

Switching goes through `peek_ui_cycle_character` / `peek_ui_set_character` and
preserves source epoch, temperature samples, detector, role, gaze mapping, seed,
phase and sleep/wake timing. A sleeping eye stays asleep in the new artwork.
Changing UI does not manufacture target confirmation. Acquisition still runs
before the latest-only display mailbox; all retained pixel assets and rendering
quality remain unchanged. Restart defaults to dragon; no persistent selection
or new flash writes are introduced by interaction.

## Try locally

```sh
python3 tools/preview.py --view dragon --flip-x --flip-y
python3 tools/control.py case dragon
python3 tools/control.py play
# Click or drag on the native preview artwork. External equivalents:
python3 tools/control.py next
python3 tools/control.py previous
python3 tools/control.py pause
python3 tests/test_switch_gsp.py
```

Native acceptance uses official `feed_pointer` press/move/release samples to
exercise the shared C observer, including the paused and sleeping state. The
simulator's convenience `tap` RPC did not deliver these observer samples in the
first attempt; that error is retained. Replacing it with real pointer samples
made the intended input route explicit. This does not change the physical input
implementation. SDK device release samples preserve the last touch position.

## Build / verification

```sh
cmake -S . -B build-host
cmake --build build-host -j4
ctest --test-dir build-host --output-on-failure
cmake -S . -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release -j4
ctest --test-dir build-release --output-on-failure
python3 tools/build_idf.py
python3 tools/report_eye_budget.py --output-dir evidence/eye-ui/switching
```

Current candidate version1.0.4-peek-switch uses isolated
`projects/peek/build/sdkconfig.eye-switch`, preserving installed1.0.3 config and
its exact restore bundle at`evidence/eye-ui/device-install/eye-trio.irisfw`.
All dependency revisions and partition layout stay pinned. Evidence is in
`evidence/eye-ui/switching/`. Host tests cover gesture boundaries, actual UI
lifecycle/registration failure, pending stale input, BSP callback binding,
partial-init cleanup and concurrent atomic count handoff. Native checks cover
both wrap directions and exact pixels of all four selected artworks, with
unchanged detector/role/time/seed/mapping; original diagnostic controls rerun.

Physical touch/AI response and new-theme device rendering remain unverified.
This local change is not on the device yet. The earlier single installation
permission was already used for1.0.3; installing this candidate requires a new
explicit device-write authorization. No device operations were made this turn.
