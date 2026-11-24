import { Color } from 'three';

const names = {
  segment: ['Unnamed road', '名称未登録の道路', '未命名道路'],
  missing: ['Lane count unavailable', '車線数未登録', '车道数未记录'],
  one: ['1 lane', '1車線', '1 车道'],
  many: ['{n} lanes', '{n}車線', '{n} 车道'],
  more: ['5+ lanes', '5車線以上', '5 条及以上'],
  split: ['{a} + {b} lanes by direction', '方向別に{a}車線・{b}車線', '两向分别为 {a}、{b} 车道'],
  forward: ['one-way', '一方通行', '单行'],
  both: ['two-way', '双方向', '双向'],
  variable: ['direction varies', '方向が変わる区間', '方向随时段变化'],
  unknown: ['direction unrecorded', '進行方向未登録', '方向未记录'],
  default: ['OSM default', 'OSMの既定値', 'OSM 默认'],
  expressway: ['Elevated expressway', '高架の首都高速', '高架高速'],
  bridge: ['Bridge', '橋梁', '桥梁'],
  coverage: ['{n} of {total} mapped road segments have a lane count.',
    '表示した{total}区間のうち{n}区間に車線数の記録があります。', '显示的 {total} 个路段中，有 {n} 个记录了车道数。'],
  access: {
    private: ['Private access', '私有道路', '限私人通行'],
    destination: ['Local access only', '目的地への通行のみ', '仅目的地通行'],
    customers: ['Customers only', '利用者のみ', '仅限顾客'],
    delivery: ['Deliveries only', '配送のみ', '仅限配送'],
    permit: ['Permit required', '許可車両のみ', '需通行许可'],
  },
};

export const trafficOverlay = {
  label: ['Lanes and direction', '車線数・進行方向', '车道数与行车方向'],
  reading: ['Color shows lanes on each mapped roadway. Arrows show direction. Select a road for details.',
    '色は道路ごとの車線数、矢印は進行方向を示します。道路を選ぶと詳細が表示されます。',
    '颜色表示每幅车行道的车道数，箭头表示行车方向。点选路段可看详情。'],
  source: 'https://www.openstreetmap.org/copyright',
  sourceLabel: '© OpenStreetMap contributors',
};

const laneColors = ['#aab0b6', '#21928e', '#355dba', '#e6ac35', '#a84259', '#513278'];
const arrowColors = ['#273447', '#ffffff', '#ffffff', '#273447', '#ffffff', '#ffffff'];
const glyphs = [
  [names.forward, '→'], [names.both, '↔'], [names.variable, '◆'], [names.unknown, '–'],
];

function unit(dx, dz) {
  const size = Math.hypot(dx, dz) || 1;
  return [dx / size, dz / size];
}

export function appendRibbon(positions, path, width) {
  const edges = path.map(([x, y, z], i) => {
    const a = path[Math.max(i - 1, 0)];
    const b = path[Math.min(i + 1, path.length - 1)];
    const [dx, dz] = unit(b[0] - a[0], b[2] - a[2]);
    return [[x + dz * width / 2, y, z - dx * width / 2], [x - dz * width / 2, y, z + dx * width / 2]];
  });
  for (let i = 1; i < edges.length; i++) {
    const [a, b] = edges[i - 1], [c, d] = edges[i];
    positions.push(...a, ...b, ...c, ...b, ...d, ...c);
  }
}

function appendArrows(positions, colors, path, width, direction, ink) {
  if (direction === 'unknown') return;
  const samples = [];
  let distance = 0;
  for (let i = 1; i < path.length; i++) {
    const a = path[i - 1], b = path[i];
    const length = Math.hypot(b[0] - a[0], b[2] - a[2]);
    if (length > .01) {
      samples.push({ a, b, start: distance, length });
      distance += length;
    }
  }
  if (distance < 5) return;
  const count = Math.max(1, Math.round(distance / 43));
  const paint = new Color(ink).toArray();
  const halfWidth = width * .48;
  const halfLength = Math.min(5.5, distance * .23);
  for (let i = 0; i < count; i++) {
    const mark = distance * (i + .5) / count;
    const { a, b, start, length } = samples.find(p => mark <= p.start + p.length);
    const dx = (b[0] - a[0]) / length, dz = (b[2] - a[2]) / length;
    const rise = (b[1] - a[1]) / length;
    const center = mark - start;
    const point = (along, side) => {
      const s = center + halfLength * along;
      return [a[0] + dx*s + dz*halfWidth*side, a[1] + rise*s, a[2] + dz*s - dx*halfWidth*side];
    };
    const tri = (...vertices) => {
      for (const p of vertices) {
        positions.push(...point(...p));
        colors.push(...paint);
      }
    };
    if (direction === 'variable') {
      tri([-0.45, 0], [0, 1], [.45, 0]);
      tri([-0.45, 0], [.45, 0], [0, -1]);
    } else {
      const back = direction === 'both' ? -.35 : -.95;
      tri([back, -.25], [.32, -.25], [.32, .25]);
      tri([back, -.25], [.32, .25], [back, .25]);
      tri([1, 0], [.27, -.88], [.27, .88]);
      if (direction === 'both') tri([-1, 0], [-.27, .88], [-.27, -.88]);
    }
  }
}

export function trafficRibbons(source, say, number) {
  const positions = [], features = [], arrows = [], arrowInk = [];
  const activeGlyphs = new Set();
  source.roads.forEach(({ lanes, paths, direction }, index) => {
    const category = Math.min(5, lanes ?? 0);
    const width = lanes ? Math.min(5.2, 2.3 + lanes * .48) : 2;
    for (const path of paths) {
      appendRibbon(positions, path, width);
      appendArrows(arrows, arrowInk, path, width, direction, arrowColors[category]);
    }
    features.push({ end: positions.length / 9, index, color: laneColors[category], outline: '#263948' });
    activeGlyphs.add(direction);
  });
  const laneLabel = n => n == null ? say(names.missing) : n === 1 ? say(names.one) :
    say(names.many).replace('{n}', number(n, 0));
  const labels = [1, 2, 3, 4, 5, 0].map(i => [
    i === 0 ? names.missing : i === 1 ? names.one :
      i === 5 ? names.more : names.many.map(label => label.replace('{n}', i)), laneColors[i],
  ]);
  const directions = ['oneway', 'both', 'variable', 'unknown'];
  return {
    positions, features, arrows, arrowInk, entries: labels,
    symbols: glyphs.filter((_, i) => activeGlyphs.has(directions[i])).map(([label, glyph]) => [label, '#f5f1ec', '#747b83', glyph]),
    note: () => say(names.coverage).replace('{n}', number(source.coverage.laneCount, 0))
      .replace('{total}', number(source.coverage.roads, 0)) + ' · ' + source.source.date.slice(0, 10),
    describe(row) {
      const road = source.roads[row];
      const direction = say(road.direction === 'oneway' ? names.forward : names[road.direction]);
      const basis = road.basis === 'default' ? ' (' + say(names.default) + ')' : '';
      const details = [laneLabel(road.lanes), direction + basis];
      if (road.byDirection) {
        const [a, b] = road.byDirection.map(n => number(n, 0));
        details.push(say(names.split).replace('{a}', a).replace('{b}', b));
      }
      if (names[road.level]) details.push(say(names[road.level]));
      if (road.access) details.push(say(names.access[road.access]));
      if (road.condition) details.push(road.condition);
      return [say(road.name) || say(names.segment), details.join(' · ')];
    },
  };
}
