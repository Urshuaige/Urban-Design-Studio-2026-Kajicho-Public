const copy = {
  zh: { title: '从设计街区到计算边界', detail: '鍛冶町 · 街区地图', overview: '东京 · 完整计算域',
    design: '设计区域', model: '周边建模范围', full: '完整计算域',
    designLegend: '设计区 · 鍛冶町一、二丁目', modelLegend: '建模建筑包络', domainLegend: '计算域边界',
    buildingsLegend: '实际纳入的建筑', note: '设计区采用当前工作边界。蓝色虚线为纳入建筑的包络，建筑仅覆盖图中绘出的范围。',
    mapHelp: '拖动平移 · 按 + / − 缩放', coreLabel: '鍛冶町 1–2', inlet: '南侧入流 ↑', outlet: '北侧出流 ↑',
    side: '侧边界', wind: '南风 → 北', zoomIn: '放大地图', zoomOut: '缩小地图',
    mapSource: '底图与边界来源', sourceText: 'OSM 在线底图；PLATEAU 2025 建筑；计算域来自当前求解网格。',
    error: '底图连接暂不可用，边界仍可查看。', loading: '正在加载地图…',
    detailAria: '鍛冶町设计区及周边建筑地图', overviewAria: '东京计算域、入流、出流与侧边界地图' },
  en: { title: 'From the design area to the domain edge', detail: 'Kajicho · Street map', overview: 'Tokyo · Full domain',
    design: 'Design area', model: 'Model extent', full: 'Full domain',
    designLegend: 'Design area · Kajicho 1–2', modelLegend: 'Building envelope', domainLegend: 'CFD boundary',
    buildingsLegend: 'Included buildings', note: 'The design area uses the current working boundary. Blue dashes show the envelope of the included buildings. Building coverage is limited to the footprints shown.',
    mapHelp: 'Drag to pan · Use + / − to zoom', coreLabel: 'KAJICHO 1–2', inlet: 'South inlet ↑', outlet: 'North outlet ↑',
    side: 'Side boundary', wind: 'South wind → north', zoomIn: 'Zoom in', zoomOut: 'Zoom out',
    mapSource: 'Map and boundary sources', sourceText: 'Live OSM map; PLATEAU 2025 buildings; domain from the current solver mesh.',
    error: 'The basemap is unavailable. Boundaries remain visible.', loading: 'Loading map…',
    detailAria: 'Map of the Kajicho design area and surrounding buildings', overviewAria: 'Map of the Tokyo CFD domain, inlet, outlet and side boundaries' },
  ja: { title: '設計対象街区から計算領域の端まで', detail: '鍛冶町 · 街区地図', overview: '東京 · 計算領域全体',
    design: '設計対象範囲', model: '周辺モデル範囲', full: '計算領域全体',
    designLegend: '設計対象 · 鍛冶町一・二丁目', modelLegend: '建物モデルの包絡', domainLegend: '計算領域の境界',
    buildingsLegend: '計算に含めた建物', note: '設計対象は現時点の作業範囲です。青い破線は採用した建物の包絡で、建物は表示した範囲に限ります。',
    mapHelp: 'ドラッグで移動 · + / − で拡大・縮小', coreLabel: '鍛冶町 1–2', inlet: '南側の流入 ↑', outlet: '北側の流出 ↑',
    side: '側面境界', wind: '南風 → 北', zoomIn: '拡大', zoomOut: '縮小',
    mapSource: '地図・境界の出典', sourceText: 'OSM オンライン地図、PLATEAU 2025 建物、現在の計算メッシュの領域。',
    error: '背景地図に接続できません。境界は表示できます。', loading: '地図を読み込み中…',
    detailAria: '鍛冶町の設計対象範囲と周辺建物の地図', overviewAria: '東京の計算領域、流入・流出・側面境界の地図' }
};
Object.assign(copy.zh,{expanded:'750 m + 10H 候选（未求解）',candidateLegend:'750 m + 10H 候选与新增对象',candidateNote:'紫色为范围对比候选，尚未进入当前发布风热场。'});
Object.assign(copy.en,{expanded:'750 m + 10H · not solved',candidateLegend:'750 m + 10H candidate and added objects',candidateNote:'Purple shows a sensitivity candidate. Published wind and heat fields still use the original geometry.'});
Object.assign(copy.ja,{expanded:'750m＋10H 候補・未計算',candidateLegend:'10H 候補境界・追加建物',candidateNote:'紫は感度比較の候補で、現在の公開風・熱場には含まれません。'});

const courseCopy={"en": {"designLegend": "Current study area", "coreLabel": "Current study area", "note": "Solid primary and dashed approximate wider outlines from Figure 5. Model envelope and domain views describe the archived experiment; the new simulation plan is on the main page."}, "zh": {"designLegend": "当前研究区", "coreLabel": "当前研究区", "note": "实线重点区与虚线概略外围区均依 Figure 5。模型与计算域视图记录历史试验，新仿真调整计划见主页。"}, "ja": {"designLegend": "現在の研究区域", "coreLabel": "現在の研究区域", "note": "実線重点区域と破線概略周辺区域は図5に基づく。モデルと計算領域は旧試行で、新計算計画はメインページに示す。"}};for(const l of Object.keys(courseCopy))Object.assign(copy[l],courseCopy[l]);
const archiveCopy={"en": {"title": "Archived computational coverage", "detail": "Current study area and archived model", "model": "Archived model extent", "full": "Archived air domain", "sourceText": "OSM map; PLATEAU 2025 buildings; air domain from the archived solver mesh.", "detailAria": "Current study area with archived model coverage", "overviewAria": "Archived computational domain and boundary conditions"}, "zh": {"title": "历史计算范围", "detail": "当前研究区与历史模型", "model": "历史模型范围", "full": "历史空气计算域", "sourceText": "OSM 底图；PLATEAU 2025 建筑；空气计算域来自历史求解网格。", "detailAria": "当前研究区与历史模型覆盖", "overviewAria": "历史计算域与边界条件"}, "ja": {"title": "旧計算の範囲", "detail": "現在の研究区域と旧モデル", "model": "旧モデルの範囲", "full": "旧空気計算領域", "sourceText": "OSM地図、PLATEAU 2025建物、旧ソルバーメッシュの計算領域。", "detailAria": "現在の研究区域と旧モデル範囲", "overviewAria": "旧計算領域と境界条件"}};for(const l of Object.keys(archiveCopy))Object.assign(copy[l],archiveCopy[l]);
let language = 'en', maps = [], labels = [], boundaries, currentView = 'design', candidateGroups = [];
const colors = { design: '#bc5036', model: '#287a94', domain: '#263c55' };
const text = key => copy[language][key];
const feature = (data, role) => data.features.find(f => f.properties.role === role);

function label(map, position, key, className = '') {
  const marker = L.marker(position, { interactive: false, keyboard: false,
    icon: L.divIcon({ className: `atlas-label ${className}`, html: '', iconSize: null }) }).addTo(map);
  labels.push({ marker, key });
}

function frame(map, area, padding = 25) {
  map.fitBounds(area, { padding: [padding, padding], animate: false });
}

function setView(view) {
  currentView = view;
  candidateGroups.forEach((group,i)=>view==='expanded'?group.addTo(maps[i]):group.remove());
  document.getElementById('domainCandidateKey').hidden=view!=='expanded';
  document.getElementById('domainCandidateNote').hidden=view!=='expanded';
  frame(maps[0], boundaries[view], view === 'design' ? 72 : 30);
  frame(maps[1],view==='expanded'?boundaries.expandedDomain:boundaries.full,28);
  document.querySelectorAll('[data-map-view]').forEach(button => {
    const active = button.dataset.mapView === view;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.getElementById('domainDetailTitle').textContent = text(view === 'design' ? 'detail' : view);
}

function addNorth(map) {
  const North = L.Control.extend({ options: { position: 'topright' }, onAdd() {
    const el = L.DomUtil.create('div', 'atlas-north');
    el.setAttribute('aria-label', 'North');
    el.innerHTML = '<span>N</span><svg viewBox="0 0 32 48" aria-hidden="true"><path d="M16 2 29 44 16 35Z" fill="#263c55"/><path d="M16 2 3 44 16 35Z" fill="#faf8ef" stroke="#263c55" stroke-width="1.2"/></svg>';
    return el;
  }});
  new North().addTo(map);
}

function addLayers(map, data, overview) {
  const canvas = L.canvas({ padding: .25 });
  L.geoJSON(data, { renderer: canvas, interactive: false,
    filter: f => f.properties.role === 'building',
    style: f => ({ color: f.properties.core ? colors.design : colors.model, weight: overview ? .2 : .55,
      opacity: overview ? .6 : .75, fillColor: f.properties.core ? colors.design : colors.model,
      fillOpacity: overview ? .35 : .22 }) }).addTo(map);
  for (const [role, color, dash, weight, opacity] of [
    ['domain', colors.domain, '10 7', 2.5, .025],
    ['model_extent', colors.model, '6 5', 2, .025],
    ['study_area','#36353a','6 4',2,0],['primary_brief','#36353a',null,3,0]
  ]) {
    L.geoJSON(feature(data, role), { interactive: false,
      style: { color, dashArray: dash, weight, fillColor: color, fillOpacity: opacity } }).addTo(map);
  }
  const designCenter = L.geoJSON(feature(data,'study_area')).getBounds().getCenter();
  label(map, designCenter, 'coreLabel', 'atlas-core');
  if (overview) {
    const d = boundaries.full;
    label(map, [d.getSouth() + .0018, d.getCenter().lng], 'inlet', 'atlas-edge');
    label(map, [d.getNorth() - .0018, d.getCenter().lng], 'outlet', 'atlas-edge');
    label(map, [d.getCenter().lat, d.getWest() + .002], 'side', 'atlas-side atlas-side-west');
    label(map, [d.getCenter().lat, d.getEast() - .002], 'side', 'atlas-side atlas-side-east');
  }
}

export function localizeDomainMap(lang) {
  language = copy[lang] ? lang : 'en';
  document.querySelectorAll('[data-map-t]').forEach(el => el.textContent = text(el.dataset.mapT));
  document.getElementById('domainMap').setAttribute('aria-label', text('detailAria'));
  document.getElementById('domainOverview').setAttribute('aria-label', text('overviewAria'));
  for (const { marker, key } of labels) marker.getElement().textContent = text(key);
  for (const map of maps) {
    const el = map.getContainer();
    for (const [selector, key] of [['.leaflet-control-zoom-in', 'zoomIn'], ['.leaflet-control-zoom-out', 'zoomOut']]) {
      const button = el.querySelector(selector);
      button.title = text(key); button.setAttribute('aria-label', text(key));
    }
  }
  if (maps.length) document.getElementById('domainDetailTitle').textContent = text(currentView === 'design' ? 'detail' : currentView);
}

export async function initDomainMap(lang) {
  localizeDomainMap(lang);
  try {
    const response = await fetch('data/domain-map.geojson');
    if (!response.ok) throw Error('Domain geometry: ' + response.status);
    const data = await response.json();
    const candidate = await (await fetch('data/domain-candidates.geojson')).json();
    boundaries = { design: L.geoJSON({type:'FeatureCollection',features:data.features.filter(f=>['study_area'].includes(f.properties.role))}).getBounds(),
      model: L.geoJSON(feature(data, 'model_extent')).getBounds(),
      full: L.geoJSON(feature(data, 'domain')).getBounds() };
    boundaries.expanded=L.geoJSON(feature(candidate,'candidate_model_extent')).getBounds();
    boundaries.expandedDomain=L.geoJSON(feature(candidate,'candidate_domain')).getBounds();
    for (const [index, id] of ['domainMap', 'domainOverview'].entries()) {
      const map = L.map(id, { scrollWheelZoom: false, zoomSnap: .1, minZoom: 11, maxZoom: 19,
        attributionControl: true });
      maps.push(map);
      map.attributionControl.setPrefix(false);
      const tiles = L.tileLayer(data.metadata.basemap.tile_url, { maxZoom: 19, keepBuffer: 1,
        referrerPolicy: 'strict-origin-when-cross-origin',
        attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors' }).addTo(map);
      let errors = 0;
      tiles.on('tileerror', () => { if (++errors > 2) {
        document.getElementById('domainTileNotice').hidden = false;
      }});
      L.control.scale({ imperial: false, maxWidth: 100, position: 'bottomleft' }).addTo(map);
      addNorth(map); addLayers(map, data, index === 1);
      const group=L.layerGroup();
      L.geoJSON(candidate,{interactive:false,renderer:L.canvas({padding:.25}),style:f=>({color:'#85549b',weight:f.properties.role==='candidate_building'?1.4:2.2,dashArray:f.properties.role==='candidate_building'?null:'3 5',fillOpacity:f.properties.role==='candidate_building'?.25:0})}).addTo(group);
      candidateGroups.push(group);
      frame(map, index ? boundaries.full : boundaries.design, index ? 28 : 72);
      new ResizeObserver(() => {
        map.invalidateSize({ pan: false });
        frame(map, index ? (currentView==='expanded'?boundaries.expandedDomain:boundaries.full) : boundaries[currentView], index ? 28 : currentView === 'design' ? 72 : 30);
      }).observe(map.getContainer());
    }
    document.querySelectorAll('[data-map-view]').forEach(button => {
      button.disabled = false;
      button.addEventListener('click', () => setView(button.dataset.mapView));
    });
    document.getElementById('domainAtlas').dataset.ready = 'true';
    localizeDomainMap(language);
  } catch (error) {
    console.error(error);
    document.getElementById('domainTileNotice').hidden = false;
    document.getElementById('domainAtlas').dataset.ready = 'failed';
  }
}
