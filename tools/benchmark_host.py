#!/usr/bin/env python3
"""A/B official native GSP: no API/status sampling inside A vs8fps API screenshots+15ms loop sleep between status reads in B.
Keep the same browser preview connected throughout both modes. Do not run builds concurrently.
"""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(Path(os.environ.get('ESP_GSP_COMPONENT_DIR',ROOT.parent/'.toolchains/esp-gsp-1.5.1/esp-gsp'))/'tools/sim_bridge')]
from control import command,state
from rpc_client import connect

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=float,default=30);parser.add_argument('--repeats',type=int,default=2);parser.add_argument('--tag',default='ab');args=parser.parse_args()
    if not 1<=args.seconds<=30 or not 1<=args.repeats<=5:parser.error('seconds1..30; repeats1..5')
    out=ROOT/'evidence/followup/performance';out.mkdir(parents=True,exist_ok=True)
    ready=json.loads((ROOT/'.run/ready.json').read_text())
    process_ids={'simulator':int(ready['pid'])}
    try:
        parent=int(next(l for l in Path(f'/proc/{ready["pid"]}/status').read_text().splitlines() if l.startswith('PPid:')).split()[1])
        for pid in Path(f'/proc/{parent}/task/{parent}/children').read_text().split():
            name=Path(Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[0].decode()).name
            if name=='peek_backend':process_ids['backend']=int(pid)
    except OSError:pass
    def process_snapshot():
        result={'load_average':list(os.getloadavg()),'processes':{}}
        for name,pid in process_ids.items():
            try:
                fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
                cpu=(int(fields[11])+int(fields[12]))/os.sysconf('SC_CLK_TCK')
                result['processes'][name]={'pid':pid,'cpu_seconds':cpu}
            except OSError:pass
        return result
    artifact_paths=[ROOT/'build-sim/peek_backend',ROOT/'build-sim/peek_backend_assets/app.gspb',ROOT/'data/idle.peek',ROOT/'data/dragon.peek']
    artifact_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifact_paths}
    (out/(args.tag+'-start-artifacts.json')).write_text(json.dumps(artifact_hashes,indent=2)+'\n')
    command('view dragon');rows=[]
    with connect(port=int(ready['api'].rsplit(':',1)[1])) as api:
        def frame_info():
            started=time.monotonic();reply=api.call('frame_info');assert 'result' in reply,reply
            return {'client_seconds':time.monotonic()-started,'result':reply['result']}
        def window(case,mode,repeat):
            name=f'{args.tag}-{case}-{mode}-{repeat}';frames=ROOT/'.run'/name;frames.mkdir(exist_ok=True)
            command('case '+case);time.sleep(.25) # settle the initial paused frame outside the measurement window
            frame_before=frame_info();command('play');before=state();process_before=process_snapshot();start=time.monotonic();next_capture=start;polls=0;captures=[];samples=[]
            if mode=='A':
                # Deliberately no loop, API calls or status reads during A.
                time.sleep(args.seconds)
            else:
                while time.monotonic()-start<args.seconds:
                    s=state();polls+=1;assert s['error']==0,s
                    samples.append({'wall_s':time.monotonic()-start,'logical_ms':s['result']['now_ms'],'sequence':s['result']['sequence'],'mode':s['role']['mode'],'data':s['result']['data'],'draws':s['draws']})
                    if time.monotonic()>=next_capture:
                        path=frames/f'{len(captures):04d}.png';t0=time.monotonic();reply=api.call('screenshot',{'path':str(path),'format':'png'});assert 'result' in reply,reply
                        captures.append({'file':path.name,'wall_s':time.monotonic()-start,'api_seconds':time.monotonic()-t0,'logical_ms':s['result']['now_ms']})
                        next_capture+=.125
                        if next_capture<time.monotonic()-.125:next_capture=time.monotonic()+.125
                    time.sleep(.015)
            elapsed=time.monotonic()-start;after=state();process_after=process_snapshot();frame_after=frame_info();command('pause');assert after['error']==0,after
            assert before['case']==after['case']==case and before['view']==after['view']=='dragon'
            a,b=before['host_timing'],after['host_timing'];ra,rb=before['render'],after['render']
            delta=lambda key:b[key]-a[key]
            draw_count=after['draws']-before['draws'];prepare_count=rb['prepares']-ra['prepares'];callback_count=delta('completed_callbacks')
            native_elapsed=(b['published_us']-a['published_us'])/1e6
            assert draw_count>0 and callback_count>0 and prepare_count>0
            assert b['target_timer_ms']==a['target_timer_ms']==33
            bins=[j-i for i,j in zip(a['interval_bins'],b['interval_bins'])];assert sum(bins)==delta('interval_count')
            result={'case':case,'condition':mode,'repeat':repeat,'client_wall_seconds':elapsed,'status_wall_seconds':native_elapsed,'logical_elapsed_ms':after['result']['now_ms']-before['result']['now_ms'],'timer_count':callback_count,'timer_hz':callback_count/native_elapsed,'timer_callback_us_mean':delta('callback_us_total')/callback_count,'timer_work_us_mean':delta('work_us_total')/callback_count,'status_publish_us_mean':delta('publish_us_total')/callback_count,'timer_interval_us_mean':delta('interval_us_total')/delta('interval_count'),'timer_interval_histogram':{'upper_us':b['interval_bins_le_us'],'counts':bins},'prepare_count':prepare_count,'prepare_us_mean':(rb['prepare_us_total']-ra['prepare_us_total'])/prepare_count,'draw_count':draw_count,'draw_hz':draw_count/native_elapsed,'draw_us_mean':(rb['draw_us_total']-ra['draw_us_total'])/draw_count,'draw_pixels':rb['pixels']-ra['pixels'],'surface':after['surface'],'status_reads_in_window':polls,'screenshots_in_window':len(captures),'frame_info_before':frame_before,'frame_info_after':frame_after,'before':before,'after':after,'process_before':process_before,'process_after':process_after,'process_cpu_ratio':{name:(value['cpu_seconds']-process_before['processes'][name]['cpu_seconds'])/elapsed for name,value in process_after['processes'].items() if name in process_before['processes']},'bridge_present_timing':'frame_info commit seq/damage only; no public per-upload/per-present duration exposed; browser visible FPS not measured'}
            if mode=='A':assert polls==len(captures)==0
            else:assert polls>args.seconds*5 and len(captures)>args.seconds*3
            rows.append(result)
            (out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            if mode=='B':
                (out/(name+'-samples.jsonl')).write_text(''.join(json.dumps(s)+'\n' for s in samples));(out/(name+'-captures.json')).write_text(json.dumps(captures,indent=2)+'\n')
            print(f"{case} {mode} repeat{repeat}: draw={result['draw_hz']:.3f}Hz timer={result['timer_hz']:.3f}Hz draw={result['draw_us_mean']:.1f}us polls={polls} screenshots={len(captures)}",flush=True)
        for repeat in range(1,args.repeats+1):
            # Reverse condition order on repeat2 to reduce a simple order/heat bias.
            for case in ('idle','dragon'):
                for mode in (('A','B') if repeat%2 else ('B','A')):window(case,mode,repeat)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in artifact_paths}
    assert hashes==artifact_hashes,'Build/data changed during paired windows'
    sources={str(p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in map(Path,['src/dragon.c','src/dragon_render.c','src/peek_ui.c','projects/peek/pc/platform_pc.c','projects/peek/ui/main.json'])}
    summary={'method':'Same running native backend+bundle, same33ms timer, one browser preview connected; A has only boundary reads/API frame_info, B uses API screenshots8fps and status polling as prior acceptance. Native status snapshots include completed prior timer work; no builds during measurement.','seconds_requested':args.seconds,'repeats':args.repeats,'artifact_sha256':hashes,'source_sha256':sources,'results':rows}
    (out/(args.tag+'-results.json')).write_text(json.dumps(summary,indent=2)+'\n')
    lines=['| Scene | Condition | Draw Hz (mean) | Timer Hz (mean) | C draw ms (mean) | Prepare ms | Timer work ms | Status write ms |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for case in ('idle','dragon'):
        for mode in ('A','B'):
            selected=[r for r in rows if r['case']==case and r['condition']==mode];mean=lambda key:sum(r[key] for r in selected)/len(selected)
            lines.append(f"| {case} | {mode} | {mean('draw_hz'):.3f} | {mean('timer_hz'):.3f} | {mean('draw_us_mean')/1000:.3f} | {mean('prepare_us_mean')/1000:.3f} | {mean('timer_work_us_mean')/1000:.3f} | {mean('status_publish_us_mean')/1000:.3f} |")
    (out/(args.tag+'-table.md')).write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
