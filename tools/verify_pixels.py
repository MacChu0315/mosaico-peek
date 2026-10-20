#!/usr/bin/env python3
"""Optional Pillow check: actual GSP white target cross agrees with native results."""
import json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
    root=ROOT/'evidence/gsp';checks=json.loads((root/'checks.json').read_text());rows=[s for s in checks if s['check'].startswith('motion frame ')]
    report=[]
    for index in (2,12,30,52,60):
        result=rows[index]['result'];image=Image.open(root/f'motion-{index:02d}.png').convert('RGB')
        points=[(x,y) for y in range(288) for x in range(384) if image.getpixel((48+x,76+y))==(255,255,255)]
        assert bool(points)==result['target'],(index,result,len(points))
        expected=None;actual=None
        if points:
            expected=[int((result['x']+.5)*12),int((result['y']+.5)*12)]
            actual=[(min(p[0] for p in points)+max(p[0] for p in points))/2,(min(p[1] for p in points)+max(p[1] for p in points))/2]
            assert all(abs(a-b)<=1 for a,b in zip(expected,actual)),(index,expected,actual)
        report.append({'frame':index,'target':result['target'],'heatmap_white_pixels':len(points),'expected_cross':expected,'actual_cross':actual})
    (root/'pixel-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS rendered heatmap: native target/cross agreement on 5 retained GSP captures')
if __name__=='__main__':main()
