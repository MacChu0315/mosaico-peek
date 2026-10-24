#!/usr/bin/env python3
import json,hashlib,subprocess,zipfile,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    movie=ROOT/'review/deep-sea-r1-vs-r2.mp4'
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,nb_frames,r_frame_rate','-of','json',str(movie)],text=True))
    assert float(info['format']['duration'])==12.5 and info['streams'][0]['nb_frames']=='750'
    (ROOT/'review/video-check.json').write_text(json.dumps(info,indent=2)+'\n')
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(movie),'-frames:v','1',str(ROOT/'review/poster.png')],check=True)
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>深海R2 · 修订审阅</title><style>body{background:#10191e;color:#dce8e7;font:16px/1.7 system-ui,sans-serif;margin:0}main{max-width:1120px;margin:auto;padding:32px 20px}h1{font-size:30px}p{color:#afc3c6}a{color:#e9c383}video,img{max-width:100%;height:auto}video{display:block;width:960px;background:black}.note{border-left:3px solid #d1ae76;background:#1c2a2e;padding:12px 18px}.links{display:flex;gap:20px;flex-wrap:wrap}section{margin:24px 0}footer{border-top:1px solid #34474d;padding:20px 0;font-size:14px}</style><main><h1>深海 R2 · 去暗块／取消回正补圈／加快瞬膜</h1><p>本轮只修订深海。R1和夜枭保留原样；没有接入主工程或操作设备。</p><div class="note">R2不再把“整个正视画面零差异”作为目标。瞳孔和近瞳高光保持原像素，周围虹膜做明暗匹配；残余接合与亮度仍待视觉审阅。</div><section><h2>同时间轴对照：左R1，右R2</h2><video controls loop preload="metadata" poster="review/poster.png"><source src="review/deep-sea-r1-vs-r2.mp4" type="video/mp4"></video><p>约5秒处慢回正；6.3秒和8.1秒开始瞬膜。R1为1,400ms，R2为100＋20＋120＝240ms。60fps是视频导出设置，不是设备性能。</p></section>'''
    for file,title in [('surfaces-r1-vs-r2.png','眼球纹理：不再粘着眼眶形贴片'),('return-to-center.png','回正检查：同一张纹理，没有补圈淡入'),('static-r1-vs-r2.png','同姿态静态对照（每对左旧右新）')]:html+=f'<section><h2>{title}</h2><a href="review/{file}"><img src="review/{file}" alt="{title}"></a></section>'
    html+='''<footer><div class="links"><a href="README.md">修改范围与重建命令</a><a href="recipe.json">R2参数</a><a href="review/validation.json">校验结果</a></div><p>独立审阅版本 · 未声称完整原虹膜无阴影分层已恢复 · 未做原生或设备验证</p></footer></main></html>'''
    (ROOT/'index.html').write_text(html)
    for path in re.findall(r'(?:src|href|poster)="([^"]+)"',html):assert (ROOT/path).is_file(),path
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.so','.o') and p.name!='CHECKSUMS.sha256']
    sums={str(p.relative_to(ROOT)):digest(p) for p in sorted(files)}
    (ROOT/'CHECKSUMS.sha256').write_text(''.join(h+'  '+n+'\n' for n,h in sums.items()))
    target=ROOT.with_suffix('.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[ROOT/'CHECKSUMS.sha256']:z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for n,h in sums.items():assert hashlib.sha256(z.read(ROOT.name+'/'+n)).hexdigest()==h
    h=digest(target);target.with_suffix('.zip.sha256').write_text(h+'  '+target.name+'\n');print(json.dumps(dict(zip=str(target),bytes=target.stat().st_size,sha256=h,files=len(files)+1),indent=2))
if __name__=='__main__':main()
