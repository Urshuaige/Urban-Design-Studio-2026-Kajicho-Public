(() => {
  const root = document.documentElement;
  const aerialSwap = 'kajicho-aerial-swap';
  let active;

  const localePage = document.currentScript.dataset.copyPage;
  if (localePage && ['ja', 'zh'].includes(localStorage.getItem('kajicho-info-lang'))) {
    const pack = document.createElement('script');
    pack.type = 'module';
    pack.setAttribute('blocking', 'render');
    const url = '/locales/' + localePage + '.json?v=20261120-scenarios';
    pack.textContent = 'import copy from ' + JSON.stringify(url) + ' with {type:"json"}; window.kajichoSetInitialCopy(copy);';
    // Avoid holding the page on a slow locale request.
    const release = setTimeout(() => pack.removeAttribute('blocking'), 220);
    window.kajichoCopyReady = new Promise(resolve => {
      function finish(copy) {
        clearTimeout(release);
        delete window.kajichoSetInitialCopy;
        resolve(copy);
      }
      window.kajichoSetInitialCopy = finish;
      pack.addEventListener('error', () => finish(), {once: true});
    });
    document.head.append(pack);
  }

  function aerialRoute(activation) {
    if (!activation?.from?.url || !activation.entry?.url) return;
    const from = new URL(activation.from.url);
    const to = new URL(activation.entry.url);
    if (from.hash || to.hash || from.origin !== to.origin) return;
    if ((from.pathname === '/' && to.pathname === '/vision') ||
        (from.pathname === '/vision' && to.pathname === '/')) return from.pathname + '→' + to.pathname;
  }

  function showMotion(transition, direction, sharedAerial) {
    active = transition;
    root.dataset.pageMotion = direction;
    root.toggleAttribute('data-shared-aerial', Boolean(sharedAerial));
    transition.finished.then(() => {
      if (active !== transition) return;
      active = undefined;
      delete root.dataset.pageMotion;
      root.removeAttribute('data-shared-aerial');
    });
  }

  window.addEventListener('pageswap', event => {
    const route = event.viewTransition && aerialRoute(event.activation);
    const image = route && document.querySelector('.atlas-cover-image img');
    const shared = image?.complete && image.naturalWidth > 0 && scrollY < 80;
    if (shared) sessionStorage.setItem(aerialSwap, route);
    else sessionStorage.removeItem(aerialSwap);
    if (event.viewTransition) showMotion(event.viewTransition, 'out', shared);
  });

  window.addEventListener('pagereveal', event => {
    const route = event.viewTransition && aerialRoute(window.navigation?.activation);
    const shared = route && route === sessionStorage.getItem(aerialSwap);
    sessionStorage.removeItem(aerialSwap);
    if (event.viewTransition) showMotion(event.viewTransition, 'in', shared);
  });

  for (const event of ['pointerdown', 'wheel', 'keydown']) {
    window.addEventListener(event, () => active?.skipTransition(), {passive: true, capture: true});
  }
})();
