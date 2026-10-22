# 预览与重建依赖

`index.html` 已嵌入PNG和时间线，离线打开无需Node、Python、CDN或网络。Canvas 2D、JavaScript、PNG解码是浏览器预览所需能力，并非设备运行依赖。

实际浏览器运行在本环境未验证（没有Chromium或系统浏览器）。同一HTML中的渲染函数已经使用现有Node与PNG/ImageData适配器执行，结果见 `node-render-checks.json` 及 `../evidence/node-reference-*.png`；这不代替浏览器交互或原生C/GSP检查。

制作工具各有独立用途：

| 操作 | 依赖 |
| --- | --- |
| `python3 preview/build_preview.py --package-root .` | Python标准库，重新嵌入PNG和时间线 |
| `python3 preview/reference_render.py --output /tmp/c.png` | Python、Pillow、NumPy，输出参考PNG |
| `python3 preview/build_evidence.py` | 上述依赖及FFmpeg，重建全部参考图和视频 |
| `python3 source/rebuild_registered_states.py` | Python、Pillow，重新注册三态原图 |
| `python3 source/build_surface.py` | Python、Pillow、NumPy，从原始材料重建表面与镜座 |
| `python3 source/shutter/build_shutter.py --input-dir source/registered_states --output-dir /tmp/c-shutter` | Python、Pillow、NumPy，重建九帧与几何源 |
| `python3 source/build_editable_sources.py` | Python、Pillow、ImageMagick，重建PSD/ORA |

全部命令从解压包根目录执行。包中没有自动安装命令，不绑定新的工程依赖版本。制作环境版本列于 `../evidence/verification.json`；重建结果可能受不同图像库的采样与舍入影响。

时间线固定28秒，无随机移动；`seed=null`表示没有使用随机数。案例和进度控制在480×480角色区域外，时间线里的confirmed/candidate/valid/state都是模拟注入字段，并非已经存在的C API。
