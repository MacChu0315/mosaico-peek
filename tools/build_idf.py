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
    env=dict(os.environ,GSPC_EXECUTABLE=str(compiler))
    command=[sys.executable,str(runner),'--project',str(ROOT/'projects/peek'),'--idf-path',str(idf)]
    subprocess.run(command+['doctor'],env=env,cwd=ROOT,check=True)
    subprocess.run(command+['build'],env=env,cwd=ROOT,check=True)
if __name__=='__main__':main()
