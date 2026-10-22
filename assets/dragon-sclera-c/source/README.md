# C 方案：可编辑栅格源

`sclera-master.psd` 与 `sclera-master.ora` 均为 **1254×1254** 的编辑容器。默认合成保持已选 C 方案 AI 原始输出的像素，不重新生成或重画。

自上而下有三个实际栅格图层：

1. `03 Geometry guide - HIDDEN`：默认隐藏的坐标辅助层。红圈表示球面半径，黄圈表示现有虹膜覆盖边界；导出时必须保持隐藏。
2. `02 Retouch - initially blank`：全透明空白修饰层，可用于后续局部修图；当前没有修改。
3. `01 AI original - flattened raster`：AI 的原始完整栅格输出。细纤维与底色已经合在这张图里，不能当作独立可编辑的绘画图层或矢量路径。

`layers/01-ai-original.png` 是生成原图的逐字节副本；另外两张 PNG 分别对应空白修饰层和隐藏辅助层。PSD / ORA 是后来制作的编辑容器，不是模型生成时就存在的原始 PSD，也不包含现有龙眼虹膜、皮肤或程序眼睑的伪造分层。

辅助线使用交接包的 480 坐标：中心 `(240,240)`、球面半径 `233`、虹膜半径 `233*26870/32768 ≈ 191.06`，统一乘以 `1254/480` 显示。它们只帮助识别纹理采样范围，不是屏幕蒙版，也不应烘焙进最终眼白。

## 运行素材与导出

正式提交的 `../submission/sclera.png` 是此前静态对比中用户选定的 **480×480、RGB、不透明 C 方案**，直接拷贝原文件，不经 PSD/ORA 再导出或重采样。其 SHA-256 为：

```text
5775c62ce834c1e3573148241f2589e434d0226a9cea4d88ad78348d2c4c9887
```

在编辑器中打开高分源后，默认合成应看到纯眼白材质，不应看到圈线。若将来确实编辑并重新缩放，请采用主交接说明中的处理方法和原 C 预览复核；不同编辑器的缩放、色彩管理或 PNG 输出可能改变像素，不能据此覆盖已选提交图并宣称内容不变。

## 已验证与未验证

`editable-checks.json` 记录实际检查：三个图层重新读取、默认合成以及 merged preview 均与原图逐像素一致；ORA ZIP CRC 通过。PSD 还通过已安装 ImageMagick 的独立读取检查。

这些检查不等于已在 Photoshop、Krita 或 GIMP 的图形界面中完成往返编辑测试。没有 GSP 或设备验证声明。

## 重建编辑容器

在完整包根目录运行：

```sh
python3 -B source/build_editable_sources.py
```

依赖为 Python 3 和 Pillow；如果已有 ImageMagick `convert`，脚本会额外读取 PSD 校验。脚本不会安装依赖，不会改变 `submission/sclera.png`，也不会写入主工程。实际版本以 `editable-checks.json` 为准。
