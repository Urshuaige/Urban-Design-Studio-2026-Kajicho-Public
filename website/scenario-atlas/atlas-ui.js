import { createAtlasView } from './atlas-view.js';

const root = document.querySelector('.vision-atlas');
const stage = root.querySelector('.atlas-stage');
const select = selector => root.querySelector(selector);
const node = (tag,text,className) => {
  const e = document.createElement(tag);
  if (text != null) e.textContent = text;
  if (className) e.className = className;
  return e;
};
const word = (en, ja, zh) => ({en,ja,zh});
let language = document.documentElement.lang.slice(0,2);
const offline = document.documentElement.dataset.atlasOffline === 'true';
const localized = phrase => typeof phrase === 'string' ? phrase : phrase?.[language] ?? phrase?.en ?? '';
const copy = {
  external: word('Open the recorded panorama in Google Maps','記録したパノラマをGoogleマップで開く','在 Google Maps 打开记录的全景'),
  panorama: word('Google Street View','Google ストリートビュー','Google Street View'),
  panoPrivacy: word('Local record','保存した調査フレーム','本地调查帧'),
  panoNote: word('The viewer may show a newer nearby image if the surveyed panorama is unavailable.',
                    '記録したパノラマが利用できない場合は、近隣の新しい画像が表示されることがあります。',
                    '若调查时的原全景已下线，Google 可能切换到附近的更新图像。'),
  cases: word('Proposal and targets','提案と目標','提案与目标'),
  proposed: word('Proposal view','提案図','提案图'),
  field: word('Field observation','現地観察','现场观察'),
  mask: word('Same-frame mask','同じフレームの分類','同帧遮罩'),
  study: word('Study figure','調査図','研究图'),
  brightness: word('Light analysis','明るさの分析','亮度分析'),
  viewNote: word('Open a plate to read the full image and source.','図版を開いて画像と出典を確認できます。','打开图板查看大图和来源。'),
  panoCaption: word('Surveyed camera positions. Open a point to see its panorama and recorded heading.','調査した撮影位置。点を開くとパノラマと撮影方向を確認できます。','图示为此前调查的相机位置。点开查看全景与记录朝向。'),
  noWebgl: word('The map is shown in plan. Study charts and source views remain available.',
                '地図は平面表示です。調査の図表と出典は利用できます。',
                '当前使用平面底图。研究图表与原始视图可以继续查看。'),
  bearings: word('North-up plane coordinates · EPSG:6677','北を上とする平面座標・EPSG:6677','上北下南 · 日本平面直角坐标 EPSG:6677'),
  chartSupport: word('Each chart names its sample and measurement window.','図表ごとに対象と計測期間を明記しています。','图表均标明样本及计算时段。'),
  source: word('Source','出典','来源'),
  noData: word('The atlas data are unavailable. Open the Future Vision proposal maps.','データを読み込めません。将来構想の地図を開いてください。','图集数据暂未加载。请查看 Future Vision 提案图。'),
};

function link(title,href,external = false) {
  const anchor = node('a',title);
  anchor.href = offline && href.startsWith('/') ? 'https://kajicho-site-atlas.specialgooood.chatgpt.site'+href : href;
  if (external) {
    anchor.target = '_blank';
    anchor.rel = 'noopener noreferrer';
  }
  return anchor;
}

async function fetchData(name) {
  const response = await fetch('/scenario-atlas/'+name);
  if (!response.ok) throw new Error(name+' HTTP '+response.status);
  return response.json();
}

function brightnessMedia(place) {
  if (!place.brightness) return [];
  const b = place.brightness;
  const source = place.references[0][1];
  const width = 700, height = 409;
  const bg = '#fbf9f6', ink = '#1c1917', muted = '#645d56';
  const dark = '#252d32', mid = '#737d7d', light = '#d4d9d0';
  const shorthand = (key,ja,zh) => localized(word(key,ja,zh));
  function sheet(id,title,caption,illustrate) {
    const paper = document.createElement('canvas');
    paper.width = width;
    paper.height = height;
    const c = paper.getContext('2d');
    c.fillStyle = bg;
    c.fillRect(0,0,width,height);
    c.fillStyle = ink;
    c.font = '600 37px "Studio UI Latin", sans-serif';
    c.fillText(localized(title),38,69);
    c.fillStyle = muted;
    c.font = '24px "Studio UI Latin", sans-serif';
    c.fillText(localized(place.title),38,112);
    illustrate(c);
    return {id,title,caption,source,src:paper.toDataURL(),aspect:width/height,width:176,
            xy:place.center,stack:!place.nativeBrightness,kind:'brightness'};
  }
  const bands = sheet('threshold-bands',word('Walkway darkness','歩道の暗さ','人行区域明暗'),
    word('Measured pixel shares grouped by the two thresholds.','2つのしきい値による画素分類の構成比。',
        '按两条阈值统计原人行选区的像素占比。'),c => {
      const severe = b.severe_darkness_pct, darkOnly = Math.max(0,b.dark_area_pct-severe);
      const values = [severe,darkOnly,100-b.dark_area_pct];
      const colors = [dark,mid,light];
      let x = 39;
      for (let i=0;i<values.length;i++) {
        const w = 6.15 * values[i];
        c.fillStyle = colors[i]; c.fillRect(x,156,w,98); x += w;
      }
      const legend = ["<40%","40–60%","≥60%"];
      values.forEach((value,i) => {
        const x = 39+i*205;
        c.fillStyle = colors[i]; c.fillRect(x,285,21,21);
        c.fillStyle = ink; c.font = '600 27px sans-serif';
        c.fillText(legend[i],x+33,305);
        c.fillStyle = muted; c.font = '24px sans-serif';
        c.fillText(value.toFixed(1)+'%',x,345);
      });
    });
  const p90 = sheet('brightness-percentile',word('Brightest 10%','上位10%の明るさ','第 90 百分位亮度'),
    word('90th percentile of 8-bit grayscale, measured in both areas of the same frame.',
         '同じ画像の2領域で求めた8ビットグレー値の90パーセンタイル。',
         '同帧两个区域分别计算的 8 位灰度第 90 百分位。'),c => {
      const labels = [shorthand('Walkway','歩道','人行区域'),shorthand('Open street','開放街路','开敞路面')];
      [b.p90,b.reference_p90].forEach((v,i) => {
        const y = 178+i*98;
        c.fillStyle = muted;c.font='27px sans-serif'; c.fillText(labels[i],40,y);
        c.fillStyle = '#e3e4dd'; c.fillRect(40,y+22,615,23);
        c.fillStyle = i ? '#76928b' : '#324947'; c.fillRect(40,y+22,615*v/255,23);
        c.fillStyle = ink;c.font='600 27px sans-serif'; c.fillText(v.toFixed(0)+' / 255',536,y);
      });
    });
  return [bands,p90];
}

const stored = document.querySelector('#atlas-local-data');
const [geography,content] = stored ? JSON.parse(stored.textContent) :
  await Promise.all([fetchData('geography.json'),fetchData('content.json')]).catch(error => {
  select('.atlas-note').textContent = localized(copy.noData);
  console.error(error);
  return [null,null];
});

if (geography && content) {
  const query = new URLSearchParams(location.search);
  let topic = content.topics.find(item=>item.id===query.get('theme')) ?? content.topics[0];
  let place = topic.places.find(item=>item.id===query.get('place')) ?? topic.places[0];
  let projection = query.get('view') === 'plan' ? 'plan' : 'axon';
  let exploded = true;
  let view = null;
  let showingFallback = false;
  const viewButtons = [...root.querySelectorAll('[data-view]')];
  const controls = [...root.querySelectorAll('.atlas-toolbar button')];
  const dialog = select('.atlas-dialog');
  const dialogBody = select('.atlas-dialog-body');
  const dialogCaption = select('.atlas-dialog-caption');

  function showPano(pano) {
    select('#atlas-dialog-title').textContent = localized(pano.title);
    select('[data-dialog-kind]').textContent = localized(copy.panorama);
    const href = link(localized(copy.external),pano.url,true);
    const data = node('p',`${pano.date} · ${Number(pano.heading).toFixed(1)}°`,'site-caption');
    if (pano.embed) {
      const frame = node('iframe');
      frame.src = pano.embed;
      frame.title = localized(pano.title);
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      dialogBody.replaceChildren(frame,data,href);
    } else {
      dialogBody.replaceChildren(data,href);
    }
    dialogCaption.textContent = localized(copy.panoNote);
    dialog.showModal();
  }

  function openPhoto(item) {
    select('#atlas-dialog-title').textContent = localized(item.title);
    select('[data-dialog-kind]').textContent = localized(copy[item.kind] || copy.panoPrivacy);
    const image = node('img');
    image.src = item.src;
    image.alt = localized(item.title);
    dialogBody.replaceChildren(image);
    if (item.kind === 'mask') {
      const legend = node('ul',null,'atlas-mask-key');
      const categories = [
        ['#af8270',word('Building','建物','建筑')],['#43b5e4',word('Walkable surface','歩行面','步行区域')],
        ['#777786',word('Road','車道','车道')],['#729572',word('Vegetation','植生','植被')],
        ['#d8e5eb',word('Sky','空','天空')],['#aa7fe4',word('People','人','人')],['#f3bd41',word('Road markings','路面表示','路面标线')]
      ];
      for (const [color,label] of categories) {
        const entry=node('li',localized(label)); entry.style.setProperty('--mask-color',color); legend.append(entry);
      }
      dialogBody.append(legend);
    }
    dialogCaption.replaceChildren(document.createTextNode(localized(item.caption)+' · '),
                                  link(localized(copy.source),item.source,!item.source.startsWith('/')));
    if (!dialog.open) dialog.showModal();
  }

  dialog.addEventListener('close',() => dialogBody.replaceChildren());

  function fallback() {
    showingFallback = true;
    controls.forEach(button=>button.disabled=true);
    select('.atlas-status').textContent = localized(copy.noWebgl);
    if (!select('.atlas-fallback-note')) {
      const message = node('p',localized(copy.noWebgl),'site-caption atlas-fallback-note');
      select('.atlas-legend').after(message);
    }
  }

  try {
    view = createAtlasView(stage,geography,{
      marker(data) {
        if (data.pano) showPano(data.pano);
        else if (data.photo) openPhoto(data.photo);
        else if (data.place) choosePlace(data.place);
      },
      photo:openPhoto,
      fallback,
      assetError(url) { console.warn('Atlas image could not load',url); },
    });
  } catch(error) {
    console.warn('Plan fallback',error.message);
    fallback();
  }

  function shareUrl() {
    if (offline) return;
    const url = new URL(location.href);
    url.searchParams.set('theme',topic.id);
    url.searchParams.set('place',place.id);
    if (projection === 'plan') url.searchParams.set('view',projection); else url.searchParams.delete('view');
    history.replaceState(null,'',url);
  }
  function chooseTopic(id) {
    const target = content.topics.find(item=>item.id===id);
    if (target === topic) return;
    topic = target;
    place = topic.places[0];
    render();
    select('.atlas-topics [aria-current="true"]')?.focus({preventScroll:true});
  }
  function choosePlace(id) {
    const target = topic.places.find(item=>item.id===id);
    if (!target || target === place) return;
    place = target;
    render();
    select('.atlas-places [aria-pressed="true"]')?.focus({preventScroll:true});
  }

  function mapChart(measure) {
    const chart = select('.atlas-chart');
    const title = node('h3',localized(measure.title));
    const note = node('p',localized(measure.note),'site-caption');
    const list = node('ul',null,'atlas-chart-list');
    for (const item of measure.rows) {
      const row = node('li',null,'atlas-chart-row');
      const label = node('span',localized(item.label));
      const n = Intl.NumberFormat(document.documentElement.lang,{minimumFractionDigits:measure.decimals,
        maximumFractionDigits:measure.decimals}).format(item.value);
      const unit = localized(measure.unit);
      const value = node('strong',n + (unit === '%' ? unit : ' '+unit));
      const track = node('span',null,'atlas-chart-track');
      const bar = node('i');
      bar.style.width = (Math.min(100,Math.max(0,100*item.value/measure.max)))+'%';
      track.setAttribute('aria-hidden','true');
      track.append(bar);
      row.append(label,value,track);
      list.append(row);
    }
    chart.replaceChildren(title,note,list);
  }

  function buildPanos(panos) {
    const list = node('ul',null,'atlas-panorama-list');
    list.setAttribute('aria-label',localized(copy.panorama));
    for (const pano of panos) {
      const item = node('li');
      const anchor = pano.embed ? node('button',localized(pano.title)) : link(localized(pano.title),pano.url,true);
      if (pano.embed) { anchor.type = 'button'; anchor.addEventListener('click',()=>showPano(pano)); }
      anchor.dataset.panorama = pano.id;
      if (pano.id === place.selectedPano) anchor.setAttribute('aria-current','true');
      item.append(anchor);
      list.append(item);
    }
    return list;
  }

  function buildGallery(media,panos) {
    const wrapper = select('.atlas-media');
    const children = media.map(item => {
      const figure = node('figure');
      const button = node('button',null,'atlas-thumb');
      button.type='button';
      button.setAttribute('aria-label',localized(item.title));
      button.addEventListener('click',()=>openPhoto(item));
      const image = node('img');
      image.src=item.src; image.alt=localized(item.title); image.loading='lazy';
      button.append(image);
      const label=node('figcaption');
      label.append(node('strong',localized(item.title)),node('span',localized(item.caption),'site-caption'),
                   link(localized(copy.source),item.source,!item.source.startsWith('/')));
      figure.append(button,label);
      return figure;
    });
    wrapper.replaceChildren(...children);
    select('.atlas-caption').textContent=localized(panos.length ? copy.panoCaption : copy.viewNote);
    select('.atlas-evidence .atlas-panorama-list')?.remove();
    if (panos.length) wrapper.after(buildPanos(panos));
  }

  function render() {
    shareUrl();
    select('.atlas-topics').replaceChildren(...content.topics.map(item => {
      const button = node('button',localized(item.title));
      button.type='button'; button.dataset.topic=item.id;
      if (item === topic) button.setAttribute('aria-current','true');
      button.addEventListener('click',()=>chooseTopic(item.id));
      return button;
    }));
    viewButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===projection)));
    select('.atlas-kind').textContent=localized(place.kind);
    select('#atlas-selected').textContent=localized(place.title);
    select('.atlas-note').textContent=localized(place.note);

    const places = select('.atlas-places');
    places.hidden=topic.places.length<2;
    places.replaceChildren(...topic.places.map(item => {
      const label = place.panoramaGroup === 'crossings' ? item.id.split('-')[1] : localized(item.title);
      const b=node('button',label);
      b.type='button';b.dataset.place=item.id;
      b.setAttribute('aria-pressed',String(item===place));
      b.setAttribute('aria-label',localized(item.title));
      b.addEventListener('click',()=>choosePlace(item.id));
      return b;
    }));
    mapChart(place.chart);
    const panos=content.panoramas.filter(p=>p.group === place.panoramaGroup);
    const selectedPano=panos.find(p=>p.id === place.selectedPano);
    const sourceLinks = [link(localized(copy.cases),place.visionLink),
                       ...place.references.map(([label,url])=>link(localized(label),url,true))];
    if (selectedPano) {
      if (selectedPano.embed) {
        const b=node('button',localized(copy.panorama),'atlas-open-pano');
        b.type='button'; b.addEventListener('click',()=>showPano(selectedPano)); sourceLinks.unshift(b);
      } else sourceLinks.unshift(link(localized(copy.external),selectedPano.url,true));
    }
    select('.atlas-read-links').replaceChildren(...sourceLinks);
    const media=[...place.media,...brightnessMedia(place)];
    const activePin={xy:place.center, label:localized(place.title),active:true,place:place.id};
    const markers=[activePin];
    for (const p of panos) {
      if (selectedPano && p.id===selectedPano.id) { activePin.pano=selectedPano; continue; }
      markers.push({xy:p.xy,label:localized(p.title),pano:p,dot:true});
    }
    for (const extra of place.extraPins??[]) markers.push({xy:extra.xy,label:localized(extra.title),photo:media[1]});
    if (place.panoramaGroup !== 'crossings') {
      for (const item of topic.places) if(item!==place)
        markers.push({xy:item.center,label:localized(item.title),place:item.id});
    }
    const paths=place.features.flatMap(id=>geography.features[id]?.paths??[]);
    if (view) view.update({center:place.center,span:place.span,paths,markers,media:media.filter(item=>item.stack),
                           ink:topic.id==='crossings'?'#47645f':undefined});
    buildGallery(media,panos);
    select('.atlas-status').textContent=showingFallback?localized(copy.noWebgl):localized(place.title);
    for (const el of root.querySelectorAll('.atlas-fallback-note')) el.textContent=localized(copy.noWebgl);
    const links=content.mapSources.map(([label,href]) => {
      const p=node('p');
      p.append(link(localized(label),href,!href.startsWith('/')));
      return p;
    });
    select('.atlas-source-grid').replaceChildren(node('p',localized(copy.bearings)),node('p',localized(copy.chartSupport)),...links);
  }

  for (const b of viewButtons) b.addEventListener('click',() => {
    projection=b.dataset.view;
    view?.view(projection);
    viewButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===projection)));
    shareUrl();
  });
  select('[data-spread]').addEventListener('click',e=>{
    exploded=!exploded;
    e.currentTarget.setAttribute('aria-pressed',String(exploded));
    view?.spread(exploded);
  });
  root.querySelectorAll('[data-scale]').forEach(b=>b.addEventListener('click',()=>view?.zoom(Number(b.dataset.scale))));
  select('[data-reset]').addEventListener('click',()=>view?.reset());
  if (projection==='plan') view?.view(projection);
  new MutationObserver(()=>{
    const lang=document.documentElement.lang.slice(0,2);
    if (lang!==language) {language=lang;render();}
  }).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  render();
}
