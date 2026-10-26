#!/usr/bin/env python3
"""Verify the SDK revision and invoke the workspace-owned low-noise builder."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--bundle",action="store_true");args=parser.parse_args()
    idf=Path(os.environ.get('IDF_PATH',ROOT.parent/'.toolchains/esp-idf-7b9cc1a')).resolve()
    revision=subprocess.check_output(['git','-C',str(idf),'rev-parse','HEAD'],text=True).strip()
    if revision!='7b9cc1ac79f865983f59bb8ff3ff43eb74ff1dbe':raise RuntimeError('Wrong ESP-IDF revision; shared SDK was not changed')
    pins=json.loads((ROOT/'dependencies.json').read_text())
    vibe=ROOT.parent/'esp-mosaico-vibe-iris02'
    for name,path in [('vibe',vibe),('bsp',vibe/'submodule/esp-mosaico-bsp'),('utils',vibe/'submodule/esp-mosaico-utils')]:
        actual=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        dirty=subprocess.check_output(['git','-C',str(path),'status','--porcelain','--untracked-files=no'],text=True).strip()
        if actual!=pins[name]['commit'] or dirty:raise RuntimeError(name+': pinned clean dependency required; no adjacent checkout was modified')
    runner=ROOT.parent/'esp-mosaico-vibe-iris02/submodule/esp-mosaico-utils/mosaico-tools/skills/idf-low-noise-build/scripts/idf_low_noise_build.py'
    utils=ROOT.parent/'esp-mosaico-vibe-iris02/submodule/esp-mosaico-utils'
    sys.path.insert(0,str(utils/'mosaico-tools/tools'))
    from mosaico_cli.gateway import iris_environment_root
    from mosaico_cli.host import virtual_environment_python
    iris_python=Path(os.environ.get('ESP_IRIS_PYTHON',virtual_environment_python(iris_environment_root(utils/'ESP-Iris'))))
    if not iris_python.is_file():raise RuntimeError('Matching Iris0.2 host Python is missing: '+str(iris_python))
    compiler=Path(os.environ.get('GSPC_EXECUTABLE',ROOT.parent/'.toolchains/gspc-0.6.1/gspc')).resolve()
    env=dict(os.environ,ESP_IRIS_PYTHON=str(iris_python),GSPC_EXECUTABLE=str(compiler),PEEK_ASSET_PYTHON=sys.executable,PEEK_EYE_UI_BUILD="1")
    command=[sys.executable,str(runner),'--project',str(ROOT/'projects/peek'),'--idf-path',str(idf)]
    subprocess.run(command+['doctor'],env=env,cwd=ROOT,check=True)
    source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    header=ROOT/'projects/peek/build/peek_build_revision.h'
    header.parent.mkdir(exist_ok=True)
    value='#define PEEK_SOURCE_REVISION "'+source_revision+'"\n'
    if not header.exists() or header.read_text()!=value:header.write_text(value)
    subprocess.run(command+['build'],env=env,cwd=ROOT,check=True)
    config=(ROOT/'projects/peek/build/sdkconfig.v1.2.0-iris02').read_text().splitlines()
    for line in ('CONFIG_TINYUSB_CDC_COUNT=2','CONFIG_ESP_IRIS_RECOVERY_ABI=2','CONFIG_ESP_IRIS_PRODUCT_CONTRACT="esp-mosaico/v2"','CONFIG_ESP_IRIS_LAYOUT_ID="mosaico-retained-test-2m-v2"','CONFIG_PEEK_IMU_MOUNT_QUARTERS=0','CONFIG_PEEK_AUTO_ORIENTATION=y','CONFIG_APP_PROJECT_VER="1.2.0"','CONFIG_ESP_IRIS_RPC_BODY_BYTES=2048','CONFIG_PEEK_CHARACTER=0','CONFIG_PEEK_EYE_SAMPLE_STEP=2','CONFIG_PEEK_GAZE_FLIP_X=y','CONFIG_PEEK_GAZE_FLIP_Y=y','# CONFIG_PEEK_DIAGNOSTIC_VIEW is not set'):
        if line not in config:raise RuntimeError('Eye UI build configuration missing: '+line)
    if args.bundle:
        subprocess.run(['cmake','--build',str(ROOT/'projects/peek/build'),'--target','system-update-bundle'],env=env,cwd=ROOT,check=True)
        subprocess.run([str(iris_python),str(ROOT/'tools/check_iris02_bundle.py'),'--bundle',str(ROOT/'projects/peek/build/peek-system-update.irisfw')],env=env,cwd=ROOT,check=True)
    print('PASS actual three-character Iris0.2 firmware configuration; no installation performed')
if __name__=='__main__':main()
