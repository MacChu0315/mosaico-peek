# Approved240 sampling trial

User explicitly accepted the earlier side-by-side comparison on2026-10-21 and rejected the current2.69Hz experience. This grants the240-detail trial on the same authorized device, not an arbitrary further reduction.

Use identical original textures, sphere/lid/pupil/shadow/color math and detector/role inputs. The shared renderer's additive sample-step setter selects1 or2, rejecting other values. Create defaults to1 for compatibility. App startup configures2 before eye callback registration. Each2x2 output cell uses the original shader's odd-center pixel `(x|1,y|1)`. Row/column replication is global-coordinate based; tile edges can start odd. Drawing remains read-only/allocation-free and480×480. Heatmap and768-temperature processing remain full precision. There is no runtime adaptive quality or prefilled focus.

Host Debug/Release CTest12/12 includes a new4-pose scalar-vs-sampled regression, odd37×29 tiles, padded strides,1×1 bottom-right edge and invalid-step checks. Native GSP27 role checkpoints pass;19 actual PNGs match all230400 RGB565 samples to the approved policy with sampled-aperture/full-closure checks. The full original511-frame/655-event recording is replayed through the real C core/role, preserving all timestamps; the new actual native movie is retained. Hardware FPS is a separate measurement, not inferred from quarter shader evaluations.

Firmware uses version1.0.1-peek-dragon240 and isolated sdkconfig.dragon240. Comparison against previous sdkconfig.dragon initially changed only APP_PROJECT_VER and PEEK_EYE_SAMPLE_STEP; the final orientation follow-up also enables PEEK_GAZE_FLIP_X/Y; dependencies, partitions, source art and detection policy remain pinned. The opaque renderer retains the same full fixed-pixel cache (plus a step field); no quarter-RAM claim.

The prior480 app bundle/manifest is preserved under evidence/sampling240/restore-480. Restore through mosaico.py iris system-update --bundle without --project, using this workspace and exact Device ID; diagnostic restore is separately documented. Preserve Vibe Mode and ota_0. Current install/measurements and user feedback are recorded in HANDOFF after actual execution.

Actual installed trial c316843 measured7.493 engine frames/s and7.857 samples/s
in a24.69s read-only window, compared with historical2.693 engine frames/s.
User confirmed visible follow and requested both gaze axes reversed. Final
source ba98632 measured7.546 engine frames/s and7.829 samples/s with both runtime
flags true. Scenes differ; no controlled same-pose speedup or physical panel FPS
is claimed. Visual smoothness acceptance remains pending. Final current
version/ELF, install and heap results are in HANDOFF and evidence/orientation/.
