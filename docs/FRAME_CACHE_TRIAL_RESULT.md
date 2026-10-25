# Full-frame cache trial stopped; stable1.1.1 restored

User requested roughly doubled active FPS and approved a full480 canonical-frame
cache experiment. It adds450KiB explicit PSRAM and keeps the same pixels/source.
Debug/Release38/38 and native pixel/input/replay checks passed on the trial.

Mechanical270deg active-open:1.1.1=4.870Hz (18.48s), trial=4.931Hz (20.89s).
Trial Canvas raster fell to9.8ms, but preparation rose to151.9ms; total cost
was essentially unchanged. Different manual inputs do not establish a controlled
percentage improvement. Added memory was not justified by this observation.

User chose to stop before deep-sea measurement and restore exact1.1.1. Restore
operation58042a78-c12c-4f0b-85a7-4cf00216f5d4, boot6106931637066069584 succeeded. Installed ELF
fad83dba1a8e4628b70dd82efbd4520d63b11006bdf12f70bd2b780442d5e33b; sourceeffb682e2a35a6b6a4e862f990d6eb5219831a9d.
Normal/VALID, runtime/IMU error0, crash_count0; both physical flips preserved.
No further device performance tests were run after that instruction.

Stable work resumes onperf/three-eye-render. Experiment source7d1d4ae and full
evidence are preserved onperf/eye-frame-cache (head74edf8750ad80cd0223ef6b67e6a6fec1c8628e1).
Review delta archive: review/mosaico-peek-frame-cache-trial.zip (29113916B),
SHA256be7fdf7934965dfc16d15e024d48df7a4b712b7b95766aa14b37a6a352c2890e. It requires baseline3797ff9, excluding build caches,
SDK copies and unchanged assets. ZIP integrity and all checksums passed.
Current receipt/result summary: evidence/frame-cache-trial-result/.
Frozen v1.1.0 tag/bundle and stable1.1.1 restore bundle remain unchanged.

The ignored projects/peek/build directory still contains trial IDF artifacts;
do not mistake these for the installed1.1.1. Exact installed ELF/map/config are
in firmware-local/1.1.1; exact bundle is evidence/render-v111/device-install/
render-v111.irisfw. Normal tools/build_idf.py regenerates stable source/config.

Stable Host rebuilt; device adapter, mounted adapter and UI lifetime checks pass
(3/3). Native preview rebuilt and started with no trial cache field/error.
Source/config/tools/assets exactly match3797ff9; only this receipt/documentation
was added. IDF build output remains labelled as trial above until rebuilt.
