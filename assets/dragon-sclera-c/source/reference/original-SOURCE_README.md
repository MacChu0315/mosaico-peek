# Peek：单只恶龙眼动效研究

本版响应的设计方向：单只恶龙眼，野性、不屑，带厚眼皮与鳞片。借鉴 Eyes of the Basilisk 的单眼组织方式，未复制该项目图片或代码。

## 查看

- `output/peek-dragon-idle.gif`：待机、左右游视、一次完整眨眼。
- `output/peek-dragon-attention.gif`：克制察觉、右上侧睨、跟随移动、回收目光。
- 同名 MP4 是色彩更完整的视频版本。
- 两段均为 480×480、25 fps、10 秒循环，无音频。

这些是预编排的视觉动效，不包含热目标检测、GSP 集成或设备测量。25 fps 是离线导出设置，不是 Mosaico 实测性能。

## 动作与素材

- `timeline.mjs`：纯 JavaScript 的两个动作时间轴，输入时间秒，输出 gazeX、gazeY、blink、squint、pupilWidth、tension。
- 视线为屏幕坐标，右/下为正；不是已确定的传感器坐标映射。
- `render.mjs`：离线渲染示例，眼球进行球面纹理映射，眼皮单独遮挡眼球。
- `assets/iris.png` 与 `assets/skin.png`：本轮使用内置 imagegen 新生成的素材。提示词见 `art-prompts.json`。

后续可以把原素材与姿态曲线交给 Cursor/Codex，用原生 C 图层或查表方式重现。当前逐像素离线渲染器不是已经优化过的设备实现。正式接口应在 Codex 检测模块交接后通过适配层连接。

## 重现本地导出

本次使用 Node.js、`@napi-rs/canvas` 0.1.100 和 FFmpeg 6.1.1。在已安装这些依赖的环境中：

```sh
node render.mjs stills
node render.mjs movies
```

每段 MP4 可以用 FFmpeg 的 palettegen/paletteuse 转成循环 GIF；本次使用全片统一 256 色调色板及 Bayer 抖动。PNG 关键帧与 GIF 编码帧已检查，元数据及循环接缝检查结果在 `output/validation.json`。实机和实时输入均未验证。

参考项目：https://www.anhadsawhney.com/eyes-of-the-basilisk
