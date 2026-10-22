用户已认可的单只恶龙眼：第二阶段唯一视觉基准

先看 output/idle-rest.png、output/attention-side.png，然后看两段 MP4。
影片各为480×480、25fps、10秒、无音频；它们是预编排的离线动效，不是实时传感器演示。

保留的原始资产：assets/iris.png、assets/skin.png。
姿态曲线：timeline.mjs（秒输入，返回 gazeX/gazeY/blink/squint/pupilWidth/tension）。
渲染参考：render.mjs、package.json。可在安装了相应依赖的环境下运行：
  node render.mjs stills
  node render.mjs movies

注意：这是用于说明球面观感、眼睑遮挡和动作气质的离线 Node 渲染器；
不是 GSP 实现，也没有验证 ESP32-S31 上的实时开销。
目光坐标右/下为正，不是已经校准的 MLX90640 物理方向。

SOURCE_README.md 保留最初交付说明，其中提及的 GIF 为原来较大的动效包内容。
本接入包只携带对应 MP4 及关键帧，以免重复携带较大的 GIF；没有改动原纹理、源代码或曲线。
art-prompts.json 保留原生成提示词；资产为本项目新生成，没有复制参考作者的图片或代码。
