import {renderStreetFrontage} from './street-frontage.js?v=20261119';

const L=(en,zh,ja)=>({en,zh,ja}), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let lang=localStorage.getItem('kajicho-info-lang')||'en';if(!['en','zh','ja'].includes(lang))lang='en';
const text=x=>typeof x==='object'&&x!==null?(x[lang]||x.en||x.zh||''):String(x??'');
const tr=x=>esc(text(x));
const lex={
 en:{policy:'Policies',conditions:'Site Data',maps:'Current maps',mapIntro:'Read every theme at the same extent, with the official primary and approximate wider study outlines.',download:'Open PNG',source:'Source',scope:'Study area',primary:'Kajicho primary area',wider:'Kanda–Nihonbashi wider area (approx.)',area:'Area / ha',objects:'Building model objects',coverage:'Footprint coverage / %',height:'Median source height / m',known:'Models with source height',proxy:'Models with proxy height',unknownUse:'Models without known use',dataTitle:'Present-day source data',dataIntro:'The two study levels use full original building footprints. Source years and missing fields remain visible.',densityNote:'Footprint coverage divides the union of selected building footprints by the whole study polygon, including streets. It differs from parcel building coverage. Height medians use source heights only. Missing energy data remain missing.',policyTitle:'Planning policy and local conditions',policyIntro:'Retained source readings explain the published rule or plan, its spatial scope and its relation to Kajicho. Publication and source-check dates belong to each record.',fact:'Published record',meaning:'Local relevance',scopeNote:'Scope',dataNotes:'Source notes',sources:'Sources and data',overview:'Study area',license:'Maps: PNG · source attribution and data years remain on each plate.',note:'Mapping updated 28 October 2026. Building age updated 13 November 2026. Each map gives its source year.'},
 zh:{policy:'规划政策',conditions:'现状数据',maps:'同一场地，十二种阅读',mapIntro:'每个专题采用相同视野，同时保留官方重点区与概略外围区两层边界。',download:'打开 PNG',source:'来源',scope:'研究范围',primary:'鍛冶町重点区',wider:'神田・日本橋外围区（概略）',area:'面积 / ha',objects:'建筑模型对象',coverage:'建筑投影覆盖 / %',height:'有源高度中位值 / m',known:'有源高度对象数',proxy:'采用代理高度对象数',unknownUse:'用途未知对象数',dataTitle:'现状来源数据',dataIntro:'两层研究范围均按完整建筑投影纳入，保留来源年份与缺失字段。',densityNote:'建筑投影覆盖率以选中建筑投影的并集除以整个研究多边形面积，分母含道路，区别于地块建蔽率。高度中位值仅使用源高度；能源缺失字段继续保留为空。',policyTitle:'规划政策与地方条件',policyIntro:'沿用原站的资料阅读，分别呈现已发布的规则或规划、适用范围及其与鍛冶町的关系。发布日期与核查日期保留在各条来源中。',fact:'已发布依据',meaning:'与场地的关系',scopeNote:'适用范围',dataNotes:'来源说明',sources:'来源与数据',overview:'场地范围',license:'地图使用 PNG，图注保留来源署名与数据年份。',note:'场地地图更新于 2026 年 10 月 28 日；建筑年龄更新于 11 月 13 日。保留各来源年份。'},
 ja:{policy:'計画・政策',conditions:'現況データ',maps:'一つの地域、十二の読み方',mapIntro:'同じ範囲で各主題を比較し、公式の重点区域と概略の周辺区域を保持します。',download:'PNGを開く',source:'出典',scope:'対象範囲',primary:'鍛冶町の重点区域',wider:'神田・日本橋の周辺区域（概略）',area:'面積 / ha',objects:'建物模型数',coverage:'建物投影の割合 / %',height:'出典高さの中央値 / m',known:'出典高さがある模型',proxy:'推定高さの模型',unknownUse:'用途不明の模型',dataTitle:'現況の出典データ',dataIntro:'二つの範囲は建物投影全体で選定し、資料年と欠損を保持します。',densityNote:'建物投影の割合は、選定建物の投影の和集合を道路を含む区域全体で除した値で、敷地の建蔽率とは異なります。高さの中央値は出典高さのみ。エネルギーの欠損は空欄のままです。',policyTitle:'計画・政策と地域の条件',policyIntro:'元サイトの資料を使い、公表された制度・計画、適用範囲、鍛冶町との関係を示します。公開日・確認日は各記録に保持。',fact:'公表資料',meaning:'地域との関係',scopeNote:'適用範囲',dataNotes:'出典の説明',sources:'出典とデータ',overview:'対象区域',license:'地図はPNG。各図に出典と資料年を保持。',note:'マッピング更新：2026年10月28日。建築年は11月13日更新。資料年を保持。'}
};
const labels=[
['Study area','场地范围','対象範囲'],['Figure & ground','建筑肌理','建物と地'],['Connections','道路与交通','道路・交通'],['Building use','建筑用途','建物用途'],['Building height','建筑高度','建物高さ'],['Land use','土地利用','土地利用'],['Planning zones','规划分区','用途地域'],['Green & water','绿地与水系','緑と水'],['Flood scenarios','洪水情景','浸水想定'],['Places & services','设施与服务','施設・サービス'],['Building age','公开楼龄','建築年'],['Development status','施工与开发','開発状況']
].map(([en,zh,ja])=>L(en,zh,ja));
const files=['00_study_area','01_figure_ground','02_connections','03_building_use','04_building_height','05_land_use','06_planning_zones','07_green_water','08_flood','09_poi','10_building_age','11_development'];
const mapSrc=(i,file)=>'study-atlas/maps/'+file+(i===10?'_'+lang:'')+'.png'+(i===10?'?v=20261113':'');

const main = document.querySelector('#info-main');
const page = document.body.dataset.infoPage;
const isData = page === 'conditions';
const file = isData ? 'statistics' : 'policy';
let data;
const dataRequest = fetch('info-data/' + file + '.json?v=20261119-languages').then(response => {
  if (!response.ok) throw new Error('Site data: ' + response.status);
  return response.json();
});

function renderMapCards(t) {
  return files.map((file, i) => {
    const title = tr(labels[i]);
    const src = mapSrc(i, file);
    return '<article class="map-card">' +
      '<button data-map="' + i + '" type="button"><img loading="lazy" src="' + src + '" alt="' + title + '"></button>' +
      '<div class="map-foot"><h3 class="site-subtitle">' + title + '</h3>' +
      '<a target="_blank" rel="noopener" href="' + src + '">' + t.download + '</a></div></article>';
  }).join('');
}

function section(id, title, body, innerId = '') {
  const inner = innerId ? '<div id="' + innerId + '">' + body + '</div>' : body;
  return '<section class="info-section" id="' + id + '"><h2 class="site-section-title">' + title + '</h2>' + inner + '</section>';
}

function renderData(t) {
  const p = data.scopes?.primary_brief || {};
  const w = data.scopes?.study_area || {};
  const metrics = [
    ['area', 'area_ha', 2], ['objects', 'selected_models', 0],
    ['coverage', 'gross_footprint_coverage_pct', 1], ['height', 'source_height_median_m', 1],
    ['known', 'source_height_models', 0], ['proxy', 'height_proxy_models', 0], ['unknownUse', 'unknown_use_models', 0],
  ];
  const value = (scope, key, digits) => typeof scope[key] === 'number' ? scope[key].toFixed(digits) : '—';
  const rows = metrics.map(([label, key, digits]) => '<tr><th scope="row">' + t[label] + '</th><td>' +
    value(p, key, digits) + '</td><td>' + value(w, key, digits) + '</td></tr>').join('');

  return section('current-data', t.dataTitle,
    '<div class="table-scroll" tabindex="0" role="region" aria-label="' + t.dataTitle + '">' +
    '<table><thead><tr><th scope="col">' + t.scope + '</th><th scope="col">' + t.primary + '</th><th scope="col">' + t.wider +
    '</th></tr></thead><tbody>' + rows + '</tbody></table></div><p class="small">' + t.densityNote + '</p>' +
    '<div class="source-links"><a href="info-data/statistics.json">' + t.source + ' / JSON</a><a href="info-data/quality_checks.json">' +
    t.dataNotes + ' / JSON</a></div>') +
    section('current-maps', t.maps, '<p class="section-intro">' + t.mapIntro + '</p><p class="site-caption">' + t.note + '</p><div class="maps-grid">' + renderMapCards(t) + '</div>', 'mapping');
}

const phases = [
  {id:'baseline', label:L('Baseline and context', '现状与背景', '現況と背景'),
    topics:['two_precincts','street_identity','wider_links','context-flood','context-earthquake']},
  {id:'design', label:L('Design and approvals', '设计与审批', '設計と許認可'),
    topics:['climate_mechanisms','rules-site-capacity','rules-nearby-districts','rules-building-environment']},
  {id:'pilot', label:L('Pilot and delivery', '试点与实施', '試行と実施'),
    topics:['station_network','small_green','context-walking']},
];
const roles = [
  {id:'ward', label:L('Chiyoda City', '千代田区', '千代田区'),
    topics:['climate_mechanisms','two_precincts','street_identity','station_network','small_green','rules-site-capacity','rules-nearby-districts','rules-building-environment','context-walking','context-flood']},
  {id:'wide', label:L('Tokyo and nearby authorities', '東京都及周边政府', '東京都・周辺自治体'),
    topics:['wider_links','context-earthquake']},
  {id:'owners', label:L('Property owners', '产权人', '土地・建物所有者'),
    topics:['climate_mechanisms','street_identity','station_network','small_green','rules-site-capacity','rules-nearby-districts','rules-building-environment','context-walking','context-flood']},
];
const allPolicies = L('All readings', '全部资料', 'すべての資料');
let activeRole = 'all';

function filterPolicies(role) {
  activeRole = role;
  const topics = roles.find(item => item.id === role)?.topics;
  let count = 0;
  for (const group of document.querySelectorAll('.policy-group')) {
    let visible = 0;
    for (const item of group.querySelectorAll('.policy-reading')) {
      item.hidden = !!topics && !topics.includes(item.dataset.topic);
      if (!item.hidden) visible++;
    }
    count += visible;
    group.hidden = visible === 0;
    const jump = document.querySelector('.page-jumps a[href="#' + group.id + '"]');
    if (jump) jump.hidden = group.hidden;
  }
  for (const button of document.querySelectorAll('[data-policy-role]')) {
    button.setAttribute('aria-pressed', String(button.dataset.policyRole === role));
  }
  document.getElementById('policy-count').textContent = text(L(count + ' of ' + data.topics.length + ' readings', count + ' / ' + data.topics.length + ' 条资料', count + ' / ' + data.topics.length + ' 件'));
}

function renderPolicy(t) {
  const refs = (items = []) => items.filter(e => e.url).map(e =>
    '<a target="_blank" rel="noopener" href="' + esc(e.url) + '">' +
    tr(e.document_title || e.title || t.source) + ' ' + esc(e.year || '') + ' ' + esc(e.page || '') + '</a>').join(' · ');
  const topics = new Map(data.topics.map(item => [item.id, item]));
  const groups = phases.map(phase => `<section class="policy-group" id="policy-phase-${phase.id}">
    <h2 class="site-section-title">${tr(phase.label)}</h2>
    <div class="policy-grid">${phase.topics.map(key => {
      const item = topics.get(key);
      return `<article class="policy-reading technical-card" id="policy-${esc(key)}" data-topic="${esc(key)}">
        <h3 class="site-subtitle">${tr(item.title)}</h3>
        <p>${tr(item.source_fact)}</p>
        <p class="small"><strong>${t.scopeNote}</strong> · ${tr(item.scope)}</p>
        <p class="policy-refs">${refs(item.evidence)}</p>
      </article>`;
    }).join('')}</div></section>`).join('');
  const filter = tr(L('Filter by who uses the policy', '按相关主体筛选', '関係者で絞り込む'));
  return `<div id="policy-readings">
    <h2 class="site-subtitle" id="policy-filter-label">${filter}</h2>
    <div class="policy-filters" role="group" aria-labelledby="policy-filter-label">
      ${[{id:'all',label:allPolicies}, ...roles].map(role =>
        `<button type="button" class="tech-button" data-policy-role="${role.id}" aria-pressed="false">${tr(role.label)}</button>`).join('')}
    </div>
    <p class="site-caption" id="policy-count" aria-live="polite"></p>
    ${groups}
    <div class="source-links" id="policy-sources"><a href="info-data/policy.json">${t.sources} / JSON</a></div>
  </div>`;
}

function recordsIndex() {
  const name = tr(L('History and building records', '历史与建筑资料', '歴史と建物の記録'));
  const entries = [
    ['/history', L('Local history','地方历史','地域の歴史'), '27', L('dated events','项年代事件','件の出来事'), 'GSI · Chiyoda City'],
    ['/building-age', L('Building age','建筑楼龄','建築年'), '1,074', L('building models','个建筑模型','件の建物模型'), 'Byear · MLIT PLATEAU'],
    ['/building-update', L('Building status review','建筑现状核查','建物現況の確認'), '2026-10-28', L('review date','核查日期','確認日'), 'MLIT PLATEAU · Studio'],
  ];
  return `<section class="info-section" id="records" aria-labelledby="records-title">
    <h2 class="site-section-title" id="records-title">${name}</h2>
    <div class="records-grid">${entries.map(([url,title,value,caption,source]) => `
      <a class="record-card technical-card" href="${url}">
        <h3 class="site-subtitle">${tr(title)}</h3>
        <p class="record-metric"><strong class="tech-value">${value}</strong> <span>${tr(caption)}</span></p>
        <span class="site-caption tech-label">${source}</span>
      </a>`).join('')}</div>
    </section>`;
}

function render() {
  const t = lex[lang];
  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang;
  document.title = t[page] + (lang === 'en' ? ' · Kajicho' : ' · 鍛冶町');
  const area = tr(L('Kajicho 1 & 2', '鍛冶町一・二丁目', '鍛冶町一・二丁目'));
  const jumps = isData
    ? [['records', tr(L('History and records','历史与建筑资料','歴史と建物の記録'))],
       ['current-data', t.dataTitle], ['current-maps', t.maps],
       ['district', tr(L('Development and heritage','开发与历史资产','開発と歴史資産'))], ['sources', t.sources]]
    : [['policy-readings', tr(allPolicies)], ...phases.map(phase => ['policy-phase-' + phase.id, tr(phase.label)]), ['policy-sources', t.sources]];
  const shortcuts = '<nav class="site-local-nav page-jumps" aria-label="' + t[page] + '">' +
    jumps.map(([id, title]) => '<a href="#' + id + '">' + title + '</a>').join('') + '</nav>';
  const hero = '<header class="page-intro" id="overview"><p class="site-kicker">' + area +
    '</p><h1 class="site-title">' + t[page] + '</h1><p class="site-lede">' +
    (isData ? t.dataIntro : t.policyIntro) + '</p></header>';
  const records = isData ? recordsIndex() : '';
  const details = data ? (isData ? renderData(t) : renderPolicy(t)) : '';
  main.innerHTML = hero + shortcuts + records + details;
  if (!data) return;

  if (isData) {
    renderStreetFrontage(document.querySelector('#current-data'), lang);
    const dialog = document.querySelector('#plate-dialog');
    for (const button of document.querySelectorAll('[data-map]')) {
      button.onclick = () => {
        const i = Number(button.dataset.map);
        const img = dialog.querySelector('#plate-image');
        img.src = mapSrc(i, files[i]);
        img.alt = text(labels[i]);
        dialog.querySelector('#plate-title').textContent = img.alt;
        dialog.showModal();
      };
    }
  } else {
    for (const button of document.querySelectorAll('[data-policy-role]')) {
      button.addEventListener('click', () => filterPolicies(button.dataset.policyRole));
    }
    document.querySelector('.page-jumps a[href="#policy-readings"]').addEventListener('click', () => filterPolicies('all'));
    filterPolicies(activeRole);
  }
}

for (const button of document.querySelectorAll('.site-languages [data-lang]')) {
  button.onclick = () => {
    lang = button.dataset.lang;
    localStorage.setItem('kajicho-info-lang', lang);
    render();
  };
}
document.querySelector('#plate-close')?.addEventListener('click', () => document.querySelector('#plate-dialog').close());
render();
dataRequest.then(result => {
  data = result;
  render();
}).catch(console.error);
