#!/usr/bin/env python3
"""Issue a local diagnostic command; detector and replay remain in native C."""
import argparse,json,socket,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def state():return json.loads((ROOT/'.run/status.json').read_text())
def command(text):
    fields=text.split()
    cases=['empty','motion','multi','gaps','recorded','aging','dragon','idle','live']
    if len(fields)==2 and fields[0]=='case' and fields[1] in cases:text='case '+str(cases.index(fields[1]))
    serial=time.time_ns()%((1<<53)-1)
    with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as sock:sock.sendto(f'{serial} {text}'.encode(),str(ROOT/'.run/control.sock'))
    deadline=time.monotonic()+3
    while time.monotonic()<deadline:
        result=state()
        if result['ack']==serial:
            if result['error']:raise RuntimeError(result)
            return result
        time.sleep(.01)
    raise TimeoutError(text)
def main():
    p=argparse.ArgumentParser();p.add_argument('command',nargs='+',help='case NAME/0..8 | view dragon/diagnostic | pause | play | step | replay | advance MS | draw | status');a=p.parse_args()
    print(json.dumps(state() if a.command==['status'] else command(' '.join(a.command)),indent=2))
if __name__=='__main__':main()
