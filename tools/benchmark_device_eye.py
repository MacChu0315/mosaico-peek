#!/usr/bin/env python3
"""Read-only, bounded device eye timing; uses official project CLI only."""
import argparse,sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from probe_device import command,payload
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--label',required=True);parser.add_argument('--seconds',type=float,default=35);parser.add_argument('--expected-version');parser.add_argument('--output-root',type=Path,default=ROOT/'evidence/eye-ui/performance');args=parser.parse_args()
if not args.label.replace('-','').isalnum() or not 5<=args.seconds<=300:parser.error('label must be alphanumeric/hyphen; seconds5..300')
out=args.output_root/args.label;out.mkdir(parents=True,exist_ok=False)
a=command(['device-status']);assert a['device']['hardware_mac']=='30:ed:a0:f4:52:a0' and a['device']['firmware_mode']=='normal' and not a['device']['stale'];assert not args.expected_version or a['device']['app_version']==args.expected_version;(out/'before.json').write_text(json.dumps(a,indent=2)+'\n');boot=a['boot_id'];start=time.monotonic();rows=[]
with (out/'samples.jsonl').open('w') as f:
 while time.monotonic()-start<args.seconds:
  value=command(['rpc','20556','1']);s=json.loads(payload(value));assert s['error']==0
  row=dict(wall_s=time.monotonic()-start,state=s);rows.append(row);f.write(json.dumps(row)+'\n');f.flush();time.sleep(.6)
b=command(['device-status']);assert b['boot_id']==boot and b['device']['crash_count']==a['device']['crash_count'];(out/'after.json').write_text(json.dumps(b,indent=2)+'\n')
if len(rows)<2 or rows[-1]["state"]["now_ms"]<=rows[0]["state"]["now_ms"]:raise RuntimeError("Insufficient distinct device samples for a rate measurement; raw observations retained")
groups={}
for x,y in zip(rows,rows[1:]):
 p,q=x['state'],y['state']
 if p['view']!=q['view'] or p.get('orientation',0)!=q.get('orientation',0):continue
 key=(p['view'],'sleeping' if p['sleeping'] and q['sleeping'] else 'active-or-transition',p.get('orientation',0))
 r=groups.setdefault(key,dict(view=key[0],condition=key[1],orientation=key[2],ms=0,frames=0,draw_us=0,raster_us=0,submit_us=0,prepare_us=0,prepares=0,samples=0,faults=0,open_frames=0,open_ms=0,open_raster_us=0,open_submit_us=0))
 for name,pkey in [('ms','now_ms'),('frames','render_frames'),('draw_us','draw_us'),('raster_us','raster_us'),('submit_us','submit_us'),('prepare_us','prepare_us'),('prepares','prepares'),('samples','samples'),('faults','faults'),('open_frames','open_frames'),('open_ms','open_elapsed_ms'),('open_raster_us','open_raster_us'),('open_submit_us','open_submit_us')]:r[name]+=q[pkey]-p[pkey]
for r in groups.values():
 r['engine_hz']=r['frames']*1000/r['ms'];r['raster_ms_frame']=r['raster_us']/max(1,r['frames'])/1000;r['submit_ms_frame']=r['submit_us']/max(1,r['frames'])/1000;r['prepare_ms_mean']=r['prepare_us']/max(1,r['prepares'])/1000;r['active_open_hz']=r['open_frames']*1000/r['open_ms'] if r['open_ms'] else None
report=dict(canvas_callback_hz=(rows[-1]['state']['draws']-rows[0]['state']['draws'])*1000/(rows[-1]['state']['now_ms']-rows[0]['state']['now_ms']),physical_panel_FPS=None,version=a['device']['app_version'],ELF_sha256=a['device']['firmware_sha256'],boot_id=str(boot),views=sorted({r['state']['view'] for r in rows}),samples=len(rows),groups=list(groups.values()),heap={k:b['device'][k] for k in ['free_internal','min_free_internal','free_spiram','min_free_spiram']},note='Physical-device engine/raster/submit counters. No screenshot within window. RPC polling and real unlabelled scene; not physical panel FPS or a controlled same-scene percentage comparison.')
(out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
shot=command(['screenshot',str(out/'screen.png')]);assert shot['boot_id']==boot;(out/'screen.json').write_text(json.dumps(shot,indent=2)+'\n')
