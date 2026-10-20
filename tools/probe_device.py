#!/usr/bin/env python3
"""Bounded read-only acceptance through official mosaico.py only."""
import argparse,base64,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEVICE='4553502d49524953010030eda0f452a0'
CLI=ROOT.parent/'esp-mosaico-vibe/mosaico.py'
def command(parts):
    args=[sys.executable,str(CLI),'iris',*parts,'--workspace',str(ROOT),'--project',str(ROOT/'projects/peek'),'--device-id',DEVICE,'--json']
    run=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=30)
    if run.returncode:raise RuntimeError(run.stderr or run.stdout)
    result=json.loads(run.stdout)
    if not result.get('ok',True):raise RuntimeError(result)
    return result

def payload(value):
    if isinstance(value,dict):
        if isinstance(value.get('payload_base64'),str):return base64.b64decode(value['payload_base64'],validate=True)
        for v in value.values():
            p=payload(v)
            if p is not None:return p
    return None

def main():
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=35);p.add_argument('--label',default='live');p.add_argument('--no-screens',action='store_true');a=p.parse_args()
    if not a.label.replace('-','').isalnum() or not 0<a.seconds<=300:p.error('invalid bounded probe')
    out=ROOT/'evidence/device-dragon'/a.label;out.mkdir(exist_ok=False)
    before=command(['device-status']);d=before['device'];assert d['hardware_mac']=='30:ed:a0:f4:52:a0' and d['app_version']=='1.0.0-peek-dragon' and d['firmware_mode']=='normal' and not d['stale']
    (out/'before.json').write_text(json.dumps(before,indent=2)+'\n');boot=before['boot_id'];begin=time.monotonic();samples=[];next_screen=0
    with (out/'samples.jsonl').open('w') as f:
        while time.monotonic()-begin<a.seconds:
            value=command(['rpc','20556','1']);raw=payload(value);assert raw is not None
            state=json.loads(raw);assert state['source']=='LIVE MLX90640' and state['error']==0
            sample=dict(host_wall_s=time.monotonic()-begin,state=state,cli=value);samples.append(sample);f.write(json.dumps(sample)+'\n');f.flush()
            if not a.no_screens and sample['host_wall_s']>=next_screen:
                capture=command(['screenshot',str(out/f'frame-{len(samples):03d}.png')]);assert capture['boot_id']==boot
                (out/f'frame-{len(samples):03d}.json').write_text(json.dumps(capture,indent=2)+'\n');next_screen+=15
            time.sleep(.5)
    after=command(['device-status']);assert after['boot_id']==boot and after['device_id']==DEVICE and after['device']['firmware_mode']=='normal' and after['device']['crash_count']==d['crash_count']
    (out/'after.json').write_text(json.dumps(after,indent=2)+'\n')
    first,last=samples[0]['state'],samples[-1]['state'];seconds=(last['now_ms']-first['now_ms'])/1000
    assert seconds>0 and last['sequence']>first['sequence'] and last['samples']>first['samples']
    rates={k:(last[k]-first[k])/seconds for k in ['captures','faults','callbacks','draws','prepares','render_frames','samples']}
    draw_count=last['draws']-first['draws'];frames=last['render_frames']-first['render_frames']
    report=dict(device=DEVICE,boot_id=str(boot),version=d['app_version'],source_revision=last['source_revision'],sampled_device_seconds=seconds,rates_hz=rates,
        draw_mean_us=(last['draw_us']-first['draw_us'])/max(1,draw_count),gsp_render_mean_us=(last['render_busy_us']-first['render_busy_us'])/max(1,frames),gsp_raster_mean_us=(last['raster_us']-first['raster_us'])/max(1,frames),gsp_submit_mean_us=(last['submit_us']-first['submit_us'])/max(1,frames),
        roles=sorted({s['state']['role'] for s in samples}),data_states=sorted({s['state']['data'] for s in samples}),heap={k:after['device'][k] for k in ['free_internal','free_spiram','min_free_internal','min_free_spiram','total_internal','total_spiram']},
        cores=dict(gsp=last.get('render_core'),sensor=last.get('sensor_core')),sequence_equals_accepted_samples=all(x['state']['sequence']==x['state']['samples'] for x in samples),physical_panel_fps=None,note='Actual sensor/role firmware. Callback/surface/render counters are distinct; no physical panel scan or visible FPS measured. Snapshots and CLI polling can affect rates. No scene labels inferred.')
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
