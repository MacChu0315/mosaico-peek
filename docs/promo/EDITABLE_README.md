# 可编辑源文件补充包

此包配合主宣传素材包使用。源文件按原字节保留，没有为本轮宣传重新拆层或修图。

- `dragon_sclera_only/`：1254×1254的眼白C PSD/ORA。包括原图、空白修饰层与隐藏坐标参考层；不是完整怪物眼的PSD，也不是原始AI生成过程的真实分层。
- `mechanical/ARCHIVED_C_WITH_UNSELECTED_MOUNT.*`：机械C原交接包的480×480 PSD/ORA，**镜座不是当前选择的A**。编辑时需用 `CURRENT_frame_A.png` 替换固定镜座，并对照主包当前正视图。
- 机械SVG快门参考含嵌入位图，不是纯矢量插画或机械CAD模型。PSD保留开态三层，ORA另有其余快门状态，详见原说明。
- 深海R2没有可提供的完整PSD/ORA；主包已提供当前透明PNG图层、辅助蒙版与原始材质，不伪造缺失文件。

当前正确外观、组合关系和动态行为以主包 `START_HERE.md`、`LAYER_GUIDE.md`、`01_ready_to_use` 为准。历史来源文档保留在 `provenance/`；某些旧路径／旧选型只用于追溯。未声称已完成Photoshop/Krita/GIMP图形界面的往返编辑验收。

解压后运行 `sha256sum -c SHA256SUMS` 可检查完整性。
