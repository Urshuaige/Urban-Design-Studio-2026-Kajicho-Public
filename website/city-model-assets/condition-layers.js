import * as THREE from 'three';
import { trafficRibbons } from './traffic-layer.js?v=20261124-renewal-map';
import { buildRenewalLayer } from './renewal-layer.js?v=20261124-renewal-map';
import { bands, facilityKeys, ndviColumnHeights, siteOverlays, sourceForOverlay, streetColors, streetRims, volumeStyle } from './condition-data.js?v=20261124-renewal-map';
import { perceptionRibbons } from './perception-layer.js?v=20261122-legend-and-base';

const version = '20261122-legend-and-base';
const renewalVersion = '20261124-renewal-map';
const asset = (name, revision = version) => '/city-model-assets/conditions/' + name + '?v=' + revision;
const core = new Set(['flood', 'ndvi', 'streets', 'perception', 'traffic', 'renewal']);
const labels = {
  source: ['Source map', '出典地図', '原图'],
  loading: ['Loading the source map…', '地図を読み込み中…', '正在加载原图…'],
  failed: ['Map unavailable. Toggle the layer to retry.', '表示できません。レイヤーを切り替えて再試行してください。', '图层加载失败。关闭后再打开可重试。'],
  basins: ['2018 Kanda basin inundation map. Water height uses the midpoint of each mapped depth class.',
    '2018年神田川流域の浸水予想。水の高さは浸水区分の中間値。', '2018 年神田川流域浸水图。水面高度取原浸水深度分档的中点。'],
  classes: [['Low', '低', '低'], ['Middle', '中', '中'], ['High', '高', '高']],
  cell: ['Cell', 'セル', '像元'],
  displayHeight: ['display height', '表示高', '显示柱高'],
  depth: ['Mapped depth', '想定浸水深', '原图浸水深'],
  segment: ['Street segment', '街路区間', '路段'],
  opacity: ['Layer opacity', 'レイヤーの不透明度', '图层不透明度'],
  chooseLocation: ['Choose a location', '地点を選択', '选择地点'],
};

export function conditionSwitch(text, translate) {
  const button = document.createElement('button');
  button.type = 'button';
  button.setAttribute('role', 'switch');
  button.setAttribute('aria-checked', 'false');
  const label = document.createElement('span');
  label.textContent = translate(text);
  const track = document.createElement('span');
  track.className = 'city-switch';
  track.setAttribute('aria-hidden', 'true');
  button.append(label, track);
  return button;
}

export function setLegend(list, entries, opacity = 1) {
  list.style.setProperty('--swatch-opacity', opacity);
  const items = entries.map(([label, color, outline, glyph]) => {
    const item = document.createElement('li');
    const chip = document.createElement('i');
    chip.style.backgroundColor = color;
    if (outline) chip.style.borderColor = outline;
    if (color === 'transparent') chip.classList.add('city-legend-outline');
    if (glyph) {
      chip.classList.add('city-legend-glyph');
      chip.textContent = glyph;
    }
    chip.setAttribute('aria-hidden', 'true');
    item.append(chip, label);
    return item;
  });
  list.replaceChildren(...items);
}

export async function loadBuildingConditions() {
  return fetchSource('building-conditions.json');
}

async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(url + ' returned HTTP ' + response.status);
  return response.json();
}

function fetchSource(name) {
  return fetchJSON(asset(name));
}

function reusable(load) {
  let pending;
  return () => pending ??= load().catch(error => {
    pending = undefined;
    throw error;
  });
}

function withOpacity(layer) {
  const preset = layer.meshes[0].material.opacity;
  const appearances = new Map(layer.meshes.map(({ material }) => [material, {
    transparent: material.transparent,
    depthWrite: material.depthWrite,
    relativeOpacity: material.opacity / preset,
  }]));
  return { ...layer, defaultOpacity: Math.round(preset * 100), appearances };
}

function applyOpacity(layer, percent) {
  const opacity = percent / 100;
  for (const [material, initial] of layer.appearances) {
    material.opacity = Math.min(1, opacity * initial.relativeOpacity);
    const transparent = initial.transparent || material.opacity < 1;
    if (material.transparent !== transparent) {
      material.transparent = transparent;
      material.needsUpdate = true;
    }
    material.depthWrite = initial.depthWrite && material.opacity === 1;
  }
  for (const mesh of layer.meshes) mesh.visible = percent > 0;
}

function triangleMesh(positions, colors, faceRows, opacity = 1, colorsWithAlpha = false) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, colorsWithAlpha ? 4 : 3));
  const material = new THREE.MeshBasicMaterial({
    vertexColors: true, side: THREE.DoubleSide, transparent: opacity < 1,
    opacity, depthWrite: opacity === 1, toneMapped: false, forceSinglePass: true,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData.faceRows = faceRows;
  return mesh;
}

function prismMeshes(records, style, display) {
  const positions = [], colors = [], faceRows = [], outlines = [];
  records.forEach((record, row) => {
    const [height, hex] = style(record);
    const top = new THREE.Color(hex);
    const wall = top.clone().multiplyScalar(.76);
    function triangle(points, color, alpha = 1) {
      for (const p of points) {
        positions.push(...p);
        colors.push(color.r, color.g, color.b, alpha);
      }
      faceRows.push(row);
    }
    for (const rings of record.polygons) {
      const xy = rings.map(ring => ring.map(([x, , z]) => new THREE.Vector2(x, z)));
      const indices = THREE.ShapeUtils.triangulateShape(xy[0], xy.slice(1));
      const elevated = rings.map(ring => ring.map(([x, y, z]) => [x, y + height, z]));
      const tops = elevated.flat();
      for (const [a, b, c] of indices) {
        const [p, q, r] = [tops[a], tops[b], tops[c]];
        const turn = (q[0] - p[0]) * (r[2] - p[2]) - (q[2] - p[2]) * (r[0] - p[0]);
        triangle(turn > 0 ? [p, r, q] : [p, q, r], top);
      }
      rings.forEach((ring, i) => {
        const above = elevated[i];
        const facesOut = THREE.ShapeUtils.isClockWise(xy[i]) === (i !== 0);
        for (let index = 0; index < ring.length; index++) {
          const next = (index + 1) % ring.length;
          const [a, b] = facesOut ? [index, next] : [next, index];
          triangle([ring[a], above[a], ring[b]], wall, .47);
          triangle([ring[b], above[a], above[b]], wall, .47);
          outlines.push(...above[a], ...above[b]);
        }
      });
    }
  });
  const mesh = triangleMesh(positions, colors, new Uint32Array(faceRows), display.opacity, true);
  mesh.material.side = THREE.FrontSide;
  mesh.renderOrder = 4;
  const edges = new THREE.BufferGeometry();
  edges.setAttribute('position', new THREE.Float32BufferAttribute(outlines, 3));
  const border = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({
    color: display.edge, opacity: .69, transparent: true, depthWrite: false, toneMapped: false,
  }));
  border.renderOrder = 5;
  return [mesh, border];
}

function widenRibbons(positions, amount) {
  const wider = Float32Array.from(positions);
  for (let offset = 0; offset < positions.length; offset += 18) {
    for (const axis of [0, 2]) {
      const a = offset + axis, b = a + 3, c = a + 6, d = a + 12;
      const near = (positions[b] - positions[a]) * amount;
      const far = (positions[d] - positions[c]) * amount;
      wider[a] = positions[a] - near;
      wider[b] = wider[a + 9] = positions[b] + near;
      wider[c] = wider[a + 15] = positions[c] - far;
      wider[d] = positions[d] + far;
    }
  }
  return wider;
}

function raisedRibbons(positions, features, lift, order, extraWidth) {
  const colors = new Float32Array(positions.length);
  const edging = new Float32Array(positions.length);
  const faceRows = new Uint32Array(positions.length / 9);
  let start = 0;
  features.forEach(({ end, color, index, outline = '#ffffff' }) => {
    const fill = new THREE.Color(color).toArray();
    const rim = new THREE.Color(outline).toArray();
    for (let i = start * 9; i < end * 9; i += 3) {
      colors.set(fill, i);
      edging.set(rim, i);
    }
    faceRows.fill(index, start, end);
    start = end;
  });
  const rim = triangleMesh(widenRibbons(positions, extraWidth + .24), edging, null);
  const fill = triangleMesh(widenRibbons(positions, extraWidth), colors, faceRows);
  for (const [mesh, priority] of [[rim, order], [fill, order + 1]]) {
    Object.assign(mesh.material, { transparent: true, depthWrite: false });
    mesh.position.y = lift;
    mesh.renderOrder = priority;
  }
  return { meshes: [rim, fill], targets: [fill] };
}

function markers(records, paint, width, height) {
  const mesh = new THREE.InstancedMesh(
    new THREE.CylinderGeometry(width * .63, width, height, 8),
    new THREE.MeshBasicMaterial({ toneMapped: false }), records.length,
  );
  const matrix = new THREE.Matrix4();
  records.forEach((record, row) => {
    const [x, y, z] = record[0];
    mesh.setMatrixAt(row, matrix.makeTranslation(x, y + height / 2, z));
    mesh.setColorAt(row, new THREE.Color(paint(record)));
  });
  return mesh;
}

async function terrainMap(ground, source) {
  const map = await new THREE.TextureLoader().loadAsync(asset(source));
  map.colorSpace = THREE.SRGBColorSpace;
  const material = new THREE.MeshBasicMaterial({
    map, side: THREE.DoubleSide, transparent: true, opacity: .82, depthWrite: false, toneMapped: false,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
  });
  return ground.map(original => {
    const mesh = new THREE.Mesh(original.geometry, material);
    mesh.matrix.copy(original.matrixWorld);
    mesh.matrixAutoUpdate = false;
    mesh.renderOrder = 1;
    return mesh;
  });
}

export function createConditionLayers({ app, scene, ground, drawSoon, translate: say, number, focusRenewal }) {
  const root = app.querySelector('[data-overlay-legend]');
  const detail = app.querySelector('[data-overlay-detail]');
  const group = new THREE.Group();
  scene.add(group);
  const active = new Map();
  const layerOpacity = new Map();
  const buttons = new Map();
  const cache = new Map();
  const geography = reusable(() => fetchSource('geography.json'));
  const streets = reusable(() => fetchSource('street-bands.json'));
  const perception = reusable(() => fetchSource('perception.json'));
  const traffic = reusable(() => fetchSource('road-traffic.json'));
  const renewal = reusable(() => Promise.all([
    fetchJSON('/field-visit/renewal.json?v=' + renewalVersion),
    fetchJSON(asset('renewal-geometry.json', renewalVersion)),
  ]));
  let inspected;
  let picker;

  async function build(key, mode) {
    const spec = siteOverlays[key];
    if (spec.image) return { meshes: await terrainMap(ground, spec.image), entries: spec.key };
    if (key === 'streets') {
      const source = await streets();
      const index = mode === 'nach' ? 1 : 0;
      const [a, b] = source.thresholds[index];
      const colors = streetColors[index];
      const ranges = [`≤ ${a.toFixed(3)}`, `> ${a.toFixed(3)} – ${b.toFixed(3)}`, `> ${b.toFixed(3)}`];
      const features = source.features.map(([end, , levels], row) => {
        const grade = levels[index];
        return { end, index: row, color: colors[grade], outline: grade === 0 ? streetRims[index] : undefined };
      });
      return {
        ...raisedRibbons(source.positions, features, 2.31, 6, .67),
        entries: ranges.map((range, i) => [[labels.classes[i], range], colors[i], i === 0 ? streetRims[index] : undefined]),
        describe: row => [source.features[row][1] || say(labels.segment), say(spec.options[mode]) + ' · ' + number(source.features[row][3][index], 5)],
      };
    }
    if (key === 'perception') {
      const source = await perception();
      const { positions, features, entries, describe } = perceptionRibbons(source, mode, say, number);
      return { ...raisedRibbons(positions, features, 3.1, 8, mode === 'frontage' ? .67 : .96), entries, describe };
    }
    if (key === 'renewal') {
      const [registry, shapes] = await renewal();
      return buildRenewalLayer(registry, shapes, mode, say);
    }
    if (key === 'traffic') {
      const { positions, features, arrows, arrowInk, entries, symbols, note, describe } =
        trafficRibbons(await traffic(), say, number);
      const band = raisedRibbons(positions, features, 1.55, 10, 0);
      const signs = triangleMesh(arrows, arrowInk, null);
      Object.assign(signs.material, { transparent: true, depthWrite: false });
      signs.position.y = 1.59;
      signs.renderOrder = 12;
      return { ...band, meshes: [...band.meshes, signs], entries, symbols, note, describe };
    }
    const source = await geography();
    if (key === 'flood') {
      const { areas } = source.flood[mode];
      const meshes = prismMeshes(areas, ({ rank }) => [rank === 1 ? .25 : 1.75, bands.flood[rank - 1][1]], volumeStyle.flood);
      Object.assign(meshes[0].material, { polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
      return { meshes, targets: [meshes[0]], entries: bands.flood,
        describe: row => [say(labels.depth) + ' · ' + bands.flood[areas[row].rank - 1][0], say(spec.options[mode])] };
    }
    if (key === 'ndvi' || key === 'heat') {
      const { cells } = source.vegetation;
      const heights = key === 'ndvi' ? ndviColumnHeights : [5, 10, 15, 20, 25];
      const meshes = prismMeshes(cells, cell => [heights[cell[key] - 1], bands[key][cell[key] - 1][1]], volumeStyle[key]);
      const entries = key === 'ndvi' ? bands.ndvi.map(([label, color], i) => [[label, heights[i] + ' m'], color]) : bands.heat;
      return { meshes, targets: [meshes[0]], entries,
        describe: row => {
          const rank = cells[row][key];
          const cell = say(labels.cell) + ' ' + cells[row].cell + ' · 30 × 30 m';
          const details = key === 'ndvi' ? cell + ' · ' + heights[rank - 1] + ' m ' + say(labels.displayHeight) : cell;
          return [say(spec.label) + ' · ' + rank + '/5', details];
        } };
    }
    if (key === 'facilities') {
      const { facilities } = source;
      const mesh = markers(facilities, ([, category]) => facilityKeys[category][1], 2.8, 6.4);
      return { meshes: [mesh], entries: Object.values(facilityKeys),
        describe: row => [facilities[row][2] || say(spec.label), say(facilityKeys[facilities[row][1]][0])] };
    }
    const { brightness } = source;
    const mesh = markers(brightness, ([, score]) => spec.key[score < 25 ? 0 : score < 50 ? 1 : 2][1], 4.6, 8);
    return { meshes: [mesh], entries: spec.key,
      describe: row => [brightness[row][2], number(brightness[row][1], 1) + '% · ' + brightness[row][3]] };
  }

  function cached(key, mode) {
    const id = key + ':' + mode;
    if (!cache.has(id)) cache.set(id, build(key, mode).then(withOpacity).catch(error => {
      cache.delete(id);
      throw error;
    }));
    return cache.get(id);
  }

  function clear() {
    const wasShown = !detail.hidden;
    const wasRenewal = Boolean(inspected?.layer.items);
    inspected = undefined;
    detail.hidden = true;
    if (wasRenewal) {
      if (picker) picker.value = '';
      writeUrl();
    }
    return wasShown;
  }

  function showDetail() {
    if (!inspected) return;
    const [title, value, links = []] = inspected.layer.describe(inspected.row);
    const heading = document.createElement('strong');
    const description = document.createElement('span');
    heading.textContent = title;
    description.textContent = value;
    detail.replaceChildren(heading, description);
    for (const [url, label] of links) {
      const link = document.createElement('a');
      link.href = url;
      link.textContent = say(label);
      detail.append(link);
    }
    detail.hidden = false;
  }

  function inspectItem(layer, row, focus = false) {
    const changedRenewal = inspected?.layer.items || layer.items;
    inspected = { layer, row };
    showDetail();
    if (focus) focusRenewal(layer.items[row]);
    if (changedRenewal) {
      if (picker) picker.value = layer.items?.[row]?.id || '';
      writeUrl();
    }
  }

  function opacityControl(key, state, lists) {
    const control = document.createElement('div');
    control.className = 'city-opacity';
    const input = document.createElement('input');
    input.type = 'range';
    input.min = '0';
    input.max = '100';
    input.id = 'city-opacity-' + key;
    input.dataset.layerOpacity = key;
    input.value = state.opacity;
    const label = document.createElement('label');
    label.htmlFor = input.id;
    label.textContent = say(labels.opacity);
    const value = document.createElement('output');
    value.setAttribute('for', input.id);
    value.dataset.layerOpacityValue = key;
    value.value = state.opacity + '%';
    input.addEventListener('input', () => {
      state.opacity = input.valueAsNumber;
      layerOpacity.set(key, state.opacity);
      applyOpacity(state.layer, state.opacity);
      value.value = state.opacity + '%';
      for (const list of lists) list.style.setProperty('--swatch-opacity', state.opacity / 100);
      if (state.opacity === 0 && inspected?.layer === state.layer) clear();
      drawSoon();
    });
    input.addEventListener('change', writeUrl);
    control.append(label, value, input);
    return control;
  }

  function showLegend() {
    const sections = [];
    const pickerWasFocused = document.activeElement === picker;
    picker = undefined;
    for (const key of Object.keys(siteOverlays)) {
      const state = active.get(key);
      if (!state) continue;
      const spec = siteOverlays[key];
      const section = document.createElement('section');
      section.dataset.overlayKey = key;
      section.dataset.status = state.layer ? 'ready' : state.error ? 'error' : 'loading';
      const heading = document.createElement('h3');
      heading.textContent = say(spec.label);
      section.append(heading);
      if (spec.options) {
        const select = document.createElement('select');
        select.dataset.overlayMode = key;
        select.setAttribute('aria-label', say(spec.label));
        for (const value of [spec.default, ...Object.keys(spec.options).filter(key => key !== spec.default)]) {
          select.add(new Option(say(spec.options[value]), value));
        }
        select.value = state.mode;
        select.addEventListener('change', () => activate(key, select.value));
        section.append(select);
      }
      if (state.layer) {
        if (state.layer.items) {
          const select = document.createElement('select');
          select.dataset.overlayItem = key;
          select.setAttribute('aria-label', say(labels.chooseLocation));
          select.add(new Option(say(labels.chooseLocation), ''));
          state.layer.items.forEach((item, row) => select.add(new Option(state.layer.itemTitle(row), item.id)));
          select.value = inspected?.layer === state.layer ? state.layer.items[inspected.row].id : '';
          select.addEventListener('change', () => {
            const row = state.layer.items.findIndex(item => item.id === select.value);
            if (row < 0) clear();
            else inspectItem(state.layer, row, true);
          });
          picker = select;
          section.append(select);
        }
        const list = document.createElement('ul');
        list.className = 'city-legend';
        const entries = state.layer.entries.map(([name, color, outline]) => [
          Array.isArray(name) && Array.isArray(name[0]) ? say(name[0]) + ' · ' + name[1] : say(name), color, outline,
        ]);
        setLegend(list, entries, state.opacity / 100);
        const legends = [list];
        if (state.layer.symbols) {
          const symbols = document.createElement('ul');
          symbols.className = 'city-legend city-legend-directions';
          setLegend(symbols, state.layer.symbols.map(([label, ...style]) => [say(label), ...style]), state.opacity / 100);
          legends.push(symbols);
        }
        section.append(opacityControl(key, state, legends));
        const reading = Array.isArray(spec.reading) ? spec.reading : spec.reading?.[state.mode];
        if (reading) {
          const guide = document.createElement('p');
          guide.className = 'city-overlay-reading';
          guide.textContent = say(reading);
          section.append(guide);
        }
        section.append(...legends);
      }
      const note = document.createElement('p');
      const noteText = state.error ? labels.failed : !state.layer ? labels.loading :
        key === 'flood' && state.mode === '2018' ? labels.basins : state.layer.note?.() ?? spec.note;
      if (noteText) {
        note.textContent = say(noteText);
        section.append(note);
      }
      if (state.layer && spec.source) {
        const link = document.createElement('a');
        link.href = sourceForOverlay(key, state.mode);
        link.target = '_blank';
        link.rel = 'noopener';
        link.textContent = say(spec.sourceLabel || labels.source);
        section.append(link);
      }
      sections.push(section);
    }
    const focused = document.activeElement;
    const focusedMode = focused?.dataset.overlayMode;
    const focusedRange = focused?.dataset.layerOpacity;
    const scroll = root.scrollTop;
    root.replaceChildren(...sections);
    root.hidden = sections.length === 0;
    root.scrollTop = scroll;
    if (pickerWasFocused) picker?.focus({ preventScroll: true });
    if (focusedMode) root.querySelector('[data-overlay-mode="' + focusedMode + '"]')?.focus({ preventScroll: true });
    if (focusedRange) root.querySelector('[data-layer-opacity="' + focusedRange + '"]')?.focus({ preventScroll: true });
  }

  function writeUrl() {
    const url = new URL(location.href);
    const item = inspected?.layer.items?.[inspected.row];
    if (item) url.searchParams.set('renewalSite', item.id);
    else url.searchParams.delete('renewalSite');
    if (active.size) url.searchParams.set('overlays', [...active.keys()].join(','));
    else url.searchParams.delete('overlays');
    const overrides = [...layerOpacity].filter(([key]) => active.has(key));
    if (overrides.length) url.searchParams.set('opacity', overrides.map(([key, value]) => key + ':' + value).join(','));
    else url.searchParams.delete('opacity');
    for (const [key, spec] of Object.entries(siteOverlays)) {
      if (!spec.options) continue;
      const mode = active.get(key)?.mode;
      if (mode && mode !== spec.default) url.searchParams.set(key, mode);
      else url.searchParams.delete(key);
    }
    history.replaceState(null, '', url);
  }

  function remove(key) {
    const state = active.get(key);
    if (!state) return;
    if (state.layer) group.remove(...state.layer.meshes);
    active.delete(key);
    buttons.get(key).setAttribute('aria-checked', 'false');
    if (inspected?.layer === state.layer) clear();
    drawSoon();
  }

  async function activate(key, mode = siteOverlays[key].default, update = true, item) {
    const spec = siteOverlays[key];
    if (!spec.options || !Object.hasOwn(spec.options, mode)) mode = spec.default;
    if (key === 'ndvi') remove('heat');
    if (key === 'heat') remove('ndvi');
    if (spec.image) {
      for (const other of active.keys()) {
        if (other !== key && siteOverlays[other].image) remove(other);
      }
    }
    remove(key);
    const state = { mode };
    active.set(key, state);
    buttons.get(key).setAttribute('aria-checked', 'true');
    if (update) writeUrl();
    showLegend();
    try {
      const result = await cached(key, mode);
      if (active.get(key) !== state) return;
      state.layer = result;
      state.opacity = layerOpacity.get(key) ?? result.defaultOpacity;
      applyOpacity(result, state.opacity);
      group.add(...result.meshes);
      group.updateMatrixWorld(true);
      const row = result.items?.findIndex(entry => entry.id === item) ?? -1;
      if (row >= 0) inspectItem(result, row, true);
      drawSoon();
    } catch (error) {
      if (active.get(key) !== state) return;
      console.warn('Kajicho map layer:', key, error);
      state.error = true;
    }
    showLegend();
  }

  for (const [key, spec] of Object.entries(siteOverlays)) {
    const button = conditionSwitch(spec.label, say);
    button.dataset.overlay = key;
    buttons.set(key, button);
    app.querySelector(core.has(key) ? '[data-overlays]' : '[data-more-overlays]').append(button);
    button.addEventListener('click', () => {
      if (active.has(key)) {
        remove(key);
        writeUrl();
        showLegend();
      } else activate(key);
    });
  }
  const query = new URLSearchParams(location.search);
  for (const token of query.get('opacity')?.split(',') || []) {
    const match = token.match(/^([a-z]+):(\d{1,3})$/);
    if (match && Object.hasOwn(siteOverlays, match[1])) {
      layerOpacity.set(match[1], Math.min(100, Number(match[2])));
    }
  }
  for (const key of new Set(query.get('overlays')?.split(',') || [])) {
    if (!Object.hasOwn(siteOverlays, key)) continue;
    if (!core.has(key)) app.querySelector('[data-more-panel]').open = true;
    activate(key, query.get(key), false, key === 'renewal' ? query.get('renewalSite') : undefined);
  }

  return {
    translate() {
      for (const [key, button] of buttons) button.firstChild.textContent = say(siteOverlays[key].label);
      showLegend();
      showDetail();
    },
    inspect(ray, buildingDistance) {
      const readable = [...active.values()].filter(state => state.opacity > 0 && state.layer?.describe).map(state => state.layer);
      const hits = ray.intersectObjects(readable.flatMap(layer => layer.targets || layer.meshes), false);
      const hit = hits.find(result => result.object.userData.overlayPin) ?? hits[0];
      if (!hit || (!hit.object.userData.overlayPin && hit.distance >= buildingDistance)) {
        clear();
        return false;
      }
      const layer = readable.find(layer => layer.meshes.includes(hit.object));
      const { renewalRow, faceRows } = hit.object.userData;
      const row = renewalRow ?? hit.instanceId ?? faceRows?.[hit.faceIndex];
      inspectItem(layer, row);
      return true;
    },
    clear,
  };
}
