import * as THREE from 'three';

const flagLabels = {
  G1: ['G1 · Strong through routes, poor walking', 'G1 · 通過経路に歩行課題', 'G1 · 穿行潜力高，步行条件差'],
  G2: ['G2 · Reachable, closed frontage', 'G2 · 到達しやすいが閉じた沿道', 'G2 · 易到达，首层界面封闭'],
  G3: ['G3 · Few places to stay near activity', 'G3 · 人の活動に対し滞在場所が少ない', 'G3 · 活动集中，停留条件少'],
  G4: ['G4 · Heat exposure', 'G4 · 暑熱リスク', 'G4 · 热暴露风险'],
  P1: ['P1 · Fine-grain streets', 'P1 · 細かな街路の肌理', 'P1 · 细肌理街道'],
  P2: ['P2 · Sites for change', 'P2 · 更新の余地がある敷地', 'P2 · 可更新场地'],
};

export const perceptionOverlay = {
  label: ['Street perception', '街路の見え方', '街道感知 Perception'],
  options: {
    structure: ['Gaps & opportunities', '課題と可能性', '街道结构 · 差距与潜力'],
    walk: ['Walking conditions', '歩きやすさ', '步行条件'],
    frontage: ['Ground-floor activity', '1階の活動', '左右两侧首层活动'],
    stay: ['Places to stay', '滞在の条件', '停留条件'],
    ...flagLabels,
  },
  default: 'structure',
  reading: {
    structure: ['A street can qualify for both a gap and an opportunity. Choose a G or P view to see one finding at a time.',
      '一つの区間に課題と可能性が重なることがあります。G・Pを選ぶと項目別に確認できます。', '同一路段可兼有差距和潜力。选择 G 或 P 可查看单项结果。'],
    walk: ['Higher scores mean the street looked easier to walk along, with fewer obstacles.',
      '点数が高いほど、街路画像では障害が少なく歩きやすい区間です。', '分数越高，表示街景中沿街步行越顺畅、障碍越少。'],
    frontage: ['Higher scores mean more of the ground-floor frontage appears active. Each side is scored separately.',
      '点数が高いほど活動の見える一階沿道が多く、左右は別々に集計します。', '分数越高，沿街首层可见的活动界面越多。道路左右两侧分别评分。'],
    stay: ['One point each for seating, shade, greenery, edges such as steps or setbacks, and open shopfronts. Each street segment shows the highest count at its sampled points. A purple outline marks a barrier.',
      '座席、日陰、緑、段差や後退部などの縁、開放的な店舗を各1点。区間内の調査地点で最も高い点数を表示します。紫の縁取りは障害を示します。',
      '座椅、遮阴、绿化、台阶或退让等街边停留空间、开敞店面各计 1 分。路段取各街景采样点的最高计数。紫色描边表示有障碍。'],
  },
  note: ['Interim audit · 400 of 435 in-scope segments have street imagery, mainly from 2022.',
    '中間調査。対象435区間のうち400区間に街路画像あり。主に2022年撮影。', '中期分析 · 研究范围内 435 条路段，400 条有街景，主要拍摄于 2022 年。'],
  source: '/studio#streets',
};

const labels = {
  gap: ['Gap', '課題', '差距'],
  potential: ['Opportunity', '可能性', '潜力'],
  both: ['Gap and opportunity', '課題と可能性', '同时有差距与潜力'],
  other: ['Other segments', 'その他の区間', '其他路段'],
  unmapped: ['No imagery or edge segment', '画像なし・周縁区間', '无街景或边界路段'],
  edge: ['Edge segment', '周縁区間', '边界路段'],
  noImages: ['No street imagery', '街路画像なし', '无街景'],
  segment: ['Street segment', '街路区間', '路段'],
  samples: ['Panoramas', 'パノラマ', '街景采样点'],
  walking: ['Walking score', '歩行スコア', '步行分数'],
  frontage: ['Left / right', '左 / 右', '左侧 / 右侧'],
  stay: ['Stay features', '滞在の要素', '停留要素'],
  barrier: ['Stay barrier', '滞在の障害', '停留障碍'],
};

export const perceptionColors = {
  gap: '#e07115', potential: '#007286', both: '#301444', other: '#abb7c4', unmapped: '#f2f6fa',
  walk: ['#efad34', '#276fbf', '#074437'],
  frontage: ['#ffe182', '#f78929', '#9250c5', '#122449'],
  stay: ['#ffe07e', '#f18c25', '#da5621', '#3658ad', '#073d34', '#0a172b'],
  paleEdge: '#674c2d',
  barrier: '#49204f',
};

const gray = perceptionColors.unmapped;
const range = (value, colors) => {
  const lower = Math.floor(value);
  return lower === value ? colors[lower] :
    '#' + new THREE.Color(colors[lower]).lerp(new THREE.Color(colors[lower + 1]), value - lower).getHexString();
};

function pattern(row) {
  if (row.edge) return 'unmapped';
  const gap = row.flags.some(flag => flag[0] === 'G');
  const potential = row.flags.some(flag => flag[0] === 'P');
  if (gap) return potential ? 'both' : 'gap';
  if (potential) return 'potential';
  return row.samples ? 'other' : 'unmapped';
}

function legend(mode) {
  const list = keys => keys.map(key => [labels[key], perceptionColors[key]]);
  if (mode === 'structure') return list(['gap', 'potential', 'both', 'other', 'unmapped']);
  if (mode === 'walk') {
    const levels = [
      ['<3 · More obstacles', '<3 · 障害が多い', '<3 · 障碍较多'],
      ['3 · Moderate', '3 · 中程度', '3 · 中等'],
      ['>3 · Easier to walk', '>3 · 歩きやすい', '>3 · 较易步行'],
    ];
    return levels.map((label, i) => [label, perceptionColors.walk[i], i === 0 ? perceptionColors.paleEdge : undefined])
      .concat(list(['unmapped']));
  }
  if (mode === 'frontage') {
    const levels = [
      ['0 · No visible activity', '0 · 活動が見えない', '0 · 无可见活动'],
      ['1 · A little', '1 · わずか', '1 · 少量'],
      ['2 · About half', '2 · 約半分', '2 · 约一半'],
      ['3 · Most', '3 · 大部分', '3 · 大部分'],
    ];
    return levels.map((label, i) => [label, perceptionColors.frontage[i], i < 2 ? perceptionColors.paleEdge : undefined])
      .concat(list(['unmapped']));
  }
  if (mode === 'stay') {
    const levels = [
      ['0 · None observed', '0 · 要素なし', '0 · 未观察到要素'],
      ['1 · One feature', '1 · 1項目', '1 · 观察到一项'],
      ['2 · Two features', '2 · 2項目', '2 · 观察到两项'],
      ['3 · Three features', '3 · 3項目', '3 · 观察到三项'],
      ['4 · Four features', '4 · 4項目', '4 · 观察到四项'],
      ['5 · All five observed', '5 · 5項目すべて', '5 · 五项都观察到'],
    ];
    return [
      ...levels.map((label, i) => [label, perceptionColors.stay[i], i < 2 ? perceptionColors.paleEdge : undefined]),
      [labels.barrier, 'transparent', perceptionColors.barrier],
      ...list(['unmapped']),
    ];
  }
  return [[flagLabels[mode], perceptionColors[mode[0] === 'G' ? 'gap' : 'potential']], ...list(['other', 'unmapped'])];
}

function streetColor(mode, row) {
  if (mode === 'structure') return perceptionColors[pattern(row)];
  if (row.edge) return gray;
  if (mode === 'walk') {
    if (!Number.isFinite(row.walk)) return gray;
    return perceptionColors.walk[row.walk < 3 ? 0 : row.walk === 3 ? 1 : 2];
  }
  if (mode === 'stay') return Number.isFinite(row.stay) ? perceptionColors.stay[row.stay] : gray;
  if (row.flags.includes(mode)) return perceptionColors[mode[0] === 'G' ? 'gap' : 'potential'];
  return row.samples ? perceptionColors.other : gray;
}

function addRibbon(path, output) {
  const sides = path.map(([x, y, z], i) => {
    const previous = path[Math.max(0, i - 1)], next = path[Math.min(path.length - 1, i + 1)];
    const dx = next[0] - previous[0], dz = next[2] - previous[2];
    const distance = Math.hypot(dx, dz) || 1;
    const ox = -.57 * dz / distance, oz = .57 * dx / distance;
    return [[x - ox, y, z - oz], [x + ox, y, z + oz]];
  });
  for (let i = 0; i < sides.length - 1; i++) {
    const [a, b] = sides[i], [c, d] = sides[i + 1];
    output.push(...a, ...b, ...c, ...b, ...d, ...c);
  }
}

export function perceptionRibbons(source, mode, say, number) {
  const positions = [], features = [];
  function add(paths, color, index, outline) {
    for (const path of paths) addRibbon(path, positions);
    features.push({ end: positions.length / 9, color, index, outline });
  }

  source.segments.forEach((row, i) => {
    if (mode === 'frontage') {
      const sides = Object.values(row.frontage);
      if (!sides.length) add(row.paths, gray, i);
      for (const side of sides) {
        const edge = side.score <= 1 ? perceptionColors.paleEdge : undefined;
        add(side.paths, range(side.score, perceptionColors.frontage), i, edge);
      }
    } else {
      let outline;
      if (mode === 'stay' && !row.edge) {
        if (row.barrier) outline = perceptionColors.barrier;
        else if (Number.isFinite(row.stay) && row.stay <= 1) outline = perceptionColors.paleEdge;
      }
      if (mode === 'walk' && !row.edge && Number.isFinite(row.walk) && row.walk < 3) outline = perceptionColors.paleEdge;
      add(row.paths, streetColor(mode, row), i, outline);
    }
  });

  function describe(index) {
    const row = source.segments[index];
    const name = row.name || say(labels.segment);
    if (row.edge) return [name, say(labels.edge)];
    const sample = say(labels.samples) + ' ' + number(row.samples, 0);
    if (mode === 'frontage' && Object.keys(row.frontage).length) {
      const value = side => row.frontage[side] ? number(row.frontage[side].score) : '—';
      return [name, say(labels.frontage) + ' ' + value('L') + ' / ' + value('R') + ' · ' + sample];
    }
    if (mode === 'walk' && Number.isFinite(row.walk)) return [name, say(labels.walking) + ' ' + number(row.walk) + ' / 5 · ' + sample];
    if (mode === 'stay' && Number.isFinite(row.stay)) {
      const barrier = row.barrier ? ' · ' + say(labels.barrier) : '';
      return [name, say(labels.stay) + ' ' + number(row.stay, 0) + ' / 5' + barrier + ' · ' + sample];
    }
    if (row.flags.length) return [name, row.flags.map(flag => say(flagLabels[flag])).join(' · ') + ' · ' + sample];
    return [name, row.samples ? sample : say(labels.noImages)];
  }

  return { positions, features, entries: legend(mode), describe };
}
