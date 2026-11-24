import * as THREE from 'three';

const leafColors = ['#788b78', '#8da18b', '#aab6a5'];
const crownClusters = [
  { height: .66, width: .79, depth: .70, shift: .27, rise: .26, angle: 0 },
  { height: .76, width: .67, depth: .72, shift: .30, rise: .24, angle: 2.1 },
  { height: .69, width: .71, depth: .52, shift: .32, rise: .23, angle: 4.4 },
];

export function addStreetDetails(scene, { sidewalks, trees, parks = [] }, colors) {
  if (sidewalks.length) {
    const paving = new THREE.BufferGeometry();
    paving.setAttribute('position', new THREE.Float32BufferAttribute(sidewalks, 3));
    paving.computeVertexNormals();
    const surface = new THREE.Mesh(paving, new THREE.MeshStandardMaterial({
      color: colors.sidewalk, roughness: .97, side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
    }));
    surface.receiveShadow = true;
    scene.add(surface);
  }
  if (parks.length) {
    const land = new THREE.BufferGeometry();
    land.setAttribute('position', new THREE.Float32BufferAttribute(parks, 3));
    land.computeVertexNormals();
    const parkVolumes = new THREE.Mesh(land, new THREE.MeshStandardMaterial({
      color: colors.park, roughness: .98, side: THREE.DoubleSide,
    }));
    parkVolumes.receiveShadow = true;
    scene.add(parkVolumes);
  }
  if (!trees.length) return;

  // Small clusters give the schematic trees the silhouette of a physical model.
  const trunks = new THREE.InstancedMesh(new THREE.CylinderGeometry(.07, .12, 1, 7),
    new THREE.MeshStandardMaterial({ color: '#827e77', roughness: 1 }), trees.length);
  const crown = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1),
    new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, flatShading: true }),
    trees.length * crownClusters.length);
  const piece = new THREE.Object3D();
  trees.forEach(([x, y, z, height, radius], index) => {
    const turn = (index * 2.39996) % (Math.PI * 2);
    piece.position.set(x, y + height * .32, z);
    piece.rotation.set(0, turn, 0);
    piece.scale.setScalar(Math.max(.85, radius * .62));
    piece.scale.y = height * .64;
    piece.updateMatrix();
    trunks.setMatrixAt(index, piece.matrix);
    crownClusters.forEach((cluster, part) => {
      const angle = turn + cluster.angle;
      piece.position.set(x + Math.cos(angle) * radius * cluster.shift,
        y + height * cluster.height, z + Math.sin(angle) * radius * cluster.shift);
      piece.rotation.y = angle;
      piece.scale.set(radius * cluster.width, height * cluster.rise, radius * cluster.depth);
      piece.updateMatrix();
      const slot = index * crownClusters.length + part;
      crown.setMatrixAt(slot, piece.matrix);
      crown.setColorAt(slot, new THREE.Color(leafColors[(part + index) % leafColors.length]));
    });
  });
  for (const mesh of [trunks, crown]) {
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);
  }
}
