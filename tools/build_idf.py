#!/usr/bin/env python3
"""Verify the SDK revision and invoke the workspace-owned low-noise builder."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    idf=Path(os.environ.get('IDF_PATH',ROOT.parent/'.toolchains/esp-idf-7b9cc1a')).resolve()
    revision=subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip()
    if revision!='7b9cc1ac79f865983f59bb8ff3ff43eb74ff1dbe':raise RuntimeError('Wrong ESP-IDF revision; shared SDK was not changed')
    runner=ROOT.parent/'esp-mosaico-vibe/submodule/esp-mosaico-utils/mosaico-tools/skills/idf-low-noise-build/scripts/idf_low_noise_build.py'
    compiler=Path(os.environ.get('GSPC_EXECUTABLE',ROOT.parent/'.toolchains/gspc-0.6.1/gspc')).resolve()
    env=dict(os.environ,GSPC_EXECUTABLE=str(compiler),PEEK_ASSET_PYTHON=sys.executable,PEEK_EYE_UI_BUILD="1")
    command=[sys.executable,str(runner),'--project',str(ROOT/'projects/peek'),'--idf-path',str(idf)]
    subprocess.run(command+['doctor'],env=env,cwd=ROOT,check=True)
    source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    header=ROOT/'projects/peek/build/peek_build_revision.h'
    header.parent.mkdir(exist_ok=True)
    value='#define PEEK_SOURCE_REVISION "'+source_revision+'"\n'
    if not header.exists() or header.read_text()!=value:header.write_text(value)
    subprocess.run(command+['build'],env=env,cwd=ROOT,check=True)
    config=(ROOT/'projects/peek/build/sdkconfig.deep-sea-r2').read_text().splitlines()
    for line in ('CONFIG_PEEK_IMU_MOUNT_QUARTERS=0','CONFIG_PEEK_AUTO_ORIENTATION=y','CONFIG_APP_PROJECT_VER="1.0.13-peek-deepsea"','CONFIG_ESP_IRIS_RPC_BODY_BYTES=2048','CONFIG_PEEK_CHARACTER=0','CONFIG_PEEK_EYE_SAMPLE_STEP=2','CONFIG_PEEK_GAZE_FLIP_X=y','CONFIG_PEEK_GAZE_FLIP_Y=y','# CONFIG_PEEK_DIAGNOSTIC_VIEW is not set'):
        if line not in config:raise RuntimeError('Eye UI build configuration missing: '+line)
    print('PASS actual four-character firmware configuration; no installation performed')
if __name__=='__main__':main()
