# 来源与加工记录

## 原工程依据

输入为用户上传的 `dragon-sclera-art-handoff-v1.zip`。其中 README 明确：旧眼白由 `dragon_render.c` 的 `eyeball()` 在虹膜外用 RGB(49,63,23) 与正弦纹理生成，没有独立“获选眼白原图”。`template/current-procedural-sclera.png` 是程序底色导出模板；坐标指南和蒙版是制作辅助资料。

输入包内的原虹膜与皮肤资料说明它们曾由 imagegen 为本项目生成。原始图、生产缩放/量化图、程序生成眼皮和预览输出是不同类别。本次没有重画、替换或把它们伪装成新的分层素材。原来源与工程说明的副本保存在 `source/reference/`；实际 C 预览工具及其必要输入位于 `preview/tool/`。

## 新眼白 C

使用 ChatGPT 内置 imagegen 制作。输入参考为旧程序眼白模板，以及输入包 `reference/right.png` 的角色外观；生成目标只包括眼球巩膜材质，不包括虹膜、瞳孔、眼皮或鳞片。

用户先要求更多墨绿色方案，随后选择了 C 的黑绿底色和细纤维方向。精确英文生成说明见 `source/imagegen-prompt.txt`。提示词中的 RGB 是创作意图，不是对实际输出像素的精确声明；交付颜色以选定 PNG 为准。

| 文件 | 分类 | 实际规格 |
| --- | --- | --- |
| `source/layers/01-ai-original.png` | AI 原始输出 | 1254×1254、RGB，2,483,578 B |
| `submission/sclera.png` | 加工后运行候选 | 480×480、RGB，382,300 B |
| `source/sclera-master.psd`、`source/sclera-master.ora` | 后期建立的编辑容器 | 1254×1254 栅格源；原图、空白修饰层、隐藏坐标参考层 |
| `evidence/poses/`、`evidence/motion.mp4` | C 离线参考合成 | 既有角色与新眼白合成后的静态/动态设计参考 |

原始输出 SHA-256：

```text
a3033cd38dffeb06125b6ff7d8081d58eedfe8c66b46d8f67f357a2ece20fd66
```

加工过程为：保持整张正方形构图，使用 Sharp 的 Lanczos3 缩放到 480×480，移除 alpha 通道并导出 RGB PNG。没有追加调色、球体阴影、镜面高光或眼眶合成；本次交接直接拷贝已展示并选定的 480 PNG，不再次重采样。完整哈希和实际工具版本见 `source/provenance.json`，文件校验见 `CHECKSUMS.sha256`。

imagegen 没有披露本次可复用的模型版本或随机种子，不能保证重新生成逐像素同图。保留原始输出、精确提示词和加工步骤，支持从该原始文件继续编辑。PSD / ORA 不是原图生成时的真实分层：细纤维没有被分离成矢量或单独图层，空白修饰层供后续编辑，坐标参考层默认隐藏且不得导入设备。

## 权利与许可

原预览工具和 C 源按输入包附带的 Apache-2.0 文本及原文件声明处理，见 `preview/tool/LICENSE`。这不自动给其中图片追加 Apache、CC0 或第三方图库商用许可。

原图属于用户已有项目资料，权利关系沿用输入资料。新增眼白是本项目通过 imagegen 生成的内容；本包不虚构独家权利、CC0 或其他未提供的图片许可。没有引入外部图库图像。

设备画面无文字，不引入字体资源。参考接触表的图外标注使用 Pillow 12.3.0 内置的 Aileron Regular 子集；实际字体元数据署名 Sora Sagano，权利字段为“No Rights Reserved.”。作者官网亦使用这一声明，并允许使用、修改和再分发，提供无担保说明：[Aileron 官方页面](https://dotcolon.net/fonts/aileron/)（查阅 2026-10-22）。本包没有分发字体二进制，也没有向设备引入字体依赖；该字体声明与本项目图片的权利声明分开处理。

可编辑文件的读取与像素重合成检查结果见 `source/editable-checks.json`；没有声称已完成 Photoshop、Krita 或 GIMP 图形界面的往返编辑验证。所有合成证据均与原生 GSP、设备实拍和检测算法验证明确分开。
