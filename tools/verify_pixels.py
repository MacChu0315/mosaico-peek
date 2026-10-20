#!/usr/bin/env python3
"""Optional Pillow check: actual GSP white target cross agrees with native results."""
import json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
    root=ROOT/'evidence/gsp';checks=json.loads((root/'checks.json').read_text());rows=[s for s in checks if s['check'].startswith('motion frame ')]
    report=[]
    for index in (0,12,30,52,60,79):
        result=rows[index]['result'];image=Image.open(root/'motion'/f'{index:03d}.png').convert('RGB')
        white=sum(p==(255,255,255) for p in image.crop((48,76,432,364)).getdata())
        assert (white>0)==result['target'],(index,result,white)
        report.append({'frame':index,'target':result['target'],'heatmap_white_pixels':white})
    (root/'pixel-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS rendered heatmap: native target/cross agreement on 6 GSP captures')
if __name__=='__main__':main()
