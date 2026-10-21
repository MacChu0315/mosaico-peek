#!/usr/bin/env python3
"""Official GSP simulator + native bridge; ephemeral ports preserve other sessions."""
import argparse,json,os,signal,socket,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--sample-step',type=int,choices=[1,2],default=2);p.add_argument('--view',choices=['dragon','diagnostic'],default='dragon');p.add_argument('--headless',action='store_true');p.add_argument('--duration',type=float,default=0);p.add_argument('--no-build',action='store_true');args=p.parse_args()
    component=Path(os.environ.get('ESP_GSP_COMPONENT_DIR',ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp')).resolve()
    compiler=Path(os.environ.get('GSPC_EXECUTABLE',ROOT.parent/'.toolchains/gspc-0.6.1/gspc')).resolve()
    sim=Path(os.environ.get('GSP_SIM_EXECUTABLE',ROOT.parent/'.toolchains/gsp-sim-1.5.1/sim')).resolve()
    run=ROOT/'.run';run.mkdir(exist_ok=True)
    # A fixed socket intentionally fails rather than taking over another Peek instance.
    env=dict(os.environ,PEEK_DATA_DIR=str(ROOT/'data'),PEEK_RUN_DIR=str(run),PEEK_VIEW=args.view,PEEK_EYE_SAMPLE_STEP=str(args.sample_step),PEEK_ASSET_PYTHON=sys.executable)
    if not args.no_build:subprocess.run([sys.executable,str(component/'tools/sim_bridge/build.py'),'--project',str(ROOT/'projects/peek/pc'),'--build-dir',str(ROOT/'build-sim'),'--component-dir',str(component),'--gspc',str(compiler)],env=env,cwd=ROOT,check=True)
    manifest=json.loads((ROOT/'build-sim/peek_backend-Release.json').read_text())
    if (run/'control.sock').exists():raise RuntimeError('Peek control.sock exists; stop its owner before a new preview. Do not remove a live socket.')
    ready=run/'ready.json';ready.unlink(missing_ok=True)
    processes=[];logs=[]
    def start(command,name):
        log=(run/name).open('w');logs.append(log)
        proc=subprocess.Popen(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);processes.append(proc)
    def wait(test):
        deadline=time.monotonic()+30
        while time.monotonic()<deadline:
            if any(x.poll() is not None for x in processes):raise RuntimeError('GSP process exited; inspect .run/host.log and .run/backend.log')
            if test():return
            time.sleep(.02)
        raise TimeoutError('GSP startup timed out')
    def stop(*_):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        start([str(sim),'--bundle',manifest['bundle'],'--frames','0','--backend-listen','tcp://127.0.0.1:0','--backend-required','--api-listen','tcp://127.0.0.1:0','--visual-listen','127.0.0.1:0','--ready-file',str(ready)],'host.log')
        wait(ready.exists);info=json.loads(ready.read_text());start([manifest['executable'],'--endpoint',info['backend']],'backend.log')
        wait(lambda:(run/'control.sock').exists() and (run/'status.json').exists())
        print('GSP preview: '+info['browser']+'\nState/logs: '+str(run),flush=True)
        if not args.headless:
            import webbrowser
            webbrowser.open(info['browser'])
        start_time=time.monotonic()
        while not args.duration or time.monotonic()-start_time<args.duration:
            if any(x.poll() is not None for x in processes):raise RuntimeError('GSP exited')
            time.sleep(.1)
    except KeyboardInterrupt:pass
    finally:
        # Ask the callback thread to stop at a poll boundary. A direct external
        # SIGTERM can interrupt select() in pinned sim_bridge 1.5.1 and mark an
        # otherwise healthy session failed (EINTR). Keep the host alive for cleanup.
        if len(processes)>1 and processes[1].poll() is None:
            try:
                with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as control:
                    control.sendto(b'1 quit',str(run/'control.sock'))
                processes[1].wait(timeout=6)
            except (OSError,subprocess.TimeoutExpired):
                processes[1].terminate()
        for proc in reversed(processes):
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=6)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
        for log in logs:log.close()
if __name__=='__main__':main()
