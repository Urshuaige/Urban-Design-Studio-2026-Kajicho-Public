const words = {
  vision: ['Future Vision', '将来構想', '未来愿景'],
  title: ['Scenario workbench', 'シナリオ比較', '情景工作台'],
  intro: ['Compare four proposals around the former Imagawa Junior High School and Kanda Kanamono-dori.',
    '旧今川中学校と神田金物通り周辺の四つの案を比較します。', '比较旧今川中学校和神田金物通周边的四组方案。'],
  choose: ['Choose a scenario', 'シナリオを選ぶ', '切换情景'],
  results: ['Results', '計算結果', '结果'],
  conflicts: ['Conflicts and checks', '競合と確認事項', '冲突与核查'],
  inputs: ['Missing inputs', '追加で必要なデータ', '待补输入'],
  sources: ['Methods and sources', '手法と出典', '方法与来源'],
  record: ['Download model results', '計算結果をダウンロード', '下载计算结果'],
  reference: ['Reference', '参照案', '参考'],
  selected: ['Selected', '選択案', '当前方案'],
  measure: ['Measure', '指標', '指标'],
  delta: ['Change', '差', '变化'],
  basis: ['Each row uses the same model and support for its reference and scenario.',
    '各行は同じモデル・同じ対象範囲で基準と選択案を比べます。', '每行用同一模型和覆盖范围比较参考与当前方案。'],
  pending: ['Pending', '要確認', '待确认'],
  conflict: ['Spatial conflict', '空間の競合', '空间冲突'],
  fits: ['Fits in this model', 'モデル内で適合', '模型内已核对'],
  screening: ['Map screening', '地図で確認', '图层筛查'],
  unavailable: ['The model results are temporarily unavailable.', '計算結果を読み込めません。', '计算结果暂未加载。'],
  energy: ['Building energy', '建物エネルギー', '建筑能源'],
  traffic: ['Kanamono-dori traffic and curb', '金物通りの交通と道路端', '金物通交通与路缘'],
  shade: ['Street shade and surface heat', '街路の日陰と地表温度', '街道遮阴与地表温度'],
  walk: ['Walking routes and river hazard', '歩行経路と河川洪水', '步行路径与河流洪水'],
  water: ['Sewer drainage', '下水排水', '管网排水'],
  uses: ['Local uses', '周辺の用途', '周边业态'],
};

const scenarios = {
  reference: {
    label: words.reference,
    note: ['Retain the existing roofs, the two modeled curb strips and the mapped walking network.',
      '現況の屋根、道路両側の路上スペースと歩行ネットワークを使用します。',
      '采用现状屋顶、两侧路缘带和已登记的步行路网。'],
  },
  roof: {
    label: ['Roof', '屋根', '屋顶'],
    note: ['Test Asuka’s roof renewal assumptions on the supported priority buildings. Keep both recorded roofs in the school block.',
      'データの揃う更新候補に Asuka の屋根更新条件を適用します。学校街区の二つの対象屋根は維持します。',
      '在已有输入的优先楼栋上测试 Asuka 的屋顶更新假设。校舍街坊中有成对数据的两处屋顶保留。'],
  },
  'open-block': {
    label: ['Open block', '街区開放', '开放街区'],
    note: ['Test a three-lane section with a cycle track and planted edge, and one trial tree. Through access at the school is pending gate and operating details.',
      '三車線、サイクルトラック、植栽帯と試験樹木一本を検討します。学校の通り抜けには門と開放条件の確認が必要です。',
      '测试保留三车道、增设骑行带和植栽带的断面，以及一棵试验树。校舍穿行待核对入口和开放条件。'],
  },
  combined: {
    label: ['Combined', '組み合わせ', '组合'],
    note: ['Apply the roof and open-block tests together. The street shade comparison uses existing building massing.',
      '屋根更新と街区開放を組み合わせます。街路の日陰は現況の建物形状で比較します。',
      '叠加屋顶与开放街区的条件。街道遮阴仍按现状建筑形体比较。'],
  },
  custom: {
    label: ['Custom scenario', '設定シナリオ', '自定义情景'],
    note: ['This result uses the selected assumptions on the same pilot foundation.',
      '同じ試験範囲で設定した条件を比較します。', '用所选参数在同一试区和底座上重算。'],
  },
};

const measures = [
  ['energy', [
    ['pv_mwh', ['Annual rooftop solar potential', '年間の屋根太陽光発電ポテンシャル', '屋顶年光伏潜力'], 'MWh/yr', 2],
    ['pv_school_mwh', ['Former Imagawa school block · solar', '旧今川中学校街区の太陽光発電', '旧今川中学校街坊光伏'], 'MWh/yr', 2],
    ['pv_kanamono_mwh', ['Kanamono-dori block · solar', '金物通り側街区の太陽光発電', '金物通侧街坊光伏'], 'MWh/yr', 2],
    ['self_supply_pct', ['Electricity self-sufficiency', '電力自給率', '用电自给率'], '%', 1],
    ['demand_and_carbon', ['Operational carbon', '運用時の炭素排出', '运行碳排放'], 'tCO₂/yr', 1],
    ['battery', ['Battery storage and dispatch', '蓄電容量と運用', '电池容量与调度'], '', 1],
  ]],
  ['traffic', [
    ['first_hour_1800', ['First-hour exits · 1,800 offered', '初時の通過台数 · 需要 1,800 台', '首小时通过量 · 输入 1,800 辆'], '', 0],
    ['first_hour_3200', ['First-hour exits · 3,200 offered', '初時の通過台数 · 需要 3,200 台', '首小时通过量 · 输入 3,200 辆'], '', 0],
    ['queue_wait_3200', ['Mean in-network wait · 3,200 offered', '平均停車時間 · 需要 3,200 台', '路段内平均停车等待 · 输入 3,200 辆'], 's', 2],
    ['parking_strip', ['Modeled curb parking width', '断面上の駐車帯の幅', '示意断面停车带合计宽度'], 'm', 1],
  ]],
  ['shade', [
    ['shade_9', ['Shaded points at 09:00', '09:00 の日陰点数', '09:00 遮阴测点'], '', 0],
    ['shade_12', ['Shaded points at 12:00', '12:00 の日陰点数', '12:00 遮阴测点'], '', 0],
    ['shade_15', ['Shaded points at 15:00', '15:00 の日陰点数', '15:00 遮阴测点'], '', 0],
    ['land_surface', ['Satellite surface temperature', '衛星地表面温度', '卫星地表温度'], '°C', 1],
  ]],
  ['walk', [
    ['walk_station', ['Station south exit to the school-side street point', '神田駅南口から学校側街路の基準点', '神田站南口至校舍外街道代理点'], 'm', 1],
    ['walk_kanamono', ['Kanamono-dori to the school-side street point', '金物通りから学校側街路の基準点', '金物通至校舍外街道代理点'], 'm', 1],
    ['river_overlap_station', ['Station route in the mapped river-flood area', '河川浸水想定区域内の駅側経路', '站口路径与河流浸水图重合'], 'm', 1],
    ['river_overlap_kanamono', ['Kanamono route in the mapped river-flood area', '河川浸水想定区域内の金物通り側経路', '金物通路径与河流浸水图重合'], 'm', 1],
    ['school_passage', ['Route through the school grounds', '学校敷地内の通り抜け', '校舍用地内穿行'], 'm', 1],
  ]],
  ['water', [
    ['sewer_overflow', ['Sewer overflow under the design rain', '設計降雨時の下水溢水', '设计雨下管网溢流'], 'm³', 1],
  ]],
  ['uses', [
    ['facilities', ['Recorded facilities in the two study blocks', '二街区内の施設記録', '两个研究街坊内的设施记录'], '', 0],
  ]],
];

const missing = [
  ['Hourly building loads', '建物別の時刻負荷', '逐栋逐时负荷'],
  ['29 sharing areas', '29 の電力融通区域', '29 个共享分区'],
  ['Battery capacity and control', '蓄電容量と制御', '电池容量与调度'],
  ['Greening and heat', '緑化・熱環境', '绿化与热环境'],
  ['Sewer drainage', '下水排水', '管网排水'],
  ['School and street access', '学校・街路の通行', '校舍与街道通行'],
  ['Shops and deliveries', '店舗・荷さばき', '商铺与配送'],
];
const missingNotes = [
  ['Get the hourly electricity, heating, cooling, hot water and gas series by building and scenario, or the original model with floor use, envelope, weather, schedules and the mapping for the two heat-pump efficiencies.',
    '建物・シナリオ別の電力、冷暖房、給湯、ガスの時系列、または用途・外皮・気象・運用時間と二つの空調効率の割当を含む元モデルが必要です。',
    '需取得分栋、分方案的用电、采暖、制冷、热水和燃气时序，或原模型的楼层用途、围护结构、天气、运行日历及两组空调效率的对应规则。'],
  ['Get the building-to-area table or a map with area IDs. Confirm treatment of railway facilities and buildings across boundaries.',
    '建物と区域の対応表、または区域 ID 付きの図面が必要です。鉄道施設と境界をまたぐ建物の扱いを確認します。',
    '需取得建筑到分区的归属表或带分区编号的图层，并核对铁路设施和跨界建筑的处理规则。'],
  ['Get the capacity assigned to each unit, power limits, charge and discharge efficiency, charge limits and initial and final state, grid rules and dispatch priority.',
    '各単位への容量配分、充放電出力・効率、蓄電量の制約と初期・最終値、系統との接続ルール、運用の優先順位が必要です。',
    '需取得各单元的容量分配、充放电功率和效率、荷电范围与初末状态、电网进出规则和调度优先级。'],
  ['Regina’s exact scene and thresholds. Both tested Landsat scenes had zero clear non-water cells in the pilot sample. Field tree clearance and weather inputs are needed for a heat comparison.',
    'Regina の元シーンと分類閾値。検証した二つの Landsat 画像には、試験範囲内で雲と水域の除外を通過した点がありません。植栽余地と現地気象が必要です。',
    'Regina 的原始影像和分类阈值。两个 Landsat 候选在试区采样均无通过云水质控的格点。热环境比较还需现场种植净空和气象输入。'],
  ['The school catchment, inlet links, pipe sizes and inverts, downstream level, storage dimensions and the matched rain time series. Keane’s surveyed pipe chain is in Kanda Sudacho.',
    '学校周辺の集水域、雨水ますと管路の接続、管径・管底高、下流端、貯留寸法と降雨時系列。Keane が照合した管路は神田須田町にあります。',
    '校舍汇水区、雨水口接管、管径和管底高程、下游水位、调蓄尺寸与降雨过程。Keane 已核对的管段在神田须田町。'],
  ['Survey usable widths and the school gate. Confirm hours, step-free access, emergency access and an operator with Chiyoda.',
    '有効幅員と学校の門を現地で確認し、開放時間、段差のない動線、緊急時アクセスと運営主体を千代田区と調整します。',
    '实测可用净宽和校门，与千代田区核实开放时段、无障碍与应急通行、运营方。'],
  ['Survey actual traffic turns and signal timings, delivery hours, loading points and existing shop access.',
    '実際の交差点右左折、信号位相、配送時間、荷さばき場所と店舗アクセス。',
    '实测车辆转向与信号、配送时段、装卸点和现有店铺入口。'],
];

const root = document.querySelector('[data-workbench]');
const qs = selector => root.querySelector(selector);
const ui = document.documentElement;
const locale = () => ui.lang.slice(0, 2);
const index = () => locale() === 'ja' ? 1 : locale() === 'zh' ? 2 : 0;
const t = pack => pack[index()];
const format = (value, digits, sign = false) => new Intl.NumberFormat(ui.lang || 'en', {
  maximumFractionDigits: digits, minimumFractionDigits: 0, signDisplay: sign ? 'exceptZero' : 'auto',
}).format(value);
const el = (tag, text, css) => {
  const node = document.createElement(tag);
  if (text != null) node.textContent = text;
  if (css) node.className = css;
  return node;
};

function item(title, body, href) {
  const row = el('li');
  if (href) {
    const link = el('a', title);
    link.href = href;
    row.append(link);
  } else row.append(el('strong', title));
  row.append(el('p', body));
  return row;
}

function localize() {
  for (const node of root.querySelectorAll('[data-word]')) node.textContent = t(words[node.dataset.word]);
}

function methodNotes(data) {
  const { roof, shade, traffic, context } = data.support;
  const factor = roof.live_sun_multiplier ?? 1.27;
  const notes = [
    [words.energy, [
      'Same ' + roof.paired_roofs + ' roofs. Reference yield uses flat area × installable share × direct-sun share. The roof action applies a sun-share factor of ' + factor + ' to the eligible renewal roofs, with resulting sun share capped at 1. Potential yield is gross.',
      '同じ ' + roof.paired_roofs + ' 屋根を比較。参照は平坦屋根面積、設置率、直達日射率から算定し、更新案は対象屋根の日射率を ' + factor + ' 倍、上限を 1 としました。値は総発電ポテンシャルです。',
      '同样的 ' + roof.paired_roofs + ' 处屋顶。参考用平屋面面积、可安装比例和直射日照比例复算。屋顶措施按所设的 ' + factor + ' 倍日照比例计算，所得比例上限为 1。结果为总发电潜力。',
    ], '/vision#source-asuka'],
    [words.traffic, [
      'SUMO replay on the full ' + traffic.axis_m + ' m named test axis. Both sections have three motor lanes and the same 90 s signal and synthetic demand. The cycle and planting strip are layout geometry in this control.',
      '全長 ' + traffic.axis_m + ' m の実験軸で SUMO を再実行。両案とも車線は三本で信号周期 90 秒、需要は共通の合成需要です。',
      '在完整 ' + traffic.axis_m + ' m 的金物通试验轴上重跑 SUMO。两种断面均保留三车道，使用相同 90 秒信号和合成需求。骑行、植栽以断面几何纳入控制试验。',
    ], '/vision#source-shair'],
    [words.shade, [
      shade.samples + ' paired road-side points on ' + shade.date_jst + '. The direct-sun test uses one prior trial tree and existing building massing. Regina’s interim priority grid is available for ' + context.regina_cells + ' cells.',
      shade.date_jst + ' の路側 ' + shade.samples + ' 点で直達日射を比較。試験樹木一本と現況建物を使用。Regina の中間資料には ' + context.regina_cells + ' セルの優先度があります。',
      shade.date_jst + ' 的 ' + shade.samples + ' 个成对路侧测点。沿用已有的单树几何遮阴测试和现状建筑形体。Regina 中期优先级图覆盖试区内 ' + context.regina_cells + ' 个格点。',
    ], '/vision#source-regina'],
    [words.walk, [
      'Replayed shortest paths in the frozen walking network. Endpoints are on the mapped street. The river-flood overlap uses the Kanda River L2 map for the maximum-assumption event.',
      '凍結した歩行ネットワークの最短経路を再計算。終点は街路上です。河川浸水との重なりは神田川流域の想定最大規模 L2 図から算定。',
      '用冻结步行网重算最短路，终点在校舍外的街道。河流浸水重合长度来自神田川流域假定最大规模 L2 图层。',
    ], '/vision#source-dingchao'],
    [words.water, [
      'Keane’s SWMM workflow needs a verified local network and rainfall sequence. The school drainage estimate is pending those inputs.',
      'Keane の SWMM には対象管網と降雨系列が必要です。学校周辺の下水流出量は入力確認後に算定します。',
      'Keane 的 SWMM 方法需要已核对的本地管网与降雨过程。校舍的管网溢流量待这些输入到位后计算。',
    ], '/vision#source-keane'],
    [words.uses, [
      'Facility points use Jiaxiang’s dated, deduplicated inventory clipped by the two shared study blocks.',
      'Jiaxiang の重複整理済み施設記録を二つの共通街区で集計しました。',
      '按两个共享研究街坊筛选 Jiaxiang 的已去重、有日期的设施清单。',
    ], '/vision#source-jiaxiang'],
  ];
  const hours = data.support.asuka_energy?.reference_hourly_samples;
  if (hours) {
    notes.splice(1, 0, [
      ['Hourly solar generation', '時刻別の太陽光発電量', '逐时光伏发电'],
      [
        'The reference uses ' + format(hours,0) + ' hours of Tokyo typical-year irradiance and current roof shading. Renewal uses the annual slide formula. Its hourly profile needs the renewed roof and shade model.',
        '参照案は東京の標準年 ' + format(hours,0) + ' 時間の日射と現況屋根の日影を使用します。更新案は年発電量の式を用い、時刻別の算定には更新形状と日影が必要です。',
        '参考案采用东京典型年的 ' + format(hours,0) + ' 小时日射和现况屋顶遮挡。更新案复算年发电潜力，逐时发电仍需更新后的屋顶和遮挡输入。',
      ],
      'https://domessolar.infop.nedo.go.jp/appww/metpv.html?p=44132',
    ]);
  }
  return notes;
}

function ruleCopy(data) {
  const { roof, walking: w } = data.support;
  return {
    school_gate: [['School edge and opening', '学校の門と開放', '校舍边界与开放'],
      ['The mapped approach stops at a street point. Confirm the physical gate, opening hours, access rights and operator.',
       '経路の終点は街路上の点です。門・開放時間・通行権・運営者を確認します。',
       '已建模路径到校舍外的街道点为止。需确认实体校门、开放时段、通行权和运营者。']],
    sewer_connection: [['School and Kanamono-dori drainage', '学校と金物通りの排水', '校舍与金物通排水'],
      ['Verify where runoff enters the sewer and what sets the downstream boundary.',
       '雨水の流入先と下流端条件を確認します。', '实地核对雨水入管位置和下游边界条件。']],
    school_roofs_retained: [['Retained school roofs', '学校街区の屋根を維持', '校舍街坊保留屋顶'],
      ['Both paired school-block roofs keep their reference inputs.', '学校街区の対象二屋根は参照条件を維持。',
       '校舍街坊的两处成对屋顶均沿用参考输入。']],
    flat_roof_area: [['Roof area in the Kanamono-side study block', '金物通り側街区の屋根面積', '金物通侧街坊的屋顶面积'],
      [roof.area_conflict_roofs + ' of ' + roof.renewal_roofs + ' renewal roofs need more panel area than their current mapped flat roof provides. The yield depends on renewed roof geometry.',
       '更新対象 ' + roof.renewal_roofs + ' 棟のうち ' + roof.area_conflict_roofs + ' 棟で、パネル面積が現況の平坦屋根を上回ります。発電量は更新形状を前提とします。',
       roof.renewal_roofs + ' 栋有成对数据的更新候选中，' + roof.area_conflict_roofs + ' 栋的拟用面板面积超过现有平屋面。发电潜力有赖于更新后的屋顶几何。']],
    roof_structure: [['Roof structure and use', '屋根構造と利用', '屋顶结构与用途'],
      ['Verify load capacity, maintenance setbacks and space for planting or retention before an installation decision.',
       '荷重・維持管理通路・植栽や貯留との面積配分を確認します。', '安装前核实荷载、检修退距、绿化和调蓄的面积分配。']],
    curb_overlap: [['One Kanamono-dori curb strip', '金物通りの片側道路端', '金物通一侧的路缘带'],
      ['The cycle track and planting take the same 2.5 m strip as one parking side. Retaining loading there would claim the strip twice.',
       '自転車道と植栽は片側 2.5 m の駐車帯を使います。そこで荷さばきを維持すると同じ帯が競合します。',
       '骑行带与植栽占用原停车侧的同一条 2.5 m 路缘带。若要在此保留装卸，两种用途会重叠。']],
    available_width: [['Clear street width', '街路の有効幅員', '街道可用净宽'],
      ['Measure the clear width and check turning and emergency access. The mapped road-surface width includes other uses.',
       '有効幅員、車両の転回と緊急アクセスを実測します。地図上の道路面幅には他用途が含まれます。',
       '实测可用净宽，核对转弯和应急通行。GIS 道路面宽包含其他用途。']],
    dry_route: [['Dry access and rain storage', '乾いたアクセスと雨水貯留', '干燥入场路径与雨水调蓄'],
      ['The river-flood map overlaps ' + w.mapped_hazard_station_m + ' m of the station approach and ' + w.mapped_hazard_office_m + ' m from Kanamono-dori. Confirm a dry, accessible route for the chosen event.',
       '河川浸水想定区域との重なりは駅側 ' + w.mapped_hazard_station_m + ' m、金物通り側 ' + w.mapped_hazard_office_m + ' m。指定降雨時に通れる経路を確認します。',
       '河流浸水图与站口路径重合 ' + w.mapped_hazard_station_m + ' m，与金物通路径重合 ' + w.mapped_hazard_office_m + ' m。需另核实所选雨情下的干燥无障碍路径。']],
    combined_shade_solar: [['Combined roof and shade geometry', '屋根と日陰の組合せ形状', '组合方案的屋顶与遮阴几何'],
      ['Obtain the renewal massing, planting and roof layout, then rerun the shared geometric effects.',
       '更新後の建物形状・植栽・屋根配置を揃え、相互の影響を再計算します。',
       '补齐更新后的建筑体量、树冠和屋顶布置，再复算相互遮挡。']],
    alternate_loading: [['Alternative loading location', '代替の荷さばき場所', '替代装卸位置'],
      ['Confirm a place and time for deliveries after reallocating this strip.',
       '道路端の再配分に合わせ、荷さばき場所と時間を調整します。', '路缘重新分配后，仍需落实配送地点和时段。']],
    tree_clearance: [['Trial tree location', '試験樹木の設置場所', '试验树位置'],
      ['Check the tree pit, utilities, pedestrian clearance and emergency access before planting.',
       '植栽桝、埋設物、有効幅員と緊急アクセスを確認します。', '种植前核实树池、地下设施、步行净宽和应急通行。']],
  };
}

function metricCell(observation, digits, total) {
  if (observation.value === null) return el('td', t(words.pending), 'wb-null');
  const label = format(observation.value, digits);
  return el('td', total ? label + ' / ' + total : label);
}

function updateResults(reference, active, data) {
  const resultRows = [];
  const support = {
    energy: ['Paired gross solar potential', '同一屋根の総発電ポテンシャル', '同一批屋顶的总发电潜力'],
    traffic: ['Synthetic demand · three motor lanes', '合成需要・三車線の対照', '合成需求 · 三车道对照'],
    shade: ['Direct-sun screening · ' + data.support.shade.samples + ' points', '直達日射の評価・' + data.support.shade.samples + ' 点',
      '直射光筛查 · ' + data.support.shade.samples + ' 个测点'],
    walk: ['Street endpoints · official river hazard overlay', '街路上の終点・公的な浸水想定図', '终点在校舍外街道 · 叠加官方河流浸水图'],
  };
  for (const [group, rows] of measures) {
    const heading = el('tr', null, 'wb-group');
    const label = el('th', t(words[group]));
    label.colSpan = 4;
    if (support[group]) label.append(el('span', t(support[group]), 'site-caption'));
    heading.append(label);
    resultRows.push(heading);
    for (const [key, name, unit, decimals] of rows) {
      const selectedDemand = data.support.traffic.control.live_demand;
      if (selectedDemand && key === 'first_hour_1800') continue;
      const displayName = selectedDemand && (key === 'first_hour_3200' || key === 'queue_wait_3200')
        ? t(name).replace('3,200', format(selectedDemand,0))
        : t(name);
      const old = reference.metrics[key];
      const datum = active.metrics[key];
      if (!old || !datum) continue;
      const change = datum.value === null || old.value === null ? '—' : format(datum.value - old.value, decimals, true);
      const total = key.startsWith('shade_') ? data.support.shade.samples : null;
      const row = el('tr');
      row.dataset.metric = key;
      const th = el('th', displayName);
      th.scope = 'row';
      if (unit) th.append(el('span', unit, 'site-caption'));
      row.append(th, metricCell(old, decimals, total), metricCell(datum, decimals, total), el('td', change));
      resultRows.push(row);
    }
  }
  qs('[data-results]').replaceChildren(...resultRows);
}

let currentView;
function render(data, activeId) {
  currentView = {data, activeId};
  localize();
  const active = data.cases.find(row => row.id === activeId);
  const buttons = qs('[data-choices]');
  if (!buttons.children.length) {
    for (const row of data.cases) {
      const b = el('button');
      b.type = 'button';
      b.dataset.case = row.id;
      b.addEventListener('click', () => {
        const url = new URL(location.href);
        url.searchParams.set('case', row.id);
        history.replaceState(null, '', url);
        render(data, row.id);
      });
      buttons.append(b);
    }
  }
  for (const button of buttons.children) {
    const key = button.dataset.case;
    button.textContent = t(scenarios[key].label);
    button.setAttribute('aria-pressed', String(active.id === key));
  }
  qs('[data-case-note]').textContent = t(scenarios[active.id].note);
  const time = new Intl.DateTimeFormat(ui.lang, {dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Tokyo'})
    .format(new Date(data.created_jst));
  qs('[data-run]').textContent = t([
    data.support.study_area_ha.toFixed(2) + ' ha across two study blocks · mdx1 results · ' + time + ' JST',
    '二つの研究街区 ' + data.support.study_area_ha.toFixed(2) + ' ha · mdx1 計算 · ' + time + ' JST',
    '两个研究街坊 ' + data.support.study_area_ha.toFixed(2) + ' 公顷 · mdx1 计算结果 · ' + time + ' JST',
  ]);
  const reference = data.cases.find(row => row.id === 'reference');
  updateResults(reference, active, data);
  const lookup = ruleCopy(data);
  qs('[data-checks]').replaceChildren(...active.checks.map(check => {
    const [title, note] = lookup[check.id];
    const row = item(t(title), t(note));
    row.dataset.rule = check.id;
    row.dataset.state = check.state;
    row.prepend(el('span', t(words[check.state]) + ' · ', 'site-caption wb-rule'));
    return row;
  }));
  qs('[data-inputs]').replaceChildren(...missing.map((name, i) => item(t(name), t(missingNotes[i]))));
  qs('[data-methods]').replaceChildren(...methodNotes(data).map(([name, note, link]) => item(t(name), t(note), link)));
  root.dataset.ready = 'true';
}

function chosen(data) {
  const caseId = new URLSearchParams(location.search).get('case');
  return data.cases.some(row => row.id === caseId) ? caseId : 'reference';
}

localize();
try {
  const response = await fetch('/workbench-assets/data.json?v=20261120-asuka');
  if (!response.ok) throw new Error('Unable to load scenario results');
  const data = await response.json();
  if (data.schema_version !== 1 || data.cases.length !== 4 || data.cases.some(c => !scenarios[c.id])) {
    throw new Error('Unexpected scenario result schema');
  }
  render(data, chosen(data));
  new MutationObserver(() => {
    if (currentView) render(currentView.data, currentView.activeId);
  }).observe(ui, {attributes:true,attributeFilter:['lang']});
} catch (error) {
  root.dataset.ready = 'false';
  qs('[data-run]').textContent = t(words.unavailable);
  console.error(error);
}

export function renderLive(data) {
  if (!currentView || data?.schema_version !== 1 || data.cases[1]?.id !== 'custom') return;
  render(data, 'custom');
}
