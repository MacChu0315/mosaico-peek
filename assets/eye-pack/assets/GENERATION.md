# AI 图像生成与加工记录

本文件区分已选定的生成原图、补充的闭眼材质参考，以及可重建的透明分层素材。生成图像不构成 C/GSP 运行截图或硬件证据。

## 来源与生成方式

- 生成日期：2026-10-21。
- 生成工具：本会话的 `image_gen` 图像生成/编辑工具。工具未在结果中提供可固定的底层模型版本或随机种子；不虚构此信息，也不保证重新生成逐像素相同。
- 三张睁眼原图：用户已经选定的夜枭眼、深海眼、机械眼，原始返回尺寸均为 1254×1254。按原始字节保存到 `assets/originals/`，没有覆盖既有恶龙眼。
- 初次生成以用户提供的现有恶龙眼图片作为视觉系列参考；该参考图片未收入运行素材，也未复制到本包。其来源与权利未由本包重新认定。
- 三张闭眼参考：以各自已选定的原图为输入，使用局部编辑说明生成。完整参考留在 `assets/design-reference/`。生成工具可能改变开口外像素，因此加工时只取眼睛开口内的闭眼材质；固定前景始终来自获选原图。
- 图片均为 AI 生成或 AI 编辑素材，不标作摄影、人工逐帧原画或来自某一第三方素材库。授权边界见 `SOURCES_AND_LICENSES.md`；图片不在本包代码 MIT 许可范围内。

## 可重复的加工步骤

`tools/build_assets.cjs` 使用 Node 与构建工具 `@napi-rs/canvas`，没有安装或升级主工程依赖。以下处理是确定性像素加工：

1. 将已选原图一次缩放至 480×480，保存 `neutral.png` 供对照。
2. 使用明示的 Bézier 开口路径，将固定前景和活动眼球拆开；路径、锚点、尺寸在 `assets/manifest.json` 中。
3. 眼球保护区取 `ceil(hypot(maxX,maxY)) + 3` 像素，覆盖最大斜向位移。画面边界外仅延展最近的源边缘像素；不新画虹膜，不改变默认合成画面。
4. 从闭眼参考的开口内材质生成 `lid_00.png` 至 `lid_08.png` 九级 Alpha 覆盖帧。闭合材质固定，显示区逐步覆盖眼球；这是可用精灵实现的参考效果，并非真实皮肤形变或逐叶片机械仿真。
5. 导出独立透明 PNG、本地预览图像容器和清单 SHA-256。校验中性合成与缩放原图一致，并检查中心、四向和四个对角的遮盖完整性。

这种加工保留睁眼获选视觉；动态眼球运动属于小幅二维贴图平移。无需 WebGL、实时模糊、动态光照、第三方运行时或设备字体。

## 原图生成说明（逐字记录）

原始提示词中的 `[image_picker_background_preview]` 是当时预览选图流程的包装标记，不是设备图像内容。下列其余内容为传给生成工具的原始说明。

### 夜枭眼 — night_owl

对应 `originals/night_owl.png`。

```text
[image_picker_background_preview]

Create ONE square, edge-to-edge, high-quality static CHARACTER UI CONCEPT for a 480x480 embedded display. Not a collage, not a review sheet, not a device mockup.
REFERENCE ROLE: the attached image is the approved existing dragon-eye UI. Use it as the visual-series reference ONLY. Preserve its artistic grammar: an extreme close-up of a SINGLE eye, dark richly detailed material filling EVERY edge of the square, beautifully detailed iris, one dominant focal point, restrained highlights and deep dimensional shadows. A creature or mechanism seems to be directly behind the glass. Create a new image; do not change or overwrite the original.
Shared composition across this series: the single eye is centered at approximately x=50%, y=55%; the eye opening spans about 80-88% of image width and 45-52% of image height. The upper brow/eyelid forms a strong arch like in the reference. Surrounding material extends beyond all four edges, no outer head silhouette, no free-floating character, no empty solid margins. Straight-on near-frontal view, centered forward gaze, neutral attentive state. Main light from upper left, subtle iris/lens reflections, corners naturally darkened but material still visible. Match the supplied reference's tactile, painterly-realistic premium game-art finish and texture density. Fixed prepainted illumination; no real-time effects implied.
ONLY the character's single eye and immediate surrounding material. NO second eye, full face, nose, beak, mouth, body, hands, scene, background landscape, frame, bezel, buttons, target dot, cursor, labels, letters, numbers, logos or watermarks. No decorative symbols, floating lights, particle effects, neon bloom, magical rays or HUD. The result itself must be one uninterrupted square screen artwork with no captions.

VARIANT 1 — NIGHT OWL EYE:
An extreme macro crop of just ONE owl-like eye, quietly inquisitive and watchful. The surrounding dragon scales are replaced with densely layered charcoal-brown and muted umber FEATHERS: very fine down near the eyelid, longer softly overlapping feather tips further from the eye, their growth flowing around the eye socket. Distinctive feathery brow and feather-fringed lower eyelid, real feather barbs visible without looking like mammal fur. All feathers remain dark; sparse warm gray edge highlights only. No ear or beak or second eye is visible.
The iris is richly textured warm COPPER-ORANGE / burnt amber with fine radial fibres and an irregular dark outer ring. Its pupil is perfectly ROUND and black, about 34% of visible iris diameter, clearly unlike the source's vertical slit. Natural reflective depth, tiny restrained catchlight, no neon or white sclera wedge. A large mostly round iris is partially occluded by soft arched upper and lower lids to fit the broad horizontal eye opening, so the composition still belongs with the dragon reference. Slight weight in the upper lid gives intelligence and focus without looking angry.
Priority: immediately recognizable feather material + round pupil; same close-up scale, dark tonal range and detailed finish as the dragon. Not a wildlife photograph showing an owl's entire head.
```

### 深海眼 — deep_sea

对应 `originals/deep_sea.png`。

```text
[image_picker_background_preview]

Create ONE square, edge-to-edge, high-quality static CHARACTER UI CONCEPT for a 480x480 embedded display. Not a collage, not a review sheet, not a device mockup.
REFERENCE ROLE: the attached image is the approved existing dragon-eye UI. Use it as the visual-series reference ONLY. Preserve its artistic grammar: an extreme close-up of a SINGLE eye, dark richly detailed material filling EVERY edge of the square, beautifully detailed iris, one dominant focal point, restrained highlights and deep dimensional shadows. A creature or mechanism seems to be directly behind the glass. Create a new image; do not change or overwrite the original.
Shared composition across this series: the single eye is centered at approximately x=50%, y=55%; the eye opening spans about 80-88% of image width and 45-52% of image height. The upper brow/eyelid forms a strong arch like in the reference. Surrounding material extends beyond all four edges, no outer head silhouette, no free-floating character, no empty solid margins. Straight-on near-frontal view, centered forward gaze, neutral attentive state. Main light from upper left, subtle iris/lens reflections, corners naturally darkened but material still visible. Match the supplied reference's tactile, painterly-realistic premium game-art finish and texture density. Fixed prepainted illumination; no real-time effects implied.
ONLY the character's single eye and immediate surrounding material. NO second eye, full face, nose, beak, mouth, body, hands, scene, background landscape, frame, bezel, buttons, target dot, cursor, labels, letters, numbers, logos or watermarks. No decorative symbols, floating lights, particle effects, neon bloom, magical rays or HUD. The result itself must be one uninterrupted square screen artwork with no captions.

VARIANT 2 — FICTIONAL DEEP-SEA CREATURE EYE:
An extreme macro crop of just ONE eye of an original mysterious soft-bodied deep-sea creature. Surrounding material is dark indigo and blue-gray living SKIN, not scales and not feathers. The texture is smooth but richly tactile, with tiny pores, subtle mottling, concentric soft folds around the socket and two heavy pliable eyelid ridges. The folds must belong to organic tissue and must not look like hard reptile scales or metal armor. Deep cool blue shadows, restrained desaturated teal on the top-left folded edges. No fins, tentacles or other body parts.
A vivid but non-emissive icy TURQUOISE / sea-glass blue iris with intricate thin radial threads and subtle concentric organic rings. A BLACK HORIZONTAL OVAL pupil, clearly distinguishable from the dragon's vertical slit and the owl's round pupil. Keep the oval centrally located and anatomically plausible for this fictional creature, with rounded ends. Small damp catchlight only. No glowing beam, no bright white sclera, no lightning pattern outside the iris.
The upper lid is thicker, softer and slightly more hooded than the dragon's; lower lid has a fine wet-looking rim. A thin inset eyelid fold at the inner corner suggests a protective membrane, but the eye is fully open and its pupil unobstructed. The expression is quiet, enigmatic and alive, with no exaggerated anger.
Priority: distinct folded skin anatomy and horizontal pupil, same premium dark macro character-portrait composition as the dragon, not a dragon recolored blue.
```

### 机械眼 — mechanical

对应 `originals/mechanical.png`。

```text
[image_picker_background_preview]

Create ONE square, edge-to-edge, high-quality static CHARACTER UI CONCEPT for a 480x480 embedded display. Not a collage, not a review sheet, not a device mockup.
REFERENCE ROLE: the attached image is the approved existing dragon-eye UI. Use it as the visual-series reference ONLY. Preserve its artistic grammar: an extreme close-up of a SINGLE eye, dark richly detailed material filling EVERY edge of the square, beautifully detailed iris, one dominant focal point, restrained highlights and deep dimensional shadows. A creature or mechanism seems to be directly behind the glass. Create a new image; do not change or overwrite the original.
Shared composition across this series: the single eye is centered at approximately x=50%, y=55%; the eye opening spans about 80-88% of image width and 45-52% of image height. The upper brow/eyelid forms a strong arch like in the reference. Surrounding material extends beyond all four edges, no outer head silhouette, no free-floating character, no empty solid margins. Straight-on near-frontal view, centered forward gaze, neutral attentive state. Main light from upper left, subtle iris/lens reflections, corners naturally darkened but material still visible. Match the supplied reference's tactile, painterly-realistic premium game-art finish and texture density. Fixed prepainted illumination; no real-time effects implied.
ONLY the character's single eye and immediate surrounding material. NO second eye, full face, nose, beak, mouth, body, hands, scene, background landscape, frame, bezel, buttons, target dot, cursor, labels, letters, numbers, logos or watermarks. No decorative symbols, floating lights, particle effects, neon bloom, magical rays or HUD. The result itself must be one uninterrupted square screen artwork with no captions.

VARIANT 3 — MECHANICAL OPTICAL EYE:
An extreme macro crop of ONE engineered optical eye, precise and observant. The square is filled edge-to-edge with the surrounding dark gunmetal and graphite ceramic HOUSING; no full robot head or external casing silhouette visible. Layered subtly worn armor plates with finely machined joints and tiny unmarked recessed fasteners form a broad arched upper brow and curved lower socket, echoing the dragon's eye composition. Texture is sophisticated matte metal with light brushing and edge wear, not heavily rusty steampunk and not glossy white plastic. The metal must look like a coherent built mechanism.
A broad horizontal mechanical eyelid opening reveals a single front-facing optical lens. The circular front glass iris is AMBER / muted warm brass inside the dark housing, partially occluded at its top/bottom by the upper and lower mechanical shutters to retain the reference's broad eye-shaped opening. Inside the lens, a crisp DARK SIX-BLADED APERTURE forms the pupil; the surrounding subtle concentric optical elements and fine radial machining are unmistakably mechanical, not an organic iris texture. Small fixed upper-left glass reflection and restrained warm internal reflections only. No luminous reticle, no digits, no warning stripes, no neon halo.
Keep lens front nearly flush to the surrounding housing, not a protruding camera barrel, and not a camera sitting on a dark background. Upper and lower shutter plates are open in an attentive neutral pose; their construction is readable and could later close over the lens.
Priority: one rich tactile mechanical eye with a precise aperture, same macro framing, visual weight, dark palette and baked lighting as the dragon reference.
```

## 闭眼编辑说明（逐字记录）

### 夜枭眼

输入：对应的已选原图；输出：`design-reference/night_owl_closed_generated.png`。

```text
Edit the attached approved eye artwork to create the CLOSED-EYE material reference for the exact same character UI.
This is a tightly scoped local edit: preserve the full square composition, original resolution/aspect, outer eye socket outline, all surrounding feathers/skin/metal, lighting, camera and texture character. Change ONLY the exposed eye aperture into naturally closed eyelids/shutters. Keep exterior geometry pixel-aligned as closely as possible. No new design, no head outline, no scene, no text, no annotations, no panels, no bezel.
The copper owl eye is fully asleep. The upper eyelid has descended and the lower lid has lifted, completely concealing the entire iris and pupil. Fill the entire former eye opening with softly layered dark brown eyelid skin and fine short downy feathers, continuous with the existing owl-feather surround. The two lids meet along one fine curved dark seam at the approximate horizontal mid-height of the existing eye opening. Very fine small feathers near the eyelid seam. No copper iris, black pupil, empty black hole, or white eyeball remains visible. A quietly resting owl eye, not a flat feather wallpaper pasted over an eye.
The top and bottom lids should retain believable material depth with restrained shading. Keep the inner closing seam approximately at 55% of the full image height, matching the original eye center, and spanning the original eye aperture. The full square must stay filled with the original character material. We will use this only as a material source for an isolated closed-eye layer while preserving the exact original outer frame.
```

### 深海眼

输入：对应的已选原图；输出：`design-reference/deep_sea_closed_generated.png`。

```text
Edit the attached approved eye artwork to create the CLOSED-EYE material reference for the exact same character UI.
This is a tightly scoped local edit: preserve the full square composition, original resolution/aspect, outer eye socket outline, all surrounding feathers/skin/metal, lighting, camera and texture character. Change ONLY the exposed eye aperture into naturally closed eyelids/shutters. Keep exterior geometry pixel-aligned as closely as possible. No new design, no head outline, no scene, no text, no annotations, no panels, no bezel.
The turquoise deep-sea creature eye is fully asleep. Its thick upper and lower soft indigo-blue eyelids are CLOSED over the complete former eye opening. Fill the former cyan iris region with soft slightly folded blue-gray eyelid membrane with tiny tactile pores consistent with the surrounding skin. The upper and lower lids meet in a single gently arched dark seam through the approximate middle height of the original eye. No turquoise iris, black pupil, empty hole, or light-emitting surface visible. It must look like the same living creature peacefully closing its eye, with subtle softness and volume.
The top and bottom lids should retain believable material depth with restrained shading. Keep the inner closing seam approximately at 55% of the full image height, matching the original eye center, and spanning the original eye aperture. The full square must stay filled with the original character material. We will use this only as a material source for an isolated closed-eye layer while preserving the exact original outer frame.
```

### 机械眼

输入：对应的已选原图；输出：`design-reference/mechanical_closed_generated.png`。

```text
Edit the attached approved eye artwork to create the CLOSED-EYE material reference for the exact same character UI.
This is a tightly scoped local edit: preserve the full square composition, original resolution/aspect, outer eye socket outline, all surrounding feathers/skin/metal, lighting, camera and texture character. Change ONLY the exposed eye aperture into naturally closed eyelids/shutters. Keep exterior geometry pixel-aligned as closely as possible. No new design, no head outline, no scene, no text, no annotations, no panels, no bezel.
The amber mechanical eye is in resting mode. The upper and lower outer curved protective shutters are fully CLOSED across the entire former exposed lens opening. Fill the former amber lens region with matching dark gunmetal shutter plates, fine brushed machining and restrained wear, with a thin gently curved horizontal mating seam at the approximate middle height of the original eye opening. The shutters slide vertically; do not make a radial camera iris shrinking in the middle, and do not leave any amber light, black opening, or lens exposed. Existing surrounding housing plates and screws stay exactly where they were. Clear coherent protective mechanical closure, not a differently shaped robot.
The top and bottom lids should retain believable material depth with restrained shading. Keep the inner closing seam approximately at 55% of the full image height, matching the original eye center, and spanning the original eye aperture. The full square must stay filled with the original character material. We will use this only as a material source for an isolated closed-eye layer while preserving the exact original outer frame.
```

## 校验与分类

全部原始、参考及加工图的相对路径、实际字节数、尺寸和 SHA-256 见 `assets/manifest.json`。关键状态截图和演示来自共享 JavaScript 模型及离屏 Canvas 渲染器的实际执行，详见 `evidence/README.md`，不能被重新标为设备实拍或 C/GSP 截图。固定种子及时间线属于可重复的动作参考；不属于原图生成种子，也不验证检测算法。


## 原始与闭眼输入文件 SHA-256

| 文件 | SHA-256 |
|---|---|
| `assets/originals/night_owl.png` | `555a4fa7e04fda422a0c57ffe9f0890284d6bca36c955fc79df6703cead2b173` |
| `assets/design-reference/night_owl_closed_generated.png` | `32ad6d0e7d41659da238b543f8eb22eeb1f058cf382312f740daaa3c0946a05f` |
| `assets/originals/deep_sea.png` | `61f282f442abd0f92ff0e8780bc675373338ea5845e36f60c5d053e55a0e309d` |
| `assets/design-reference/deep_sea_closed_generated.png` | `cc385e84b45d39f8a3b6ba124bdecda7cb7c62250df238136b89ff259ea8cdd3` |
| `assets/originals/mechanical.png` | `3eba1f5c3fe7ac4b23fce090b75248d464a2a9f66f362bd5097b920da67eaede` |
| `assets/design-reference/mechanical_closed_generated.png` | `81d77ffd667662fd0f8a59bcbc859e45d7315ac919699de8c5553d951685d494` |
