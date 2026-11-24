import * as THREE from 'three';
import { appendRibbon } from './traffic-layer.js?v=20261124-renewal-map';

const stages = {
  cleared: [['Cleared or demolished', '更地・解体', '清场或拆除'], '#a04470'],
  operating: [['Local activity', '地域活動', '地方活动'], '#127358'],
  study: [['Under study', '検討中', '研究中'], '#3556a3'],
  planned: [['Published plan', '公表計画', '已公示计划'], '#a95b0e'],
  complete: [['Completed', '竣工', '已竣工'], '#455564'],
};

const caseColors = { streets: '#a34c35', roofs: '#7c47a0', blocks: '#275e9a', school: '#13786a' };
const basisLabels = {
  former: ['Former building outlines', '旧建物の輪郭', '原建筑轮廓'],
  block: ['Block reference point', '街区の参照点', '街区参考点'],
  district: ['Station-side area reference', '駅周辺の地区参照点', '车站一侧的地区参考点'],
  address: ['Mapped project point', '事業の位置', '项目位置点'],
  field: ['Fieldwork location', '現地調査の地点', '实地调研点'],
  corridor: ['Named street sections', '対象街路区間', '指定街道路段'],
  candidate: ['Candidate block outline', '候補街区の輪郭', '候选街区轮廓'],
  retained: ['Retained school footprint', '既存校舎の輪郭', '保留校舍轮廓'],
};

const openRecord = ['Project record', '事業記録', '开发项目记录'];
const openDiagram = ['Proposal diagram', '提案の関係図', '方案关系图'];
const openVision = ['Future Vision', '将来構想', '未来愿景'];

export const renewalOverlay = {
  label: ['Renewal and proposals', '更新と提案', '更新与方案'],
  default: 'projects',
  options: {
    projects: ['Development projects', '開発事業', '开发项目'],
    proposals: ['Studio proposal sites', 'スタジオの提案地点', '工作室方案地点'],
  },
  reading: {
    projects: ['Color shows project stage. Hollow rings mark block or area references.',
      '色は事業段階、白抜きの丸は街区・地区の参照点。', '颜色表示项目阶段，空心圈表示街区或地区参考位置。'],
    proposals: ['A–D mark the studio’s proposal sites. Select a site for its diagram.',
      'A〜Dはスタジオの提案地点。選ぶと関係図を開けます。', 'A–D 对应四个方案地点，选中可打开关系图。'],
  },
  source: '/field-visit#relationship-explorer',
  sourceLabel: ['Renewal overview', '更新の全体図', '更新关系总图'],
};

function makeSurface(positions, color, opacity, order) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  const material = new THREE.MeshBasicMaterial({
    color, side: THREE.DoubleSide, opacity, transparent: true, depthWrite: false,
    toneMapped: false, forceSinglePass: true,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.renderOrder = order;
  return mesh;
}

function makeAreas(polygons, color) {
  const body = [], borders = [];
  for (const rings of polygons) {
    const vectors = rings.map(ring => ring.map(([x, , z]) => new THREE.Vector2(x, z)));
    const faces = THREE.ShapeUtils.triangulateShape(vectors[0], vectors.slice(1));
    const vertices = rings.flat();
    for (const face of faces) {
      for (const index of face) {
        const [x, y, z] = vertices[index];
        body.push(x, y + .92, z);
      }
    }
    for (const ring of rings) appendRibbon(borders, [...ring, ring[0]], 1.3);
  }
  const fill = makeSurface(body, color, .26, 13);
  const border = makeSurface(borders, color, .89, 14);
  border.position.y = .97;
  return [fill, border];
}

function makeMarker(geometry, paint, glyph, hollow, row) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 64;
  const pen = canvas.getContext('2d');
  pen.beginPath();
  pen.arc(32, 32, 25, 0, Math.PI * 2);
  pen.fillStyle = hollow ? '#fbf9f6' : paint;
  pen.fill();
  pen.lineWidth = 5;
  pen.strokeStyle = hollow ? paint : '#fbf9f6';
  pen.stroke();
  if (glyph) {
    pen.font = '600 35px system-ui, sans-serif';
    pen.fillStyle = '#fff';
    pen.textAlign = 'center';
    pen.textBaseline = 'middle';
    pen.fillText(glyph, 32, 33);
  }
  const map = new THREE.CanvasTexture(canvas);
  map.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map, sizeAttenuation: false, transparent: true, depthTest: false, depthWrite: false, toneMapped: false,
  }));
  sprite.position.set(...geometry.center);
  sprite.position.y += 4;
  sprite.scale.setScalar(glyph ? .043 : .032);
  sprite.renderOrder = 24;
  Object.assign(sprite.userData, { renewalRow: row, overlayPin: true });
  return sprite;
}

export function buildRenewalLayer(registry, geometry, mode, say) {
  const proposals = mode === 'proposals';
  const data = proposals ? registry.cases : registry.projects;
  const spatial = new Map(geometry[mode].map(item => [item.id, item]));
  const markers = [], surfaces = [], items = [];
  for (const [row, item] of data.entries()) {
    const shape = spatial.get(item.id);
    if (!shape) throw new Error('Missing renewal location ' + item.id);
    const color = proposals ? caseColors[item.id] : stages[item.status][1];
    const glyph = proposals ? item.letter : '';
    const marker = makeMarker(shape, color, glyph, ['block', 'district'].includes(shape.basis), row);
    markers.push(marker);
    const parts = shape.polygons.length ? makeAreas(shape.polygons, color) : [];
    if (shape.paths.length) {
      const positions = [];
      for (const path of shape.paths) appendRibbon(positions, path, 4.2);
      const path = makeSurface(positions, color, .94, 15);
      path.position.y = 2.65;
      parts.push(path);
    }
    for (const part of parts) part.userData.renewalRow = row;
    surfaces.push(...parts);
    items.push({
      id: item.id,
      center: shape.center, extent: shape.extent,
    });
  }
  const prefix = '/field-visit#';
  const entries = proposals ? data.map(item => [
    item.name.map(value => item.letter + ' · ' + value), caseColors[item.id],
  ]) : Object.values(stages);
  return {
    meshes: [...markers, ...surfaces], targets: [...markers, ...surfaces], items, entries,
    itemTitle: row => (proposals ? data[row].letter + ' · ' : '') + say(data[row].name),
    describe(row) {
      const item = data[row];
      const basis = say(basisLabels[spatial.get(item.id).basis]);
      return proposals
        ? [this.itemTitle(row), basis, [[prefix + 'renewal-' + item.id, openDiagram], ['/vision#case-' + item.id, openVision]]]
        : [say(item.name), [say(stages[item.status][0]), say(item.actor), basis].join(' · '),
          [[prefix + 'development-' + item.id, openRecord]]];
    },
  };
}
