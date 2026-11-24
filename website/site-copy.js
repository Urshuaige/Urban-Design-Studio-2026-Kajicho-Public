const page = document.body.dataset.sitePage;
const scopes = {
  home: 'main',
  studio: 'main',
  vision: 'main',
  workshop: 'main',
  scenarios: 'main',
  guide: 'main',
  credits: 'main',
  conditions: '#district, #sources, #plate-close',
};

const normalize = value => value.replace(/\s+/g, ' ').trim();
const roots = scopes[page] ? [...document.querySelectorAll(scopes[page])] : [];
let localized;

function bindText(element, copy) {
  const children = [...element.children];
  const original = [...element.childNodes];
  const source = normalize(original.map(node => {
    if (node.nodeType === Node.TEXT_NODE) return node.nodeValue;
    return node.nodeType === Node.ELEMENT_NODE ? '{' + children.indexOf(node) + '}' : '';
  }).join(''));
  if (!Object.hasOwn(copy, source)) return;

  function apply(translation) {
    if (!translation) {
      element.replaceChildren(...original);
      return;
    }
    const nodes = translation.split(/\{(\d+)\}/).map((part, index) =>
      index % 2 ? children[Number(part)] : document.createTextNode(part));
    element.replaceChildren(...nodes);
  }
  return {source, apply};
}

function bindCopy(copy) {
  const bindings = [];
  const bindAttribute = (element, attr) => {
    const source = element.getAttribute(attr);
    if (source && Object.hasOwn(copy, source)) {
      bindings.push({source, apply: translation => element.setAttribute(attr, translation ?? source)});
    }
  };
  for (const scope of roots) {
    for (const element of [scope, ...scope.querySelectorAll('*')]) {
      if (element.closest('.timeline-stage, script, style, svg')) continue;
      const replace = bindText(element, copy);
      if (replace) bindings.push(replace);
      bindAttribute(element, 'alt');
      bindAttribute(element, 'aria-label');
    }
  }
  if (page !== 'conditions') {
    const title = document.title;
    bindings.push({source: title, apply: translation => { document.title = translation ?? title; }});
    const description = document.querySelector('meta[name="description"]');
    if (description) bindAttribute(description, 'content');
  }
  return bindings;
}

function loadCopy(copy) {
  const bindings = bindCopy(copy);
  let lastLanguage = 'en';
  return lang => {
    if (lang === lastLanguage) return;
    const position = lang === 'ja' ? 0 : lang === 'zh' ? 1 : null;
    for (const {source, apply} of bindings) apply(position === null ? null : copy[source]?.[position]);
    const locale = document.documentElement.lang;
    for (const scope of roots) {
      scope.lang = locale;
    }
    lastLanguage = lang;
    document.dispatchEvent(new Event('site-copy-change'));
  };
}

export async function localizePageCopy(lang) {
  if (!roots.length || (lang === 'en' && !localized)) return;
  localized ??= Promise.resolve(globalThis.kajichoCopyReady).then(async initialCopy => {
    if (initialCopy) return initialCopy;
    const response = await fetch(new URL('locales/' + page + '.json?v=20261120-scenarios', import.meta.url));
    if (!response.ok) throw new Error('Could not load page translations: ' + response.status);
    return response.json();
  }).then(loadCopy);
  try {
    const render = await localized;
    render(document.documentElement.lang.slice(0, 2));
  } catch (error) {
    localized = undefined;
    console.error(error);
  }
}
