#!/usr/bin/env python3
"""Summarize retained paired counters, without attributing opaque bridge/present latency."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'evidence/followup/performance';data=json.loads((out/'ab-results.json').read_text());rows=data['results'];groups=[]
    for case in ('idle','dragon'):
        for mode in ('A','B'):
            selected=[r for r in rows if r['case']==case and r['condition']==mode];assert len(selected)==data['repeats']
            seconds=sum(r['status_wall_seconds'] for r in selected);client=sum(r['client_wall_seconds'] for r in selected)
            draws=sum(r['draw_count'] for r in selected);timers=sum(r['timer_count'] for r in selected);prepares=sum(r['prepare_count'] for r in selected)
            weighted=lambda key,count:sum(r[key]*r[count] for r in selected)/sum(r[count] for r in selected)
            draw_us=weighted('draw_us_mean','draw_count');timer_us=weighted('timer_callback_us_mean','timer_count');rate=draws/seconds
            commits=sum(r['frame_info_after']['result']['seq']-r['frame_info_before']['result']['seq'] for r in selected)
            calls=[]
            if mode=='B':
                for r in selected:
                    captures=json.loads((out/f"ab-{case}-{mode}-{r['repeat']}-captures.json").read_text());calls.extend(c['api_seconds'] for c in captures)
            else:assert all(r['status_reads_in_window']==r['screenshots_in_window']==0 for r in selected)
            groups.append({'case':case,'condition':mode,'repetitions':len(selected),'native_wall_seconds':seconds,'client_wall_seconds':client,'draw_hz':rate,'timer_hz':timers/seconds,'commit_seq_hz_at_boundaries':commits/client,'draw_us_mean':draw_us,'prepare_us_mean':weighted('prepare_us_mean','prepare_count'),'timer_callback_us_mean':timer_us,'timer_work_us_mean':weighted('timer_work_us_mean','timer_count'),'status_publish_us_mean':weighted('status_publish_us_mean','timer_count'),'screenshot_hz':sum(r['screenshots_in_window'] for r in selected)/client,'status_read_hz':sum(r['status_reads_in_window'] for r in selected)/client,'surface':selected[-1]['surface'],'screenshot_roundtrip_us_mean':sum(calls)/len(calls)*1e6 if calls else None,'screenshot_roundtrip_us_p95':sorted(calls)[math.ceil(.95*len(calls))-1]*1e6 if calls else None,'cycle_not_covered_by_backend_draw_or_callback_us':1e6/rate-draw_us-timer_us,'residual_note':'Indicative unmeasured cycle time, not an isolated bridge/present duration. Draw and timer segments are measured in the single backend owner; frame commit seq is not browser-visible FPS.'})
    text=['# Host normal-preview vs screenshot/poll comparison','',data['method'],'','A: no screenshot or status read inside the measured window. B: API screenshot target8fps with15ms loop sleep; actual read/sample rates below. Same browser preview connected, no browser automation or builds during windows. Each scene/condition has two30s runs with order reversal.','', '| Scene | Mode | Draw Hz | Timer Hz | Commit seq Hz | C draw ms | Prepare ms | Timer callback ms | Status write ms | Screenshot Hz | Status read Hz |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in groups:text.append(f"| {g['case']} | {g['condition']} | {g['draw_hz']:.3f} | {g['timer_hz']:.3f} | {g['commit_seq_hz_at_boundaries']:.3f} | {g['draw_us_mean']/1000:.3f} | {g['prepare_us_mean']/1000:.3f} | {g['timer_callback_us_mean']/1000:.3f} | {g['status_publish_us_mean']/1000:.3f} | {g['screenshot_hz']:.3f} | {g['status_read_hz']:.3f} |")
    text+=['','Timer callbacks include prepare/core work and status-file publication. Counters are cumulative and published through the previous completed callback. Raw before/after snapshots retain exact clock values and interval histograms. All surface bounds and process CPU/load snapshots are retained. Surface extrema and prepare_us_max_session are session-cumulative, not independent window extrema. `frame_info` exposes commit seq/damage, not per-upload/present durations or browser display timing.','', 'The residual column in JSON is not assigned to a particular library. The visible browser frame rate and device FPS/RAM remain unmeasured. No public dependency, timer target or texture was changed to chase a number.']
    (out/'AB_COMPARISON.md').write_text('\n'.join(text)+'\n');(out/'ab-summary.json').write_text(json.dumps(groups,indent=2)+'\n');print('\n'.join(text))
if __name__=='__main__':main()
