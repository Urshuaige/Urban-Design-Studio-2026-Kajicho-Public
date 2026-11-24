import * as THREE from 'three';

export function createSiteBase(terrain) {
  const { min, max } = new THREE.Box3().setFromObject(terrain, true);
  const floor = min.y - 36;
  const footprint = [
    { axis: 'z', along: 'x', edge: min.z, order: 1, samples: new Map() },
    { axis: 'x', along: 'z', edge: max.x, order: 1, samples: new Map() },
    { axis: 'z', along: 'x', edge: max.z, order: -1, samples: new Map() },
    { axis: 'x', along: 'z', edge: min.x, order: -1, samples: new Map() },
  ];
  const vertices = terrain.geometry.getAttribute('position');
  const point = new THREE.Vector3();
  for (let i = 0; i < vertices.count; i++) {
    point.fromBufferAttribute(vertices, i).applyMatrix4(terrain.matrixWorld);
    for (const side of footprint) {
      if (Math.abs(point[side.axis] - side.edge) > .002) continue;
      const coordinate = point[side.along];
      const previous = side.samples.get(coordinate);
      if (previous && point.y <= previous.y) continue;
      const top = point.clone();
      top[side.axis] = side.edge;
      side.samples.set(coordinate, top);
    }
  }

  const positions = [];
  for (const { samples, order } of footprint) {
    const edge = [...samples.entries()].sort(([a], [b]) => order * (a - b)).map(([, top]) => top);
    for (let i = 1; i < edge.length; i++) {
      const a = edge[i - 1], b = edge[i];
      positions.push(a.x, a.y, a.z, b.x, b.y, b.z, b.x, floor, b.z,
        a.x, a.y, a.z, b.x, floor, b.z, a.x, floor, a.z);
    }
  }
  positions.push(min.x, floor, min.z, max.x, floor, min.z, max.x, floor, max.z,
    min.x, floor, min.z, max.x, floor, max.z, min.x, floor, max.z);
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  const slab = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color: '#c2c9d0', roughness: .98 }));
  slab.name = 'Terrain model base';
  return slab;
}
