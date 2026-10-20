#!/usr/bin/env python3
"""Read actual pixels from the official local GSP API; never inject role coordinates."""
import argparse,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
component=Path(os.environ.get('ESP_GSP_COMPONENT_DIR',ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp'))
sys.path.insert(0,str(component/'tools/sim_bridge'))
from rpc_client import connect
def main():
    p=argparse.ArgumentParser();p.add_argument('path',type=Path);args=p.parse_args();args.path.parent.mkdir(parents=True,exist_ok=True)
    ready=json.loads((ROOT/'.run/ready.json').read_text())
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        for method,params in [('wait',{'frames':2}),('screenshot',{'path':str(args.path.resolve()),'format':'png'})]:
            reply=api.call(method,params)
            if 'error' in reply:raise RuntimeError(reply)
        print(json.dumps(reply))
if __name__=='__main__':main()
