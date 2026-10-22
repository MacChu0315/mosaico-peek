# 复现与依赖

## 直接查看

交付的 PNG 和 MP4 可直接查看；PSD / ORA 用兼容的图像编辑器打开。查看素材不需要安装项目 SDK、浏览器运行时或新固件依赖。

## C 离线参考预览

`tool/preview.py` 和其 `source/` 是用户上传包的逐字节副本。工具在自己的 `build/` 内编译离线 C 可执行文件，在指定输出目录生成图像；不改这些原始 C 文件，也不连接设备或传感器。最终 ZIP 不携带编译产物、缓存或依赖副本。

从交接包根目录执行，输出目录必须尚不存在：

```bash
python3 -B preview/tool/preview.py \
  --surface submission/sclera.png \
  --output /tmp/dragon-c-preview --movie
```

去掉 `--movie` 只输出 11 个静态姿态。去掉 `--surface submission/sclera.png` 复现原程序眼白基线。默认 `--sample-step 2`，对应输入包既有的 240 采样复制到 480 输出；这不授权更改任何其他角色的采样规则。可选 `--sample-step 1` 是更细的离线标量检查，不等于 GSP 验证。

需要已有 Python 3、Pillow、C11 编译器、系统 libm；导出视频另需 FFmpeg。实际使用 Python 3.12.14、Pillow 12.3.0、GCC 13.3.0、FFmpeg 6.1.1。输入包验证环境是 Pillow 10.4.0 / GCC 11.4.0 / FFmpeg 4.4.2；本包在当前环境实际重建基线，并与输入参考逐像素核对，结果见 `evidence/verification.json`。未安装或升级依赖。

本工具的候选注入是 raw RGB 双线性眼白采样，仅用于美术参考。正式资源编码、缓存和 GSP 采样由 main thread 完成。

## 眼白素材与可编辑源重建

正式 `submission/sclera.png` 是用户选中的 C 文件逐字节副本。若要核对从高分原图到 480px 的处理，可使用已有 Node.js 与 sharp：

```bash
node tools/build_surface.cjs /tmp/dragon-c-sclera-rebuilt.png
python3 -B source/build_editable_sources.py
```

素材重建脚本会拒绝覆盖正式提交 PNG。实际生成使用 Node.js v24.19.0、sharp 0.35.5、libvips 8.18.7；脚本优先普通 Node 模块解析，也兼容制作环境的 `CODEX_PRIMARY_RUNTIME_NODE_MODULES`。它不下载依赖。可编辑源构建需要 Python 3 和 Pillow；具体说明见 `source/README.md`。

完整包的只读检查：`python3 -B tools/verify_delivery.py`。它核对选定 PNG、11 个姿态的眼白差分边界、闭眼不变、编辑源文件哈希和整包校验清单，不连接设备。

## 时间线

`motion-timeline.json` 记录原工具的确定性轨迹，`../evidence/input-timeline.csv` 记录 200 个实际导出帧的精确输入。无随机数，也没有检测状态机。8 秒、25fps 是参考视频导出设置，不是设备帧率。静态图覆盖正视、四向、四个对角和半闭／全闭；视频按输入包原轨迹覆盖其中一部分方向并闭合、重新睁开。
