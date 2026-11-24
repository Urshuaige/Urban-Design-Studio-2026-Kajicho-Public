import { trafficOverlay } from './traffic-layer.js?v=20261124-renewal-map';
import { renewalOverlay } from './renewal-layer.js?v=20261124-renewal-map';
import { perceptionOverlay } from './perception-layer.js?v=20261122-legend-and-base';

export const unknownColor = '#cfd1d4';
const access = ['Local access · NAIN400', '局所アクセス · NAIN400', '局部可达性 · NAIN400'];
const through = ['Through routes · NACH800', '通過経路 · NACH800', '穿行潜力 · NACH800'];

export const buildingLayers = {
  workers: {
    label: ['Workers', '従業者', '就业人数'],
    source: ['2021 workplace census · GIS building allocation', '2021年経済センサス · 建物への配分', '2021 经济普查 · GIS 逐栋分配'],
    breaks: [20, 50, 100, 250], colors: ['#e5e0d6', '#d3c2a4', '#bba071', '#997344', '#6f4b2e'],
    units: ['workers', '人', '人'],
  },
  residents: {
    label: ['Residents', '居住者', '居住人数'],
    source: ['Oct 2026 register · GIS building allocation', '2026年10月住民台帳 · 建物への配分', '2026 年 10 月住民登记 · GIS 逐栋分配'],
    breaks: [5, 20, 50, 100], colors: ['#dce7e4', '#b2ccc4', '#80aea0', '#4d8976', '#235f4d'],
    units: ['residents', '人', '人'],
  },
  households: {
    label: ['Households', '世帯', '住户数'],
    source: ['Oct 2026 register · GIS building allocation', '2026年10月住民台帳 · 建物への配分', '2026 年 10 月住民登记 · GIS 逐栋分配'],
    breaks: [2, 5, 15, 40], colors: ['#e2dce8', '#c5bad4', '#aa97c0', '#8a74a1', '#685083'],
    units: ['households', '世帯', '户'],
  },
  height: {
    label: ['Building height', '建物高さ', '建筑高度'],
    source: ['PLATEAU and mapped model heights', 'PLATEAU と現況モデルの高さ', 'PLATEAU 和现状模型高度'],
    breaks: [10, 20, 30, 45], colors: ['#e4e8ed', '#c6d1dc', '#a0b3c7', '#7290ad', '#4b6b8b'],
    units: ['m', 'm', 'm'],
  },
  age: {
    label: ['Building age', '建物の築年数', '建筑年龄'],
    source: ['Age in 2026 · latest building register', '2026年時点 · 最新の建築年台帳', '以 2026 年计 · 最新楼龄登记'],
    breaks: [20, 40, 60], colors: ['#e2d7d2', '#cfae9e', '#ad7f6b', '#844f44'],
    units: ['yr', '年', '年'],
  },
};

export const ndviColumnHeights = [6, 14, 28, 50, 78];
export const bands = {
  flood: [['< 0.5 m', '#64d8ee'], ['0.5–< 3 m', '#144c95']],
  ndvi: [
    [['1 · Lowest', '1 · 最低', '1 · 最低'], '#ffdf63'],
    [['2 · Low', '2 · 低', '2 · 低'], '#ff9b26'],
    [['3 · Medium', '3 · 中', '3 · 中'], '#70841a'],
    [['4 · High', '4 · 高', '4 · 高'], '#086047'],
    [['5 · Highest', '5 · 最高', '5 · 最高'], '#061e31'],
  ],
  heat: [
    [['1 · Coolest', '1 · 最も低温', '1 · 最凉'], '#b9ecf2'],
    ['2', '#4eb0de'], ['3', '#b17b19'], ['4', '#bd421e'],
    [['5 · Hottest', '5 · 最も高温', '5 · 最热'], '#571337'],
  ],
};
export const streetColors = [
  ['#59cce7', '#2463c8', '#101c43'],
  ['#ef92cb', '#a83491', '#310d43'],
];
export const streetRims = ['#123e61', '#5a1b54'];
export const volumeStyle = {
  flood: { opacity: .57, edge: '#164566' },
  ndvi: { opacity: .70, edge: '#2f4e35' },
  heat: { opacity: .67, edge: '#5c383e' },
};

const sources = {
  rain: 'https://www.kensetsu.metro.tokyo.lg.jp/river/chusho_seibi/panhulink/menu/menu02-01',
  basin: 'https://www.kensetsu.metro.tokyo.lg.jp/documents/d/kensetsu/000031272',
  atlas: '/conditions',
};

export const siteOverlays = {
  flood: {
    label: ['Flood depth', '浸水深', '洪水深度'],
    reading: ['Darker blue marks the deeper flood class.', '濃い青は浸水深の大きい区分です。', '深蓝表示更深的浸水档。'],
    note: ['Tokyo maximum-rainfall scenario. Water height uses the midpoint of each mapped depth class.',
      '東京都の想定最大規模。水の高さは浸水区分の中央値。', '东京都最大规模降雨情景。水面高度取原浸水深度分档的中点。'],
    options: {
      '2024': ['Kanda river flood · 2024', '神田川流域 洪水 · 2024', '神田川河流洪水 · 2024'],
      '2018': ['Kanda basin inundation · 2018', '神田川流域 浸水 · 2018', '神田川流域浸水 · 2018'],
    },
    default: '2024', source: sources.rain,
  },
  ndvi: {
    label: ['NDVI greenness', '緑の強さ · NDVI', '植被指数 NDVI'],
    reading: ['Higher classes show a stronger vegetation signal. Column heights use a nonlinear display scale.',
      '数字が大きいほど植生指数が高く、柱の高さは非線形の表示用尺度です。', '档位越高，植被指数越高。柱高用非线性比例放大档位差。'],
    note: ['Regina’s original 30 × 30 m cells. The legend shows display height for each class.',
      '中間発表の30 × 30 mセル。凡例に表示用の高さを示します。', '沿用原生 30 × 30 米像元。图例中的米数是显示柱高。'],
    source: '/studio',
  },
  streets: {
    label: ['Street access', '街路アクセス', '街道可达性'],
    reading: {
      nain: ['Higher scores indicate streets that are easier to reach from nearby streets within 400 m.',
        '数値が高いほど、400 m圏内の周辺街路から到達しやすい区間です。', '分数越高，从 400 米范围内的周边街道越容易到达。'],
      nach: ['Higher scores indicate street segments that occur on more through routes within 800 m.',
        '数値が高いほど、800 m圏内の通過経路に含まれやすい区間です。', '分数越高，路段越可能出现在 800 米范围内的穿行路径上。'],
    },
    note: ['Raised bands show the interim segment scores. Bands follow the road edges where mapped, and the center elsewhere.',
      '高く表示した帯は中間発表の街路区分。道路縁のない箇所では街路中心線を使用。', '悬浮色带沿用中期路段分档。已测道路边界的路段沿两侧显示，其余沿路段中心显示。'],
    options: { nain: access, nach: through }, default: 'nain', source: '/studio',
  },
  perception: perceptionOverlay,
  traffic: trafficOverlay,
  renewal: renewalOverlay,
  heat: {
    label: ['Land surface temperature', '地表面温度', '地表温度'],
    reading: ['Higher classes indicate hotter surfaces in the interim satellite map.',
      '数字が大きいほど衛星画像で地表面温度が高かった区分です。', '档位越高，表示卫星图中的相对地表温度越高。'],
    note: ['Interim temperature classes 1–5 on the original 30 × 30 m cells.', '中間発表の30 × 30 mセル。地表面温度を5段階で表示。', '用原生 30 × 30 米像元展示中期的 1–5 档地表温度。'],
    source: '/studio',
  },
  land: {
    label: ['Observed land use', '土地利用', '现状用地'],
    note: ['Current GIS land-use inventory.', '現況の土地利用GIS。', '沿用 GIS 现状用地图。'],
    image: 'land-use.png', source: sources.atlas,
    key: [
      [['Business & retail', '業務・商業', '办公与商业'], '#e3642a'],
      [['Housing & mixed use', '住宅・併用', '居住与混合'], '#ffbc3d'],
      [['Land for facilities', '施設用地', '设施用地'], '#501367'],
      [['Transport & water', '交通・水域', '交通与水面'], '#3da3da'],
      [['Parking & vacant land', '駐車場・空地', '停车与空地'], '#35495c'],
      [['Green space', '緑地', '绿地'], '#236f4e'],
    ],
  },
  zoning: {
    label: ['Planning zones', '都市計画用途', '规划分区'],
    reading: ['Floor area ratio is total floor area divided by lot area. A higher percentage allows more floor area per unit of land.',
      '容積率は延べ面積の敷地面積に対する割合です。数値が高いほど敷地当たりの上限が大きくなります。', '容积率是总建筑面积与用地面积之比。百分比越高，每平方米用地允许的建筑面积越多。'],
    note: ['Commercial zones colored by floor area ratio (FAR).', '商業地域の容積率。', '商业区按容积率分色。'],
    image: 'zoning.png', source: sources.atlas,
    key: [['≤600%', '#ffd151'], ['>600% to 800%', '#cf5735'], ['>800%', '#51218a']],
  },
  green: {
    label: ['Green and water', '緑と水', '绿地与水系'],
    note: ['Mapped parks, trees and water.', '公園・樹木・水域の地図。', 'GIS 中已登记的公园、树木和水系。'],
    image: 'green-water.png', source: sources.atlas,
    key: [[['Parks', '公園', '公园'], '#7cd53f'], [['Trees', '樹木', '树木'], '#07513d'],
      [['Water', '水域', '水面'], '#247cc8']],
  },
  facilities: {
    label: ['Local facilities', '地域の施設', '周边设施'],
    note: ['Interim inventory within the current Wider Boundary.', '中間発表の施設台帳を現行の周辺区域で表示。', '中期汇报的设施清单，按现行 Wider Boundary 显示。'],
    source: '/studio',
  },
  development: {
    label: ['Development status', '開発状況', '开发进度'],
    note: ['Reviewed sites and recorded project locations.', '確認した敷地と計画位置。', 'GIS 已核查的地块与项目位置。'],
    image: 'development.png', source: sources.atlas,
    key: [[['Completed', '竣工', '已竣工'], '#118a5b'], [['Cleared or demolition', '更地・解体', '拆除或已清场'], '#ed9528'],
      [['Plan or review', '計画・確認', '规划或待核对'], '#7136ad']],
  },
  connections: {
    label: ['Streets and rail', '道路と鉄道', '道路与铁路'],
    note: ['Mapped main roads, rail lines and stations.', '主な道路、鉄道路線と駅。', '基础 GIS 主路、铁路和车站。'],
    image: 'connections.png', source: sources.atlas,
    key: [[['Main roads', '幹線道路', '主路'], '#667689'], [['Rail', '鉄道', '铁路'], '#8b3a2b'],
      [['Stations', '駅', '车站'], '#69c4ef']],
  },
  boundaries: {
    label: ['Study boundaries', '研究区域', '研究边界'],
    note: ['Primary and wider study outlines.', '重点区域と周辺区域の境界。', '重点区与外围研究区边界。'],
    image: 'boundaries.png', source: sources.atlas,
    key: [[['Primary', '重点区域', '重点区'], '#c83635'], [['Wider', '周辺区域', '外围区'], '#128fa1']],
  },
  crossings: {
    label: ['Crossing brightness', '横断部の明るさ', '铁路穿越点明暗'],
    reading: ['A higher percentage means the walkway was brighter relative to the open street in the same image.',
      '数値が高いほど、同じ画像内の開けた道路に対して通路が明るく写っています。', '相对于同一张图里的开敞街道，百分比越高，穿越通道越亮。'],
    note: ['Relative brightness from eight daytime views.', '昼間の8画像から計測した相対的な明るさ。', '8 个日间视角的相对亮度。'],
    source: '/studio',
    key: [['<25%', '#39234d'], ['25–<50%', '#2881b0'], ['≥50%', '#facc4a']],
  },
};

export const facilityKeys = {
  food: [['Food & drink', '飲食', '餐饮'], '#e95717'],
  retail: [['Retail', '小売', '零售'], '#f4c61f'],
  work: [['Work & services', '業務・サービス', '办公与服务'], '#2857c5'],
  health: [['Health', '医療', '医疗'], '#ec75b6'],
  culture: [['Culture & leisure', '文化・余暇', '文化与休闲'], '#652382'],
  civic: [['Civic & learning', '公共・教育', '公共与教育'], '#068177'],
  transit: [['Transit', '交通', '交通'], '#132d45'],
  stay: [['Stays', '宿泊', '住宿'], '#77ca39'],
};

export const sourceForOverlay = (key, mode) =>
  key === 'flood' && mode === '2018' ? sources.basin : siteOverlays[key].source;
