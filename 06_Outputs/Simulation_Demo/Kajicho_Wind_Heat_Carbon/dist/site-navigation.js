/* Global pages, parent location and sibling routes; section links live in page-outline. */
const vocabulary={
 en:{atlas:'Atlas',research:'Research review',studies:'Studies',team:'Team desk',parameters:'Current 3D model',plan:'Work plan',cfd:'CFD diagnostics',visit:'Sunday visit',style:'Type & maps',home:'Kajicho',local:'Sections on this page: use the left outline',global:'Main pages',location:'You are here',siblings:'Pages in this section',siblingsLabel:'Pages in this section',contents:'On this page'},
 zh:{atlas:'场地图集',research:'研究综述',studies:'模拟研究',team:'团队工作台',parameters:'当前三维模型',plan:'工作计划',cfd:'CFD 诊断',visit:'周日调研',style:'字体与图纸',home:'鍛冶町',local:'本页章节见左侧目录',global:'全站栏目',location:'当前位置',siblings:'本栏目页面',siblingsLabel:'本栏目页面',contents:'本页目录'},
 ja:{atlas:'敷地アトラス',research:'研究レビュー',studies:'シミュレーション',team:'チームデスク',parameters:'現在の3D模型',plan:'作業計画',cfd:'CFD診断',visit:'日曜調査',style:'文字と地図',home:'鍛冶町',local:'ページ内の章は左の目次へ',global:'全体メニュー',location:'現在地',siblings:'同じ区分のページ',siblingsLabel:'同じ区分',contents:'このページ'}
};
function refreshGlobalNavigation(){
 const lang=document.documentElement.lang.startsWith('zh')?'zh':document.documentElement.lang.startsWith('ja')?'ja':'en',w=vocabulary[lang];
 document.querySelectorAll('.site-languages [data-lang]').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.lang===lang));b.classList.toggle('active',b.dataset.lang===lang);});
 document.querySelectorAll('[data-site-label]').forEach(el=>el.textContent=w[el.dataset.siteLabel]);
 document.querySelector('.site-global-nav')?.setAttribute('aria-label',w.global);
 document.querySelector('.site-breadcrumb')?.setAttribute('aria-label',w.location);
 document.querySelector('.site-siblings')?.setAttribute('aria-label',w.siblings);
}
refreshGlobalNavigation();
new MutationObserver(refreshGlobalNavigation).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
