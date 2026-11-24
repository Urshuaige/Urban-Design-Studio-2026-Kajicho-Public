const copy = {
  title: ['How renewal works', '地域更新の進め方', '地区更新如何推进'],
  intro: [
    'Follow local renewal and see who each Future Vision proposal affects.',
    '地域の更新がどう進み、将来構想の4つの提案が誰に関わるかを確認する。',
    '从地区更新的组织和程序出发，查清 Future Vision 四个地点的方案会涉及谁。'
  ],
  diagramKey: [
    'Solid arrows show the order of work. Dashed arrows show where studio decisions need to be checked against local plans or procedures.',
    '実線は作業の順序、破線はスタジオ案と地域の計画・手続を照合する箇所。',
    '实线表示工作顺序，虚线表示工作室需要核对地区项目或适用程序的环节。'
  ],
  projects: ['Development in and around Kajicho', '鍛冶町と周辺の開発動向', '鍛冶町及周边的开发项目'],
  map: ['Open in 3D', '3D地図で開く', '在 3D 中查看'],
  allProjects: ['View development projects in 3D', '開発事業を3D地図で見る', '在 3D 中查看开发项目'],
  allCases: ['View proposal sites in 3D', '提案地点を3D地図で見る', '在 3D 中查看方案地点'],
  projectRecord: ['Record and sources', '記録と出典', '项目记录与来源'],
  options: ['Full option details', '提案の詳細', '完整方案说明'],
  cleared: ['Clearance recorded', '解体・更地を確認', '记录为拆除或清场'],
  study: ['Under study', '検討中', '研究中'],
  planned: ['Published plan', '公表計画', '已公示计划'],
  operating: ['Local activity', '地域活動', '地方活动'],
  complete: ['Completed', '竣工', '已竣工'],
  cases: ['Who each proposal involves', '提案ごとの関係者', '每个方案涉及谁'],
  case: ['Case', '提案', '方案'],
  studies: ['Studio studies', 'スタジオの分析', '工作室研究'],
  nearbyProjects: ['Local projects to check', '照合する地域の事業', '需核对的地区项目'],
  action: ['Design option', '設計案', '设计选项'],
  actor: ['Who to involve', '関係者', '需要联系谁'],
  check: ['What to agree or check', '協議・確認事項', '要协商或核对什么'],
  phase: ['Phases to check', '確認する段階', '对应阶段'],
  vision: ['Future Vision', '将来構想', '未来愿景'],
  limits: ['Studio limits and decision steps', '比較条件と判断手順', '方案约束与决策步骤'],
  local: ['Field visit relationships', '現地調査で確認した関係', '调研记录中的关系'],
  open: ['Read the field record', '現地調査の記録', '查看调研资料'],
  related: ['Relevant studio step', '関係する提案の手順', '对应的方案步骤']
};

const choices = [
  ['Option A', '案A', '选项 A'],
  ['Option B', '案B', '选项 B'],
];

const researchers = {
  asuka: 'Asuka', jiaxiang: 'Jiaxiang', regina: 'Regina',
  keane: 'Keane', shair: 'Shair', dingchao: 'Dingchao'
};

const fieldRecords = {
  actors: ['#actors', '/vision#policies-rights'],
  process: ['#renewal-process', '/vision#delivery'],
  'rights-flow': ['#rights', '/vision#plan-block-rebuild'],
  activity: ['#legal-guide', '/vision#plan-street-rain-garden']
};

const langIndex = {en: 0, ja: 1, zh: 2};

function cityLink(mode, id) {
  const params = new URLSearchParams({overlays: 'renewal'});
  if (mode !== 'projects') params.set('renewal',mode);
  if (id) params.set('renewalSite',id);
  return '/city-model?' + params;
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);
}

export function renderRenewalDiagram(diagram, lang) {
  const local = value => value[langIndex[lang]];
  const t = value => escapeHTML(local(value));
  const stepWidth = 200;
  const stepHeight = 96;
  const column = index => 128 + 224 * index;
  const lane = index => 24 + 180 * index;
  const connectors = diagram.lanes.flatMap((_, row) =>
    [0, 1, 2].map(index =>
      `<path class="edge" d="M${column(index) + stepWidth + 4} ${lane(row) + 48} H${column(index + 1) - 8}" marker-end="url(#renewal-arrow)"/>`
    )
  ).join('');
  const checks = diagram.checks.map((message, index) => {
    const x = column(index + 1) + stepWidth / 2;
    return `<path class="edge renewal-check-line" d="M${x} 124 V145 M${x} 179 V196" marker-end="url(#renewal-arrow)"/>
      <text class="renewal-edge-label" x="${x}" y="168" text-anchor="middle">${t(message)}</text>`;
  }).join('');
  const rows = diagram.lanes.map((row, rowIndex) => {
    const y = lane(rowIndex);
    const label = local(row.label).map((line, index) =>
      `<tspan x="16" dy="${index ? 21 : 0}">${escapeHTML(line)}</tspan>`
    ).join('');
    return `<text class="renewal-lane" x="16" y="${y + 42}">${label}</text>` +
      row.steps.map((step, index) => {
        const x = column(index);
        const [title, actor, output] = local(step).map(escapeHTML);
        const focal = rowIndex === 1 && index === 2 ? ' renewal-node-focal' : '';
        return `<g class="renewal-node${focal}">
          <rect class="node-bg" x="${x}" y="${y}" width="${stepWidth}" height="${stepHeight}" rx="4"/>
          <text class="renewal-node-title" x="${x + 12}" y="${y + 24}">${title}</text>
          <text class="renewal-node-detail" x="${x + 12}" y="${y + 51}">
            <tspan x="${x + 12}">${actor}</tspan><tspan x="${x + 12}" dy="20">${output}</tspan>
          </text>
        </g>`;
      }).join('');
  }).join('');

  return `<svg class="renewal-diagram" xmlns="http://www.w3.org/2000/svg" width="1024" height="324" viewBox="0 0 1024 324" role="img" aria-labelledby="renewal-svg-title renewal-svg-desc">
    <title id="renewal-svg-title">${t(diagram.label)}</title>
    <desc id="renewal-svg-desc">${t(diagram.description)}</desc>
    <defs><marker id="renewal-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0 L8 4 L0 8 Z"/>
    </marker></defs>
    <path class="renewal-divider" d="M16 160 H324 M792 160 H1000"/>
    ${connectors}${checks}${rows}
  </svg>`;
}

export function renderProposalDiagram(item, lang) {
  const local = value => value[langIndex[lang]];
  const t = value => escapeHTML(local(value));
  const columns = [copy.action, copy.actor, copy.check];
  const x = i => 16 + i * 344;
  const id = 'proposal-diagram-' + item.id;
  const heads = columns.map((title, i) =>
    `<text class="proposal-column" x="${x(i)}" y="27">${t(title)}</text>`).join('');
  const rows = item.steps.map((step, row) => {
    const y = 44 + row * 88;
    const paths = [0, 1].map(i =>
      `<path class="edge" d="M${x(i) + 308} ${y + 34} H${x(i+1) - 8}" marker-end="url(#${id}-arrow)"/>`).join('');
    const nodes = step.flow.map((content, i) => {
      const lines = local(content);
      const title = lines.length > 1 ? y + 28 : y + 40;
      const tone = i === 0 ? ' proposal-choice' : '';
      return `<g class="proposal-node${tone}">
        <rect class="node-bg" x="${x(i)}" y="${y}" width="304" height="68" rx="4"/>
        <text class="proposal-label" x="${x(i) + 12}" y="${title}">${lines.map((line, j) =>
          `<tspan x="${x(i) + 12}" dy="${j ? 20 : 0}">${escapeHTML(line)}</tspan>`).join('')}</text>
      </g>`;
    }).join('');
    return `<g class="proposal-row" id="renewal-step-${step.id}">${paths}${nodes}</g>`;
  }).join('');
  const description = item.steps.map(step =>
    [t(step.name), t(step.actors), t(step.check)].map(line => /[.。]$/.test(line) ? line : line + '.').join(' ')).join(' ');
  return `<svg class="renewal-diagram proposal-diagram" xmlns="http://www.w3.org/2000/svg" width="1024" height="216" viewBox="0 0 1024 216" role="img" aria-labelledby="${id}-title ${id}-desc">
    <title id="${id}-title">${t(item.name)}</title>
    <desc id="${id}-desc">${description}</desc>
    <defs><marker id="${id}-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
      <path d="M0 0 L8 4 L0 8 Z"/>
    </marker></defs>
    ${heads}${rows}
  </svg>`;
}

export function renderRenewal(data, graphs, sources, lang) {
  const t = value => escapeHTML(value[langIndex[lang]]);
  const recorded = value => escapeHTML(value[lang]);
  const c = key => t(copy[key]);
  const link = (url, label) => `<a href="${escapeHTML(url)}">${label}</a>`;
  const group = (links, label) => `<nav class="renewal-links" aria-label="${label}">${links.join('')}</nav>`;
  const caseLabel = item => `${c('case')} ${item.letter}`;
  const caseLabelByID = Object.fromEntries(data.cases.map(item => [item.id, caseLabel(item)]));
  const projectCards = data.projects.map(project => `
    <article class="renewal-project" id="development-${project.id}">
      <strong class="renewal-status" data-stage="${project.status}">${c(project.status)}</strong>
      <h4>${link(cityLink('projects', project.id), t(project.name))}</h4>
      <p>${t(project.actor)}</p>
      <details data-development-details>
        <summary>${c('projectRecord')}</summary>
        <p class="renewal-place">${t(project.place)}</p>
        <p>${t(project.record)}</p>
        <div class="renewal-source-links">${project.sources.map(([url, label]) => link(url, t(label))).join(' · ')}</div>
        <div class="renewal-source-links">${project.cases.map(id => link('#renewal-' + id, caseLabelByID[id])).join(' · ')}</div>
      </details>
    </article>`).join('');

  const cases = data.cases.map(item => {
    const nearby = data.projects.filter(project => project.cases.includes(item.id))
      .map(project => link('#development-' + project.id, t(project.name)));
    const steps = item.steps.map(step => `
      <tr>
        <th scope="row">${link('/vision#plan-' + step.id, t(step.name))}</th>
        <td>${t(step.actors)}</td>
        <td>${t(step.check)}</td>
        <td class="renewal-phase">${step.phases.map(year => link('/vision#phase-' + year, year)).join(' · ')}</td>
      </tr>`).join('');
    const destination = '/vision#case-' + item.id;
    return `<article class="renewal-case" id="renewal-${item.id}" aria-labelledby="renewal-title-${item.id}">
      <h4 id="renewal-title-${item.id}"><span>${caseLabel(item)}</span> ${t(item.name)}</h4>
      ${group([link(cityLink('proposals', item.id), c('map')), link(destination, c('vision')),
        ...item.steps.map((step, i) => link('/vision#plan-' + step.id, t(choices[i])))], caseLabel(item))}
      <div class="renewal-diagram-frame">${renderProposalDiagram(item, lang)}</div>
      <details class="renewal-option-details">
        <summary>${c('options')}</summary>
        ${group(item.studies.map(id => link('/vision#source-' + id, researchers[id])), c('studies'))}
        ${nearby.length ? `<p class="renewal-related"><strong>${c('nearbyProjects')}</strong> ${nearby.join(' · ')}</p>` : ''}
        <div class="renewal-table-wrap"><table class="renewal-table renewal-proposals" aria-labelledby="renewal-title-${item.id}">
          <thead><tr><th scope="col">${c('action')}</th><th scope="col">${c('actor')}</th><th scope="col">${c('check')}</th><th scope="col">${c('phase')}</th></tr></thead>
          <tbody>${steps}</tbody>
        </table></div>
      </details>
    </article>`;
  }).join('');

  const references = graphs.map(graph => {
    const nodes = new Map(graph.nodes.map(node => [node.id, recorded(node.label)]));
    const sourcesByID = new Map(sources.map(source => [source.id, source]));
    const edges = graph.edges.map(edge => `<li>
      <p><strong>${nodes.get(edge.source)}</strong> → ${recorded(edge.label)} → <strong>${nodes.get(edge.target)}</strong></p>
      <div class="renewal-source-links">${edge.refs.map(id => {
        const source = sourcesByID.get(id);
        return link(source.url, recorded(source.title));
      }).join(' · ')}</div>
    </li>`).join('');
    const [field, vision] = fieldRecords[graph.id];
    return `<details class="renewal-record">
      <summary>${recorded(graph.title)}</summary>
      <p>${recorded(graph.summary)}</p>
      ${group([link(field, c('open')), link(vision, c('related'))], recorded(graph.title))}
      <ul class="renewal-record-list">${edges}</ul>
    </details>`;
  }).join('');

  return `<h2 class="site-section-title" id="how-renewal-works">${c('title')}</h2>
    <p class="renewal-lede">${c('intro')}</p>
    <figure class="renewal-figure">
      <div class="renewal-diagram-frame">${renderRenewalDiagram(data.diagram, lang)}</div>
      <figcaption>${c('diagramKey')} ${link('#renewal-process', c('open'))}</figcaption>
    </figure>
    ${group([link('#renewal-projects', c('projects')), ...data.cases.map(item =>
      link('#renewal-' + item.id, caseLabel(item))), link('/vision#constraints', c('limits'))], c('title'))}
    <section class="renewal-subsection" id="renewal-projects" aria-labelledby="renewal-projects-title">
      <div class="renewal-section-heading">
        <h3 id="renewal-projects-title">${c('projects')}</h3>
        ${link(cityLink('projects'), c('allProjects'))}
      </div>
      <div class="renewal-projects">${projectCards}</div>
    </section>
    <section class="renewal-subsection" id="renewal-interventions" aria-labelledby="renewal-cases-title">
      <div class="renewal-section-heading">
        <h3 id="renewal-cases-title">${c('cases')}</h3>
        ${link(cityLink('proposals'), c('allCases'))}
      </div>
      ${cases}
    </section>
    <section class="renewal-subsection" id="renewal-records" aria-labelledby="renewal-records-title">
      <h3 id="renewal-records-title">${c('local')}</h3>
      ${references}
    </section>`;
}
