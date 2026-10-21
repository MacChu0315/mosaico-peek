#!/usr/bin/env python3
"""Normal connected preview: boundary-only reads, active versus sleeping."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp/tools/sim_bridge')]
from control import command,state
from rpc_client import connect
OUT=ROOT/'evidence/eye-ui'
def main():
    ready=json.loads((ROOT/'.run/ready.json').read_text());rows=[]
    artifacts=[ROOT/'build-sim/peek_backend',ROOT/'build-sim/peek_backend_assets/app.gspb'];digest=lambda:{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts};before_hash=digest()
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def info():
            r=api.call('frame_info');assert 'result' in r;return r['result']
        for theme in ['night_owl','deep_sea','mechanical']:
            command('view '+theme)
            for scene in ['active','sleeping']:
                command('case '+('dragon' if scene=='active' else 'idle'));command('advance '+('3000' if scene=='active' else '12000'));api.call('wait',{'frames':3})
                command('play');before=state();frame_before=info();start=time.monotonic();time.sleep(5);elapsed=time.monotonic()-start;frame_after=info();after=state();command('pause')
                assert before['view']==after['view']==theme and not after['error']
                if scene=='active':assert before['result']['target'] and after['result']['target'] and not before['role']['sleeping'] and not after['role']['sleeping']
                else:assert before['role']['pose']['blink']==after['role']['pose']['blink']==1
                n=after['draws']-before['draws'];a,b=before['render'],after['render'];p=b['prepares']-a['prepares'];wall=(after['host_timing']['published_us']-before['host_timing']['published_us'])/1e6
                rows.append(dict(theme=theme,scene=scene,seconds=elapsed,native_status_seconds=wall,callback_hz=n/wall,full_canvas_pixel_equivalents_hz=(b['pixels']-a['pixels'])/230400/wall,GSP_committed_frame_sequence_hz=(frame_after['seq']-frame_before['seq'])/elapsed,draw_ms_mean=(b['draw_us_total']-a['draw_us_total'])/max(1,n)/1000,prepare_ms_mean=(b['prepare_us_total']-a['prepare_us_total'])/max(1,p)/1000,before=before,after=after,frame_before=frame_before,frame_after=frame_after,screenshots_during_window=0,status_reads_during_window=0));print(theme,scene,rows[-1]['callback_hz'],flush=True)
    assert digest()==before_hash,'Artifacts changed during benchmark'
    report=dict(method='One connected Chrome native preview.5s per theme/state; no screenshots, status polls, browser automation or builds inside windows. Boundary frame_info and cumulative counters retained. Active window contains moving gaze/blinks; closed idle separate. One short observation per condition, not statistical device acceptance.',artifacts=before_hash,physical_panel_FPS=None,browser_visible_FPS=None,results=rows)
    (OUT/'host-performance.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['| Theme | State | Canvas callbacks/s | GSP commit seq/s | C draw ms | Prepare ms |','| --- | --- | ---: | ---: | ---: | ---: |']
    for r in rows:lines.append(f"| {r['theme']} | {r['scene']} | {r['callback_hz']:.2f} | {r['GSP_committed_frame_sequence_hz']:.2f} | {r['draw_ms_mean']:.2f} | {r['prepare_ms_mean']:.3f} |")
    (OUT/'host-performance.md').write_text('\n'.join(lines)+'\n\n'+report['method']+'\n\nCallbacks were full480x480 in this Host run. On device a callback may be a tile; callback rate is not engine full-frame rate or physical screen FPS. GSP commit sequence is the Host complete-frame counter; browser-visible and physical panel FPS are unmeasured. Video sampling/encoding FPS is not throughput.\n')
if __name__=='__main__':main()
