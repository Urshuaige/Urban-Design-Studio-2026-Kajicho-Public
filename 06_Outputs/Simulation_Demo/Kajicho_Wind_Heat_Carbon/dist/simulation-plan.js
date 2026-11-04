const copy = {
  en: {
    eyebrow: 'Simulation plan',
    title: 'Match each model to the design question',
    intro: 'Figure 5 defines the primary design focus and approximate wider reporting scope. Wind and shade models also retain the surrounding geometry that affects the chosen street.',
    scope: 'Study area', pending: 'Boundary review in progress', models: 'complete building models',
    flowLabel: 'From the study area to useful comparisons',
    steps: [
      ['Figure 5 study levels', 'Retain the source outlines, update membership and check edge sensitivity.'],
      ['Complete geometry', 'Keep full buildings and check the surrounding context.'],
      ['Place and design', 'Choose a street or building group and the change to compare.'],
      ['Weather and metrics', 'Set the time, physical model, useful measures and budget.'],
      ['Model checks', 'Check the mesh, inlet, convergence and heat balance where relevant.'],
      ['Paired evidence', 'Compare options on common samples and test sensitivity.']
    ],
    tableTitle: 'What we can reuse, and what changes',
    cols: ['Work', 'Reuse', 'Update'],
    rows: [
      ['Site data', 'Original buildings, roads, water, planning and weather sources', 'Building membership, street inventory and metric denominators'],
      ['Shade and radiation', 'Source geometry and solar-position methods', 'Surrounding shade context, surface grids, times and results'],
      ['Wind and heat', 'Builders, diagnostics and recorded numerical criteria', 'Coverage, air domain, inlet, mesh, samples and selected solutions'],
      ['Energy and carbon', 'Use classes, area sources and energy-input templates', 'Area/use groups, energy ranges and dated carbon factors']
    ],
    chooseTitle: 'Set these before a new calculation',
    choices: [
      ['Place + change', 'A pilot street or building group and a specific intervention.'],
      ['Weather', 'Relevant hours and wind directions, with source quality flags.'],
      ['Measures', 'Wind, shade, radiation or energy measures that follow the design change.'],
      ['Budget + checks', 'Model size, useful compute capacity, checks and a review point.']
    ],
    domain: 'The air domain is set after the pilot, surrounding buildings and wind cases are known. Its dimensions remain open.',
    archive: 'Earlier wind/heat runs remain numerically unaccepted. Re-clipping those fields does not create an accepted baseline for this area.',
    repeat: 'If only a reporting mask changes, an accepted field can be resampled after checking coverage. Fresh solves follow changed geometry or physical inputs.',
    sources: 'Sources and method',
    plan: 'Scope plan · 18 October 2026',
    brief: 'Theme B brief · p. 4, Figure 5',
    cost: 'COST 732 · urban CFD guidance',
    error: 'The simulation plan could not load. Reload this page to read the current plan.'
  },
  zh: {
    eyebrow: '模拟计划',
    title: '让模型回应具体的设计问题',
    intro: 'Figure 5 研究范围用于整理现状和统计结果。风场与遮阴模型还要保留会影响目标街道的周边几何。',
    scope: '研究区', pending: '边界正在复核', models: '个完整建筑模型',
    flowLabel: '从研究区到方案比较',
    steps: [
      ['Figure 5 研究范围', '确定道路、河流边线和建筑清单。'],
      ['完整几何', '保留完整建筑，核对周边模型覆盖。'],
      ['地点与设计', '选定街道或建筑组，以及要比较的改动。'],
      ['天气与指标', '确定时段、物理模型、指标和计算预算。'],
      ['模型检查', '核对网格、来流、收敛及适用的热收支。'],
      ['成对比较', '在共同样点比较方案，并检查敏感性。']
    ],
    tableTitle: '哪些资料可复用，哪些内容要更新',
    cols: ['工作', '可复用', '需要更新'],
    rows: [
      ['场地资料', '原始建筑、道路、水系、规划与气象来源', '建筑归属、街道清单和各项统计分母'],
      ['遮阴与辐射', '源几何和太阳位置方法', '周边遮阴范围、地表网格、时段和结果'],
      ['风场与热', '建模脚本、诊断方法和已有数值准则', '覆盖范围、空气域、来流、网格、样点及选定计算'],
      ['能源与碳', '用途、面积来源和能源录入模板', '面积及用途组、能源范围和对应年份的碳系数']
    ],
    chooseTitle: '新计算前需要确定的内容',
    choices: [
      ['地点＋改动', '选定试点街道或建筑组，以及具体干预。'],
      ['天气', '选择相关时段和风向，保留来源质量码。'],
      ['指标', '按设计改动选择风、遮阴、辐射或能源指标。'],
      ['预算＋检查', '确定模型规模、可用算力、检查项和复核节点。']
    ],
    domain: '空气计算域要在试点、周边建筑和风向确定后设置，具体尺寸暂不固定。',
    archive: '此前的风热试算尚未通过完整数值检查。重新裁剪旧场不能生成这个研究区的合格基线。',
    repeat: '若仅改变结果统计范围，覆盖充分且已通过检查的场可以重新采样。几何或物理条件改变时，再按具体问题重新求解。',
    sources: '文件来源与方法',
    plan: '范围调整计划 · 2026 年 10 月 18 日',
    brief: 'Theme B 任务书 · 第 4 页图 5',
    cost: 'COST 732 · 城市 CFD 指南',
    error: '模拟计划未能加载，请重新加载页面以查看当前计划。'
  },
  ja: {
    eyebrow: '解析計画',
    title: '設計の問いに合わせてモデルを選ぶ',
    intro: '一つの研究区域で現況と集計範囲を統一します。風と日陰のモデルには、対象街路に影響する周辺形状も含めます。',
    scope: '研究区域', pending: '境界を確認中', models: '件の完全な建物モデル',
    flowLabel: '研究区域から案の比較まで',
    steps: [
      ['一つの研究区域', '道路・河川の境界と建物一覧を確定します。'],
      ['完全な形状', '建物全体を保持し、周辺の収録範囲を確認します。'],
      ['場所と設計', '街路や建物群、比較する変更を選びます。'],
      ['気象と指標', '時刻、物理モデル、指標、計算予算を定めます。'],
      ['モデルの確認', '格子、流入、収束、必要な熱収支を確認します。'],
      ['対応する案の比較', '共通の評価点で案を比較し、感度を調べます。']
    ],
    tableTitle: '再利用できる資料と更新する内容',
    cols: ['作業', '再利用', '更新'],
    rows: [
      ['現況資料', '元の建物・道路・水系・計画・気象資料', '建物の所属、街路一覧、各指標の分母'],
      ['日陰と放射', '元の形状と太陽位置の計算方法', '周辺の日陰形状、地表格子、時刻、結果'],
      ['風と熱', '作成スクリプト、診断法、記録済みの数値基準', '収録範囲、流体領域、流入、格子、評価点、選定した計算'],
      ['エネルギーと炭素', '用途・面積の資料と入力様式', '面積・用途群、エネルギーの範囲、対応年の排出係数']
    ],
    chooseTitle: '新しい計算の前に定めること',
    choices: [
      ['場所＋変更', '対象街路や建物群と具体的な対策を選びます。'],
      ['気象', '問いに合う時刻・風向を選び、品質フラグを保持します。'],
      ['指標', '設計の変更に対応する風・日陰・放射・エネルギー指標を選びます。'],
      ['予算＋確認', 'モデル規模、利用可能な計算資源、確認項目、見直す時点を定めます。']
    ],
    domain: '流体領域は対象地、周辺建物、風向を決めてから設定します。寸法は現時点で固定しません。',
    archive: '以前の風・熱試算は数値基準をすべて満たしていません。旧結果を切り抜いても、この区域の合格した現況結果にはなりません。',
    repeat: '集計範囲だけを変更する場合、収録範囲が十分な合格済み結果は再抽出できます。形状や物理条件の変更に応じて再計算します。',
    sources: '資料と方法',
    plan: '範囲変更計画 · 2026 年 10 月 18 日',
    brief: 'Theme B 課題書 · 4 ページ図 5',
    cost: 'COST 732 · 都市 CFD 指針',
    error: '解析計画を読み込めませんでした。ページを再読み込みしてください。'
  }
};

const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let planRequest;
async function loadPlan() {
  if (!planRequest) planRequest = fetch(new URL('./data/simulation-scope-plan.json', import.meta.url), {cache:'no-store'})
    .then(response => { if (!response.ok) throw new Error('Simulation plan unavailable'); return response.json(); })
    .catch(error => { planRequest = undefined; throw error; });
  return planRequest;
}

export async function renderSimulationPlan(lang = 'en', host) {
  const text = copy[lang] || copy.en;
  const root = typeof host === 'string' ? document.querySelector(host) : host;
  if (!root) throw new Error('Simulation plan host is missing');
  let data;
  try { data = await loadPlan(); }
  catch (error) {
    root.innerHTML = '<div class="sim-plan sim-plan-error" role="status">' + escape(text.error) + '</div>';
    return {loaded:false};
  }
  const area = data.boundary || {};
  const areaValue = Number.isFinite(area.area_ha) ? area.area_ha.toLocaleString(lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : 'en-US', {minimumFractionDigits:2, maximumFractionDigits:2}) + ' ha' : '';
  const count = Number.isInteger(area.building_count) ? area.building_count.toLocaleString(lang === 'zh' ? 'zh-CN' : lang === 'ja' ? 'ja-JP' : 'en-US') + ' ' + text.models : '';
  const pending = !area.geometry_sha256 || String(area.status || '').includes('pending');
  const scope = [areaValue, count].filter(Boolean).join(' · ');
  root.innerHTML = `
    <section class="sim-plan" aria-labelledby="sim-plan-title">
      <header class="sim-plan-head">
        <p class="sim-plan-eyebrow">${escape(text.eyebrow)}</p>
        <h3 id="sim-plan-title">${escape(text.title)}</h3>
        <p>${escape(text.intro)}</p>
        ${scope ? '<p class="sim-plan-scope"><strong>' + escape(text.scope) + '</strong> ' + escape(scope) + (pending ? '<span>' + escape(text.pending) + '</span>' : '') + '</p>' : ''}
      </header>
      <ol class="sim-plan-flow" aria-label="${escape(text.flowLabel)}">
        ${text.steps.map((step, index) => '<li><span class="sim-plan-step-no" aria-hidden="true">' + (index + 1) + '</span><h4>' + escape(step[0]) + '</h4><p>' + escape(step[1]) + '</p></li>').join('')}
      </ol>
      <h4 class="sim-plan-subhead">${escape(text.tableTitle)}</h4>
      <div class="sim-plan-table-wrap" tabindex="0" role="region" aria-label="${escape(text.tableTitle)}">
        <table class="sim-plan-table"><thead><tr>${text.cols.map(col => '<th scope="col">' + escape(col) + '</th>').join('')}</tr></thead>
        <tbody>${text.rows.map(row => '<tr><th scope="row">' + escape(row[0]) + '</th><td>' + escape(row[1]) + '</td><td>' + escape(row[2]) + '</td></tr>').join('')}</tbody></table>
      </div>
      <h4 class="sim-plan-subhead">${escape(text.chooseTitle)}</h4>
      <dl class="sim-plan-choices">${text.choices.map(item => '<div><dt>' + escape(item[0]) + '</dt><dd>' + escape(item[1]) + '</dd></div>').join('')}</dl>
      <div class="sim-plan-notes"><p>${escape(text.domain)}</p><p>${escape(text.archive)}</p><p>${escape(text.repeat)}</p></div>
      <footer class="sim-plan-sources"><strong>${escape(text.sources)}</strong>
        <a href="https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho/blob/main/docs/Simulation_Scope_Plan_2026-10-18.md" target="_blank" rel="noopener noreferrer">${escape(text.plan)}</a>
        <a href="https://drive.google.com/file/d/1LkMUcYlM57gvMKpN3Hs6T2u5ykOVmIwf/view" target="_blank" rel="noopener noreferrer">${escape(text.brief)}</a>
        <a href="https://www.mi.uni-hamburg.de/en/arbeitsgruppen/windkanallabor/documents.html" target="_blank" rel="noopener noreferrer">${escape(text.cost)}</a>
      </footer>
    </section>`;
  return {loaded:true, boundary:area.id, area_ha:area.area_ha, building_count:area.building_count, pending, lang:copy[lang] ? lang : 'en'};
}
