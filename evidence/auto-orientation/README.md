# Orientation physical acceptance —2026-10-22

Target MAC30:ed:a0:f4:52:a0 / Device4553502d49524953010030eda0f452a0 only.
Main UI sources and artwork were integrated locally atd01c49c; the main worktree
was not modified. Axis correction source74a0f44 is installed as1.0.9-peek-orient.

## Results

-1.0.8 installed successfully but user ultimately reported ALL FOUR orientations
wrong; the prior positive answer was withdrawn. Upright physical pose measured
approximately(+0.053,+0.913,+0.385)g with artwork270; clockwise90 pose measured
(-0.451,+0.234,+0.863)g with artwork0. Labelled raw records are in device/.
- Sensor-to-screen mapping must account for XY handedness, not just a mounting
rotation. Corrected gravity-down is(-ax,+ay); optional mounting quarter-turn0.
The real measurements fail the old device adapter test and pass the fix.
- User confirmed1.0.9 upright and clockwise90 both upright, then inverted and
counterclockwise90 both upright with gaze following the hand. View was dragon.
140 observations over138.244s contain all four angles, IMU/runtime error0 and
no thermal fault increment. Other artwork shares the tested layer, but it was
not separately rotated on-device during this quick check.

## Installation

Original1.0.8 operation862149bf-00bf-4d2a-ace8-1d55d7ed0578 succeeded.
First1.0.9 operation01a880f6-f512-438f-92d7-0944ec081bc2 becameoutcome_unknown
at the partition-table phase. New Recovery Boot5265465015941919363 reported
reset_reason5; failed app address0x20000/ELF54f72372 identify Recovery. The
read-only reconciliation retained insufficient-evidence/unknown, while the
new boot was healthy/idle, queue empty and old job1 absent (0x105).
After explicit user approval, exactly one identical-bundle retry succeeded:
8457eb46-23bb-4c1a-ac0c-70314e60e4df, healthy/validated,
initial app Boot16320435194263765134.

Bundle SHA39d8a58d987c6f101550d54949bf1b9553620341f60aa925038c4cc05883587c;
ELF47dc46dec991d830c94972b55b89833a56819634d4e6fb79d43736ff7c745c5a.
Partition-table/UI payloads matched prior packages exactly; no bootloader or
Recovery component. A newly built local bootloader differed from the prior
build but was never in the update package. Device inventory confirms the
installed bootloader hash remained unchanged. The pre-existing retained crash
artifact stayed outside the repo; no raw core dump was copied.

## Final checks and limits

The observation ended on endpoint loss. Later screenshot/status/RPC checks
reconnected to power-on Boot11903143034352040053 (reset_reason1), expected
1.0.9 ELF/version, crash_count0, IMU/runtime error0 and VALID fresh target data.
The final RPC had2 cumulative thermal faults on that new boot; their cause is
unverified. This is not an uninterrupted-run or zero-total-capture-fault claim.
The screenshot is a panel-coordinate image, not a world-oriented camera photo.
No physical panel FPS, exact settling latency or long-term stability claim.

Checks run: integrated/calibrated CTest28/28, pinned-IDF doctor/build, official
bundle inspect/preflight, official System Update, device-status, RPC20556/1,
read-only reconciliation/job query and final screenshot. The retained factory
size warning remains; app6,681,344B fits unchangedota_0. Full artifact paths and
integration notes are in docs/AUTO_ORIENTATION.md.
