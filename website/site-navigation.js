import {localizePageCopy} from './site-copy.js?v=20261124-workshop-page';

const labels = {
  en: {
    home: 'Kajicho', brand: 'Urban Design Studio 2026', global: 'Main navigation',
    visit: 'Field Visit', conditions: 'Site Data', policy: 'Policies',
    studio: 'Interim Progress', workshop: 'Workshop', vision: 'Future Vision', guide: 'Design Guide',
    skip: 'Skip to content', language: 'Page language', references: 'Website references',
    footer: 'Urban Design Studio 2026 · Theme B · University of Tokyo',
    visitFooter: 'Urban Design Studio 2026 · Field visit 25 October · Source review 26 October',
    credits: 'Figure and photograph credits',
    loadingVisit: 'Loading the field visit guide…', loadingHistory: 'Loading the historical reading…',
  },
  zh: {
    home: '鍛冶町', brand: '城市设计工作室 2026', global: '全站导航',
    visit: '场地调研', conditions: '现状数据', policy: '规划政策',
    studio: '中期成果', workshop: '会议摘要', vision: '未来愿景', guide: '网站设计规范',
    skip: '跳到正文', language: '页面语言', references: '网站资料',
    footer: '東京大学 · 2026 城市设计工作室 · B 组',
    visitFooter: '2026 城市设计工作室 · 10 月 25 日场地调研 · 10 月 26 日资料核查',
    credits: '图表与照片来源',
    loadingVisit: '正在加载场地调研指南…', loadingHistory: '正在加载场地历史…',
  },
  ja: {
    home: '鍛冶町', brand: '都市デザインスタジオ 2026', global: 'メインメニュー',
    visit: '現地調査', conditions: '現況データ', policy: '計画・政策',
    studio: '中間報告', workshop: '検討会', vision: '将来構想', guide: 'デザインガイド',
    skip: '本文へ移動', language: 'ページの言語', references: 'サイトの参考資料',
    footer: '東京大学・都市デザインスタジオ2026・テーマB',
    visitFooter: '都市デザインスタジオ2026・10月25日現地調査・10月26日資料確認',
    credits: '図版と写真の出典',
    loadingVisit: '現地調査ガイドを読み込み中…', loadingHistory: '地域の歴史を読み込み中…',
  },
};

const root = document.documentElement;
const savedLanguage = 'kajicho-info-lang';
const switcher = document.querySelector('.site-languages');
const buttons = switcher.querySelectorAll('[data-lang]');
const footer = document.querySelector('.site-footer');

function setLanguage(lang) {
  if (Object.hasOwn(labels, lang)) root.lang = lang === 'zh' ? 'zh-CN' : lang;
}

function translateNavigation() {
  const lang = root.lang.slice(0, 2);
  const words = labels[lang] || labels.en;
  for (const node of document.querySelectorAll('[data-site-label]')) {
    const word = words[node.dataset.siteLabel];
    if (word) node.textContent = word;
  }
  for (const button of buttons) {
    button.setAttribute('aria-pressed', String(button.dataset.lang === lang));
  }
  document.querySelector('.site-global-nav')?.setAttribute('aria-label', words.global);
  switcher.setAttribute('aria-label', words.language);
  if (footer) {
    footer.lang = root.lang;
    footer.querySelector('nav')?.setAttribute('aria-label', words.references);
  }
  localizePageCopy(lang);
}

setLanguage(localStorage.getItem(savedLanguage));
if (!document.body.hasAttribute('data-translated-content')) {
  for (const button of buttons) {
    button.addEventListener('click', () => {
      localStorage.setItem(savedLanguage, button.dataset.lang);
      setLanguage(button.dataset.lang);
    });
  }
}

translateNavigation();
new MutationObserver(translateNavigation).observe(root, { attributes: true, attributeFilter: ['lang'] });

// On the data pages, the target may arrive after the initial fragment navigation.
if (document.body.hasAttribute('data-translated-content') && location.hash) {
  const targetId = location.hash.slice(1);
  if (!document.getElementById(targetId)) {
    const waitForTarget = new MutationObserver(() => {
      const target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({behavior: 'instant'});
        waitForTarget.disconnect();
      }
    });
    waitForTarget.observe(document.querySelector('main'), {childList: true, subtree: true});
  }
}

const header = document.querySelector('body > .site-header');
if (header) {
  const measureHeader = () => root.style.setProperty('--top-shell', header.getBoundingClientRect().height + 'px');
  measureHeader();
  new ResizeObserver(measureHeader).observe(header);
}

const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let sectionFrame = 0;
let jumpFrame = 0;

function markCurrentSections() {
  sectionFrame = 0;
  const headerBottom = header?.getBoundingClientRect().bottom ?? 0;
  const maxScroll = Math.max(0, root.scrollHeight - innerHeight);
  const atPageEnd = scrollY > 0 && scrollY >= maxScroll - 2;

  for (const nav of document.querySelectorAll('.page-jumps')) {
    const readingLine = Math.max(headerBottom, 0) + nav.offsetHeight + 24;
    const links = [...nav.querySelectorAll('a[href^="#"]')];
    let currentLink;
    let lastLink;
    let closestTop = -Infinity;
    let firstTop = Infinity;

    for (const link of links) {
      const target = document.getElementById(link.hash.slice(1));
      if (link.hidden || !target?.getClientRects().length) continue;
      lastLink = link;
      const top = target.getBoundingClientRect().top;
      firstTop = Math.min(firstTop, top);
      if (top <= readingLine && top >= closestTop) {
        closestTop = top;
        currentLink = link;
      }
    }

    const progressStart = Math.max(0, scrollY + firstTop - readingLine);
    const progress = Math.max(0, Math.min(1, (scrollY - progressStart) / Math.max(1, maxScroll - progressStart)));
    nav.style.setProperty('--reading-progress', Number.isFinite(progress) ? progress.toFixed(4) : '0');

    if (atPageEnd) currentLink = lastLink;
    for (const link of links) {
      if (link === currentLink) {
        if (link.getAttribute('aria-current') !== 'location') link.setAttribute('aria-current', 'location');
      } else {
        link.removeAttribute('aria-current');
      }
    }
  }
}

function scheduleSectionUpdate() {
  if (!sectionFrame) sectionFrame = requestAnimationFrame(markCurrentSections);
}

function endSectionJump() {
  cancelAnimationFrame(jumpFrame);
  jumpFrame = 0;
}

function jumpToSection(event) {
  const link = event.target.closest('a[href^="#"]');
  if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey ||
      event.shiftKey || event.altKey || reducedMotion.matches) return;

  const target = document.getElementById(link.hash.slice(1));
  if (!target?.getClientRects().length) return;

  const start = scrollY;
  const margin = parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
  const maxScroll = Math.max(0, root.scrollHeight - innerHeight);
  const destination = Math.max(0, Math.min(maxScroll, start + target.getBoundingClientRect().top - margin));
  const distance = destination - start;
  endSectionJump();
  if (Math.abs(distance) < 2) return;

  event.preventDefault();
  if (location.hash !== link.hash) history.pushState(history.state, '', link.hash);
  const started = performance.now();
  const duration = Math.min(420, 160 + Math.sqrt(Math.abs(distance)) * 3);
  const moveFocus = event.detail === 0;

  function move(now) {
    const time = Math.min(1, (now - started) / duration);
    const eased = 1 - (1 - time) ** 3;
    window.scrollTo({top: start + distance * eased, behavior: 'instant'});
    if (time < 1) {
      jumpFrame = requestAnimationFrame(move);
    } else {
      jumpFrame = 0;
      if (moveFocus) {
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({preventScroll: true});
      }
    }
  }
  jumpFrame = requestAnimationFrame(move);
}

const main = document.querySelector('main');
if (main) {
  main.addEventListener('click', jumpToSection);
  window.addEventListener('wheel', endSectionJump, {passive: true});
  window.addEventListener('pointerdown', endSectionJump, {passive: true});
  window.addEventListener('keydown', endSectionJump);
  window.addEventListener('popstate', endSectionJump);
  reducedMotion.addEventListener('change', endSectionJump);
  window.addEventListener('scroll', scheduleSectionUpdate, {passive: true});
  window.addEventListener('resize', scheduleSectionUpdate);
  window.addEventListener('hashchange', scheduleSectionUpdate);
  window.addEventListener('pageshow', scheduleSectionUpdate);
  document.addEventListener('site-copy-change', scheduleSectionUpdate);
  new MutationObserver(scheduleSectionUpdate).observe(main, {
    attributes: true,
    attributeFilter: ['hidden'],
    childList: true,
    subtree: true,
  });
  new ResizeObserver(scheduleSectionUpdate).observe(main);
  scheduleSectionUpdate();
}
