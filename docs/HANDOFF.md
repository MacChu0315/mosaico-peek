# Peek1.2.0 — Vibe Mode0.2 hardware verified (2026-10-26)

Current branchfeat/vibe-02-migration. Original Peek MAC30:ed:a0:f4:52:a0 /
Device ID4553502d49524953010030eda0f452a0 now runs Peek1.2.0 on reviewed Vibe
Mode0.2.0 / Recovery ABI2, productesp-mosaico/v2, layoutmosaico-retained-test-2m-v2.
No other board was written. Current software attachment:
releases/v1.2.0/mosaico-peek-v1.2.0.irisfw (6301404B), SHA256
b881507941bbbfffc7d1603ad4196db4f38e194e614e582c60e051f049068d59.
Sourceb672117486d65ab76893fb833103594b019636f8; ELF
d99572ee4ee4322d1575aa2ca16d1b2617aa470ae3f430a3f4162e3008c85d04.
Final normal Boot3927091703191660807; VALID, runtime/IMU error0, crash_count0.

## Actual migration and acceptance

After the explicit base-write explanation, user reconnected the original board
and requested actual flashing/test. Live legacy identity was verified and retained
crash evidence archived. The official workflow requested manual ROM entry; user
completed Boot+power-on. Recover operationc6878691-daa8-418a-a741-8f328154f521
verified VibeMode0.2.0 on the same identity. Application update
140379a2-5291-4058-80fd-2fbcaab75883 installed the exact artifact above.

The first application operation13638cfa-4966-47f1-8c42-dc1c7b2af377 failed before
transfer because no independent data link was ready. A retained iris run client
and verified matching control/data links resolved this. Explicit data-endpoint
claim returned a selector error (primary endpoint remained control); it is not
recorded as success. Only after terminal failure, empty queue and positive live
link checks was the same bundle retried. No dependency patch or base rewrite.

Host Debug/Release37/37; native44 orientation images,16 input checks,17 sea phase
checks and511 recorded arrays/655 events pass. Actual75s smoke window:74.97s,
588 accepted samples,0 faults, monotonic sequence==accepted samples, all three
roles, observed orientations0/270 and sleeping. User confirmed tap/swipe/AI
switching, tracking directions and reopening. The150ms wake transient was not
captured in periodic telemetry; reopening is user acceptance. Closed dragon and
deep-sea framebuffer RGB565 match production C. Maintenance roundtrip verified:
normal1.2.0 Boot7955376229059211969 -> VibeMode0.2.0 Boot14074660692523048517 ->
normal1.2.0 Boot3927091703191660807, same DeviceID/ELF, continued valid sampling.

Evidence: evidence/iris02/DEVICE_ACCEPTANCE.json, device-migration/, device-tests/.
The own iris run client was ended normally; no other client's Gateway was stopped.

## Preserved behavior and limits

Dragon selected sclera C / approved240 sampling; deep-sea R2 full480 without rim
fade,240ms membrane; mechanical C full480 with socket A and centered closed gaze.
Owl remains retired. Stable UI IDs0/2/3, tap/left swipe/AI=next, right swipe=previous.
One acquisition-owned detector/controller before lossy display snapshots; never
submit samples from draw. Both gaze flips enabled and calibrated IMU(-ax,+ay),
mount0, automatic orientation retained. Shared timing and visible assets unchanged.

In the mixed manual270deg windows, active GSP rates were dragon7.246Hz,
deep-sea6.600Hz and mechanical4.738Hz; no controlled speedup or panel-FPS claim.
Deep-sea closed8.7s produced no new frames while source sampling continued.
Observed heap after smoke: free internal171155B / PSRAM4480380B; lifetime minima
119456B /3458840B. Task-level memory query is unsupported (HTTP501), not a reboot;
status heap observations remain valid. No largest-block/allocator-peak, prolonged
soak, forced-crash, physical AI-power-on entry or new90/180deg physical claim.

App7258864B; UI94480B unchanged; explicit bitmap PSRAM3418224B unchanged.
New BSP batches display transfers differently; actual measurements above supersede
assumptions based solely on old-source figures. No extra frame-cache buffer.

## Build, deliver and history

Pinned independent environment: ../esp-mosaico-vibe-iris02; dependencies.json.
python3 tools/bootstrap.py
python3 tools/build_idf.py --bundle
python3 tools/preview.py --view deep_sea --flip-x --flip-y
python3 tools/control.py next / previous
python3 tools/control.py case sleep; python3 tools/control.py play / replay

For a fresh0.2 USB session, keep an official iris run client and verify BOTH
control/data links bound to the selected DeviceID/BootID before an update. Never
retry an uncertain write without operation reconciliation. Use only mosaico.py.

The exact delivered bundle is unchanged since its source-commit clean check.
Receipt-only commits do not relabel the firmware source; checking that exact
artifact against HEAD requires checking out its recorded source commit.
Website upload/review has not been performed. User explicitly authorized publishing
the completed migration and hardware acceptance (b672117/c17b8c3) to GitHub master
on2026-10-26. Exact local releases/ attachments remain ignored by Git; the native
.irisfw path and hash above identify the separately retained software attachment.

Frozen v1.1.0 and exact ABI1 v1.1.1 remain archival sources/bundles; they cannot be
installed as ordinary rollback packages on this ABI2 base. Rejected full-frame
cache trial remains separate onperf/eye-frame-cache and is not re-enabled.
Publicity packages remain under review/mosaico-peek-promo-v111-20261026*.zip;
artwork is still current, but their1.1.1 metadata predates this ABI2 migration.
See docs/IRIS02_MIGRATION.md and docs/FRAME_CACHE_TRIAL_RESULT.md for details.
