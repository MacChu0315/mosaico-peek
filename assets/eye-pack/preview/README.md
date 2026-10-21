# 离线参考预览

直接用桌面浏览器打开 `index.html`。所有位图均位于同目录的 `assets-data.js` 中；没有网络请求、CDN、第三方运行时或字体下载，不需要 npm 安装。保持本目录文件的相对位置。

角色画布的内部尺寸是 480×480；窄窗口下可按比例缩小显示。主题、场景、播放/暂停、时间轴、输入状态及低成本眼睑选项均在画面外。时间线中的“隐藏”表示模拟切出该 UI，画布为黑；实际产品此时由主工程显示另一套 UI。

如浏览器对 `file://` 施加额外限制，可在上级包目录使用已有 Python：

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

再打开 `http://127.0.0.1:8000/preview/index.html`。这是可选的本地文件服务，不操作设备。

## 固定输入与复现

完整场景 `full` 为48秒；直接进入场景 `enter_target`、`enter_empty`、`enter_asleep` 各6秒。输入全部模拟并明确标记。三主题消费相同输入，未确认候选不驱动眼睛。动作固定种子为 `0x4d4f5341`，模型以规范60Hz时间网格计算；该频率不是设备性能承诺。

```js
await window.previewReady;
await window.setPreviewTime(22725, "night_owl", "full");
```

这会显示与 `evidence/screenshots/night_owl_waking.png` 相同输入时点的参考画面。浏览器与离屏证据共用模型和渲染器，但不同 Canvas 实现的像素滤波可能不同。

## 文件职责

| 文件 | 职责 |
|---|---|
| `index.html` | 审阅页面、控件及播放器时钟 |
| `timeline.js` | 固定模拟场景；外部注入状态和确认标志 |
| `model.js` | 纯动作参考计算；不读取传感器或墙钟 |
| `renderer.js` | 共用2D Canvas图层合成；不持有动画时钟 |
| `assets-data.js` | 33张运行PNG的本地图像容器；不是设备资源格式 |

运行期依赖是支持 Canvas 2D、Promise、requestAnimationFrame 的现代桌面浏览器。本环境未提供可用 Chromium，因此实际浏览器控件尚未验收；已执行的检查仅限离屏参考渲染和JavaScript模型。

## 重建与验证的依赖

日常查看预览不需要这些构建工具。仅在重建素材/证据时使用现成的工具环境；本包不带依赖副本或安装脚本。

| 操作 | 命令（包根目录） | 所需工具 |
|---|---|---|
| 验证模型边界 | `node tools/verify_preview.js` | Node标准库 |
| 重建透明分层 | `node tools/build_assets.cjs` | Node、`@napi-rs/canvas` |
| 只导出截图 | `node tools/render_evidence.cjs --stills-only` | Node、`@napi-rs/canvas` |
| 导出完整视频与输入 | `node tools/render_evidence.cjs` | Node、`@napi-rs/canvas`、ffmpeg、ffprobe |

交付制作环境使用 Node v24.19.0、`@napi-rs/canvas` 0.1.100。若当前工作环境已将模块放入公共运行时目录，构建脚本支持 `CODEX_PRIMARY_RUNTIME_NODE_MODULES`；否则通过标准 Node 模块解析寻找现成的包。无需更改主工程依赖。

证据外部英文标注使用系统已有 DejaVu Sans，不打包字体二进制。重建可用 `EYE_HANDOFF_FONT` 指定已有的同一字体路径；缺失时退回系统 sans-serif，标注文字的像素会随字体环境变化。480×480角色本身不使用文字。字体声明见 `assets/FONT_LICENSE.txt`。

全包数据和模拟状态不能用作检测算法准确率、原生GSP能力或硬件性能的证明。
