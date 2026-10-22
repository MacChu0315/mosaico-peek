# 机械眼 C · 圆形镜座与内部快门

本包把已选定的 C 方向整理为独立美术交接：完整琥珀色机械眼球、中央快门开合素材、固定圆形镜座，以及源文件和可复现的参考预览。中央快门随眼球转动；固定镜座保持在屏幕原位。休眠由中央快门闭合表达。

这是素材与参考动作包。共享 C / 原生 GSP 接入、固件资源构建、设备运行与性能验证由主工程完成。本包没有修改主工程、检测模块、全局切换、设备配置或其他角色。

## 从哪里开始

| 入口 | 用途 |
| --- | --- |
| `evidence/overview.png` | 先看正视、快门开合与分层效果 |
| `preview/index.html` | 双击打开的离线参考预览；PNG 已内嵌，无 CDN、构建工具或设备连接 |
| `evidence/all-angles-open.png`、`evidence/all-angles-closed.png` | 检查全开 / 全闭的九方向效果 |
| `evidence/scenario-reference.mp4`、`evidence/aperture-cycle.mp4` | 固定模拟场景与中央快门开合演示 |
| `evidence/rotation-reference.mp4` | 8秒固定姿态扫描，检查原摆幅下的四向与对角 |
| `assets/processed/` | 接入所需的 PNG 素材；具体规格见下表与 `VISUAL_SPEC.md` |
| `source/mechanical_c.psd`、`source/mechanical_c.ora` | 可编辑栅格分层源文件 |
| `source/shutter/shutter-rig.svg`、`shutter-rig.json`、`build_shutter.py` | 单姿态六叶片编辑参考、形变参数和九帧构建脚本 |
| `MOTION_SPEC.md`、`INTEGRATION.md` | 状态动作、接入边界、资源估算与待确认项 |
| `SOURCES.md`、`evidence/verification.json` | 来源 / 制作说明及实际检查记录 |

原始概念图只作为设计参考，不直接作为完整运行图层。`source/build_surface.py` 与 `source/registered_states/` 保留眼球表面的重建材料。PSD 包含开态的三个栅格层；ORA 另外保留八张隐藏的快门状态。SVG 是单姿态六叶片可编辑参考，不是完整光圈物理模型；重新生成动画应使用 JSON 参数及构建脚本。

## 加工素材

所有坐标均以眼球贴图或屏幕左上角为原点，x 向右、y 向下。

| 文件 | 尺寸 / 原点 | 用途 |
| --- | --- | --- |
| `assets/processed/eye_surface.png` | 480×480 RGBA8，原点 `(0,0)`，alpha 全 255 | 完整眼球底图，保留开态的原黑孔底色 |
| `assets/processed/shutter/shutter_00..08.png` | 每帧 240×240 RGBA8，贴图原点 `(120,125)`，本地中心 `(120,120)` | 中央快门；本地半径 110px 外及开孔区域透明；00 全开，08 全闭 |
| `assets/processed/frame.png` | 480×480 RGBA8，屏幕原点 `(0,0)` | 固定圆镜座；相对球心半径不超过 221px 的内部透明，221–232px 为窄环，外围为不透明黑底 |

合成顺序是 **眼球底图 + 局部快门 → 整体球面投影 → 固定镜座**。默认将闭合程度映射为最近的九帧之一，不混合相邻帧，以避免双叶片边缘。快门开孔的透明部分必须露出底图原黑孔，不能直接填成另一种颜色。

## 预览与复现

直接打开 `preview/index.html`。设备画面区域只显示角色；状态、时间线与调试控制位于画面外。浏览器预览只展示设计，不代表原生接入已完成。

在解压后的 `mechanical-c-assets-v1` 根目录，可以用已有 Python 环境输出一个极限对角、闭合姿态：

```bash
python3 preview/reference_render.py \
  --gaze-x 0.78 --gaze-y 0.58 --shutter 1 \
  --output /tmp/mechanical-c-diagonal-closed.png
```

重建参考预览的入口：

```bash
python3 preview/build_preview.py --package-root .
```

Python 渲染使用 Pillow、NumPy；视频编码使用 FFmpeg。HTML 查看不依赖这些制作工具。依赖版本和实际构建命令以制作说明为准，本包不安装或升级主工程环境。

`preview/timeline.json` 是 28 秒固定模拟时间线，逐帧输入记录在 `evidence/input-timeline.csv`。它覆盖无目标、确认进入、左右 / 上下移动、停住、离开、待机休眠、确认后唤醒、动作中切出再进入，以及无效数据与恢复。**全部时长只用于演示，不是主工程新默认规则。**

## 与前一版的关系

用户在完整眼球方向上选定了 C：去掉原先上下眼皮，使用中央快门。原先机械眼的 `frame.png` 与 `lid_00..08.png` 不属于 C 的运行图层；尤其不能把原外眼皮的九帧与本包中央快门九帧混用。恶龙眼、夜枭、深海及其原素材均保持原样。

新素材从 AI 概念图派生和加工，不承诺与旧机械眼正视图逐像素一致。它不是满足旧 `locked_mask.png` 的直接替换件；旧检查器的整片像素锁定条件不适用于这次获选结构。

本次保留的是 C 概念开态经注册对齐后的中央半径 184px 区域，共 106,353 个底图像素；这不是旧恶龙眼或旧机械眼的像素保护声明。半径 184–196px 处理接合，196px 外补充连续金属采样面，避免球体转动时把原概念图的外部黑背景带入。完整加工参数随源文件保留。

快门九帧采用六叶片对应点的二维形变，08 帧把原 AI 闭态中央的小六边形补片收束为六叶交点。它表达开合外观，不是真实刚体叶片或物理光圈运动。极限斜向下，原正视投影纹理仍可能出现拉伸，需要 main thread 做 C/GSP 对照和视觉检查。

当前可用工程依据是用户给定的 `eye-surface-art-handoff-v1.zip` 几何快照。**本轮未收到主工程最新 `AGENTS.md`、`README`、`docs/HANDOFF.md`。** 主工程必须先核对这些文件，再决定实际输入接口、状态时序、资源格式及渲染接入点；本包不替代它们。

## 完成边界

- 本包只交付可审阅的美术资源、图层约定、加工源文件与模拟预览。
- 固定时间线中的位置是明确标注的模拟姿态，不能证明热目标检测有效。
- 技术验证只覆盖 `evidence/verification.json` 实际记录的检查项，不自动代表视觉验收；素材尺寸、像素保留或预览输出成功也不等于旧锁定规则通过。
- 未完成共享 C / 原生 GSP 逐像素对比、资源导入器适配、设备帧率 / 内存 / 带宽测量及实机验证。
- HTML的同一JavaScript渲染函数已在Node中实际执行并检查中心、斜向及切出/切回；本环境缺少浏览器可执行文件，尚未完成真实浏览器界面/交互验证，详见 `preview/preview-checks.json`。未安装浏览器或升级依赖。
- PSD以ImageMagick重新读取图层并合成、ORA核对合成预览，均与源PNG合成一致；Photoshop、Krita或GIMP图形界面的往返编辑未验证。

本包没有新增人体身份识别、物体分类或精确测距能力，也没有独立检测器。
