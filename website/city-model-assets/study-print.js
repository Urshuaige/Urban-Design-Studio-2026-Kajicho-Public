import * as THREE from 'three';

const revision = '?v=20261121-printed-materials';
const asset = name => '/city-model-assets/' + name + revision;

async function loadCoordinates() {
  const response = await fetch(asset('plateau-print-uv.bin'));
  if (!response.ok) throw new Error('PLATEAU texture coordinates could not be loaded');
  const bytes = await response.arrayBuffer();
  const size = new DataView(bytes).getUint32(0, true);
  const index = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes, 4, size)));
  return new Map(Object.entries(index).map(([key, [offset, count]]) =>
    [key, new Uint16Array(bytes, 4 + size + offset, count * 2)]));
}

export async function loadStudyPrint() {
  const loader = new THREE.TextureLoader();
  const [paper, photos] = await Promise.allSettled([
    loader.loadAsync(asset('mono-paper.webp')),
    Promise.all([loader.loadAsync(asset('plateau-ink.webp')), loadCoordinates()]),
  ]);
  if (paper.status === 'rejected') console.warn('Kajicho paper texture:', paper.reason);
  if (photos.status === 'rejected') console.warn('Kajicho PLATEAU textures:', photos.reason);
  return {
    paper: paper.value,
    atlas: photos.value?.[0],
    coordinates: photos.value?.[1] ?? new Map(),
  };
}

export function createStudyPrint(base, assets, meshes, pixelRatio) {
  const { paper, atlas, coordinates } = assets;
  if (!paper && !atlas) return base;
  const neutral = new THREE.DataTexture(new Uint8Array([0, 0, 0, 255]), 1, 1);
  neutral.needsUpdate = true;
  if (paper) {
    paper.wrapS = paper.wrapT = THREE.RepeatWrapping;
    paper.minFilter = THREE.LinearMipmapLinearFilter;
  }
  if (atlas) {
    // The stored coordinates follow glTF's image origin at the upper left.
    atlas.flipY = false;
    atlas.minFilter = THREE.LinearMipmapLinearFilter;
  }
  for (const mesh of meshes) {
    const count = mesh.geometry.getAttribute('position').count;
    const coords = coordinates.get(mesh.userData.key);
    const uv = coords?.length === 2 * count ? coords : new Uint16Array(2 * count);
    mesh.geometry.setAttribute('plateauInkUv', new THREE.BufferAttribute(uv, 2, true));
  }

  const finish = base.clone();
  finish.customProgramCacheKey = () => 'kajicho-study-print';
  finish.onBeforeCompile = shader => {
    shader.uniforms.plateauInk = { value: atlas ?? neutral };
    shader.uniforms.printPaper = { value: paper ?? neutral };
    shader.uniforms.charcoalInk = { value: new THREE.Color('#30343A') };
    shader.uniforms.printPixelRatio = { value: pixelRatio };
    shader.vertexShader = shader.vertexShader.replace('#include <common>', `
      #include <common>
      attribute vec2 plateauInkUv;
      varying vec2 vPlateauInkUv;
      varying vec3 vStudyWorld;
    `).replace('#include <begin_vertex>', `
      #include <begin_vertex>
      vPlateauInkUv = plateauInkUv;
      vStudyWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;
    `);
    shader.fragmentShader = shader.fragmentShader.replace('#include <common>', `
      #include <common>
      uniform sampler2D plateauInk;
      uniform sampler2D printPaper;
      uniform vec3 charcoalInk;
      uniform float printPixelRatio;
      varying vec2 vPlateauInkUv;
      varying vec3 vStudyWorld;
    `).replace('#include <color_fragment>', `
      #include <color_fragment>
      vec3 dx = dFdx(vStudyWorld);
      vec3 dy = dFdy(vStudyWorld);
      float metresPerPixel = printPixelRatio * max(length(dx), length(dy));
      float photoFade = 1.0 - smoothstep(0.16, 0.72, metresPerPixel);
      float paperFade = 1.0 - smoothstep(0.08, 0.32, metresPerPixel);
      vec3 p = vStudyWorld * 0.04;
      vec3 weight = abs(cross(dx, dy));
      weight /= max(weight.x + weight.y + weight.z, 0.000001);
      float paperGrain = dot(weight, vec3(
        texture2D(printPaper, p.zy).r,
        texture2D(printPaper, p.xz).r,
        texture2D(printPaper, p.xy).r
      ));
      float photoGrain = texture2D(plateauInk, vPlateauInkUv).r;
      float coverage = min(0.17, 0.135 * photoFade * photoGrain * (0.88 + 0.12 * paperGrain)
        + 0.075 * paperFade * paperGrain);
      diffuseColor.rgb = mix(diffuseColor.rgb, charcoalInk, coverage);
    `);
  };
  return finish;
}
