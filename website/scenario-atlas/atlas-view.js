import * as THREE from './vendor/three.module.min.js';

const radians = THREE.MathUtils.degToRad;
const palette = {paper: '#f7f5f0', highlight: '#944a3e', trace: '#746a60', white: '#fcfaf5', rail: '#47645f'};
const plateHeading = radians(-26);
const plateLean = radians(-18);
const motion = matchMedia('(prefers-reduced-motion: reduce)');

function surface(map, color, opacity = 1) {
  return new THREE.MeshBasicMaterial({map, color, transparent: opacity !== 1, opacity,
    side: THREE.DoubleSide, toneMapped: false});
}

function clear(group) {
  group.traverse(o => {
    o.geometry?.dispose();
    if (o.material) o.material.dispose();
  });
  group.clear();
}

export function createAtlasView(host, geography, actions) {
  const mount = host.querySelector('.atlas-webgl');
  const labels = host.querySelector('.atlas-map-labels');
  const scale = host.querySelector('.atlas-scale-key i');
  const renderer = new THREE.WebGLRenderer({antialias: true, alpha: false, powerPreference: 'low-power'});
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.8));
  renderer.setClearColor(palette.paper);
  renderer.autoClear = false;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  mount.append(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, .5, 4300);
  camera.up.set(0,0,-1);
  const figureScene = new THREE.Scene();
  const figureCamera = new THREE.OrthographicCamera(-1,1,1,-1,1,2000);
  figureCamera.position.z = 1000;
  const map = new THREE.Group();
  const accents = new THREE.Group();
  const plates = new THREE.Group();
  scene.add(map, accents);
  figureScene.add(plates);
  const [west,south,east,northBounds] = geography.bbox;
  const centerE = (west + east) / 2;
  const centerN = (south + northBounds) / 2;
  const xyz = ([e,n], y = 0) => new THREE.Vector3(e - centerE, y, centerN - n);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(east - west, northBounds - south), surface(null, palette.paper));
  ground.rotation.x = -Math.PI / 2;
  map.add(ground);

  let width = 1, height = 1, frame = 0;
  let state = {x:0,z:0,span:840,explode:1,show:1};
  let transition = null;
  let choice = null, board = [], markerNodes = [];
  let grab = null;
  let failed = false;
  const textures = new Map();
  const cursor = new THREE.Vector2();
  const raycaster = new THREE.Raycaster();

  function requestDraw() {
    if (!frame && !failed) frame = requestAnimationFrame(draw);
  }

  function texture(url) {
    if (textures.has(url)) return textures.get(url);
    const obj = new THREE.TextureLoader().load(url, t => {
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
      requestDraw();
    }, undefined, () => actions.assetError(url));
    obj.colorSpace = THREE.SRGBColorSpace;
    textures.set(url, obj);
    return obj;
  }

  const groundTexture = texture(geography.groundUri || '/scenario-atlas/ground.png');
  ground.material.map = groundTexture;
  ground.material.color.set('#ffffff');

  function positionCamera() {
    const half = state.span / 2;
    camera.left = -half * (width / height);
    camera.right = half * (width / height);
    camera.top = half;
    camera.bottom = -half;
    camera.position.set(state.x,1250,state.z);
    camera.lookAt(state.x,0,state.z);
    camera.updateProjectionMatrix();
    camera.updateMatrixWorld();
    figureCamera.left = -width/2;
    figureCamera.right = width/2;
    figureCamera.top = height/2;
    figureCamera.bottom = -height/2;
    figureCamera.updateProjectionMatrix();
    figureCamera.updateMatrixWorld();
  }

  const xyScreen = p => {
    const {x,y,z} = p.clone().project(camera);
    return {x: (x + 1) * width / 2, y: (1 - y) * height / 2, inView: z > -1 && z < 1 && Math.abs(x) < .97 && Math.abs(y) < .94};
  };

  function draw(time) {
    frame = 0;
    if (transition) {
      const u = Math.min(1,(time - transition.start)/transition.duration);
      const ease = 1 - Math.pow(1 - u, 3);
      for (const key of Object.keys(state)) state[key] = THREE.MathUtils.lerp(transition.from[key], transition.to[key], ease);
      if (u === 1) transition = null;
    }
    positionCamera();
    const count = board.length;
    const narrow = width < 480;
    const distance = narrow ? Math.min(width*0.25,96) : Math.min(width*0.172,166);
    for (const item of board) {
      const {mesh, backing, line, src, anchor, index} = item;
      const original = xyScreen(anchor);
      const minWidth = narrow ? 79 : 112;
      const maxWidth = narrow ? width * .37 : Math.min(width*.29,205);
      const ratio = src.width/src.height;
      const w = Math.min(THREE.MathUtils.clamp(src.width * height / state.span * 1.24,minWidth,maxWidth),
                         ratio*height*(narrow ? .39 : .34));
      const h = w/ratio;
      const extent = w/2 + 16;
      const offset = (index-(count-1)/2)*distance*state.explode;
      const lift = (24 + Math.min(height*.19,96)*state.explode + (index%2)*20)*state.show;
      const px = THREE.MathUtils.clamp(original.x + offset,extent,width-extent);
      const py = THREE.MathUtils.clamp(original.y - lift - .38*h,h*.5+15,height-h*.50-13);
      const center = new THREE.Vector3(px-width/2,height/2-py,index*1.5+5);
      mesh.position.copy(center);
      backing.position.copy(center);
      backing.position.z -= .8;
      mesh.scale.set(w,h,1);
      backing.scale.set(w+4,h+4,1);
      mesh.rotation.set(plateLean*state.show,plateHeading*state.show,radians(-6)*state.show,'YXZ');
      backing.rotation.copy(mesh.rotation);
      const attribute = line.geometry.attributes.position;
      attribute.setXYZ(0,original.x-width/2,height/2-original.y,0);
      attribute.setXYZ(1,center.x,center.y-(.46*h),.6);
      attribute.needsUpdate = true;
      line.geometry.computeBoundingSphere();
      mesh.visible = backing.visible = line.visible = state.show > .06 && original.x > -w && original.x < width+w &&
                                                     original.y > -h && original.y < height+h;
      mesh.material.opacity = state.show;
      backing.material.opacity = state.show;
      line.material.opacity = .90*state.show;
    }
    for (const item of markerNodes) {
      const location = xyScreen(item.anchor);
      item.node.hidden = !location.inView;
      if (location.inView) {
        item.node.style.transform = `translate(${Math.round(location.x)}px,${Math.round(location.y)}px) translate(-50%,-105%)`;
      }
    }
    scale.style.width = `${Math.round(50 * height / state.span)}px`;
    renderer.clear();
    renderer.render(scene,camera);
    renderer.clearDepth();
    renderer.render(figureScene,figureCamera);
    if (transition) requestDraw();
  }

  function animate(to, duration = 590) {
    const isReduced = motion.matches;
    const target = {...(transition?.to ?? state), ...to};
    if (isReduced || !duration) {
      state = target;
      transition = null;
    } else {
      transition = {from:{...state}, to:target, start: performance.now(), duration};
    }
    requestDraw();
  }

  function focus() {
    if (!choice) return;
    const anchor = xyz(choice.center);
    const narrow = width / height < 1.04;
    const span = choice.span * (narrow ? 1.12 : 1);
    animate({x:anchor.x,z:anchor.z,span});
  }

  function accentLine(path, color, size = 3.2) {
    const vertices = [];
    for (let i = 1; i < path.length; i++) {
      const a = xyz(path[i-1],1.2), b = xyz(path[i],1.2);
      const tangent = new THREE.Vector3().subVectors(b,a);
      if (tangent.lengthSq() < .02) continue;
      const normal = new THREE.Vector3(tangent.z,0,-tangent.x).normalize().multiplyScalar(size/2);
      const p = a.clone().add(normal), q = a.clone().sub(normal), r = b.clone().add(normal), s = b.clone().sub(normal);
      for (const pt of [p,q,r,r,q,s]) vertices.push(pt.x,pt.y,pt.z);
    }
    if (!vertices.length) return;
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
    accents.add(new THREE.Mesh(geometry,surface(null,color,.86)));
  }

  function update(payload) {
    choice = payload;
    clear(accents);
    clear(plates);
    labels.replaceChildren();
    for (const path of payload.paths) accentLine(path,payload.ink ?? palette.highlight);
    board = payload.media.filter(item => item.src).map((item,index) => {
      const paneWidth = item.width ?? 155;
      const paneHeight = paneWidth / (item.aspect ?? 1.58);
      const front = new THREE.Mesh(new THREE.PlaneGeometry(1,1),surface(texture(item.src),'#ffffff'));
      const backing = new THREE.Mesh(new THREE.PlaneGeometry(1,1),surface(null,index === 0 ? palette.trace : '#aea497'));
      const line = new THREE.Line(new THREE.BufferGeometry().setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,1,1,1],3)),
        new THREE.LineBasicMaterial({color: index === 0 ? palette.highlight : palette.trace,transparent:true,opacity:.75}));
      front.material.transparent = backing.material.transparent = true;
      front.userData.media = item;
      plates.add(backing,front,line);
      return {anchor:xyz(item.xy || payload.center),mesh:front,backing,line,src:{width:paneWidth,height:paneHeight},index};
    });
    markerNodes = payload.markers.map(data => {
      const node = document.createElement('button');
      node.type = 'button';
      node.className = data.dot ? 'atlas-pano-pin' : '';
      node.dataset.active = data.active ? 'true' : 'false';
      node.textContent = data.dot ? '' : data.label;
      node.title = data.label;
      node.setAttribute('aria-label',data.label);
      node.addEventListener('click',() => actions.marker(data));
      labels.append(node);
      return {anchor:xyz(data.xy,2.8),node};
    });
    focus();
  }

  const resize = new ResizeObserver(() => {
    const wasNarrow = width / height < 1.04;
    width = host.clientWidth || 1;
    height = host.clientHeight || 1;
    renderer.setSize(width,height,false);
    if ((width/height < 1.04) !== wasNarrow) focus();
    requestDraw();
  });
  resize.observe(host);

  const canvas = renderer.domElement;
  canvas.addEventListener('pointerdown', e => {
    if (e.button !== 0) return;
    grab = {x:e.clientX, y:e.clientY, sx:e.clientX, sy:e.clientY, moved:false};
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', e => {
    if (!grab) return;
    if (Math.hypot(e.clientX - grab.sx,e.clientY - grab.sy) > 4) grab.moved = true;
    if (grab.moved) {
      host.dataset.drag = 'true';
      const metres = state.span / height;
      const dx = -(e.clientX - grab.x) * metres;
      const dy = -(e.clientY - grab.y) * metres;
      pan(dx,dy);
    }
    grab.x = e.clientX; grab.y = e.clientY;
  });
  canvas.addEventListener('pointerup', e => {
    const moved = grab?.moved;
    grab = null;
    host.dataset.drag = 'false';
    if (moved) return;
    const rect = canvas.getBoundingClientRect();
    cursor.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);
    raycaster.setFromCamera(cursor,figureCamera);
    const hit = raycaster.intersectObjects(board.filter(row => row.mesh.visible).map(row => row.mesh))[0];
    if (hit) actions.photo(hit.object.userData.media);
  });
  canvas.addEventListener('pointercancel',() => {grab = null;host.dataset.drag = 'false';});
  canvas.addEventListener('webglcontextlost', e => {
    e.preventDefault();
    failed = true;
    host.dataset.ready = 'false';
    mount.hidden = true;
    labels.hidden = true;
    actions.fallback();
  });

  function pan(dx,dy) {
    animate({x:state.x+dx,z:state.z+dy},0);
  }
  function zoom(factor) {
    const old = transition?.to.span ?? state.span;
    animate({span:THREE.MathUtils.clamp(old*factor,200,1530)},300);
  }
  host.addEventListener('keydown', e => {
    if (e.target !== host) return;
    const shifts = {ArrowLeft:[-34,0],ArrowRight:[34,0],ArrowUp:[0,-34],ArrowDown:[0,34]};
    if (shifts[e.key]) {e.preventDefault(); pan(...shifts[e.key]);}
    if (e.key === '+' || e.key === '=') {e.preventDefault(); zoom(.83);}
    if (e.key === '-') {e.preventDefault(); zoom(1.2);}
  });
  canvas.addEventListener('wheel', e => {
    if (!e.ctrlKey && !e.metaKey && document.activeElement !== host) return;
    e.preventDefault();
    zoom(e.deltaY < 0 ? .85 : 1.16);
  },{passive:false});

  host.dataset.ready = 'true';
  requestDraw();
  return {
    update, zoom, reset:focus,
    view(mode) { animate({show:mode === 'axon' ? 1 : 0},395); },
    spread(value) {animate({explode:value ? 1:0},490);},
  };
}
