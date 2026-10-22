# 龙眼 C · 黑绿纤维眼白交接

用户在 2026-10-22 的静态对比中选择了 C：黑绿色底、细密且低对比的纤维纹理。本包冻结这张已展示的眼白，不重新生成或调色。它只替换现有 dragon 的程序眼白，原虹膜、竖瞳、紫黑鳞片、眼睑、闭眼造型、摆幅和动作时序均沿用主工程。

## 先看这些文件

| 入口 | 用途 |
| --- | --- |
| `submission/sclera.png` | 正式交回的 480×480 RGB 不透明眼白纹理；与获选 C 文件逐字节一致 |
| `source/sclera-master.psd`、`source/sclera-master.ora` | 1254×1254 可编辑栅格源；原图、空白修饰层和默认隐藏的坐标参考层 |
| `source/layers/01-ai-original.png` | 本次 AI 原始输出，1254×1254 RGB |
| `source/imagegen-prompt.txt`、`source/provenance.json` | 精确提示词、来源、加工方法、工具版本与哈希 |
| `evidence/poses/contact-sheet.png` | 正视、四向、四对角、半闭及全闭，共 11 个姿态 |
| `evidence/motion.mp4` | 8 秒转动、闭合和睁开的 C 离线参考；25fps 是导出设置 |
| `preview/motion-timeline.json`、`evidence/input-timeline.csv` | 固定演示曲线与逐帧姿态输入 |
| `INTEGRATION.md`、`SOURCE.md` | 接入边界、素材规格和来源说明 |
| `evidence/verification.json`、`source/editable-checks.json` | 像素保留、文件和可编辑源重合成检查 |
| `CHECKSUMS.sha256` | 交付文件校验清单 |

`submission/sclera.png` 的 SHA-256：

```text
5775c62ce834c1e3573148241f2589e434d0226a9cea4d88ad78348d2c4c9887
```

## 重现参考预览

从解压后的本包根目录执行，输出目录必须尚不存在：

```bash
python3 -B preview/tool/preview.py \
  --surface submission/sclera.png \
  --output /tmp/dragon-c-preview --movie
```

只需静态图时去掉 `--movie`。工具输出 11 个姿态、相应眼白影响蒙版、接触表和 `render.json`；加 `--movie` 后另导出 8 秒视频。无新纹理的基线可以省略 `--surface`，并指定另一个尚不存在的输出目录。

依赖为已有 Python 3、Pillow、C11 编译器和系统 libm；视频另需 FFmpeg。具体版本和使用限制见 `preview/DEPENDENCIES.md`。不需要浏览器、HTML 或新设备运行时，不要为查看本包升级主工程依赖。

## 完成与验收边界

素材保留范围已通过 11 个静态姿态检查：相对原包参考，变化都落在各姿态的眼白影响蒙版内，全闭眼画面不变。可编辑源的默认合成应以随包检查记录为准；空白修饰层和隐藏参考层不是 AI 原生分层，纤维细节仍是栅格像素。

这些图像和视频使用原包的 C 绘制器及预览专用眼白采样分支，属于**实际执行的 C 离线参考合成**；不是原生 GSP 截图、固件接入完成证明、实时热源输入或设备录像。用户选择 C 的视觉方向不等于原生工程验收。生产资源编码、缓存、速度、内存和实机色彩仍由 main thread 验证。

本包依据上传的 `dragon-sclera-art-handoff-v1.zip` 快照。未取得主工程最新 `AGENTS.md`、`README`、`docs/HANDOFF.md`，接入时必须先核对它们。未修改主工程、其他角色、共享检测、全局手势或设备配置。
