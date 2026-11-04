const pick=(v,lang)=>typeof v==='string'?v:(v?.[lang]||v?.en||'');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const currentLang=()=>document.documentElement.lang.startsWith('zh')?'zh':document.documentElement.lang.startsWith('ja')?'ja':'en';
const labels={
 en:{output:'First output',check:'Check before moving on',data:'Data',reuse:'Reuse after checking',rebuild:'Rebuild or collect',task:'Task',grid:'Starting grid',reason:'How to choose',note:'These lengths are proposed starts, not a universal accuracy standard.',methods:'Technical methods and sources ↗',review:'Existing integrative review ↗',model:'Inspect the current 3D model →',plan:'Read the work plan →',legacy:'Historical CFD diagnostics →',full:'Full report and source registry on GitHub ↗',update:'20 OCTOBER 2026 / NEXT STUDIO WORK',les:'The 2026 AIJ LES guideline is verified in publisher metadata; its full numerical prescriptions still need reading before a LES plan.'},
 zh:{output:'第一项交付',check:'进入下一步前检查',data:'资料',reuse:'核对后复用',rebuild:'需要重建或补查',task:'工作',grid:'起始网格',reason:'选择依据',note:'这些尺度是建议起点，不是通用精度标准。',methods:'技术方法与依据 ↗',review:'已有整合性综述 ↗',model:'检查当前三维模型 →',plan:'阅读工作计划 →',legacy:'历史 CFD 诊断 →',full:'GitHub 完整说明与来源记录 ↗',update:'2026 年 10 月 20 日 / 后续研究',les:'2026 年 AIJ LES 指南已核实出版信息；制定 LES 数值方案前仍需阅读其完整方法。'},
 ja:{output:'最初の成果',check:'次に進む前の確認',data:'データ',reuse:'確認して再利用',rebuild:'再構築・追加調査',task:'作業',grid:'開始格子',reason:'選び方',note:'提案する開始値であり、一般的な精度基準ではない。',methods:'技術手法と根拠 ↗',review:'既存の統合的レビュー ↗',model:'現在の3D模型を見る →',plan:'作業計画を読む →',legacy:'過去のCFD診断 →',full:'GitHubの詳細資料と出典記録 ↗',update:'2026年10月20日 / 次の調査',les:'2026年AIJ LES指針は出版情報を確認済み。LES計画の前に数値手法の全文を読む必要がある。'}
};
const root=document.querySelector('[data-work-plan]');
let plan,sources;
function render(){
 if(!plan||!root)return;
 const l=currentLang(),w=labels[l],p=v=>esc(pick(v,l)),h=plan.headings;
 root.innerHTML='<section class="work-hero" id="overview"><div><p class="work-kicker">'+w.update+'</p><h1>'+p(plan.title)+'</h1><p>'+p(plan.intro)+'</p></div><aside class="work-scope"><p>'+p(plan.scope)+'</p><a href="studies.html">'+w.model+'</a></aside></section><p class="work-status">'+p(plan.status)+'</p>'+
 '<section class="work-section" id="sequence"><h2>'+p(h.stages)+'</h2><ol class="work-flow">'+plan.stages.map((s,i)=>'<li><a href="#stage-'+s.id+'"><b>0'+(i+1)+'</b>'+p(s.title)+'</a></li>').join('')+'</ol><div class="work-stage-grid">'+plan.stages.map((s,i)=>'<article class="work-card" id="stage-'+s.id+'"><small>0'+(i+1)+'</small><h3>'+p(s.title)+'</h3><p>'+p(s.body)+'</p><dl><dt>'+w.output+'</dt><dd>'+p(s.output)+'</dd><dt>'+w.check+'</dt><dd>'+p(s.check)+'</dd></dl></article>').join('')+'</div></section>'+
 '<section class="work-section" id="data"><h2>'+p(h.reuse)+'</h2><div class="work-table-wrap" tabindex="0" aria-label="'+p(h.reuse)+'"><table class="work-table"><thead><tr><th>'+w.data+'</th><th>'+w.reuse+'</th><th>'+w.rebuild+'</th></tr></thead><tbody>'+plan.reuse.map(row=>'<tr>'+row.map(v=>'<td>'+p(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div></section>'+
 '<section class="work-section" id="resolution"><h2>'+p(h.resolution)+'</h2><span class="work-label">'+p(h.proposal)+'</span><p>'+w.note+'</p><div class="work-table-wrap" tabindex="0" aria-label="'+p(h.resolution)+'"><table class="work-table"><thead><tr><th>'+w.task+'</th><th>'+w.grid+'</th><th>'+w.reason+'</th></tr></thead><tbody>'+plan.resolution.map(row=>'<tr>'+row.map(v=>'<td>'+p(v)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div><p style="margin-top:22px">'+w.les+'</p></section>'+
 '<section class="work-section" id="validation"><h2>'+p(h.verify)+'</h2><ol class="work-checks">'+plan.checks.map(v=>'<li>'+p(v)+'</li>').join('')+'</ol></section>'+
 '<section class="work-section" id="discussion"><h2>'+p(h.meeting)+'</h2><div class="work-questions">'+plan.meeting.map(v=>'<article class="work-question"><p>'+p(v)+'</p></article>').join('')+'</div><p style="margin-top:28px">'+p(plan.twin)+'</p></section>'+
 '<section class="work-section" id="sources"><h2>'+p(h.sources)+'</h2><div class="work-links"><a href="https://github.com/Urshuaige/Urban-Design-Studio-2026-Kajicho/blob/main/docs/Environmental_Work_Plan_2026-10-20/METHODS.md">'+w.methods+'</a><a href="research.html">'+w.review+'</a><a href="cfd.html">'+w.legacy+'</a></div><ul class="work-sources">'+sources.map(s=>'<li><a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(s.title)+' ↗</a><small>'+esc(s.year||'')+' · '+esc(s.locators.join('; '))+' · '+esc(s.read_scope)+'</small></li>').join('')+'</ul></section>';
}
if(document.body.hasAttribute('data-work-page')){
 let saved;try{saved=localStorage.getItem('kajicho-language-20261017');}catch{}
 document.documentElement.lang=['en','zh','ja'].includes(saved)?saved:'en';
 document.querySelectorAll('.site-languages [data-lang]').forEach(b=>b.addEventListener('click',()=>{
  document.documentElement.lang=b.dataset.lang;try{localStorage.setItem('kajicho-language-20261017',b.dataset.lang);}catch{}
 }));
}
if(root){
 Promise.all([fetch('work-plan.json?v=20261020').then(r=>{if(!r.ok)throw Error(r.status);return r.json()}),fetch('work-plan-sources.json?v=20261020').then(r=>r.json())]).then(([p,s])=>{plan=p;sources=s;render();root.dataset.ready='true'}).catch(e=>{root.textContent='The work plan could not load. Open the technical report on GitHub.';console.error(e)});
 new MutationObserver(render).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
}
export {currentLang,pick,esc};

const nextWords={en:{title:'Next studio work',cleanup:'20 October: obsolete native CFD fields and meshes removed. Retained teaching snapshots remain unconverged.',cleanupLink:'Cleanup record ↗',plan:'Fieldwork, heat and CFD work plan →',model:'Current LOD2 model →'},zh:{title:'后续研究',cleanup:'10 月 20 日：过时 CFD 原生场与网格已清理；保留的教学快照仍未收敛。',cleanupLink:'清理记录 ↗',plan:'场地调研、热环境与 CFD 工作计划 →',model:'当前 LOD2 模型 →'},ja:{title:'次の調査',cleanup:'10月20日：古いCFD場・格子を削除。保持した教材スナップショットは未収束。',cleanupLink:'削除記録 ↗',plan:'現地・熱環境・CFDの作業計画 →',model:'現在のLOD2模型 →'}};
function nextLabels(){const w=nextWords[currentLang()];document.querySelectorAll('[data-next-label]').forEach(n=>n.textContent=w[n.dataset.nextLabel]);}
nextLabels();new MutationObserver(nextLabels).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
