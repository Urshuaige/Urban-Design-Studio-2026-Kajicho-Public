/* Shared reading outline. Authored IDs stay intact; fallback IDs follow structure,
   not translated heading text. data-outline-ignore/key/label are optional hooks. */
const main = document.querySelector('main');
if (main && !document.querySelector('[data-page-outline]')) {
  const words = {
    en:{contents:'On this page',open:'Open contents',close:'Close contents',project:'Overview','study-area':'Study area',context:'Context',evidence:'Data & risk',mapping:'Mapping','simulation-plan':'Next studies',questions:'Design agenda',downloads:'Shared resources'},
    zh:{contents:'本页目录',open:'展开目录',close:'收起目录',project:'概览','study-area':'研究范围',context:'文件背景',evidence:'数据与风险',mapping:'场地图集','simulation-plan':'后续研究',questions:'设计议题',downloads:'共用资料'},
    ja:{contents:'このページ',open:'目次を開く',close:'目次を閉じる',project:'概要','study-area':'対象区域',context:'背景資料',evidence:'データとリスク',mapping:'マッピング','simulation-plan':'次の調査',questions:'設計の論点',downloads:'共有資料'}
  };
  const make = (tag,cls,text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const root = make('aside','page-outline');
  root.dataset.pageOutline = '';
  root.hidden = true;
  const marks = make('div','outline-marks');
  marks.setAttribute('aria-hidden','true');
  const trigger = make('button','outline-trigger');
  trigger.type = 'button';
  trigger.setAttribute('aria-controls','page-outline-panel');
  trigger.setAttribute('aria-expanded','false');
  const mobileLabel = make('span','outline-mobile-label');
  trigger.append(mobileLabel);
  const panel = make('div','outline-panel');
  panel.id = 'page-outline-panel';
  panel.inert = true;
  panel.setAttribute('aria-hidden','true');
  const header = make('div','outline-header');
  const title = make('b','outline-title');
  const close = make('button','outline-close','×');
  close.type = 'button';
  const nav = make('nav','outline-links');
  header.append(title,close);
  panel.append(header,nav);
  root.append(marks,trigger,panel);
  document.body.append(root);
  document.documentElement.dataset.pageOutlineReady = '';
  const pageHeader = document.querySelector('body > header,[data-page-header]');
  const finePointer = matchMedia('(min-width:701px) and (hover:hover) and (pointer:fine)');
  const reducedMotion = matchMedia('(prefers-reduced-motion:reduce)');
  const generated = new Map();
  let entries = [], activeId = '', open = false, refreshing = false;
  let refreshFrame = 0, scrollFrame = 0, pendingHash = location.hash, lastOffset = -1;
  const language = () => document.documentElement.lang.startsWith('zh') ? 'zh' : document.documentElement.lang.startsWith('ja') ? 'ja' : 'en';
  const textOf = node => (node.innerText || node.textContent).trim().replace(/\s+/g,' ');
  const ignore = 'dialog,[role="dialog"],nav,[data-outline-ignore],.inspector,.type-specimen';
  const isVisible = heading => !heading.closest(ignore+', [hidden],[inert],[aria-hidden="true"]')
    && !heading.closest('details:not([open])')
    && heading.getClientRects().length > 0 && getComputedStyle(heading).visibility !== 'hidden' && !!textOf(heading);

  function headerOffset() {
    if (!pageHeader) return 0;
    const style = getComputedStyle(pageHeader);
    if (!['fixed','sticky'].includes(style.position) || style.display === 'none') return 0;
    return Math.max(0,pageHeader.getBoundingClientRect().height + (parseFloat(style.top) || 0));
  }
  function updateOffset() {
    const value = Math.ceil(headerOffset());
    if (value !== lastOffset) {
      lastOffset = value;
      document.documentElement.style.setProperty('--page-outline-header-offset',value+'px');
    }
    return value;
  }
  function setOpen(value) {
    value = Boolean(value && !root.hidden);
    if (open === value) return;
    open = value;
    root.dataset.open = String(value);
    trigger.setAttribute('aria-expanded',String(value));
    trigger.setAttribute('aria-label',words[language()][value ? 'close' : 'open']);
    panel.setAttribute('aria-hidden',String(!value));
    panel.inert = !value;
    if (value) {
      const current = nav.querySelector('[aria-current="location"]');
      if (current) nav.scrollTop = Math.max(0,current.offsetTop - nav.clientHeight/2);
    }
  }
  function setActive(entry) {
    if (!entry || entry.id === activeId) return;
    activeId = entry.id;
    for (const item of entries) {
      const active = item === entry;
      const parent = !active && item.level === 1 && entry.parent === item.id;
      item.link.classList.toggle('is-current',active);
      item.mark.classList.toggle('is-current',active);
      item.link.classList.toggle('is-parent',parent);
      item.mark.classList.toggle('is-parent',parent);
      if (active) item.link.setAttribute('aria-current','location');
      else item.link.removeAttribute('aria-current');
    }
  }
  function updateActive() {
    scrollFrame = 0;
    const line = updateOffset() + 32;
    if (!entries.length) return;
    let active = entries[0];
    for (const item of entries) {
      if (item.target.getBoundingClientRect().top <= line) active = item;
    }
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 3) active = entries.at(-1);
    setActive(active);
  }
  function scheduleActive() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateActive);
  }
  function hashKey(key) {
    let value = 2166136261;
    for (const character of key) value = Math.imul(value ^ character.charCodeAt(0),16777619);
    return (value >>> 0).toString(36);
  }
  function structuralKey(node) {
    const parts = [];
    for (let cursor = node; cursor && cursor !== main; cursor = cursor.parentElement) {
      // Language alternatives share a semantic path even while both remain in the DOM.
      if (cursor.hasAttribute('data-guide-lang') || cursor.hasAttribute('data-outline-language')) {
        parts.unshift('language-content');
        break;
      }
      const siblings = cursor.parentElement ? [...cursor.parentElement.children].filter(n=>n.tagName===cursor.tagName) : [cursor];
      parts.unshift(cursor.tagName.toLowerCase()+':'+siblings.indexOf(cursor));
    }
    return parts.join('/');
  }
  function headingKey(heading) {
    const explicit = heading.getAttribute('data-outline-key');
    if (explicit) return 'key:'+explicit;
    const scope = heading.parentElement.closest('[id]');
    const prefix = scope && scope !== main ? scope.id+'/' : '';
    for (const attribute of ['data-t','data-i18n','data-guide-t','data-map-t','data-team-t']) {
      const token = heading.getAttribute(attribute) || heading.querySelector('['+attribute+']')?.getAttribute(attribute);
      if (token) return prefix+attribute+':'+token;
    }
    return 'path:'+structuralKey(heading);
  }
  function stableTarget(heading,level,headings,key) {
    if (heading.id && !heading.hasAttribute('data-outline-generated')) return heading;
    if (level === 1) {
      const section = heading.closest('section[id],article[id]');
      if (section && headings.find(h=>section.contains(h)) === heading) return section;
    }
    let record = generated.get(key);
    if (record && record.node !== heading && record.node.id === record.id) {
      record.node.removeAttribute('id');
      record.node.removeAttribute('data-outline-generated');
    }
    let id = record?.id || 'outline-'+hashKey(key);
    const base = id;
    let count = 1;
    while (document.getElementById(id) && document.getElementById(id) !== heading) id = base+'-'+(++count);
    heading.id = id;
    heading.dataset.outlineGenerated = '';
    generated.set(key,{id,node:heading});
    return heading;
  }
  function scrollToEntry(item,focus=false,behavior='auto') {
    if (focus) {
      if (!item.target.hasAttribute('tabindex')) item.target.setAttribute('tabindex','-1');
      item.target.focus({preventScroll:true});
    }
    window.scrollTo({
      top:Math.max(0,window.scrollY+item.target.getBoundingClientRect().top-updateOffset()-24),
      behavior:reducedMotion.matches ? 'auto' : behavior
    });
    setActive(item);
  }
  function resolveHash() {
    if (!pendingHash) return;
    let id;
    try { id = decodeURIComponent(pendingHash.slice(1)); } catch { pendingHash = ''; return; }
    const item = entries.find(entry=>entry.id===id);
    if (item) {
      pendingHash = '';
      requestAnimationFrame(()=>{ if (item.target.isConnected) scrollToEntry(item); });
    }
  }
  function refresh() {
    refreshFrame = 0;
    refreshing = true;
    const t = words[language()];
    const previousFocus = entries.find(item=>item.link===document.activeElement)?.id;
    const previousScroll = nav.scrollTop;
    for (const item of entries) item.target.removeAttribute('data-outline-target');
    title.textContent = mobileLabel.textContent = t.contents;
    nav.setAttribute('aria-label',t.contents);
    trigger.setAttribute('aria-label',t[open ? 'close' : 'open']);
    trigger.title = t.open;
    close.setAttribute('aria-label',t.close);
    close.title = t.close;
    const list = make('ol','outline-list');
    const fragment = document.createDocumentFragment();
    const headings = [...main.querySelectorAll('h1,h2,h3')].filter(isVisible);
    const keys = new Map();
    entries = [];
    let parent = '', children = null;
    for (const heading of headings) {
      const section = heading.closest('section');
      const ownChapter = section && !section.parentElement.closest('section') && headings.find(h=>section.contains(h))===heading && !headings.some(h=>h!==heading && /H[12]/.test(h.tagName) && section.contains(h));
      const level = heading.tagName === 'H3' && !ownChapter && parent ? 2 : 1;
      let key = headingKey(heading);
      const duplicate = keys.get(key) || 0;
      keys.set(key,duplicate+1);
      if (duplicate) key += ':repeat:'+duplicate;
      const target = stableTarget(heading,level,headings,key);
      if (entries.some(item=>item.id===target.id)) continue;
      const label = heading.getAttribute('data-outline-label') || (main.classList.contains('folio') && t[target.id]) || textOf(heading);
      target.setAttribute('data-outline-target','');
      const item = make('li','outline-item outline-level-'+level);
      const link = make('a','outline-link',label);
      link.href = '#'+encodeURIComponent(target.id);
      link.title = textOf(heading);
      link.dataset.outlineLevel = String(level);
      const mark = make('span','outline-mark outline-level-'+level);
      item.append(link);
      if (level === 1) {
        parent = target.id;
        list.append(item);
        children = make('ol','outline-children');
        item.append(children);
      } else if (children) children.append(item);
      else list.append(item);
      fragment.append(mark);
      entries.push({id:target.id,parent:level===1 ? '' : parent,level,target,link,mark});
    }
    nav.replaceChildren(list);
    marks.replaceChildren(fragment);
    nav.scrollTop = previousScroll;
    root.style.setProperty('--outline-count',String(entries.length));
    root.hidden = entries.length < 2;
    if (root.hidden) setOpen(false);
    activeId = '';
    updateActive();
    if (previousFocus && open) (entries.find(item=>item.id===previousFocus)?.link || trigger).focus({preventScroll:true});
    refreshing = false;
    resolveHash();
  }
  function scheduleRefresh() {
    if (!refreshFrame) refreshFrame = requestAnimationFrame(refresh);
  }
  function relevantMutation(record) {
    if (record.type === 'characterData') return !!record.target.parentElement?.closest('h1,h2,h3');
    const target = record.target;
    if (record.type === 'attributes') return target === main || target.matches('h1,h2,h3') || !!target.querySelector('h1,h2,h3');
    if (target.closest?.('h1,h2,h3')) return true;
    return [...record.addedNodes,...record.removedNodes].some(node=>node.nodeType===1 && (node.matches('h1,h2,h3') || node.querySelector('h1,h2,h3')));
  }
  root.addEventListener('pointerenter',()=>{ if (finePointer.matches) setOpen(true); });
  root.addEventListener('pointerleave',()=>{ if (!root.contains(document.activeElement)) setOpen(false); });
  trigger.addEventListener('click',event=>setOpen(finePointer.matches && event.detail>0 ? true : !open));
  trigger.addEventListener('keydown',event=>{
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      setOpen(true);
      (event.key === 'ArrowUp' ? entries.at(-1) : entries[0])?.link.focus();
    }
  });
  close.addEventListener('click',()=>{ trigger.focus({preventScroll:true}); setOpen(false); });
  root.addEventListener('focusin',event=>{ if (event.target!==trigger && !refreshing) setOpen(true); });
  root.addEventListener('focusout',event=>{ if (!refreshing && !root.contains(event.relatedTarget)) setOpen(false); });
  root.addEventListener('keydown',event=>{
    if (event.key === 'Escape') {
      event.preventDefault();
      trigger.focus({preventScroll:true});
      setOpen(false);
    } else if (nav.contains(event.target) && ['ArrowDown','ArrowUp','Home','End'].includes(event.key)) {
      const index = entries.findIndex(item=>item.link===event.target);
      if (index<0) return;
      event.preventDefault();
      const next = event.key==='Home' ? 0 : event.key==='End' ? entries.length-1 : (index+(event.key==='ArrowUp' ? -1 : 1)+entries.length)%entries.length;
      entries[next].link.focus();
    }
  });
  document.addEventListener('pointerdown',event=>{ if (open && !root.contains(event.target)) setOpen(false); });
  nav.addEventListener('click',event=>{
    const link = event.target.closest('a');
    if (!link || event.button!==0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const item = entries.find(entry=>entry.link===link);
    if (!item) return;
    event.preventDefault();
    if (location.hash!==link.hash) history.pushState(null,'',link.getAttribute('href'));
    pendingHash = '';
    scrollToEntry(item,true,'smooth');
    setOpen(false);
  });
  window.addEventListener('scroll',scheduleActive,{passive:true});
  window.addEventListener('resize',()=>{ scheduleRefresh(); scheduleActive(); },{passive:true});
  window.addEventListener('hashchange',()=>{ pendingHash=location.hash; resolveHash(); scheduleActive(); });
  finePointer.addEventListener('change',()=>setOpen(false));
  new MutationObserver(records=>{ if (records.some(relevantMutation)) scheduleRefresh(); }).observe(main,{
    childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['hidden','aria-hidden','inert','class','style','open']
  });
  new MutationObserver(scheduleRefresh).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  if ('ResizeObserver' in window) {
    const observer = new ResizeObserver(scheduleActive);
    observer.observe(main);
    if (pageHeader) observer.observe(pageHeader);
  }
  document.fonts?.ready.then(scheduleRefresh);
  refresh();
}
