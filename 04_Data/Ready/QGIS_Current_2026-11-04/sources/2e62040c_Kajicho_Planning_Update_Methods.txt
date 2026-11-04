# Planning update / 规划资料同步

完成日期：2026-11-02。原始 QGIS 工程、已接受的 37 张 Figma Slides 及 Google Slides 快照不变。本轮新增两页，Figma 共 39 页，仍为原有的 10 张隐藏页。

## Deliverables / 交付

- `Kajicho_Planning_Update_2026-11-02.qgz`：独立可编辑 QGIS 工程，EPSG:6677，项目树内相对路径。
- `data/Kajicho_Planning_Update.gpkg`：22 个完整地区计划外边界、1 个已建项目地址定位点、7 条政策/项目来源记录。
- `data/Planning_Inventory.csv`、`QA/Plan_Intersection.json`：与实际 wider 范围及出图框的相交统计。
- `maps/Konyacho.png`、`maps/Taiichi.png`：2100 × 2970 PNG。
- `QA/Planning_Slide.png`、`QA/Taiichi_Slide.png`：Figma 实际整页导出，1920 × 1080；不是本地拼版替代图。
- [神田紺屋町地区计划页](https://www.figma.com/slides/hh16ci0VeM3JQj2tZFvdbX?node-id=254-2)：全 deck 第 20 页、当前可播放第 19 页。
- [神田多壱小路案例页](https://www.figma.com/slides/hh16ci0VeM3JQj2tZFvdbX?node-id=254-70)：全 deck 第 21 页、当前可播放第 20 页。

页面文字、A/B 对照、数字、店铺—通路—活动广场示意均为 Figma 原生可编辑对象；地图为 QGIS PNG，其地理样式/数据保留在 QGIS。

## Synced / 已同步的资料

### 1. MLIT A55 / 地区计划外边界

来源：国土数値情報「都市計画決定情報・2024年度版」。
- 数据时点：2024-03-26；制作日：2024-04-01；公开版本：2025-11；本轮获取/核查：2026-11-02。
- [原始千代田区 ZIP](https://nlftp.mlit.go.jp/ksj/gml/data/A55/A55-24/A55-24_13101_GEOJSON.zip)；[数据说明](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-A55-2024.html)。
- 许可：CC BY 4.0。署名：国土数値情報（都市計画決定情報・2024年度版）（国土交通省）を加工して作成。
- 原 CRS：EPSG:6668；派生 CRS：EPSG:6677。
- 原空间单位：完整地区计划外边界。资料包按周边 bbox 选择 22 个 whole features；本轮只重投影并添加来源、相交面积及现行性字段，不裁断原边界、不简化几何。
- 附带原始属性 `DistName`、`INDate`、`FNDate`、`INNumber`、`FNNumber` 等全部保留。完整来源与许可见 `sources/A55_open/open_qgis_package/provenance_license.json`。
- 未使用千代田受独立利用条款约束的 Experience GIS 截图或 REST geometry。

与实际 wider（42.43712 ha）有实质相交的主要范围：岩本町東神田（50,485.89 m²交叠）、神田紺屋町周辺（44,725.36 m²）、神田須田町二丁目北部周辺（15,189.06 m²）。中神田中央仅 35.21 m² 边缘相交，登记为几何边缘差异，不视为主要适用范围。

[现行地区计划清单](https://www.city.chiyoda.lg.jp/koho/machizukuri/toshi/chikukekaku/gaiyo.html)核查日 2026-11-02：神田紺屋町的 2004-06-21 变更日与 A55 相符；神田佐久間町（2025-07-07）、大手町・丸の内・有楽町（2025-06-27）已有晚于 A55 的变更，已加 current_check 标记，未宣称其 2024 几何代表最新边界。

### 2. Kanda Konyacho / 神田紺屋町周辺地区地区計画

[区官方 PDF](https://www.city.chiyoda.lg.jp/documents/4355/13konyachou20151023.pdf)，用户原附件保存在 `sources/都市計画神田紺屋町周辺地区地区計画.pdf`。这是现行清单所链接的文件；文件名中的 2015 不是法定末次变更年。

- 2000-07-10 决定，2004-06-21 末次变更；官方概数 4.5 ha。A55 投影几何面积约 4.4725 ha，不用几何面积替代公布概数。
- A：昭和通沿线约 1.0 ha，一般高度上限 45 m；B：内部约 3.5 ha，一般上限 40 m。
- 仅接宽度 6 m 以下道路的敷地，高度上限为 26 m。建筑基准法第 59 条之 2 等例外需逐址核查。
- 住宅恢复、多样居住及业态复合是政策目标。10 户以上且 4 层以上的公寓适用相应户型面积构成要求：超过 30 m² 户型的住宅延床面积合计不低于 2/3，40 m² 以上不低于 1/3；原文另有例外。页面仅概括住房多样性，不将比例扩大到所有建筑。
- 容积率奖励有条件。A 的基准按 800% 与相应前面道路宽度限制取值，再按条文加值并受 800% 上限约束；B 基准按 600% 与道路宽度限制，按条文加值并受 700% 上限约束。狭小道路及其他条件另有规定。不能将 800% / 700% 作为全区无条件额度。
- 超过基准容积的部分限条文规定的住宅等用途。退让、道路条件和例外须同时核查。
- 官方文字在本轮属性表中摘要登记；没有生成 A/B 分区、退让线、道路设施或逐地块可建包络。
- 页码：PDF p1 目标与范围；p2 用途/容积及户型；p3–4 退让/高度等。表格已实际渲染核查。

### 3. Kanda Taiichi Koji / 神田多壱小路

[NTT 都市开发开业公告](https://www.nttud.co.jp/news/detail/id/n26840.html)；[官方四页 PDF](https://www.nttud.co.jp/news_pdf/news_241219_002.pdf)。公告日 2024-12-19，本轮获取 2026-11-02。

- 地址：内神田三丁目17番9。开业 2024-12-19；工程竣工日 2024-10-11，不混为同一日期。
- 用地 535.62 m²；延床合计 198.76 m²（99.38 m² × 2）；两栋两层木造店铺。
- 约 130 m² 广场可以用于当地活动；东西向路地增加穿行联系。官方记载 2024 年 10 月活动曾设置儿童游戏、品酒及露天影院，不能据此推定日常到访量或全天开放承诺。
- 地图点 P1 为作者依据官方 PDF p4 地址图和既有多町大通/神田警察通几何设置的概略位置：EPSG:6677 (-5764, -34124)，约 20–30 m 定位精度。它不是测量点、项目地界或新建楼栋轮廓。
- Figma 的店铺/通路/广场图为原生概念关系示意，不按面积绘制、不表示真实相对方位或施工总平。
- 版权处理：NTT 网站条款没有提供一般改编/共享图片许可；本页采用事实摘要和原创关系示意，未转载其摄影或原地图。[条款](https://www.nttud.co.jp/copyright.html)。

### 4. Context / 邻近资料登记

- 神田須田町二丁目北部周辺地区地区計画：A55 外边界与原属性已同步；这是法定规划范围，不等同新开工项目。
- 外神田一丁目南部：A55 地区计划外边界作为外部背景保留。地区计划决定日 2023-10-13 与再开发都市计划决定 2024-03 是不同手续，不能混用；未新增一页挤占主体信息，也未宣称已开工。参考 [东京都项目页](https://www.toshiseibi.metro.tokyo.lg.jp/machizukuri/shigaichi_seibi/sai-kai/saikaihatsu/chiyoda_01_25)。
- 内神田停车地域规则：仅列待核查的非空间来源记录；未声称已同步其条款、适用范围或停车指标。

## Method / 制作与核查

1. 保留用户原始 PDF、授权 A55 包和来源元数据；安全解包排除 AppleDouble 等元数据文件。
2. `work/build_planning.py` 重投影 22 个完整计划面，计算其与当前 wider / 出图框的交叠面积，并生成项目点和非空间政策表。
3. 复用已接受的 QGIS 地图底图与版式。`work/final_labels.py` 添加来自既有 OSM 属性的顺线道路名。
4. 两张布局：`PL — Konyacho`、`PL — Taiichi`；同 CRS、extent、map item 198 × 270 mm、scale 1:4500。范围：(-5902.94, -34762.45)–(-5011.94, -33547.45)。页面 210 × 297 mm，导出 2100 × 2970 PNG；Figma 两图均以 540 × 764 px、FIT 显示。
5. 图例、北针、比例尺均无白底/边框；北针 x10/y30 mm，比例尺 x10/y49 mm，在其正下方。保持深灰研究建筑、淡灰周边建筑、淡蓝水体。
6. `work/export_one.py` 每次仅渲染一张，避免本机 QGIS 连续二次导图卡住；`work/verify_project.py` 在独立进程重新读取工程。11 个图层均有效、两张布局一致；见 `QA/QGIS_Reopen_QA.json`。
7. Figma 两页使用 IBM Plex Sans：标题44、结论26 Regular、分组30 Bold、说明22–24、来源/固定页脚14。地图源在 QGIS，原生示意/文字在 Figma 可编辑。
8. 两页实际截图已目视核验。案例页底部两栏碰撞已通过短句与显式断行修正，最终截图无遮挡。原有 10 张隐藏页的 ID 完全保留。
9. 新图前实际浏览两项中文小红书参考：舒克舒克《作品集04｜控规》、Deep Planning《街坊里巷 包容性更新思路》。仅借清楚图底、分组与标签逻辑，不复制其资产/事实。

## Portability / 使用说明

本工程使用共享项目树内的正常相对路径，依赖现有 `05_QGIS` 和 `06_Outputs/Slides/Space_Syntax_2026-11-02/data/Orientation_Landmarks.geojson`。它不是独立 ZIP；请在完整 Urban Design Studio 项目树中打开，不单独搬走 qgz。未生成或交付 SVG 地图，没有项目宏、网络底图或额外插件依赖。

每轮新输出已执行 `08_Scripts/file_hygiene.py --clean`。该脚本在成功清理后附带的“独立包验证”会因共享树相对路径超出本输出子目录而报错；这不影响完整项目树内重载。未宣称本目录本身是已打包的独立移机成果。
