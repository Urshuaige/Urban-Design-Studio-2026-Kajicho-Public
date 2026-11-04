# Kajicho spatial configuration / 空间句法

本轮完成 wider 范围的地表步行路网角度线段分析。两张主图分别表示 400 m 范围内的局部整合度与 800 m 范围内的穿行选择度。它们解释道路结构提供的步行潜力，可与现场活动、车流、用途和街道断面叠合判断。

## Open / 打开

- `Kajicho_Space_Syntax_2026-11-02.qgz`：在本项目目录树中打开的独立工程，沿用已接受的现状样式，不覆盖原工程。
- Layout `SS — NAIN400`：Local accessibility，局部到达潜力。
- Layout `SS — NACH800`：Through-movement potential，穿行潜力。
- `maps/NAIN400.png`、`maps/NACH800.png`：1980 × 2700 px，PNG。
- 同名 `_Sheet.png`：2100 × 2970 px，包含标题与来源页脚，便于独立查看。
- `data/Kajicho_Angular_Segments.gpkg` / `angular_segments`：全部计算线段、原始统计及标准化指标，可重新设色、筛选和标注。
- `Results_QA.json`、`Network_QA.json`：数值与拓扑核查。
- `Named_Street_Summary.csv`：与 wider 相交的有名线段，按线长加权汇总。不是整条道路的普查值。

当前工程依赖项目树内的原有底图，使用相对路径。它不是独立分享 ZIP；复制单个 qgz 到其他机器不会连带复制底图。原 QGIS 工程、原始数据和已接受的 Figma 页面保持不变。GUI 锁屏状态下没有进行桌面重开，保存后用已安装的 QGIS 引擎读取和渲染检查。

## Findings / 初步空间判断

1. **平成通的局部到达潜力突出。** 400 m 整合度图的高值横向联系集中在基地中北段，平成通的已命名线段属于其中。它适合作为后续检验日常公共空间和步行连接的重点。
2. **金物通和向南的日银通具有较高穿行潜力。** 800 m 选择度显示，东西横向通路与南向联系承担不同的网络角色。不能用一条概念直线把它们替代，也不能只依据主干机动车道路的宽度判断步行结构。
3. **高值通路与支巷存在差别。** 中部的贯通联系普遍比部分北端及短支路更突出。后续方案可比较连接支巷、调整穿越口后，潜力如何变化；本轮不加入任何拟议道路。

这里的高值是角度路径结构结果，不是人流计数。地图高低档为本次 wider 主连通网络的五分位，不能直接与另一城市的颜色比较。

## Source / 数据口径

| Item | Value |
|---|---|
| 原道路数据 | `05_QGIS/Projects/Kajicho_QGIS_Master_Map_2026-10-29/data/Walkability_2026-10-28/Kajicho_Walkability.gpkg`, `walk_network` |
| 原始 OSM 响应 | `04_Data/Raw/Walkability_2026-10-28/OSM_Walking_Context.json` |
| 原始查询 | 同目录 `query.overpassql`；Overpass `https://overpass.private.coffee/api/interpreter` |
| 数据时间 | OSM 响应 `timestamp_osm_base = 2026-06-01T08:52:28Z` |
| 下载时间 | 2026-10-28T12:52:06.591037+00:00 |
| 本轮处理 | 2026-11-02 UTC，版本和进程记录见 `work/Run.json` |
| 许可 | © OpenStreetMap contributors，ODbL 1.0，https://www.openstreetmap.org/copyright |
| CRS | JGD2011 / Japan Plane Rectangular CS IX，EPSG:6677，单位 m |
| 展示范围 | 当前 `study_boundaries` 中 `boundary_id=study_area`，42.437122 ha |
| 计算范围 | 已有约 3.7 × 4.1 km 上下文路网，不按 wider 裁断计算 |
| 底图 | 既有 GSI 图层与现有建筑图层，沿用各层原始年份/来源。未下载新地理底图 |

原 `walk_network` 来源于 OSM 步行网络准备，并非现场逐段测量。机动车单行不自动限制步行；仅保留明确的步行方向限制。铁路和高速不作为步行连边。

## Method / 可复现方法

使用 UCL **depthmapX 官方 SegmentTulip 核心**，固定源码提交 `6ea9755efe30d51603b99b842898b62a2591b850`：
https://github.com/SpaceGroupUCL/depthmapX/tree/6ea9755efe30d51603b99b842898b62a2591b850

官方角度求解核心没有修改。`work/angular_runner.cpp` 是本轮输入适配器，按 OSM 节点 ID 建立连接，避免普通平面线相交自动连通造成高架错误。它调用 `SegmentTulip`，1024 Tulip bins，无长度/人口权重，全起点分析；角度成本为转角/(π/2)，即转向 90° 的成本为 1。半径是 **metric radius**，主计算 400/800/1200 m，不能把它们理解为角度阈值。

各半径保留 `NC`（可达线段计数）、`TD`（总角度深度）、`CH`（官方选择度原始输出）。标准化采用官方 QGIS Space Syntax Toolkit 的约定：

`NAIN = NC^1.2 / (TD + 2)`

`NACH = ln(CH + 1) / ln(TD + 3)`

公式来源：https://github.com/SpaceGroupUCL/qgisSpaceSyntaxToolkit/blob/master/esstoolkit/analysis/engines/Depthmap/DepthmapEngine.py

负数缺失哨兵改为空；NC≤1 不设标准化值。未将普通网络 closeness/betweenness 改名。原官方 Integration 字段和未加工 TSV 另保留在 `work/context_full.tsv`，与本轮 NAIN 字段区分。

处理顺序：

1. 原始 36,175 边，复核 foot/access 与道路类型。
2. 本次地表场景额外排除 1,614 条地下边、351 条明确站内循环边、15 条 indoor 边。保留有地表通行意义的 building passage、人行桥和楼梯。
3. 清除 3 条相同端点且相同几何的重复边。不得把空间接近但节点不同的道路强行吸附。
4. 仅合并度为 2 且道路/层级/通行属性一致的连续线，再用 Douglas–Peucker 2 m 简化中间几何点。所有交叉口、死胡同、属性变化和单向步行变化点保留。简化后拆成直线段供角度计算。保留源 segment ID 与 way ID，循环线不简化。
5. 全域 24,289 条分析线段；与 wider 相交 1,049 条，其中主连通分量 1,029 条。另 20 条保留为灰色虚线“Separate components · review”，不误作低潜力道路。
6. 以完整上下文求解，再筛选显示。仅相交的完整线段着色，因此色线可略超出 wider 边界；外围其余网络淡灰连续保留。

图面保持 EPSG:6677、相同 extent `[-5902.94, -34762.45, -5011.94, -33547.45]`，图框 198 × 270 mm，scale 4500。各指标独立五分位分档，实际阈值及颜色见 `Map_Manifest.json`。图例/北针/比例尺透明，比例尺在北针下方。数值四舍五入到三位仅用于图例，数据保留原精度。

## QA / 核查

- 输入适配器的五个测试场景通过，覆盖角度、连接、方向及半径，其中包含 metric-radius 断言。记录在 `work/Adapter_Test_QA.json`。
- wider 附近两处不相连的几何交点均为 `way 202905127` 人行桥（layer 2）跨地面 footway（layer 0），没有增加连接。
- 简化前后总长约 621.117 / 620.278 km，变化约 0.135%。真实死胡同保留 2,189 个节点。
- 以 wider 外 1,000 m 选取上下文（14,200 段）和完整上下文（24,289 段）比较，wider 主分量四个 400/800 m 指标逐值一致。该结果是本次敏感性检查，不表示任何有限范围都没有边界效应。1200 m 仅作为上下文字段，没有做同样的较小范围复核。
- 简化 1 m 复算 25,726 段，按相同原始边对应比较：NAIN400 Spearman 0.9782，NACH800 0.9857；高值前20%重合 Jaccard 分别 0.9170 / 0.8784。个别线段可明显变化，数值不当作绝对实测。对应边重复只用于稳定性诊断，不作独立统计样本推断。
- 主求解 117.719 s，1000 m 上下文 25.462 s，1 m 简化 75.453 s。运行在 mdx2，三个独立单线程任务并行，不使用 GPU。构建使用32线程；三台主机检查与选择记录在 `00_Start/Compute_Snapshot_Space_Syntax_2026-11-02_*.json`。

## Interpretation limits / 使用边界

本场景只包含地表步行。地下车站、室内商业通道和站台不纳入；站内换乘路径不能由此判断。源查询没有完整 barrier 节点盘点，门禁/开放时段仍需现场核查。OSM 同时有道路中心线、独立人行道和过街设施，线段颗粒度及双侧人行道表达会影响无权重的节点计数与路径选择，跨数据集比较前须统一建网方式。

道路类型、桥梁/隧道/层级及明确 access 已检查；没有声称完成每个入口的实地通行核验。独立分量保留为待复核，不解释为真实隔绝。分析没有纳入店铺吸引力、入口权重、过街等待、坡度或交通压力，因此与现场人流和机动车量是不同证据。

## Reproduce / 复现

`work/prepare_network.py`：本机现有 `geoenv`，生成三组输入。

官方源码固定上述 commit。把 `work/CMakeLists.txt`、`angular_runner.cpp` 放到隔离构建目录并按 CMakeLists 的 source 路径构建；远程实际目录和输入 SHA256 在 `work/Run.json`。运行 `kajicho_angular data/context_full.tsv results/context_full.tsv 400,800,1200`，另两组为400,800。`work/test_adapter.py` 可运行适配器测试。

`work/process_results.py`：本机 geoenv，生成指标、GPKG、敏感性记录。

`work/render_maps.py`：已安装 QGIS Python 3.32.3，创建独立工程及两张布局；`work/export_one.py NAIN400` 与 `NACH800` 在独立进程逐张导出，避免同一无界面进程连续渲染停滞。路径均在同一项目目录树，不安装额外 QGIS 插件。

`work/finalize_project.py` 将新工程收束为13个实际使用图层和两张布局，并加入现有资料核实的车站/旧学校定位；该步骤不改原工程。最终 PNG 由这个收束后的工程重开导出，13个源路径及表均有效。`export_one.py NAIN400 sheet` 导出含页脚整图。

## Visual references / 仅借图示层级

按本项目流程先以中文检索小红书“空间句法 整合度 选择度 分析图”。实际查看：

- 规创设计工作室《空间句法整合度与 GIS 梦幻联动 可叠加分析》，https://www.xiaohongshu.com/explore/69bbb81a000000001a025d2b 。参考浅底与路线高低层级，不采用大北针和无背景定位。
- 木右几《制图教程｜QGIS城市路网空间句法分析图》，2024-10-29，https://www.xiaohongshu.com/explore/671f3d01000000001402d4f1 。实际查看其首张路网图，借连续线网和线宽层级，保留本项目白底，不复制黑底封面。第二帖浏览器截图无数据，使用浏览器已加载图像查看。

参考图只用于内部视觉研究，没有放入交付地图。计算方法依据官方源码，未采纳参考帖作为算法证据。
