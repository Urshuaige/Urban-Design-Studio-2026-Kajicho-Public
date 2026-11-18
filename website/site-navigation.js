/* Public atlas navigation. The reading outline is shared with the Personal Site. */
const words={
 en:{studio:'Studio',studioDate:'18 November 2026 · Interim review',studioTitle:'Between the Centers',studioIntro:'Follow six studio studies through Kajicho’s buildings, climate and streets.',studioAction:'Explore the studio exhibition →',visit:'Field visit',atlas:'Atlas',history:'History',policy:'Policy',conditions:'Site data',home:'Urban Design Studio 2026',global:'Main pages',location:'You are here',local:'Sections on this page: use the left outline',skip:'Skip to content'},
 zh:{studio:'设计成果',studioDate:'2026年11月18日 · 中期汇报',studioTitle:'Between the Centers',studioIntro:'从六位组员的研究出发，了解鍛冶町的建筑、气候与街道。',studioAction:'浏览设计成果 →',visit:'调研与更新',atlas:'场地图集',history:'历史脉络',policy:'政策资料',conditions:'现状资料',home:'Urban Design Studio 2026',global:'全站栏目',location:'当前位置',local:'本页章节见左侧目录',skip:'跳到正文'},
 ja:{studio:'スタジオ',studioDate:'2026年11月18日 · 中間発表',studioTitle:'Between the Centers',studioIntro:'6人のスタジオ研究を通して、鍛冶町の建物、気候、街路を読み解きます。',studioAction:'スタジオの成果を見る →',visit:'現地調査',atlas:'敷地アトラス',history:'歴史',policy:'政策資料',conditions:'現況資料',home:'Urban Design Studio 2026',global:'全体メニュー',location:'現在地',local:'ページ内の章は左の目次へ',skip:'本文へ移動'}
};
function refreshGlobalNavigation(){
 const lang=document.documentElement.lang.startsWith('zh')?'zh':document.documentElement.lang.startsWith('ja')?'ja':'en',w=words[lang];
 document.querySelectorAll('[data-site-label]').forEach(el=>{const text=w[el.dataset.siteLabel];if(text)el.textContent=text;});
 document.querySelectorAll('.site-languages [data-lang]').forEach(button=>{button.setAttribute('aria-pressed',String(button.dataset.lang===lang));button.classList.toggle('active',button.dataset.lang===lang);});
 document.querySelector('.site-global-nav')?.setAttribute('aria-label',w.global);
 document.querySelector('.site-breadcrumb')?.setAttribute('aria-label',w.location);
}
refreshGlobalNavigation();
new MutationObserver(refreshGlobalNavigation).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
