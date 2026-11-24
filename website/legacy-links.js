const hash = location.hash.slice(1);
const dataAnchors = new Set(['overview', 'mapping', 'current-data', 'current-maps', 'sources']);

if (document.body.dataset.sitePage === 'home' && hash) {
  let destination;
  if (dataAnchors.has(hash) || hash.startsWith('frontage')) destination = '/conditions';
  if (hash === 'info-main') destination = '/conditions';
  if (/^(kajicho-2050|framework|evidence|locations|case-.+|targets(?:-.+)?|constraints|delivery|plan-sources|feedback(?:-.+)?|source-.+|phase-.+)$/.test(hash)) {
    destination = '/vision';
  }
  if (destination) location.replace(destination + location.search + location.hash);
} else if (document.body.dataset.sitePage === 'legacy-plan') {
  location.replace('/vision' + location.search + (hash === 'sources' ? '#plan-sources' : location.hash));
} else if (document.body.dataset.sitePage === 'studio' && hash === 'district') {
  location.replace('/conditions' + location.search + '#district');
}
