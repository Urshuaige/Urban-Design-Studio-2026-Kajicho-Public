import * as THREE from 'three';

function addContourEdges(mesh, starts, ends, faceA, faceB) {
  const geometry = mesh.geometry;
  const positions = geometry.getAttribute('position');
  const index = geometry.index;
  const vertices = Array.from({ length: positions.count }, (_, i) =>
    new THREE.Vector3().fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld));
  // Weld positions across material and normal seams in the triangulated model.
  const keys = vertices.map(p =>
    [p.x, p.y, p.z].map(value => Math.round(value * 10000)).join(','));
  const edges = new Map();
  const ab = new THREE.Vector3();
  const ac = new THREE.Vector3();
  for (let i = 0; i < (index?.count ?? positions.count); i += 3) {
    const triangle = index ? [index.getX(i), index.getX(i + 1), index.getX(i + 2)] : [i, i + 1, i + 2];
    const [a, b, c] = triangle.map(vertex => vertices[vertex]);
    const normal = new THREE.Vector3().crossVectors(ab.subVectors(b, a), ac.subVectors(c, a));
    if (normal.lengthSq() < 1e-12) continue;
    normal.normalize();
    for (let j = 0; j < 3; j++) {
      const start = triangle[j];
      const end = triangle[(j + 1) % 3];
      if (keys[start] === keys[end]) continue;
      const key = keys[start] < keys[end] ? keys[start] + '|' + keys[end] : keys[end] + '|' + keys[start];
      const edge = edges.get(key);
      if (edge) edge.normals.push(normal);
      else edges.set(key, { start, end, normals: [normal] });
    }
  }
  for (const { start, end, normals } of edges.values()) {
    if (normals.length !== 2 || Math.abs(normals[0].dot(normals[1])) > .99999) continue;
    starts.push(...vertices[start]);
    ends.push(...vertices[end]);
    faceA.push(...normals[0]);
    faceB.push(...normals[1]);
  }
}

export function createStudyContours(meshes) {
  const starts = [];
  const ends = [];
  const faceA = [];
  const faceB = [];
  for (const mesh of meshes) addContourEdges(mesh, starts, ends, faceA, faceB);

  const geometry = new THREE.InstancedBufferGeometry();
  geometry.setIndex([0, 2, 1, 2, 3, 1]);
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(
    [0, -1, 0, 0, 1, 0, 1, -1, 0, 1, 1, 0], 3));
  for (const [name, values] of Object.entries({ edgeStart: starts, edgeEnd: ends, faceA, faceB })) {
    geometry.setAttribute(name, new THREE.InstancedBufferAttribute(new Float32Array(values), 3));
  }
  geometry.instanceCount = starts.length / 3;
  const material = new THREE.ShaderMaterial({
    uniforms: {
      viewport: { value: new THREE.Vector2(1, 1) },
      width: { value: .2 },
      pixelRatio: { value: 1 },
      strength: { value: 1 },
    },
    transparent: true,
    depthWrite: false,
    polygonOffset: true,
    polygonOffsetFactor: -1,
    polygonOffsetUnits: -1,
    toneMapped: false,
    vertexShader: `
      uniform vec2 viewport;
      uniform float width;
      uniform float pixelRatio;
      attribute vec3 edgeStart;
      attribute vec3 edgeEnd;
      attribute vec3 faceA;
      attribute vec3 faceB;
      varying float across;

      void main() {
        gl_Position = vec4(2.0, 0.0, 0.0, 1.0);
        across = 0.0;
        vec3 eye = cameraPosition - edgeStart;
        // Only an edge between a front-facing and a back-facing face is a contour.
        if ((dot(faceA, eye) < 0.0) == (dot(faceB, eye) < 0.0)) return;
        vec4 start = projectionMatrix * viewMatrix * vec4(edgeStart, 1.0);
        vec4 end = projectionMatrix * viewMatrix * vec4(edgeEnd, 1.0);
        float nearStart = start.z + start.w;
        float nearEnd = end.z + end.w;
        if (nearStart < 0.0 && nearEnd < 0.0) return;
        if (nearStart < 0.0) start = mix(start, end, nearStart / (nearStart - nearEnd));
        else if (nearEnd < 0.0) end = mix(end, start, nearEnd / (nearEnd - nearStart));

        vec2 direction = (end.xy / end.w - start.xy / start.w) * viewport;
        if (length(direction) < 0.0001) return;
        vec2 normal = normalize(vec2(-direction.y, direction.x));
        across = position.y * (width + 1.0 / pixelRatio) * 0.5;
        vec4 point = mix(start, end, position.x);
        point.xy += normal * across * 2.0 / viewport * point.w;
        gl_Position = point;
      }
    `,
    fragmentShader: `
      uniform float width;
      uniform float pixelRatio;
      uniform float strength;
      varying float across;

      void main() {
        float halfPixel = 0.5 / pixelRatio;
        float halfWidth = 0.5 * width;
        float coverage = min(across + halfPixel, halfWidth) - max(across - halfPixel, -halfWidth);
        gl_FragColor = vec4(0.0, 0.0, 0.0, 0.88 * strength * clamp(coverage * pixelRatio, 0.0, 1.0));
      }
    `,
  });
  const contours = new THREE.Mesh(geometry, material);
  contours.frustumCulled = false;
  return contours;
}
