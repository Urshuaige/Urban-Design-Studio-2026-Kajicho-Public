/* Interactive mechanism diagrams. Geometry is presentational; every edge retains sources. */
export function mountGraphExplorer(root,{data,content,lang,state={}}) {
 const L={en:{title:'How renewal works',intro:'Follow one relationship at a time. Select a node to see its links, role and evidence.',reset:'Show all connections',details:'Open supporting detail',links:'Connected roles and steps',sources:'Evidence for this node',edgeSources:'Evidence for this connection',legend:'Recorded relationship',consult:'Consultation / later route',money:'Funding',current:'Current in the handout · 25 Oct 2026',future:'Later step in the described route',hint:'Select a box or a labelled connection. Scroll the diagram sideways on a narrow screen.',all:'All connections',selected:'Selected',stage:'Process position',prev:'Previous step',next:'Next step'},zh:{title:'更新如何运作',intro:'一次看清一组关系。选择节点，查看它连接谁、承担什么角色，以及依据在哪里。',reset:'显示全部关系',details:'展开详细依据',links:'相连的角色与步骤',sources:'节点依据',edgeSources:'连线依据',legend:'材料记录的关系',consult:'协商／后续路径',money:'资金',current:'讲义标注的当前位置 · 2026 年 10 月 25 日',future:'所述路径的后续环节',hint:'点击节点或带文字的连线；窄屏可左右滚动关系图。',all:'全部关系',selected:'已选择',stage:'流程位置',prev:'上一步',next:'下一步'},ja:{title:'更新の仕組み',intro:'一つずつ関係をたどる。ノードを選ぶと接続先・役割・根拠を表示する。',reset:'全ての関係を表示',details:'詳細資料を開く',links:'つながる主体・段階',sources:'ノードの根拠',edgeSources:'接続の根拠',legend:'資料にある関係',consult:'協議・後続手続',money:'資金',current:'資料の現在地 · 2026年10月25日',future:'説明上の後続段階',hint:'ノードまたは接続の文字を選択。狭い画面では図を横にスクロールできる。',all:'全ての関係',selected:'選択中',stage:'手続の位置',prev:'前の段階',next:'次の段階'}}[lang];
 const str=x=>typeof x==='object'&&x!==null?(x[lang]||x.en||''):String(x??'');
 const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const t=x=>esc(str(x));
 const refs=ids=>'<ul class="fg-sources">'+[...new Set(ids)].map(id=>{const s=content.sources.find(s=>s.id===id);return '<li><a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+t(s.title)+' ↗</a></li>'}).join('')+'</ul>';
 let active=data.graphs.some(g=>g.id===state.active)?state.active:data.graphs[0].id,selected=null,selectedEdge=null,observer;
 root.innerHTML='<div class="fg-intro"><p class="kicker">RELATIONSHIPS / PROCESS</p><h2 id="how-renewal-works">'+L.title+'</h2><p>'+L.intro+'</p></div><div class="fg-tabs" role="tablist" aria-label="'+L.title+'">'+data.graphs.map((g,i)=>'<button type="button" role="tab" data-graph-tab="'+g.id+'" aria-controls="graph-panel" id="tab-'+g.id+'" tabindex="'+(i?'-1':'0')+'">'+String(i+1).padStart(2,'0')+' <span>'+t(g.title)+'</span></button>').join('')+'</div><div id="graph-panel" role="tabpanel"></div>';
 const panel=root.querySelector('#graph-panel');
 function current(){return data.graphs.find(g=>g.id===active)}
 function jump(id){const target=document.getElementById(id);if(!target)return;for(let p=target.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;target.scrollIntoView?.({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'start'});history.replaceState(null,'','#'+id);}
 function draw(){
  const g=current(),board=root.querySelector('.fg-board'),svg=root.querySelector('.fg-lines');if(!board||!svg)return;
  const br=board.getBoundingClientRect(),width=br.width||1000;
  svg.setAttribute('viewBox','0 0 '+width+' '+g.height);
  function box(n){const el=board.querySelector('[data-node="'+n.id+'"]'),r=el.getBoundingClientRect();return r.width&&r.height?{x:r.left-br.left,y:r.top-br.top,w:r.width,h:r.height}:{x:n.x/1000*width,y:n.y,w:(n.width||230)/1000*width,h:110}}
  let paths='<defs><marker id="fg-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#80708d"/></marker></defs>';
  g.edges.forEach((e,i)=>{
   const a=box(g.nodes.find(n=>n.id===e.source)),b=box(g.nodes.find(n=>n.id===e.target));
   const ac={x:a.x+a.w/2,y:a.y+a.h/2},bc={x:b.x+b.w/2,y:b.y+b.h/2};let p,q,d,m;
   if(e.via==='left'){
    p={x:a.x,y:ac.y};q={x:b.x,y:bc.y};const bend=Math.min(a.x,b.x)-95;d=`M${p.x},${p.y} H${bend} V${q.y} H${q.x}`;m={x:bend,y:(p.y+q.y)/2};
   }else if(Math.abs(ac.x-bc.x)<30){
    const down=bc.y>ac.y;p={x:ac.x,y:down?a.y+a.h:a.y};q={x:bc.x,y:down?b.y:b.y+b.h};d=`M${p.x},${p.y} L${q.x},${q.y}`;m={x:p.x,y:(p.y+q.y)/2};
   }else{
    const right=bc.x>ac.x;p={x:right?a.x+a.w:a.x,y:ac.y};q={x:right?b.x:b.x+b.w,y:bc.y};
    const mid=(p.x+q.x)/2;d=`M${p.x},${p.y} C${mid},${p.y} ${mid},${q.y} ${q.x},${q.y}`;m={x:mid,y:(p.y+q.y)/2};
   }
   const dim=(selected&&!([e.source,e.target].includes(selected)))||(selectedEdge!==null&&selectedEdge!==i);
   const label=str(e.label),lw=Math.min(175,Math.max(48,[...label].reduce((v,c)=>v+(c.charCodeAt(0)>255?12:6.4),18)));
   paths+='<g class="fg-edge '+e.kind+(dim?' is-dim':'')+'" data-edge="'+i+'"><path class="fg-edge-line" d="'+d+'" marker-end="url(#fg-arrow)"/><g role="button" tabindex="0" aria-label="'+esc(str(g.nodes.find(n=>n.id===e.source).label)+' → '+label+' → '+str(g.nodes.find(n=>n.id===e.target).label))+'" data-edge-button="'+i+'"><rect x="'+(m.x-lw/2)+'" y="'+(m.y-12)+'" width="'+lw+'" height="24" rx="4"/><text x="'+m.x+'" y="'+(m.y+4)+'" text-anchor="middle">'+esc(label)+'</text></g></g>';
  });svg.innerHTML=paths;
  svg.querySelectorAll('[data-edge-button]').forEach(b=>{const run=()=>selectEdge(Number(b.dataset.edgeButton));b.addEventListener('click',run);b.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();run()}})});
 }
 function highlight(){
  const g=current(),near=new Set(selected?[selected]:g.nodes.map(n=>n.id));
  if(selected)g.edges.filter(e=>e.source===selected||e.target===selected).forEach(e=>{near.add(e.source);near.add(e.target)});
  if(selectedEdge!==null){near.clear();near.add(g.edges[selectedEdge].source);near.add(g.edges[selectedEdge].target)}
  root.querySelectorAll('[data-node]').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.node===selected));b.classList.toggle('is-dim',!near.has(b.dataset.node));});draw();
 }
 function nodeLink(n){return '<button type="button" data-select="'+n.id+'">'+t(n.label)+'</button>'}
 function selectNode(id,focus=false){
  const g=current(),n=g.nodes.find(n=>n.id===id);selected=id;selectedEdge=null;state.active=active;state.selected=id;
  const connections=g.edges.map((e,i)=>({e,i})).filter(({e})=>e.source===id||e.target===id);
  root.querySelector('.fg-inspector').innerHTML='<p class="kicker">'+(n.kind==='current'?L.current:n.kind==='future'?L.future:L.selected)+'</p><h3>'+t(n.label)+'</h3>'+(n.subtitle?'<p class="small">'+t(n.subtitle)+'</p>':'')+'<p>'+t(n.body)+'</p>'+(n.note?'<p class="fg-caution">'+t(n.note)+'</p>':'')+'<h4>'+L.links+'</h4><ul class="fg-connections">'+connections.map(({e,i})=>'<li><button type="button" data-select-edge="'+i+'">'+t(g.nodes.find(x=>x.id===e.source).label)+' <span>→ '+t(e.label)+' →</span> '+t(g.nodes.find(x=>x.id===e.target).label)+'</button></li>').join('')+'</ul><h4>'+L.sources+'</h4>'+refs(n.refs)+(n.link?'<button class="fg-detail-link" type="button" data-detail="'+n.link+'">'+L.details+' ↘</button>':'');
  bindInspector();highlight();
  if(focus){const b=root.querySelector('[data-node="'+id+'"]');b.focus({preventScroll:true});b.scrollIntoView?.({block:'nearest',inline:'nearest',behavior:'auto'});}
 }
 function selectEdge(i){const g=current(),e=g.edges[i];selected=null;selectedEdge=i;state.active=active;state.selected=null;
  root.querySelector('.fg-inspector').innerHTML='<p class="kicker">'+L.links+'</p><h3>'+t(e.label)+'</h3><div class="fg-edge-route">'+nodeLink(g.nodes.find(n=>n.id===e.source))+'<span aria-hidden="true">↓</span>'+nodeLink(g.nodes.find(n=>n.id===e.target))+'</div><p class="small">'+t(g.note)+'</p><h4>'+L.edgeSources+'</h4>'+refs(e.refs);bindInspector();highlight();}
 function bindInspector(){root.querySelectorAll('[data-select]').forEach(b=>b.onclick=()=>selectNode(b.dataset.select,true));root.querySelectorAll('[data-select-edge]').forEach(b=>b.onclick=()=>selectEdge(Number(b.dataset.selectEdge)));root.querySelectorAll('[data-detail]').forEach(b=>b.onclick=()=>jump(b.dataset.detail));}
 function render(){
  const g=current();selected=state.active===active&&g.nodes.some(n=>n.id===state.selected)?state.selected:g.default;selectedEdge=null;
  root.querySelectorAll('[data-graph-tab]').forEach(b=>{const on=b.dataset.graphTab===active;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;});
  panel.setAttribute('aria-labelledby','tab-'+g.id);
  panel.innerHTML='<div class="fg-heading"><div><h3 data-outline-ignore>'+t(g.question)+'</h3><p>'+t(g.summary)+'</p></div><button type="button" class="fg-reset">'+L.reset+'</button></div><p class="fg-hint">'+L.hint+'</p><div class="fg-layout"><div class="fg-chart"><div class="fg-scroll" tabindex="0" role="region" aria-label="'+t(g.title)+'"><div class="fg-board" style="height:'+g.height+'px"><svg class="fg-lines" xmlns="http://www.w3.org/2000/svg" aria-label="'+L.links+'"></svg>'+g.nodes.map(n=>'<button type="button" class="fg-node '+n.kind+'" data-node="'+n.id+'" style="left:'+n.x/10+'%;top:'+n.y+'px;width:'+(n.width||230)/10+'%" aria-controls="graph-inspector" aria-pressed="false">'+(n.kind==='current'?'<small class="fg-now">'+(lang==='zh'?'讲义当前位置':lang==='ja'?'資料の現在地':'CURRENT IN HANDOUT')+'</small>':n.kind==='future'?'<small>'+L.future+'</small>':n.subtitle?'<small>'+t(n.subtitle)+'</small>':'')+'<strong>'+t(n.label)+'</strong></button>').join('')+'</div></div><div class="fg-legend"><span>'+L.legend+'</span><span class="dash">'+L.consult+'</span><span class="money">'+L.money+'</span></div><p class="small fg-note">'+t(g.note)+'</p></div><aside id="graph-inspector" class="fg-inspector" data-outline-ignore aria-live="polite"></aside></div>';
  root.querySelectorAll('[data-node]').forEach(b=>b.onclick=()=>selectNode(b.dataset.node));
  root.querySelector('.fg-reset').onclick=()=>{selected=null;selectedEdge=null;root.querySelector('.fg-inspector').innerHTML='<p class="kicker">'+L.all+'</p><h3>'+t(g.question)+'</h3><p>'+L.intro+'</p>'+refs(g.edges.flatMap(e=>e.refs));highlight();};
  selectNode(selected);
  if(observer)observer.disconnect();if(typeof ResizeObserver!=='undefined'){observer=new ResizeObserver(()=>draw());observer.observe(root.querySelector('.fg-board'));}
  requestAnimationFrame(draw);
 }
 const tabs=[...root.querySelectorAll('[data-graph-tab]')];tabs.forEach((b,i)=>{b.onclick=()=>{active=b.dataset.graphTab;state.selected=null;render()};b.onkeydown=e=>{let j=i;if(e.key==='ArrowRight')j=(i+1)%tabs.length;else if(e.key==='ArrowLeft')j=(i+tabs.length-1)%tabs.length;else if(e.key==='Home')j=0;else if(e.key==='End')j=tabs.length-1;else return;e.preventDefault();tabs[j].click();tabs[j].focus();}});
 render();return ()=>observer?.disconnect();
}
