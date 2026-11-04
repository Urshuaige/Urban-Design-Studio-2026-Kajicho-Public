/* Source-linked policy and brief diagrams. Content stays in context.json. */
const words = {
  en: {
    briefTitle: 'From brief to studio work',
    briefNote: 'Seven brief requirements. Team outputs show how the studio will address them.',
    requirement: 'Brief requirement', output: 'Team output',
    source: 'Source says', check: 'Check here', action: 'Design action',
    document: 'DOCUMENT SOURCES', record: 'Full source readings and citations',
    milestones: 'Printed milestones / brief p.6', milestoneNames: ['Kick-off', 'Interim presentation', 'Final presentation'],
    stages: ['Set the frame', 'Build the model', 'Apply it', 'Deliver'],
    groups: {
      climate: ['Climate + energy', 'Connect energy, climate comfort and a workable sequence.'],
      streets: ['Streets + local character', 'Read routes, green space and existing local activity together.'],
      buildings: ['Building + site rules', 'Check the conditions that apply to each candidate site.'],
      delivery: ['Delivery + resilience', 'Connect operators and permissions with continuity during hazards.']
    }
  },
  zh: {
    briefTitle: '从任务书到课程工作',
    briefNote: '七项任务书要求；“团队成果”说明本组怎样落实。',
    requirement: '任务书要求', output: '团队成果',
    source: '来源要点', check: '本区核查', action: '设计行动',
    document: 'DOCUMENT SOURCES / 文献来源', record: '完整资料解读与引用记录',
    milestones: '任务书日期 / 第 6 页', milestoneNames: ['开题汇报', '中期汇报', '最终汇报'],
    stages: ['确定框架', '建立模式', '应用到场地', '交付成果'],
    groups: {
      climate: ['气候与能源', '把用能、街道舒适和实施次序连接起来。'],
      streets: ['街道与地方特征', '一起阅读动线、绿化和已有地方活动。'],
      buildings: ['建筑与地块规则', '逐一核查候选地块适用的条件。'],
      delivery: ['实施与韧性', '连接运营、许可与灾害期间的功能维持。']
    }
  },
  ja: {
    briefTitle: '課題書からスタジオの作業へ',
    briefNote: '課題書の七つの要求と、それに応えるチームの成果を示す。',
    requirement: '課題書の要求', output: 'チームの成果',
    source: '出典の要点', check: '現地で確認', action: '設計の行動',
    document: 'DOCUMENT SOURCES / 文献出典', record: '資料の全文解読と引用記録',
    milestones: '課題書の発表日 / p.6', milestoneNames: ['キックオフ', '中間発表', '最終発表'],
    stages: ['枠組みを決める', 'モデルをつくる', '現地に適用する', '成果をまとめる'],
    groups: {
      climate: ['気候とエネルギー', '省エネ、街路の快適性、実施の順序を結ぶ。'],
      streets: ['街路と地域の特徴', '動線、緑、既存の地域活動を合わせて読む。'],
      buildings: ['建物と敷地のルール', '候補敷地に適用される条件を個別に確認する。'],
      delivery: ['実施とレジリエンス', '運営と許可を、災害時の機能継続へつなぐ。']
    }
  }
};

const groups = [
  ['climate', ['district_climate', 'climate_mechanisms', 'two_supports', 'time_and_stock', 'energy_fabric']],
  ['streets', ['two_precincts', 'station_network', 'small_green', 'street_identity', 'wider_links', 'context-walking', 'context-kajini-trial']],
  ['buildings', ['rules-site-capacity', 'rules-nearby-districts', 'rules-building-environment']],
  ['delivery', ['context-management', 'context-flood', 'context-earthquake']]
];
const briefStages = [
  ['scope'],
  ['issues_visions_actions', 'platform', 'stakeholders'],
  ['application'],
  ['booklet', 'slides']
];
const briefLabels = {
  scope: {
    en: ['Scope + 2050', 'One working area, source record and time horizon.'],
    zh: ['研究范围与 2050', '一个工作范围、来源记录与时间范围。'],
    ja: ['研究範囲と2050年', '一つの作業範囲、出典記録、対象期間。']
  },
  issues_visions_actions: {
    en: ['Issues → vision → actions', 'Trace each action to evidence and a design question.'],
    zh: ['问题 → 愿景 → 行动', '每项行动都能回到证据和设计问题。'],
    ja: ['課題 → 将来像 → 行動', '各行動を根拠と設計課題につなぐ。']
  },
  platform: {
    en: ['Data + platform → decisions', 'State objects, assumptions, comparisons and decisions.'],
    zh: ['数据与平台 → 判断', '说明对象、假设、比较与对应判断。'],
    ja: ['データと基盤 → 判断', '対象、仮定、比較、対応する判断を示す。']
  },
  stakeholders: {
    en: ['People + implementation', 'Name business, government, academic and resident roles.'],
    zh: ['参与者与实施', '说明企业、政府、学术界与居民的角色。'],
    ja: ['担い手と実施', '企業、行政、大学、住民の役割を示す。']
  },
  application: {
    en: ['Apply the model locally', 'Name places, objects, actors and open decisions.'],
    zh: ['把模式应用到本区', '写清地点、对象、主体与待讨论事项。'],
    ja: ['モデルを地域に適用', '場所、対象、主体、協議事項を明記する。']
  },
  booklet: {
    en: ['Booklet', 'Explain the model, maps, comparisons and delivery.'],
    zh: ['Booklet / 说明册', '解释模式、地图、比较与实施。'],
    ja: ['Booklet / 冊子', 'モデル、地図、比較、実施を説明する。']
  },
  slides: {
    en: ['PowerPoint', 'Summarize judgments and drawings from the booklet.'],
    zh: ['PowerPoint / 汇报', '概括与说明册一致的判断与图纸。'],
    ja: ['PowerPoint / 発表', '冊子と整合する判断と図面を要約する。']
  }
};

function node(tag, text, className) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (className) item.className = className;
  return item;
}
function localized(value, lang) {
  if (value && typeof value === 'object') return value[lang] || value.en || '';
  return String(value ?? '');
}
function externalLink(label, value, className) {
  const item = node('a', label, className);
  if (typeof value !== 'string' || !value.trim()) return node('span', label, className);
  try {
    const url = new URL(value, window.location.href);
    if (!['https:', 'http:'].includes(url.protocol)) return node('span', label, className);
    item.href = url.href;
  } catch {
    return node('span', label, className);
  }
  item.target = '_blank';
  item.rel = 'noopener';
  return item;
}

function sourceList(records, lang) {
  const t = words[lang];
  const footer = node('footer', undefined, 'policy-documents');
  footer.append(node('p', t.document, 'policy-document-label'));
  const list = node('ul', undefined, 'policy-source-list');
  const merged = new Map();
  for (const source of records || []) {
    const title = localized(source.document_title || source.title, lang);
    const key = String(source.url || '') + '\n' + title;
    if (!merged.has(key)) merged.set(key, { ...source, title, pages: new Set(), numbers: new Set() });
    const record = merged.get(key);
    if (source.page) record.pages.add(String(source.page));
    for (const page of source.pdf_page || []) if (Number.isInteger(page)) record.numbers.add(page);
  }
  for (const record of merged.values()) {
    const item = node('li', undefined, 'policy-source-item');
    const label = record.title || t.document;
    item.append(externalLink(label + ' ↗', record.url, 'policy-source-title'));
    const pages = record.numbers.size ? 'pp.' + [...record.numbers].sort((a, b) => a - b).join(', ') : [...record.pages].join(' · ');
    const meta = [record.year, pages].filter(Boolean).join(' · ');
    if (meta) item.append(node('span', meta, 'policy-source-meta'));
    list.append(item);
  }
  footer.append(list);
  return footer;
}

function arrow() {
  const item = node('span', '→', 'policy-arrow');
  item.setAttribute('aria-hidden', 'true');
  return item;
}
function briefFlow(study, lang, host) {
  const t = words[lang];
  host.replaceChildren();
  host.classList.add('policy-brief-host');
  const heading = node('header', undefined, 'policy-section-heading');
  heading.append(node('p', 'THE BRIEF / 2026', 'policy-kicker'),
    node('h3', t.briefTitle), node('p', t.briefNote));
  host.append(heading);
  const byId = new Map((study.brief_checklist || []).map(item => [item.id, item]));
  const diagram = node('div', undefined, 'policy-brief-flow');
  const evidence = [];
  briefStages.forEach((ids, index) => {
    const stage = node('section', undefined, 'policy-brief-stage');
    stage.append(node('h4', String(index + 1).padStart(2, '0') + ' / ' + t.stages[index]));
    const stack = node('div', undefined, 'policy-brief-stack');
    for (const id of ids) {
      const requirement = byId.get(id);
      if (!requirement) continue;
      const label = briefLabels[id]?.[lang] || briefLabels[id]?.en;
      const card = node('article', undefined, 'policy-brief-node');
      card.dataset.requirementId = id;
      card.append(node('p', t.requirement, 'policy-node-label'),
        node('h5', label?.[0] || localized(requirement.requirement, lang)),
        node('p', t.output, 'policy-node-label policy-output-label'),
        node('p', label?.[1] || localized(requirement.response, lang), 'policy-output'));
      stack.append(card);
      evidence.push(...(requirement.evidence || []));
    }
    stage.append(stack);
    diagram.append(stage);
    if (index < briefStages.length - 1) diagram.append(arrow());
  });
  host.append(diagram);
  if (study.course_schedule?.milestones?.length) {
    const schedule = node('section', undefined, 'policy-milestones');
    schedule.append(node('h4', t.milestones));
    const row = node('div', undefined, 'policy-milestone-row');
    study.course_schedule.milestones.forEach((milestone, index) => {
      const item = node('div', undefined, 'policy-milestone');
      item.append(node('b', t.milestoneNames[index] || milestone.name),
        node('span', milestone.date), node('span', milestone.time + ' JST'));
      row.append(item);
    });
    schedule.append(row);
    host.append(schedule);
    if (evidence[0]) evidence.push({ ...evidence[0], page: study.course_schedule.page || 'p.6', pdf_page: [6] });
  }
  host.append(sourceList(evidence, lang));
}
function topicPanel(topic, lang) {
  const t = words[lang];
  const panel = node('article', undefined, 'policy-topic');
  panel.id = 'context-' + topic.id;
  panel.dataset.topicId = topic.id;
  const heading = node('header', undefined, 'policy-topic-heading');
  heading.append(node('h4', localized(topic.title, lang)));
  panel.append(heading);
  const flow = node('div', undefined, 'policy-topic-flow');
  const entries = [
    ['source', topic.compact?.source, 'policy-source-node'],
    ['check', topic.compact?.check, 'policy-check-node'],
    ['action', topic.compact?.action, 'policy-action-node']
  ];
  entries.forEach(([key, value, className], index) => {
    const box = node('section', undefined, 'policy-node ' + className);
    box.append(node('h5', t[key], 'policy-node-label'),
      node('p', localized(value, lang)));
    flow.append(box);
    if (index < entries.length - 1) flow.append(arrow());
  });
  panel.append(flow, sourceList(topic.evidence, lang));
  return panel;
}
function topicFlows(study, lang, host) {
  const t = words[lang];
  host.replaceChildren();
  host.classList.add('policy-topics-host');
  const topics = new Map((study.topics || []).map(topic => [topic.id, topic]));
  const shown = new Set();
  for (const [groupId, ids] of groups) {
    const group = node('section', undefined, 'policy-group');
    group.dataset.policyGroup = groupId;
    const header = node('header', undefined, 'policy-group-heading');
    header.append(node('h3', t.groups[groupId][0]), node('p', t.groups[groupId][1]));
    group.append(header);
    for (const id of ids) {
      const topic = topics.get(id);
      if (!topic) continue;
      shown.add(id);
      group.append(topicPanel(topic, lang));
    }
    host.append(group);
  }
  for (const [id, topic] of topics) {
    if (!shown.has(id)) host.append(topicPanel(topic, lang));
  }
  const record = node('p', undefined, 'policy-record-link');
  const link = node('a', t.record);
  link.href = 'context-study/context.json';
  record.append(link);
  host.append(record);
}

/** Render source/check/action diagrams without altering evidence or source fields. */
export function renderPolicyDiagrams(study, lang = 'en', { briefHost, topicHost } = {}) {
  const selected = words[lang] ? lang : 'en';
  if (!study) return;
  if (briefHost) briefFlow(study, selected, briefHost);
  if (topicHost) topicFlows(study, selected, topicHost);
}
