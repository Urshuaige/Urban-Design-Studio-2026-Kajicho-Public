import * as THREE from 'three';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { addStreetDetails } from './street-details.js?v=20261122-model-display';
import { createStudyContours } from './study-contours.js?v=20261122-layer-opacity';
import { createStudyPrint, loadStudyPrint } from './study-print.js?v=20261121-printed-materials';
import { buildingLayers, unknownColor } from './condition-data.js?v=20261124-renewal-map';
import { conditionSwitch, createConditionLayers, loadBuildingConditions, setLegend } from './condition-layers.js?v=20261124-renewal-map';
import { createSiteBase } from './site-base.js?v=20261122-model-display';

const words = {
  title: ['Kajicho in 3D', '鍛冶町 3D', '鍛冶町三维'],
  workbench: ['Scenario workbench', 'シナリオ比較', '情景工作台'],
  places: ['Places', '場所', '地点'],
  kanamono: ['Kanda Kanamono-dori', '神田金物通り', '神田金物通'],
  school: ['Former Imagawa Junior High School', '旧今川中学校', '旧今川中学校'],
  heisei: ['Heisei-dori', '平成通り', '平成通'],
  riverContext: ['Kanda River & Route 1', '神田川と首都高1号', '神田川与东侧高架'],
  akihabara: ['Akihabara Station', '秋葉原駅', '秋叶原站'],
  contextView: ['Context view', '周辺視点', '周边视角'],
  contextLevels: ['GSI banks · indicative water and deck levels', '河岸はGSI標高・水面と高架床版は参考値', '河岸为 GSI 高程 · 水面与桥面为展示值'],
  stationLevels: ['JR track alignment · indicative deck heights', 'JR線の線形・高架の高さは参考値', 'JR 轨道按实际走向 · 高架高度为展示值'],
  street: ['Street view', '街路視点', '街道视角'],
  block: ['Block view', '街区視点', '街坊视角'],
  layers: ['Layers', 'レイヤー', '图层'],
  mapOverlays: ['Map overlays', '地図レイヤー', '地图叠加层'],
  buildingColor: ['Building color', '建物の色分け', '建筑着色'],
  moreLayers: ['More mapped data', 'その他の地図データ', '更多现状图层'],
  use: ['Building use', '建物用途', '建筑用途'],
  solar: ['Rooftop solar', '屋根の太陽光', '屋顶光伏'],
  building: ['Building', '建物', '建筑'],
  choose: ['Select a building in the model.', 'モデル内の建物を選択します。', '点选模型中的建筑。'],
  clearSelection: ['Clear selection', '選択を解除', '取消选中'],
  height: ['Height', '高さ', '高度'],
  storeys: ['Storeys', '地上階数', '地上层数'],
  built: ['Built', '建築年', '建成年份'],
  potential: ['Annual rooftop solar potential', '屋根の年間発電ポテンシャル', '屋顶年光伏潜力'],
  asuka: ['Asuka’s method · existing roof', 'Asuka の手法 · 現況屋根', 'Asuka 的方法 · 现状屋顶'],
  buildingId: ['Building ID', '建物 ID', '建筑 ID'],
  current: ['Existing conditions', '現状', '现状'],
  overview: ['Overview', '全体表示', '总览'],
  renewalView: ['Renewal site', '更新の地点', '更新地点'],
  study: ['Study area', '研究範囲', '研究区'],
  loading: ['Loading the Kajicho model…', '鍛冶町のモデルを読み込んでいます…', '正在加载鍛冶町模型…'],
  failed: ['Could not load the 3D model. Reload the page to try again.', '3D モデルを読み込めません。ページを再読み込みしてください。', '三维模型加载失败，请刷新页面重试。'],
  pending: ['Pending', '要確認', '待确认'],
  orbitHelp: ['Drag to rotate. Scroll to zoom. Click a building.', 'ドラッグで回転、スクロールでズーム、クリックで建物を選択。', '拖动旋转，滚轮缩放，点选建筑。'],
  streetHelp: ['Drag to look around. Scroll or use ↑ and ↓ to move along the street.', 'ドラッグで見回し、スクロールまたは上下キーで街路を移動。', '拖动转头，滚轮或上下方向键沿街移动。'],
  energySource: ['Solar method', '太陽光の算定手法', '光伏方法'],
  office: ['Office', '業務', '办公'], commerce: ['Commercial', '商業', '商业'],
  housing: ['Housing / mixed', '住宅・併用', '住宅及混合'],
  civic: ['Public / education', '公共・教育', '公共及教育'],
  other: ['Other', 'その他', '其他'], unknown: ['Use unrecorded', '用途の記録なし', '用途待确认'],
  solarLow: ['Under 1 MWh/yr', '1 MWh/年未満', '低于 1 MWh/年'],
  solarMid: ['1–5 MWh/yr', '1–5 MWh/年', '1–5 MWh/年'],
  solarHigh: ['5–10 MWh/yr', '5–10 MWh/年', '5–10 MWh/年'],
  solarTop: ['10+ MWh/yr', '10 MWh/年以上', '10 MWh/年以上'],
  solarMissing: ['No estimate', '未算定', '待估算'],
  zoomIn: ['Zoom in', '拡大', '放大'], zoomOut: ['Zoom out', '縮小', '缩小'],
  forward: ['Move forward', '前進', '沿街前进'], back: ['Move back', '後退', '沿街后退'],
  aerial: ['Aerial photo', '航空写真', '航空影像'],
  aerialCredit: [' · Tokyo 2023 edition · 24 cm/px', ' · 東京23区 2023年度 · 24 cm/画素', ' · 东京 2023 年度 · 24 厘米/像素'],
  aerialFull: ['Full image', '全画像', '查看整幅影像'],
  aerialLoading: ['Loading the aerial photo…', '航空写真を読み込み中…', '正在加载航空影像…'],
  aerialUnavailable: ['Aerial photo unavailable. Try again.', '航空写真を読み込めません。再度お試しください。', '航空影像加载失败，请重试。'],
  demandPending: ['Asuka’s electricity and gas tables pending', 'Asuka の電力・ガス需要データは未確認', 'Asuka 的逐栋用电和燃气原表待补'],
  electricity: ['Electricity', '電力', '用电'],
  gas: ['Gas', 'ガス', '燃气'],
  energyTablePending: ['Source table pending', '元データは未確認', '原表待补'],
  buildingOpacity: ['Study buildings opacity', '研究範囲内の建物の不透明度', '场地内建筑不透明度'],
  missingValue: ['No GIS value', 'GIS値なし', 'GIS 无记录'],
  sourcesConflict: ['Conflicting sources', '出典が不一致', '来源有冲突'],
  yearBound: ['Built by {year}', '{year}年までに建築', '{year} 年或更早建成'],
  knownValues: ['{n} buildings with records', '記録のある建物 {n} 棟', '{n} 栋建筑有记录'],
  modelCount: ['{n} buildings', '建物 {n} 棟', '{n} 栋建筑'],
  useCount: ['{n} buildings with a PLATEAU use', 'PLATEAU 用途のある建物 {n} 棟', '{n} 栋有 PLATEAU 用途'],
  solarCount: ['{n} roofs with a solar estimate', '太陽光の推計がある屋根 {n} 棟', '{n} 栋有屋顶光伏估算'],
  focusedLayer: ['Layer shown on the selected building', '選択した建物にレイヤーを適用', '图层仅应用于所选建筑'],
  road: ['Ground roads', '地上道路', '地面道路'],
  highway: ['Elevated highway', '高架高速', '高架高速'],
  sidewalk: ['Sidewalk', '歩道', '人行道'],
  railway: ['Railway', '鉄道', '铁路轨道'],
  river: ['River', '河川', '河道'],
  parks: ['Parks', '公園', '公园与绿地'],
  trees: ['Street trees', '街路樹', '街树'],
  greenInventory: ['Tokyo green inventory', '東京都の緑のオープンデータ', '东京绿化资料'],
  studyBuildings: ['Study area buildings', '研究範囲内の建物', '研究范围内建筑'],
};

const buildingGray = '#d6d8db';
const useColors = {
  office: '#b9b4bf', commerce: '#cc9c96', housing: '#a6bcad',
  civic: '#94ACC1', other: '#cbc2ac', unknown: buildingGray,
};
const solarColors = {
  solarLow: '#e0e6f0', solarMid: '#b8c7dd', solarHigh: '#879fbe',
  solarTop: '#536f91', solarMissing: buildingGray,
};
const contextColors = {
  ground: '#dfe3e6', road: '#ffffff', highway: '#85898d', sidewalk: '#d3d8dd',
  park: '#83a080',
  station: '#d9dde0',
  water: '#839eae', riverBank: '#9ba8ae', bridge: '#bac1c6', highwayStructure: '#a4adb6',
};

const app = document.querySelector('[data-city]');
const element = selector => app.querySelector(selector);
const view = element('[data-view]');
const mount = element('[data-canvas]');
const lang = () => document.documentElement.lang?.slice(0, 2) || 'en';
const say = value => Array.isArray(value) ? value[lang() === 'ja' ? 1 : lang() === 'zh' ? 2 : 0] : value;
const t = key => say(words[key]);
const number = (n, digits = 1) => new Intl.NumberFormat(lang(), { maximumFractionDigits: digits }).format(n);
const write = (key, value) => { element(key).textContent = value; };
const href = name => '/city-model-assets/' + name;
const siteAccent = getComputedStyle(app).getPropertyValue('--accent').trim() || '#8b3a2b';
const railColor = new THREE.Color(siteAccent).lerp(new THREE.Color('#ffffff'), .13);
const railFinish = new THREE.MeshStandardMaterial({
  color: railColor, roughness: .96, transparent: true, opacity: .57, depthWrite: false,
});
const focusedColor = '#' + new THREE.Color(siteAccent).lerp(new THREE.Color(buildingGray), .32).getHexString();
const contextBuildingColor = '#' + new THREE.Color(buildingGray).lerp(new THREE.Color(siteAccent), .18).getHexString();
const legacyRailRoles = new Set(['jr', 'shinkansen', 'piers']);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#eaedf0');
const camera = new THREE.PerspectiveCamera(42, 1, .25, 6000);
const overviewTarget = new THREE.Vector3(60, 3, -90);
const overviewOffset = new THREE.Vector3(-1180, 1540, 1870);
const sun = new THREE.DirectionalLight('#fcfdff', 1.76);
sun.position.set(-370, 550, 170);
sun.target.position.set(2, 10, -244);
sun.castShadow = true;
Object.assign(sun.shadow.camera, { left: -1080, right: 1080, top: 1140, bottom: -1140, near: 15, far: 2250 });
sun.shadow.camera.updateProjectionMatrix();
sun.shadow.mapSize.set(3072, 3072);
sun.shadow.normalBias = .27;
sun.shadow.bias = -.00023;
sun.shadow.radius = 2;
sun.shadow.intensity = .64;
const fill = new THREE.DirectionalLight('#eff4fc', .49);
fill.position.set(230, 170, -360);
const selectedOutline = new THREE.Group();
const selectionStroke = new THREE.LineBasicMaterial({
  color: siteAccent, transparent: true, opacity: .82, depthWrite: false,
});
scene.add(new THREE.HemisphereLight('#fafcff', '#ccd3db', 1.42), fill, sun, sun.target, selectedOutline);

let renderer, controls, data, terrain, studyContours, studyFinish, selection, currentPlace, transition, scheduled, asphalt, conditionLayers;
let layer = null;
let street = null;
let buildingOpacity = 100;
let conditionRecords = { population: {}, ages: {} };
const conditionCounts = {};
const populationKeys = ['workers', 'residents', 'households'];
const parts = new Map();
const studyBuildings = new Set();
const hitTargets = [];
const places = {};
const materials = new Map();
const fadedMaterials = new WeakMap();
const ray = new THREE.Raycaster();

function material(hex, block = false) {
  const key = block ? 'building-' + hex : hex;
  if (!materials.has(key)) {
    materials.set(key, new THREE.MeshStandardMaterial({
      color: hex, roughness: .96, side: THREE.DoubleSide,
      emissive: block ? hex : 0x000000, emissiveIntensity: .10,
      polygonOffset: block, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    }));
  }
  return materials.get(key);
}

function solarBand(value) {
  if (value === null) return 'solarMissing';
  if (value < 1000) return 'solarLow';
  if (value < 5000) return 'solarMid';
  return value < 10000 ? 'solarHigh' : 'solarTop';
}

function conditionValue(key, type) {
  if (type === 'height') return data.records[key].height;
  if (type === 'age') {
    const record = conditionRecords.ages[key];
    return record?.[1] === 'year' ? 2026 - record[0] : null;
  }
  return conditionRecords.population[key]?.[type];
}

function buildingColor(key) {
  if (selection && key !== selection) return buildingGray;
  const record = data.records[key];
  if (layer === 'solar') return solarColors[solarBand(record.solarKwh)];
  if (layer === 'use') return useColors[record.group] || buildingGray;
  if (Object.hasOwn(buildingLayers, layer)) {
    const definition = buildingLayers[layer];
    const value = conditionValue(key, layer);
    if (!Number.isFinite(value)) return unknownColor;
    const index = definition.breaks.findIndex(limit => value < limit);
    return definition.colors[index < 0 ? definition.breaks.length : index];
  }
  if (key === selection) return focusedColor;
  return studyBuildings.has(key) ? buildingGray : contextBuildingColor;
}

function styleBuildings() {
  const opacity = buildingOpacity / 100;
  const print = !layer && !selection && buildingOpacity === 100;
  for (const [key, meshes] of parts) {
    const inStudy = studyBuildings.has(key);
    let finish = print && inStudy ? studyFinish : material(buildingColor(key), true);
    const fade = inStudy && buildingOpacity < 100;
    if (fade) {
      if (!fadedMaterials.has(finish)) {
        const translucent = finish.clone();
        Object.assign(translucent, { transparent: true, depthWrite: false, side: THREE.FrontSide });
        fadedMaterials.set(finish, translucent);
      }
      finish = fadedMaterials.get(finish);
      finish.opacity = opacity;
    }
    for (const mesh of meshes) {
      mesh.material = finish;
      mesh.visible = !inStudy || buildingOpacity > 0;
      mesh.castShadow = !fade;
      mesh.renderOrder = fade ? 2 : 0;
    }
  }
  const studyKey = element('[data-study-key]');
  studyKey.hidden = Boolean(layer || selection);
  studyKey.style.setProperty('--ground-swatch-opacity', opacity);
  studyContours.visible = !selection && buildingOpacity > 0;
  studyContours.material.uniforms.strength.value = opacity;
  for (const line of selectedOutline.children) line.geometry.dispose();
  selectedOutline.clear();
  if (!selection) return;
  const selectedInStudy = studyBuildings.has(selection);
  if (selectedInStudy && buildingOpacity === 0) return;
  if (!(selectedInStudy && buildingOpacity < 100) && ![buildingGray, unknownColor].includes(buildingColor(selection))) return;
  selectionStroke.opacity = selectedInStudy ? .82 * opacity : .82;
  for (const mesh of parts.get(selection)) {
    const edge = new THREE.EdgesGeometry(mesh.geometry, 42).applyMatrix4(mesh.matrixWorld);
    const line = new THREE.LineSegments(edge, selectionStroke);
    line.renderOrder = 1;
    selectedOutline.add(line);
  }
}

function roadMaterial(mesh) {
  if (!asphalt) {
    const size = 128;
    const pixels = new Uint8Array(size * size * 4);
    let seed = 43691;
    for (let i = 0; i < pixels.length; i += 4) {
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      const gray = 238 + (seed >>> 28);
      pixels.set([gray, gray, gray, 255], i);
    }
    const texture = new THREE.DataTexture(pixels, size, size);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
    texture.generateMipmaps = true;
    texture.needsUpdate = true;
    asphalt = new THREE.MeshStandardMaterial({
      color: contextColors.highway, map: texture, roughness: .98, side: THREE.DoubleSide,
    });
  }
  const positions = mesh.geometry.getAttribute('position');
  const uv = new Float32Array(positions.count * 2);
  for (let i = 0; i < positions.count; i++) {
    uv[2 * i] = positions.getX(i) * .25;
    uv[2 * i + 1] = positions.getZ(i) * .25;
  }
  mesh.geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  return asphalt;
}

function applyRoadsToTerrain(ground, roads, water, bounds) {
  const span = bounds.getSize(new THREE.Vector3());
  const tile = document.createElement('canvas');
  tile.width = Math.ceil(span.x * 2);
  tile.height = Math.ceil(span.z * 2);
  const paint = tile.getContext('2d');
  paint.fillStyle = contextColors.ground;
  paint.fillRect(0, 0, tile.width, tile.height);
  paint.fillStyle = contextColors.road;
  const vertex = new THREE.Vector3();
  for (const mesh of roads) {
    const positions = mesh.geometry.getAttribute('position');
    const index = mesh.geometry.index;
    const xy = new Float32Array(positions.count * 2);
    for (let i = 0; i < positions.count; i++) {
      vertex.fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld);
      xy[2 * i] = (vertex.x - bounds.min.x) * tile.width / span.x;
      xy[2 * i + 1] = (vertex.z - bounds.min.z) * tile.height / span.z;
    }
    paint.beginPath();
    for (let i = 0; i < (index?.count ?? positions.count); i += 3) {
      const a = 2 * (index ? index.getX(i) : i);
      let b = 2 * (index ? index.getX(i + 1) : i + 1);
      let c = 2 * (index ? index.getX(i + 2) : i + 2);
      if ((xy[b] - xy[a]) * (xy[c + 1] - xy[a + 1]) < (xy[c] - xy[a]) * (xy[b + 1] - xy[a + 1])) {
        [b, c] = [c, b];
      }
      paint.moveTo(xy[a], xy[a + 1]);
      paint.lineTo(xy[b], xy[b + 1]);
      paint.lineTo(xy[c], xy[c + 1]);
      paint.closePath();
    }
    paint.fill();
  }
  const map = new THREE.CanvasTexture(tile);
  map.colorSpace = THREE.SRGBColorSpace;
  map.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
  const finish = new THREE.MeshStandardMaterial({
    map, roughness: .98, side: THREE.DoubleSide,
  });
  const patchFinish = finish.clone();
  Object.assign(patchFinish, { polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
  for (const mesh of [...ground, ...water]) {
    const positions = mesh.geometry.getAttribute('position');
    const uv = new Float32Array(positions.count * 2);
    for (let i = 0; i < positions.count; i++) {
      vertex.fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld);
      uv[2 * i] = (vertex.x - bounds.min.x) / span.x;
      uv[2 * i + 1] = 1 - (vertex.z - bounds.min.z) / span.z;
    }
    mesh.geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  }
  for (const mesh of ground) mesh.material = mesh === terrain ? finish : patchFinish;
}

function connectImagery(surfaces) {
  const control = element('[data-aerial]');
  const credit = element('[data-aerial-credit]');
  const status = element('[data-aerial-status]');
  const modelFinishes = surfaces.map(mesh => mesh.material);
  let photos;
  let enabled = false;

  function statusText(key) {
    status.hidden = !key;
    if (key) {
      status.dataset.copy = key;
      status.textContent = t(key);
    }
  }

  async function showPhoto(next) {
    if (control.disabled || next === enabled) return;
    control.disabled = true;
    statusText();
    try {
      if (next && !photos) {
        statusText('aerialLoading');
        const map = await new THREE.TextureLoader().loadAsync(href('imagery/kajicho-2023.jpg?v=20261122-river-and-imagery'));
        map.colorSpace = THREE.SRGBColorSpace;
        map.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
        const byMaterial = new Map();
        photos = modelFinishes.map(finish => {
          if (!byMaterial.has(finish)) {
            byMaterial.set(finish, new THREE.MeshBasicMaterial({
              map, side: finish.side, toneMapped: false,
              polygonOffset: finish.polygonOffset, polygonOffsetFactor: finish.polygonOffsetFactor,
              polygonOffsetUnits: finish.polygonOffsetUnits,
            }));
          }
          return byMaterial.get(finish);
        });
      }
      const finishes = next ? photos : modelFinishes;
      surfaces.forEach((mesh, i) => mesh.material = finishes[i]);
      enabled = next;
      control.setAttribute('aria-pressed', String(enabled));
      credit.hidden = !enabled;
      view.toggleAttribute('data-aerial-active', enabled);
      const url = new URL(location.href);
      if (enabled) url.searchParams.set('imagery', '1');
      else url.searchParams.delete('imagery');
      history.replaceState(null, '', url);
      statusText();
      drawSoon();
    } catch {
      statusText('aerialUnavailable');
    } finally {
      control.disabled = false;
    }
  }

  control.addEventListener('click', () => showPhoto(!enabled));
  if (new URLSearchParams(location.search).get('imagery') === '1') showPhoto(true);
}

function showBuilding() {
  const record = data?.records[selection];
  element('[data-building]').hidden = !record;
  element('[data-building-empty]').hidden = !!record;
  element('[data-clear-selection]').hidden = !record;
  if (!record) return;
  const label = record.use?.[lang()] || record.use?.en || t('pending');
  const title = element('[data-building-title]');
  title.hidden = !record.name;
  title.textContent = record.name || '';
  write('[data-use]', label);
  write('[data-height]', Number.isFinite(record.height) ? number(record.height) + ' m' : t('pending'));
  write('[data-storeys]', record.storeys === null ? t('pending') : number(record.storeys, 0));
  write('[data-pv]', record.solarKwh === null ? t('pending') : number(record.solarKwh, 0) + ' kWh/yr');
  for (const key of populationKeys) {
    const value = conditionValue(selection, key);
    write('[data-' + key + ']', Number.isFinite(value) ? number(value, 0) : t('missingValue'));
  }
  const age = conditionRecords.ages[selection];
  element('[data-date-fact]').hidden = !age;
  if (age) {
    write('[data-built]', age[1] === 'year' ? age[0] : age[1] === 'bound' ?
      t('yearBound').replace('{year}', age[0]) : t('sourcesConflict'));
  }
  write('[data-id]', record.gml || selection);
  element('[data-building]').dataset.building = selection;
}

function legend() {
  const list = element('[data-legend]');
  list.hidden = !layer;
  const condition = buildingLayers[layer];
  if (condition) {
    const { breaks, colors, units } = condition;
    const entries = colors.map((color, index) => {
      const lower = breaks[index - 1], upper = breaks[index];
      const interval = index === 0 ? '0–<' + upper : upper === undefined ? '≥' + lower : lower + '–<' + upper;
      return [interval + ' ' + say(units), color];
    });
    entries.push([t('missingValue'), unknownColor]);
    setLegend(list, entries, buildingOpacity / 100);
    const count = t('knownValues').replace('{n}', number(conditionCounts[layer] || 0, 0));
    write('[data-coverage]', say(condition.source) + ' · ' + (selection ? t('focusedLayer') : count));
    return;
  }
  const palette = layer === 'solar' ? solarColors : layer === 'use' ? useColors : {};
  setLegend(list, Object.entries(palette).map(([key, color]) => [t(key), color]), buildingOpacity / 100);
  if (data) {
    const count = layer === 'solar' ? data.totals.asukaSolar : layer === 'use' ? data.totals.plateauUse : data.totals.buildings;
    const label = layer === 'solar' ? 'solarCount' : layer === 'use' ? 'useCount' : 'modelCount';
    write('[data-coverage]', layer && selection ? t('focusedLayer') : t(label).replace('{n}', number(count, 0)));
  }
}

function translate() {
  for (const node of app.querySelectorAll('[data-copy]')) node.textContent = t(node.dataset.copy);
  for (const node of app.querySelectorAll('[data-building-label]')) {
    node.textContent = say(buildingLayers[node.dataset.buildingLabel].label);
  }
  conditionLayers?.translate();
  write('[data-view-title]', t(view.dataset.mode === 'renewal' ? 'renewalView' : currentPlace || 'overview'));
  const levels = element('[data-context-levels]');
  const levelsKey = currentPlace === 'akihabara' ? 'stationLevels' : currentPlace === 'riverContext' ? 'contextLevels' : null;
  levels.hidden = !levelsKey;
  if (levelsKey) levels.textContent = t(levelsKey);
  write('[data-view-help]', t(street ? 'streetHelp' : 'orbitHelp'));
  app.querySelector('[data-zoom="in"]').setAttribute('aria-label', t(street ? 'forward' : 'zoomIn'));
  app.querySelector('[data-zoom="out"]').setAttribute('aria-label', t(street ? 'back' : 'zoomOut'));
  legend();
  showBuilding();
}

function updateUrl() {
  const url = new URL(location.href);
  if (currentPlace) url.searchParams.set('place', currentPlace);
  else url.searchParams.delete('place');
  if (selection) url.searchParams.set('building', selection);
  else url.searchParams.delete('building');
  if (layer) url.searchParams.set('layer', layer);
  else url.searchParams.delete('layer');
  url.searchParams.delete('fade');
  if (buildingOpacity < 100) url.searchParams.set('buildingOpacity', buildingOpacity);
  else url.searchParams.delete('buildingOpacity');
  history.replaceState(null, '', url);
}

function select(key, update = true) {
  selection = parts.has(key) ? key : undefined;
  styleBuildings();
  showBuilding();
  legend();
  if (update) updateUrl();
  drawSoon();
  if (selection && update) {
    const panel = element('.city-sidebar');
    const record = element('[data-building]').closest('section');
    const overhang = record.getBoundingClientRect().bottom - panel.getBoundingClientRect().bottom;
    if (overhang > 0) panel.scrollTop += overhang;
  }
}

function switchLayer(next, update = true) {
  layer = next;
  styleBuildings();
  for (const button of app.querySelectorAll('[data-layer]')) {
    button.setAttribute('aria-checked', String(button.dataset.layer === layer));
  }
  legend();
  if (update) updateUrl();
  drawSoon();
}

function setBuildingOpacity(value) {
  const wasOpaque = buildingOpacity === 100;
  buildingOpacity = THREE.MathUtils.clamp(Math.round(value), 0, 100);
  element('[data-building-opacity]').value = buildingOpacity;
  write('[data-building-opacity-value]', buildingOpacity + '%');
  styleBuildings();
  legend();
  if (wasOpaque !== (buildingOpacity === 100)) renderer.shadowMap.needsUpdate = true;
  drawSoon();
}

function groundAt(x, z) {
  ray.set(new THREE.Vector3(x, 175, z), new THREE.Vector3(0, -1, 0));
  return ray.intersectObject(terrain, false)[0]?.point.y ?? 8;
}

function toWorld(easting, northing) {
  const x = easting - data.origin[0], z = data.origin[1] - northing;
  return new THREE.Vector3(x, groundAt(x, z), z);
}

function installPlaces() {
  for (const [key, point] of Object.entries(data.places)) {
    const center = toWorld(...point.center);
    const entry = { mode: point.mode, center, offset: point.offset };
    if (point.mode === 'street') {
      const segments = point.path.map(p => toWorld(...p));
      const line = new THREE.CurvePath();
      for (let i = 1; i < segments.length; i++) {
        if (segments[i - 1].distanceToSquared(segments[i]) > .15) {
          line.add(new THREE.LineCurve3(segments[i - 1], segments[i]));
        }
      }
      entry.route = line;
    }
    places[key] = entry;
  }
}

function draw(now) {
  scheduled = false;
  if (transition) {
    const { from, to, lookFrom, lookTo, started, duration } = transition;
    const fraction = Math.min((now - started) / duration, 1);
    const eased = 1 - (1 - fraction) ** 3;
    camera.position.lerpVectors(from, to, eased);
    controls.target.lerpVectors(lookFrom, lookTo, eased);
    camera.lookAt(controls.target);
    if (fraction === 1) {
      transition = null;
      controls.enabled = !street;
      if (controls.enabled) controls.update();
    } else drawSoon();
  }
  // Keep depth precision over the district without clipping the near street-level view.
  const near = street && !transition ? .25 : THREE.MathUtils.clamp(camera.position.distanceTo(controls.target) / 120, .4, 24);
  if (Math.abs(near - camera.near) > .001) {
    camera.near = near;
    camera.updateProjectionMatrix();
  }
  renderer.render(scene, camera);
}

function drawSoon() {
  if (renderer && !scheduled) {
    scheduled = true;
    requestAnimationFrame(draw);
  }
}

function animate(eye, target, duration = 690) {
  const direct = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const focus = controls.target.clone();
  controls.enabled = false;
  if (direct) {
    camera.position.copy(eye);
    controls.target.copy(target);
    camera.lookAt(target);
    controls.enabled = !street;
    if (controls.enabled) controls.update();
  } else {
    transition = {
      from: camera.position.clone(), to: eye, lookFrom: focus, lookTo: target,
      started: performance.now(), duration,
    };
  }
  drawSoon();
}

function streetAim(position) {
  const pitch = street.pitch;
  return position.clone().add(new THREE.Vector3(
    Math.sin(street.yaw) * Math.cos(pitch), Math.sin(pitch),
    -Math.cos(street.yaw) * Math.cos(pitch),
  ).multiplyScalar(25));
}

function moveStreet(distance = 0, entry = false) {
  street.offset = THREE.MathUtils.clamp(street.offset + distance / street.route.getLength(), .01, .99);
  const eye = street.route.getPoint(street.offset);
  eye.y += 1.65;
  const look = streetAim(eye);
  if (entry) animate(eye, look, 920);
  else {
    camera.position.copy(eye);
    controls.target.copy(look);
    camera.lookAt(look);
    drawSoon();
  }
}

function go(key, update = true) {
  currentPlace = places[key] ? key : undefined;
  const place = places[currentPlace];
  street = null;
  if (place?.route) {
    const direction = place.route.getPoint(.57).sub(place.route.getPoint(.46));
    const offset = currentPlace === 'heisei' ? .25 : .21;
    street = { route: place.route, offset, yaw: Math.atan2(direction.x, -direction.z), pitch: .04 };
    moveStreet(0, true);
  } else if (place?.mode === 'region') {
    const focus = place.center.clone();
    const offset = place.offset || [-315, 465, 445];
    animate(focus.clone().add(new THREE.Vector3(...offset)), focus);
  } else if (place) {
    const focus = place.center.clone().add(new THREE.Vector3(0, 8, 0));
    animate(focus.clone().add(new THREE.Vector3(-83, 92, 108)), focus);
  } else {
    animate(overviewTarget.clone().add(overviewOffset), overviewTarget.clone());
  }
  for (const button of app.querySelectorAll('[data-place]')) {
    button.setAttribute('aria-pressed', String(button.dataset.place === currentPlace));
  }
  view.dataset.mode = street ? 'street' : currentPlace ? 'block' : 'overview';
  camera.fov = street ? 51 : 42;
  camera.updateProjectionMatrix();
  translate();
  if (update) updateUrl();
}

function focusRenewal({ center, extent }) {
  street = null;
  currentPlace = undefined;
  const target = new THREE.Vector3(...center);
  const distance = Math.max(105, Math.min(extent * 1.58, 690));
  const offset = new THREE.Vector3(-.71, .92, 1).multiplyScalar(distance);
  animate(target.clone().add(offset), target);
  for (const button of app.querySelectorAll('[data-place]')) button.setAttribute('aria-pressed', 'false');
  view.dataset.mode = 'renewal';
  write('[data-view-title]', t('renewalView'));
  camera.fov = 42;
  camera.updateProjectionMatrix();
  updateUrl();
}

function zoom(inward) {
  if (transition) return;
  if (street) {
    moveStreet(inward ? 7 : -7);
    return;
  }
  const delta = camera.position.clone().sub(controls.target);
  const newDistance = THREE.MathUtils.clamp(
    delta.length() * (inward ? .8 : 1.25), controls.minDistance, controls.maxDistance,
  );
  camera.position.copy(controls.target.clone().add(delta.setLength(newDistance)));
  controls.update();
  drawSoon();
}

function connectInputs() {
  const canvas = renderer.domElement;
  let pointer;
  canvas.addEventListener('pointerdown', event => {
    if (event.button !== 0 || transition) return;
    view.focus({ preventScroll: true });
    pointer = { x: event.clientX, y: event.clientY, yaw: street?.yaw, pitch: street?.pitch, moved: false };
    if (street) canvas.setPointerCapture(event.pointerId);
  });
  canvas.addEventListener('pointermove', event => {
    if (!pointer || transition) return;
    const dx = event.clientX - pointer.x, dy = event.clientY - pointer.y;
    if (Math.hypot(dx, dy) > 4) pointer.moved = true;
    if (street && pointer.moved) {
      street.yaw = pointer.yaw - dx * .004;
      street.pitch = THREE.MathUtils.clamp(pointer.pitch - dy * .004, -1.35, 1.35);
      moveStreet();
    }
  });
  canvas.addEventListener('pointercancel', () => { pointer = null; });
  canvas.addEventListener('pointerup', event => {
    if (pointer && !pointer.moved && !transition) {
      const box = canvas.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(
        (event.clientX - box.left) * 2 / box.width - 1,
        1 - (event.clientY - box.top) * 2 / box.height,
      ), camera);
      const hits = ray.intersectObjects(hitTargets, false).filter(hit => hit.object.visible);
      const building = hits[0];
      const obstruction = buildingOpacity === 100 ? building :
        hits.find(hit => !studyBuildings.has(hit.object.userData.key));
      if (conditionLayers?.inspect(ray, obstruction?.distance ?? Infinity)) {
        if (selection) select();
      } else select(building?.object.userData.key);
    }
    pointer = null;
  });
  canvas.addEventListener('wheel', event => {
    if (!street) return;
    event.preventDefault();
    if (!transition) moveStreet(event.deltaY < 0 ? 5 : -5);
  }, { passive: false });
  view.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      if (conditionLayers?.clear()) return;
      if (selection) select();
      else go();
    }
    if (!street || transition || !['ArrowUp', 'ArrowDown'].includes(event.key)) return;
    event.preventDefault();
    moveStreet(event.key === 'ArrowUp' ? 6 : -6);
  });
  for (const button of app.querySelectorAll('[data-place]')) button.addEventListener('click', () => go(button.dataset.place));
  for (const button of app.querySelectorAll('[data-layer]')) {
    button.addEventListener('click', () => switchLayer(layer === button.dataset.layer ? null : button.dataset.layer));
  }
  for (const button of app.querySelectorAll('[data-zoom]')) button.addEventListener('click', () => zoom(button.dataset.zoom === 'in'));
  const slider = element('[data-building-opacity]');
  slider.addEventListener('input', () => setBuildingOpacity(slider.valueAsNumber));
  slider.addEventListener('change', updateUrl);
  element('[data-reset]').addEventListener('click', () => go());
  element('[data-clear-selection]').addEventListener('click', () => select());
}

function installModels(buildings, land, context, extension, printAssets, withParkVolumes) {
  scene.add(land, context, extension, buildings);
  scene.updateMatrixWorld(true);
  const ground = [];
  const roads = [];
  const water = [];
  const bridges = material(contextColors.bridge).clone();
  // The model includes downward-facing bridge bases at the water elevation.
  bridges.side = THREE.FrontSide;
  bridges.shadowSide = THREE.DoubleSide;
  const river = material(contextColors.water).clone();
  Object.assign(river, { polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });

  for (const group of [land, context, extension]) group.traverse(node => {
    if (!node.isMesh) return;
    const role = node.userData.sceneRole || node.parent.userData.sceneRole;
    if (role === 'boundary' || (role === 'park' && withParkVolumes) ||
        legacyRailRoles.has(role) || node.name.startsWith('station-Yamanote centerline')) {
      node.visible = false;
      return;
    }
    if (role === 'road') {
      roads.push(node);
      node.visible = false;
      return;
    }
    const color = contextColors[role] || contextColors.station;
    node.material = role === 'highway' ? roadMaterial(node) : role === 'railway' ? railFinish : material(color);
    if (role === 'bridge') node.material = bridges;
    if (role === 'water') {
      node.material = river;
      water.push(node);
    }
    if (role === 'railway') node.renderOrder = 3;
    node.receiveShadow = true;
    node.castShadow = ['station', 'bridge', 'highway', 'highwayStructure'].includes(role);
    if (role === 'ground') terrain = node;
    if (role === 'ground' || role === 'groundPatch') ground.push(node);
  });
  applyRoadsToTerrain(ground, roads, water, new THREE.Box3().setFromObject(terrain));
  buildings.updateMatrixWorld(true);
  buildings.traverse(node => {
    const key = node.userData.buildingKey || node.parent?.userData.buildingKey;
    if (!node.isMesh || !data.records[key]) return;
    const role = node.userData.sceneRole || node.parent?.userData.sceneRole;
    if (role === 'primary' || role === 'wider') studyBuildings.add(key);
    node.userData.key = key;
    node.castShadow = true;
    if (!parts.has(key)) parts.set(key, []);
    parts.get(key).push(node);
    hitTargets.push(node);
  });
  if (!terrain || parts.size !== data.totals.buildings) throw new Error('Building model and records differ');
  const studyMeshes = [...studyBuildings].flatMap(key => parts.get(key));
  studyContours = createStudyContours(studyMeshes);
  studyFinish = createStudyPrint(material(buildingGray, true), printAssets, studyMeshes, renderer.getPixelRatio());
  scene.add(studyContours, createSiteBase(terrain));
  scene.updateMatrixWorld(true);
  return { ground, imagery: [...ground, ...water] };
}

async function start() {
  const message = element('[data-message]');
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.6));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.shadowMap.autoUpdate = false;
    mount.append(renderer.domElement);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.minDistance = 16;
    controls.maxDistance = 2950;
    controls.maxPolarAngle = Math.PI * .49;
    controls.target.copy(overviewTarget);
    camera.position.copy(overviewTarget.clone().add(overviewOffset));
    controls.update();

    const loader = new GLTFLoader();
    const [records, buildings, land, context, streetDetails, additions, outerBuildings, surroundings, printAssets, conditions] = await Promise.all([
      fetch(href('records.json')).then(async response => {
        if (!response.ok) throw new Error('Building records could not be loaded');
        return response.json();
      }),
      loader.loadAsync(href('buildings.glb')),
      loader.loadAsync(href('terrain.glb?v=20261121-akihabara')),
      loader.loadAsync(href('site.glb')),
      fetch(href('street-details.json?v=20261122-model-display')).then(async response => {
        if (!response.ok) throw new Error('Street details could not be loaded');
        return response.json();
      }).catch(error => {
        console.warn('Kajicho street details:', error);
        return null;
      }),
      fetch(href('context-records.json?v=20261121-wider-current')).then(async response => {
        if (!response.ok) throw new Error('Outer-area building records could not be loaded');
        return response.json();
      }),
      loader.loadAsync(href('context-buildings.glb?v=20261121-wider-current')),
      loader.loadAsync(href('context-site.glb?v=20261121-akihabara')),
      loadStudyPrint(),
      loadBuildingConditions().catch(error => {
        console.warn('Kajicho building conditions:', error);
        return conditionRecords;
      }),
    ]);
    data = records;
    conditionRecords = conditions;
    const outerKeys = Object.keys(additions);
    if (outerKeys.some(key => Object.hasOwn(records.records, key))) throw new Error('Duplicate building in the extension');
    Object.assign(data.records, additions);
    data.totals.buildings += outerKeys.length;
    data.totals.plateauUse += Object.values(additions).filter(record => record.use).length;
    data.places.study = { mode: 'region', center: [-5440.32, -34213.39], offset: [-570, 990, 850] };
    data.places.riverContext = { mode: 'region', center: [-5450, -33606] };
    data.places.akihabara = { mode: 'region', center: [-5450, -33473], offset: [-232, 302, 358] };
    buildings.scene.add(outerBuildings.scene);
    const withParkVolumes = Boolean(streetDetails?.parks?.length);
    const { ground, imagery } = installModels(buildings.scene, land.scene, context.scene, surroundings.scene, printAssets, withParkVolumes);
    conditionLayers = createConditionLayers({ app, scene, ground, drawSoon, translate: say, number, focusRenewal });
    for (const name of Object.keys(buildingLayers)) {
      conditionCounts[name] = [...parts.keys()].filter(key => Number.isFinite(conditionValue(key, name))).length;
    }
    if (streetDetails) {
      addStreetDetails(scene, streetDetails, contextColors);
      view.dataset.streetTrees = streetDetails.trees.length;
      view.dataset.parks = streetDetails.parkCount ?? 0;
      element('[data-park-key]').hidden = !withParkVolumes;
      element('[data-green-credit]').hidden = !withParkVolumes;
      element('[data-tree-key]').hidden = streetDetails.trees.length === 0;
      element('[data-sidewalk-key]').hidden = streetDetails.sidewalks.length === 0;
    }
    element('[data-road-key]').style.setProperty('--ground-swatch', contextColors.road);
    element('[data-highway-key]').style.setProperty('--ground-swatch', contextColors.highway);
    element('[data-sidewalk-key]').style.setProperty('--ground-swatch', contextColors.sidewalk);
    element('[data-rail-key]').style.setProperty('--ground-swatch', '#' + railColor.getHexString());
    element('[data-river-key]').style.setProperty('--ground-swatch', contextColors.water);
    element('[data-park-key]').style.setProperty('--ground-swatch', contextColors.park);
    element('[data-study-key]').style.setProperty('--ground-swatch', buildingGray);
    renderer.shadowMap.needsUpdate = true;
    installPlaces();
    connectInputs();
    controls.addEventListener('change', drawSoon);
    const resize = () => {
      renderer.setSize(view.clientWidth, view.clientHeight, false);
      studyContours.material.uniforms.viewport.value.set(view.clientWidth, view.clientHeight);
      studyContours.material.uniforms.pixelRatio.value = renderer.getPixelRatio();
      camera.aspect = view.clientWidth / view.clientHeight;
      camera.updateProjectionMatrix();
      drawSoon();
    };
    new ResizeObserver(resize).observe(view);
    resize();
    const query = new URLSearchParams(location.search);
    const requestedLayer = query.get('layer');
    const available = ['use', 'solar', ...Object.keys(buildingLayers)];
    if (requestedLayer === 'height' || requestedLayer === 'age') element('[data-more-panel]').open = true;
    const opacity = query.get('buildingOpacity');
    if (opacity !== null && /^\d{1,3}$/.test(opacity)) setBuildingOpacity(Number(opacity));
    else if (query.get('fade') === '1') setBuildingOpacity(34);
    switchLayer(available.includes(requestedLayer) ? requestedLayer : null, false);
    if (query.has('building')) select(query.get('building'), false);
    if (query.has('place')) go(query.get('place'), false);
    for (const button of app.querySelectorAll('button:disabled')) button.disabled = false;
    element('[data-building-opacity]').disabled = false;
    message.hidden = true;
    view.dataset.state = 'ready';
    view.dataset.buildings = parts.size;
    view.dataset.mode ||= 'overview';
    translate();
    connectImagery(imagery);
  } catch (error) {
    renderer?.dispose();
    view.dataset.state = 'error';
    message.querySelector('p').dataset.copy = 'failed';
    translate();
    console.error('Kajicho 3D:', error);
  }
}

for (const [key, spec] of Object.entries(buildingLayers)) {
  const button = conditionSwitch(spec.label, say);
  button.dataset.layer = key;
  button.firstChild.dataset.buildingLabel = key;
  button.disabled = true;
  element(populationKeys.includes(key) ? '[data-building-layers]' : '[data-more-building-layers]').append(button);
}
translate();
new MutationObserver(translate).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
start();
