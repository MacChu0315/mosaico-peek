# Follow-up to review of463a3588

Scope: preserve approved visual art and existing core detector. No device operations, candidate-algorithm merge, tracking-worktree edits or shared dependency upgrade. Pre-existing root `.codex-runs/` diagnostic logs belong to other activity; left untouched and excluded from this review.

## Correctness / asset build stage

The supplied `repro/run.py` returned2 against463a3588, reproducing30Hz HOLD vs60/120Hz TRACKING at receive2200. `dragon_update` now expires the **previous** observation before new capture identity/evidence can overwrite it, and retains the post-event expiry check. All three rates return TRACKING, stationary=false, quiet_since=2000. Thresholds300/900ms, velocity, spring, held and detector policy stay unchanged.

`tests/test_dragon_timing.c` uses production Celsius arrays and detector with eight receive-delay/boundary/held scenarios at30/60/120Hz, fixed125ms delay, arrival at2175/2176, an over-aged new capture, stopped input and same-time idempotence. Existing behavior/raster tests remain in place.

Ordinary baking reads and validates retained PNG, pixel, quantization and include hashes without writing the source tree. Build-local generation JSON records the actual tool version independently of original provenance. `--check` is read-only; `--update-assets` is explicit, requires original art and the pinned Pillow version. Script and CMake read-only regressions include source content/mtime, tamper rejection and successful explicit updates in temporary copies. The651780-byte C asset payload and retained art are unchanged.

Performance measurements and current image/map/XIP budget follow in the second stage; normal/no-query preview and screenshot/poll conditions use the same version/scene/timer. Device diagnostic work is separate and is not evidence of mainline hardware acceptance.
