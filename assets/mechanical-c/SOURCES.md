# 来源与加工记录

## 图像来源

| 材料 | 角色与来源 | 许可/使用说明 |
| --- | --- | --- |
| `assets/originals/concept-C-triptych.png` | 2026-10-21本对话内置image_gen生成，用户随后选择C。原图1942×809，三态概念参考 | AI生成素材；工具未披露底层模型版本、随机种子或专门的图片许可。不得标为CC0、第三方商用图库或独占版权 |
| `assets/originals/c-reference-eye-v3.png` | 前一轮完整机械眼结构稿，作为C生成的主要参考 | 含用户原始机械眼中央核心及AI补绘；原输入包的来源/授权边界保持不变 |
| `assets/originals/c-reference-with-old-frame.png` | C生成时的第二张上下文参考，只提供旧金属配色与构图 | 原旧眼眶不用于C设备素材，也没有被覆盖 |
| `assets/originals/generated-metal-backing.png` | 2026-10-22内置image_gen基于注册C睁眼图补画的全幅金属采样底稿，1254×1254 | AI生成派生素材；只采用外围金属，中央光学区恢复选中C稿的像素 |
| `source/registered_states/concept-*-480.png` | 从选中的三联概念图确定性注册、裁切和缩放得到 | 加工中间素材，不是新的原始生成图或设备运行截图 |

两轮生成均使用内置image_gen，没有调用外部付费图库或额外API。`source/concept-C-generation-prompt.txt`保留C的生成说明，`source/backing-generation-prompt.txt`保留本次补面实际提示词。`source/generation-record.json`记录工具、文件与可获得的元数据。随机重跑不能保证再次获得相同图片，确定性复现从包内原始PNG开始。

用户最初提供的工程美术包为 `eye-surface-art-handoff-v1.zip`，SHA256 `3faaecef36f38f1102774b111b955c79ececa94f33d0917329ae0073409603e7`。该包及其旧机械眼、恶龙眼、夜枭、深海文件未被修改。本包只带必要图像、说明和投影快照，没有复制其工程、.git、依赖、设备数据或缓存。

## 加工与可编辑性

1. 三联稿按 `source/registration.json` 的中心/缩放参数注册为480×480。
2. 补面底稿缩放至500×500，裁切(10,1,490,481)。保留C睁眼图中心r184原像素，仅在外围金属接合；步骤见 `source/build_surface.py`。
3. 从三态中央区提取240×240素材，按六个叶片区域的对应点生成九档。孔径逐档收拢，闭合档将原中央补片收为六叶交点；见 `source/shutter/shutter-rig.json` 和 `build_shutter.py`。
4. PSD提供正常睁眼合成的三个栅格图层；ORA同时保存全部快门档位的可见性；SVG提供收拢姿态下六个可编辑叶片区域，纹理是嵌入位图。它们不是矢量重绘或完整机械CAD。
5. 参考图和视频由包内Python合成器从最终图层渲染；HTML使用同一素材与固定模拟时间线。视频不是实机拍摄，PNG不是C/GSP截图。

## 代码、字体与依赖

- `source/reference/eye_projection.h`来自用户工程快照，保留其原有SPDX Apache-2.0声明；许可正文随附 `source/licenses/Apache-2.0.txt`。Python/JS逆投影公式由该快照改写，仅为参考。
- 本包其余脚本、几何参数、时间线和说明为本轮整理成果；主工程合入时按项目贡献与许可规则处理。图像许可与代码许可分别对待，不将所有AI图像自动归入Apache-2.0。
- 证据画面外英文标签使用系统DejaVu Sans，其源字体为Bitstream Vera许可、DejaVu修改为public domain；本包保留环境提供的版权说明 `source/licenses/DejaVu-fonts-copyright.txt`，没有分发字体二进制。字体不进入480×480角色画面。
- HTML使用浏览器系统字体，未加载网页字体或CDN。原AI概念板文字已烘焙为像素，不声称它使用某个可下载字体。
- 素材加工与参考渲染使用已有Python、Pillow、NumPy；PSD输出使用已有ImageMagick；视频编码使用已有FFmpeg。实际环境版本见 `evidence/verification.json`。本轮没有安装或升级依赖。

## 未验证项

共享C/GSP接入、设备表现、实际资源构建、设备FPS及BSP输入事件均未验证。HTML是否在实际浏览器中验证，以 `preview/preview-checks.json` 为准；不能将脚本检查等同浏览器运行成功。用户已选择C设计方向，不意味着已验收本次新增分层与全角度效果。
