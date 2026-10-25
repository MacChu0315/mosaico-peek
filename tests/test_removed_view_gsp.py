#!/usr/bin/env python3
"""Reject retired view through both Host entry points without changing source."""
import json,os,socket,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from control import command,state
out=Path(os.environ.get('PEEK_EVIDENCE_DIR',ROOT/'evidence/remove-owl/native-rejection'));out.mkdir(parents=True,exist_ok=True)
command('view deep_sea');command('case dragon');command('advance 10750');before=state()
for args in (['tools/preview.py','--view','night_owl','--no-build','--headless'],['tools/control.py','view','night_owl']):
    run=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True);assert run.returncode!=0
    assert 'night_owl' in run.stderr or 'retired view' in run.stderr
assert state()['view']=='deep_sea' and state()['error']==0
order=[]
for _ in range(9):
    s=command('next');order.append(s['view']);assert s['result']==before['result'] and s['role']==before['role']
assert order==['mechanical','dragon','deep_sea']*3
before=state()
serial=time.time_ns()%((1<<53)-1)
with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as sock:sock.sendto(f'{serial} view night_owl'.encode(),str(ROOT/'.run/control.sock'))
deadline=time.monotonic()+3
while state()['ack']!=serial and time.monotonic()<deadline:time.sleep(.01)
after=state();assert after['ack']==serial and after['view']=='deep_sea' and after['error']==258
for key in ('result','role','render_layers','actions'):assert before[key]==after[key],key
(out/'report.json').write_text(json.dumps(dict(retired_backend_command_error=258,source_state_preserved=True,CLI_entries_reject=True,forward_cycles=order),indent=2)+'\n')
print('PASS retired view rejected by backend/CLIs; three-view cycles preserve detector/role')
