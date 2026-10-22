# 素材清单

设备接入候选只位于 `processed/`。`originals/` 是出处与生成记录，不直接编入设备。

| 类别 | 文件 | 用途 / 尺寸 |
| --- | --- | --- |
| 加工后，移动底图 | `processed/eye_surface.png` | 480×480 RGBA8不透明；完整金属采样面+琥珀镜片，原点(0,0) |
| 加工后，固定镜座 | `processed/frame.png` | 480×480 RGBA8，屏幕原点(0,0)，内开口透明、外部黑色 |
| 加工后，局部开合帧 | `processed/shutter/shutter_00.png` … `shutter_08.png` | 每张240×240 RGBA8；眼球贴图原点(120,125)，00开/04收拢/08闭 |
| 原始AI概念参考 | `originals/concept-C-triptych.png` | 1942×809三态概念图，用户选择的C方向 |
| 生成输入参考 | `originals/c-reference-eye-v3.png` | 480×480前一轮完整眼球，用于C的图像生成 |
| 生成上下文参考 | `originals/c-reference-with-old-frame.png` | 480×480旧框构图参考；旧眼皮不是本包运行素材 |
| 新生成的原始补面 | `originals/generated-metal-backing.png` | 1254×1254连续金属底稿，仅采用外围区域 |

更详细的逐文件尺寸、字节数、SHA256、alpha范围和坐标在 `manifest.json`。透明度使用straight alpha；完全透明像素RGB清零。快门孔径透明，必须露出公共底图的原黑孔。

## 源文件与设计参考的区别

- `../source/mechanical_c.psd`：可编辑三个栅格图层（镜座、开态快门、移动底图）。
- `../source/mechanical_c.ora`：同一合成，保留全部九档快门图层；其余八档默认隐藏。
- `../source/shutter/shutter-rig.svg`：收拢姿态的六个叶片分组，纹理为嵌入位图；几何可编辑，不是矢量绘制或机械CAD。
- `../source/registered_states/`：加工中间图，按原三联图注册裁切，仅供素材重建。
- `../evidence/`：从加工后素材实际合成的Python/JS参考输出，全部明确为模拟；没有原生C/GSP或设备截图。

来源及许可说明见 `../SOURCES.md`。所有像素图均由用户原项目图像和本对话AI生成图派生；没有使用第三方图库。不将AI图片虚构为CC0或专有商用授权。
