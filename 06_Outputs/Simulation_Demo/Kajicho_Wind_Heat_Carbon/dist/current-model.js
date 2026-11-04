import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';
import {currentLang,pick,esc} from './work-plan.js';
const vocab={
 en:{kicker:'CURRENT SITE MODEL / 20 OCTOBER 2026',title:'Read the roofs and streets',intro:'Original PLATEAU LOD2 roofs and walls, matched to the current Figure 5 inventory. No textures.',scope:'1,074 wider-area objects / 277 primary objects. Source IDs and the reporting outlines remain unchanged.',plan:'Read the next work plan →',model:'Current geometry',overview:'Overview',top:'Top view',primary:'Primary area',reset:'Reset view',only:'Primary objects only',legend:'Purple: primary objects. Grey: wider-area objects. Neutral display lighting.',controls:'Drag to rotate · scroll or pinch to zoom · click a building to inspect',precision:'LOD is geometric detail. Original source elevations are retained; terrain, trees and canopies need separate checks.',select:'Select a building to inspect its source geometry.',nextTitle:'Use this model to prepare the next question',nextBody:'The detailed scene supports geometry review. Shade occluders and CFD solids are prepared separately from the same source IDs. Historical simulated fields retain their original geometry.',archive:'Historical CFD diagnostics →',review:'Research review →',sources:'Source and geometry record',objects:'current model objects',lod:'actual LOD2 coverage',triangles:'source triangles',ready:'Current source geometry ready · display only',sourceId:'Source IDs and reproduction',height:'Geometry height',sourceHeight:'Source measured height',area:'Area',wider:'Wider area',use:'Source use',focus:'Focus on building',record:'Geometry and processing record',license:'License and attribution',modelYear:'Model release',surveyYear:'Use survey',sourceDate:'Source creation',note:'Official delivery catalogue checked on 20 October 2026: no higher LOD3/4 data resolved for these two wards. Every selected object uses its original CityGML LOD2 surfaces.',error:'The 3D scene could not load. The geometry record and work plan remain available below.'},
 zh:{kicker:'当前场地模型 / 2026 年 10 月 20 日',title:'看清屋顶与街道',intro:'读取 PLATEAU 原始 LOD2 屋顶和墙面，对应当前 Figure 5 建筑清单，无贴图。',scope:'外围 1,074 个对象，重点区 277 个。源 ID 和统计边线保持一致。',plan:'阅读后续工作计划 →',model:'当前几何',overview:'总览',top:'顶视图',primary:'重点区',reset:'重置视角',only:'只显示重点区对象',legend:'紫色：重点区对象；灰色：外围区对象。采用中性展示光照。',controls:'拖动旋转 · 滚轮或双指缩放 · 点击建筑查看',precision:'LOD 表示几何细节。保留源高程；地形、树木和雨棚仍需分别核对。',select:'点击建筑，查看其源几何信息。',nextTitle:'用这个模型准备下一步问题',nextBody:'精细场景用于几何核对。遮阴遮挡面与 CFD 实体按同一源 ID 单独准备。历史数值场保留其原始几何。',archive:'历史 CFD 诊断 →',review:'研究综述 →',sources:'来源与几何记录',objects:'当前模型对象',lod:'实际 LOD2 覆盖',triangles:'源三角面',ready:'当前源几何已载入 · 仅作展示',sourceId:'源 ID 与复现',height:'几何高度',sourceHeight:'源记录实测高度',area:'范围',wider:'外围区',use:'源用途',focus:'聚焦此建筑',record:'几何与处理记录',license:'许可与署名',modelYear:'模型发布',surveyYear:'用途调查',sourceDate:'源数据生成',note:'2026 年 10 月 20 日核对官方分发目录：两区均未解析到更高的 LOD3／4 数据。所有选定对象都使用其原始 CityGML LOD2 表面。',error:'三维场景未能载入，下方几何记录与工作计划仍可访问。'},
 ja:{kicker:'現在の敷地模型 / 2026年10月20日',title:'屋根と街路を読む',intro:'現在の図5建物台帳に対応するPLATEAUの元LOD2屋根・壁面。テクスチャなし。',scope:'周辺1,074モデル、重点277モデル。元IDと集計境界は維持。',plan:'次の作業計画を読む →',model:'現在の形状',overview:'全体',top:'上面',primary:'重点区域',reset:'視点を戻す',only:'重点区域のみ表示',legend:'紫：重点建物。灰：周辺建物。表示用の中立照明。',controls:'ドラッグで回転・ホイールやピンチで拡大・建物クリックで確認',precision:'LODは形状の詳細度。元の高さを保持し、地形・樹木・庇は別途確認。',select:'建物を選ぶと元の形状情報を確認できます。',nextTitle:'次の問いを準備する模型',nextBody:'詳細模型で形状を確認。日陰の遮蔽物とCFDソリッドは同じ元IDから別途作成。過去の計算場は元の形状を維持。',archive:'過去のCFD診断 →',review:'研究レビュー →',sources:'出典と形状記録',objects:'現在のモデル数',lod:'実際のLOD2対応',triangles:'元の三角面',ready:'現在の形状を読込済み・表示用',sourceId:'元IDと再現',height:'形状高さ',sourceHeight:'元の実測高さ',area:'区域',wider:'周辺区域',use:'元の用途',focus:'建物に注目',record:'形状と処理記録',license:'利用条件と出典',modelYear:'公開モデル',surveyYear:'用途調査',sourceDate:'元データ作成',note:'2026年10月20日に公式配信を確認。両区のLOD3・4は該当なし。全対象で元CityGMLのLOD2面を使用。',error:'3D模型を読み込めませんでした。下の形状記録と作業計画をご覧ください。'}
};
let summary,index,selected=null,selectedMesh=null,sceneModel,currentView='overview';
const viewer=document.querySelector('#current-scene'),status=document.querySelector('#model-status');
let renderer,scene,camera,controls,overallBox,primaryBox;
const meshes=[],raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
function words(){return vocab[currentLang()]}
function translate(){
 const w=words();document.querySelectorAll('[data-model-i18n]').forEach(n=>n.textContent=w[n.dataset.modelI18n]);
 if(summary){
  document.querySelector('#model-stats').innerHTML=[['1,074',w.objects],['100%',w.lod],[Number(summary.asset.triangles).toLocaleString(),w.triangles]].map(([n,l])=>'<div><strong>'+n+'</strong><span>'+esc(l)+'</span></div>').join('');
  document.querySelector('#geometry-record').innerHTML='<p>'+esc(w.note)+'</p><p>'+esc(w.modelYear)+': 2025 · '+esc(w.surveyYear)+': 2021 · EPSG:6677 · metres</p><p>PLATEAU / MLIT, Chiyoda & Chuo · '+esc(summary.attribution)+'</p><div class="work-links"><a href="current-model/geometry-summary.json">'+esc(w.record)+' ↗</a><a href="'+esc(summary.license_url)+'" target="_blank" rel="noopener">'+esc(w.license)+' ↗</a><a href="'+esc(summary.source_documentation)+'" target="_blank" rel="noopener">PLATEAU API ↗</a></div><p>'+esc(summary.license)+'</p>';
  if(viewer.dataset.ready==='true')status.textContent=w.ready;
 }
 renderSelection();
}
function renderSelection(){
 if(!selected)return;
 const w=words(),b=selected;
 document.querySelector('#model-selection').innerHTML='<h3>LOD'+esc(b.lod)+' · '+esc(b.primary?w.primary:w.wider)+'</h3><p>'+esc(w.height)+': <strong>'+Number(b.geometry_height_m).toFixed(2)+' m</strong><br>'+esc(w.sourceHeight)+': '+(b.source_height_m==null?'—':Number(b.source_height_m).toFixed(1)+' m')+'<br>'+esc(w.use)+': '+esc(b.usage||'—')+'</p><button type="button" id="focus-building">'+esc(w.focus)+'</button><details><summary>'+esc(w.sourceId)+'</summary><code>'+esc(b.asset_id)+'</code><p>'+esc(w.modelYear)+': '+esc(b.model_release_year)+' · '+esc(w.surveyYear)+': '+esc(b.use_survey_year)+'<br>'+esc(w.sourceDate)+': '+esc(b['core:creationDate']||'—')+'</p></details>';
 document.querySelector('#focus-building').addEventListener('click',()=>fit(new THREE.Box3(new THREE.Vector3(...b.bounds_local_m[0]),new THREE.Vector3(...b.bounds_local_m[1]))));
}
function render(){if(renderer&&scene&&camera)renderer.render(scene,camera)}
function fit(box,top=false){
 if(!box||box.isEmpty())return;
 const size=box.getSize(new THREE.Vector3()),target=box.getCenter(new THREE.Vector3());target.y=Math.max(8,target.y*.45);
 const span=Math.max(size.x/Math.min(1,camera.aspect),size.z,size.y*2),dist=Math.max(75,span/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov*.5)))*1.18);
 controls.target.copy(target);camera.up.set(0,1,0);
 const dir=top?new THREE.Vector3(0.001,1,.001):new THREE.Vector3(.88,.9,1.05).normalize();
 camera.position.copy(target.clone().addScaledVector(dir,dist));controls.update();render();
}
async function init(){
 [summary,index]=await Promise.all([fetch('current-model/geometry-summary.json?v=20261020').then(r=>r.json()),fetch('current-model/geometry-index.json?v=20261020').then(r=>r.json())]);translate();
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0xeeebe4);renderer.outputColorSpace=THREE.SRGBColorSpace;
 renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','Current source building geometry; rotate, zoom and inspect');viewer.prepend(renderer.domElement);
 scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(42,1,1,10000);
 controls=new OrbitControls(camera,renderer.domElement);controls.maxPolarAngle=Math.PI*.495;controls.minDistance=35;controls.maxDistance=5000;controls.screenSpacePanning=true;controls.listenToKeyEvents(renderer.domElement);controls.addEventListener('change',render);
 scene.add(new THREE.HemisphereLight(0xffffff,0x9693a0,2.0));const light=new THREE.DirectionalLight(0xffffff,2.1);light.position.set(-350,800,400);scene.add(light);
 const gltf=await new GLTFLoader().loadAsync('current-model/kajicho-current-untextured.glb?v=20261020');
 sceneModel=gltf.scene;scene.add(sceneModel);primaryBox=new THREE.Box3();
 const byId=new Map(index.buildings.map(b=>[b.asset_id,b]));
 sceneModel.traverse(o=>{
  if(!o.isMesh)return;
  let n=o;while(n&&!n.userData.asset_id)n=n.parent;
  const b=n?byId.get(n.userData.asset_id):null;if(!b)throw Error('Missing current model source ID');
  o.userData.currentBuilding=b;o.material=new THREE.MeshStandardMaterial({color:b.primary?0x89729f:0xb0b1ac,roughness:.85,metalness:0,side:THREE.DoubleSide,flatShading:true});meshes.push(o);
  if(b.primary)primaryBox.union(new THREE.Box3().setFromObject(o));
 });
 if(meshes.length!==1074)throw Error('Unexpected current geometry count: '+meshes.length);
 overallBox=new THREE.Box3().setFromObject(sceneModel);
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,1600),new THREE.MeshStandardMaterial({color:0xe4e1d8,roughness:1,side:THREE.DoubleSide}));ground.rotation.x=-Math.PI/2;ground.position.set(overallBox.getCenter(new THREE.Vector3()).x,.5,overallBox.getCenter(new THREE.Vector3()).z);scene.add(ground);
 const boundary=await fetch('current-model/boundaries.json').then(r=>r.json());
 for(const f of boundary.features){
  const pts=f.coordinates.map(([x,z])=>new THREE.Vector3(x,1.5,z));const geom=new THREE.BufferGeometry().setFromPoints(pts);
  const mat=f.id==='primary_brief'?new THREE.LineBasicMaterial({color:0x59457f}):new THREE.LineDashedMaterial({color:0x69656a,dashSize:9,gapSize:5});
  const line=new THREE.Line(geom,mat);line.computeLineDistances();scene.add(line);
 }
 const resize=()=>{const w=viewer.clientWidth,h=viewer.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render()};new ResizeObserver(resize).observe(viewer);resize();fit(overallBox);
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-view]').forEach(n=>n.setAttribute('aria-pressed',String(n===b)));currentView=b.dataset.view;fit(currentView==='primary'||document.querySelector('#primary-only').checked?primaryBox:overallBox,currentView==='top')}));
 document.querySelector('#model-reset').addEventListener('click',()=>{currentView='overview';document.querySelector('#primary-only').checked=false;meshes.forEach(o=>o.visible=true);document.querySelectorAll('[data-view]').forEach(n=>n.setAttribute('aria-pressed',String(n.dataset.view==='overview')));fit(overallBox)});
 document.querySelector('#primary-only').addEventListener('change',e=>{meshes.forEach(o=>o.visible=!e.target.checked||o.userData.currentBuilding.primary);fit(e.target.checked||currentView==='primary'?primaryBox:overallBox,currentView==='top')});
 let down;
 renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
 renderer.domElement.addEventListener('pointerup',e=>{
  if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;
  const rect=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(pointer,camera);
  const hit=raycaster.intersectObjects(meshes.filter(m=>m.visible),false)[0];if(!hit)return;
  if(selectedMesh)selectedMesh.material.emissive.setHex(0);
  selectedMesh=hit.object;selectedMesh.material.emissive.setHex(0x3c2020);selected=selectedMesh.userData.currentBuilding;renderSelection();render();
 });
 viewer.dataset.ready='true';viewer.dataset.modelCount=String(meshes.length);viewer.dataset.lod='2';viewer.dataset.triangles=String(summary.asset.triangles);translate();render();
}
new MutationObserver(translate).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});translate();
init().catch(e=>{status.textContent=words().error;status.classList.add('model-error');viewer.dataset.error='true';console.error(e)});
