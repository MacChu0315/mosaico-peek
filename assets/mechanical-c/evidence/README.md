# 证据分类

| 文件 | 实际来源 | 可证明的内容 |
| --- | --- | --- |
| `overview.png`、`shutter-stages.png` | Python读取交付PNG图层并合成 | 正视三态与九档快门素材的外观 |
| `gaze-*.png`、`all-angles-open.png`、`all-angles-closed.png` | Python参考球面投影 | 既定摆幅的正视、四向、四角参考外观 |
| `scenario-reference.mp4`、`input-timeline.csv` | 28秒固定模拟注入，12fps编码 | 无目标、候选、确认、跟随、停住、离开、休眠/唤醒、切出/切回、失效与恢复的参考演示 |
| `rotation-reference.mp4`、对应inputs.csv | 8秒固定模拟姿态 | 四向和对角连续扫描 |
| `aperture-cycle.mp4`、对应inputs.csv | 4秒固定开合参数 | 中央快门闭合和重新开放 |
| `node-reference-*.png` | 实际执行同一HTML中的JS渲染函数，Node+PNG/ImageData适配器输出 | JS中心/斜向图像生成、图层与快门合成 |
| `verification.json` | 本轮实际运行的素材/源文件/归档检查 | 尺寸、alpha、保护区、重建一致性、资源大小等记录 |

视频尺寸480×520，上方480×480是角色画面，最下40px是外部说明。视频的12fps是参考编码帧率，不是设备FPS。所有模拟位置、状态和确认标志都来自固定时间线，不验证目标检测算法。

**没有实际C/GSP运行截图、设备录像或热传感器记录。** Node执行同一JS函数不代表浏览器界面已验证；当前缺少浏览器可执行文件，真实浏览器交互未测试。C/GSP舍入、性能、资源驻留、触控与AI事件均待主工程验证。

用户已选择C概念方向；新增分层、九档开合和全角度效果尚待本轮审阅，`visual_approved`不会因技术检查通过而自动变为true。
