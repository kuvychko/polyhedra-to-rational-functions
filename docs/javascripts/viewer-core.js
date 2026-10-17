// Shared parts of the site's 3D viewers: a solid inside the unit sphere, with the zeros (blue)
// and poles (red) of a function drawn just outside it. Used by geometry-viewer.js (one view per
// object page) and recipe-explorer.js (two linked views on the comparison page).
//
// The data is plain JSON from polyhedral_functions.viewer_data: vertices at circumradius 1,
// polygonal faces, and markers {p: unit direction, order, cell}. three.js 0.170.0 is vendored
// under ./vendor/ (see its README), so the site loads nothing from third parties.
import * as THREE from "./vendor/three-0.170.0/three.module.min.js";
import { OrbitControls } from "./vendor/three-0.170.0/OrbitControls.js";

export { THREE };

const ZERO = 0x2a5ea6;
const POLE = 0xb4312c;
const SOLID = 0xd9d4c7;
const EDGE = 0x4a4a4a;
const DISTANCE = 4.6;

export function markerRadius(order, maxOrder) {
  return 0.035 + 0.035 * Math.sqrt(order / maxOrder);
}

function solidGeometry(solid) {
  const positions = [];
  for (const face of solid.faces) {
    // Faces are convex polygons; a fan from the first vertex triangulates them.
    for (let k = 1; k < face.length - 1; k++) {
      for (const i of [face[0], face[k], face[k + 1]]) positions.push(...solid.vertices[i]);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  return geometry;
}

function edgeGeometry(solid) {
  const seen = new Set();
  const positions = [];
  for (const face of solid.faces) {
    for (let k = 0; k < face.length; k++) {
      const a = face[k];
      const b = face[(k + 1) % face.length];
      const key = a < b ? `${a}-${b}` : `${b}-${a}`;
      if (seen.has(key)) continue;
      seen.add(key);
      positions.push(...solid.vertices[a], ...solid.vertices[b]);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  return geometry;
}

export function withArticle(word) {
  return `${/^[aeiou]/i.test(word) ? "an" : "a"} ${word}`;
}

export function describe(marker) {
  const kind = marker.kind === "zero" ? "zero (a pit)" : "pole (a spike)";
  return `${kind} of order ${marker.order}, at ${withArticle(marker.cell)} direction`;
}

function dispose(object) {
  object.traverse((o) => {
    if (o.geometry) o.geometry.dispose();
    if (o.material) o.material.dispose();
  });
}

// The common stage: renderer, scene with lights, z-up camera with orbit controls, and resizing to
// the stage's width. Throws if WebGL is unavailable; callers keep their static fallback then.
// Used by createView below and by riemann-primer.js (the introduction page).
export function createStage(stage, { ariaLabel, view, aspect = 0.8, distance = DISTANCE, maxDistance = 9 }) {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setClearColor(0xffffff, 1);
  const canvas = renderer.domElement;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", ariaLabel);
  canvas.tabIndex = 0;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  camera.up.set(0, 0, 1);
  scene.add(camera);
  scene.add(new THREE.AmbientLight(0xffffff, 1.4));
  const headlight = new THREE.DirectionalLight(0xffffff, 1.6);
  headlight.position.set(1, 1, 2);
  camera.add(headlight);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.minDistance = 2.2;
  controls.maxDistance = maxDistance;

  function resetCamera(direction = view) {
    camera.position.set(...direction).normalize().multiplyScalar(distance);
    camera.up.set(0, 0, 1);
    controls.target.set(0, 0, 0);
    controls.update();
  }
  resetCamera();

  function resize() {
    const width = stage.clientWidth;
    if (!width) return;
    const height = Math.round(width * aspect);
    renderer.setSize(width, height, false);
    canvas.style.width = "100%";
    canvas.style.height = `${height}px`;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  stage.append(canvas);
  new ResizeObserver(resize).observe(stage);
  resize();

  return {
    renderer, scene, camera, controls, canvas, resetCamera,
    render: () => renderer.render(scene, camera),
  };
}

// One solid with its zeros and poles. Throws if WebGL is unavailable.
export function createView(stage, { ariaLabel, view, aspect = 0.8 }) {
  const { scene, camera, controls, canvas, resetCamera, render } =
    createStage(stage, { ariaLabel, view, aspect });
  scene.add(
    new THREE.Mesh(
      new THREE.SphereGeometry(1, 64, 32),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.12, depthWrite: false }),
    ),
  );

  let content = null;
  let markers = [];

  // solid: {vertices, faces}; zeros/poles: marker lists; maxOrder: the marker size scale.
  function show(solid, zeros, poles, maxOrder) {
    if (content) {
      scene.remove(content);
      dispose(content);
    }
    content = new THREE.Group();
    content.add(
      new THREE.Mesh(
        solidGeometry(solid),
        new THREE.MeshStandardMaterial({
          color: SOLID, transparent: true, opacity: 0.55, side: THREE.DoubleSide,
          depthWrite: false, roughness: 0.9,
        }),
      ),
    );
    content.add(new THREE.LineSegments(edgeGeometry(solid), new THREE.LineBasicMaterial({ color: EDGE })));
    const scale = maxOrder || Math.max(1, ...zeros.map((m) => m.order), ...poles.map((m) => m.order));
    markers = [];
    for (const [kind, list, color] of [["zero", zeros, ZERO], ["pole", poles, POLE]]) {
      for (const m of list) {
        const mesh = new THREE.Mesh(
          new THREE.SphereGeometry(markerRadius(m.order, scale), 24, 16),
          new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.1 }),
        );
        mesh.position.set(...m.p).multiplyScalar(1.04);
        mesh.userData = { ...m, kind };
        content.add(mesh);
        markers.push(mesh);
      }
    }
    scene.add(content);
    hideTooltip();
  }

  const tooltip = document.createElement("div");
  tooltip.className = "geometry-viewer__tooltip";
  tooltip.hidden = true;

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let highlighted = null;
  function hideTooltip() {
    tooltip.hidden = true;
    highlighted = null;
  }
  function pick(event) {
    const rect = canvas.getBoundingClientRect();
    pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1,
                -((event.clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(markers)[0];
    if (highlighted && (!hit || hit.object !== highlighted)) {
      highlighted.material.emissive.setHex(0x000000);
      highlighted = null;
    }
    if (!hit) {
      tooltip.hidden = true;
      return;
    }
    highlighted = hit.object;
    highlighted.material.emissive.setHex(0x333333);
    tooltip.textContent = describe(highlighted.userData);
    tooltip.style.left = `${event.clientX - rect.left + 12}px`;
    tooltip.style.top = `${event.clientY - rect.top + 12}px`;
    tooltip.hidden = false;
  }
  canvas.addEventListener("pointermove", pick);
  canvas.addEventListener("pointerdown", pick); // taps on touch screens
  canvas.addEventListener("pointerleave", () => { tooltip.hidden = true; });

  stage.append(tooltip);

  return { camera, controls, canvas, show, resetCamera, render };
}

// --- functions on the sphere, shared with riemann-primer.js and stellation-viewer.js -------------
//
// A function is its divisor (zeros and poles as markers {p, order}). The evaluation follows
// polyhedral_functions.evaluation:
//   log|f(x)| = sum m log chi(x, a)   (chordal distance; the site's normalization),
//   arg f(z)  = sum over finite a of m arg(z - a)   (the chart's phase, constant C > 0).
// The chart is the site's: z = 0 is the south pole, z = infinity the north pole.

// Unit vector -> chart coordinate [re, im], or null at the north pole (infinity).
export function toChart([x, y, h]) {
  if (h > 1 - 1e-9) return null;
  // Near the north pole 1 - h cancels; use w (1 + h) / |w|^2 there (as chart.to_chart does).
  if (h > 0) {
    const s = (1 + h) / (x * x + y * y);
    return [x * s, y * s];
  }
  return [x / (1 - h), y / (1 - h)];
}

export function divisorOf(entry) {
  const points = [
    ...entry.zeros.map((m) => ({ ...m, m: m.order, kind: "zero" })),
    ...entry.poles.map((m) => ({ ...m, m: -m.order, kind: "pole" })),
  ];
  for (const a of points) a.z = toChart(a.p);
  const finite = points.filter((a) => a.z);
  return {
    points,
    logModulus([x, y, h]) {
      let sum = 0;
      for (const a of points) {
        const dx = x - a.p[0];
        const dy = y - a.p[1];
        const dh = h - a.p[2];
        sum += a.m * 0.5 * Math.log(dx * dx + dy * dy + dh * dh);
      }
      return sum;
    },
    phase(re, im) {
      let sum = 0;
      for (const a of finite) sum += a.m * Math.atan2(im - a.z[1], re - a.z[0]);
      return sum;
    },
  };
}

export function paletteIndex(phase, size) {
  const turns = (phase + Math.PI) / (2 * Math.PI);
  return Math.floor((turns - Math.floor(turns)) * size) % size;
}

// SphereGeometry, turned so its poles lie on the z axis (the chart's south and north poles).
export function unitSphere(widthSegments, heightSegments) {
  const geometry = new THREE.SphereGeometry(1, widthSegments, heightSegments);
  geometry.rotateX(Math.PI / 2);
  return geometry;
}

// After computeVertexNormals, SphereGeometry's seam column and the pole rows are separate
// vertices at the same point; give each group one averaged normal so no crease shows.
export function weldNormals(geometry, widthSegments, heightSegments) {
  const normal = geometry.attributes.normal;
  const row = widthSegments + 1;
  const v = new THREE.Vector3();
  const w = new THREE.Vector3();
  const average = (indices) => {
    v.set(0, 0, 0);
    for (const i of indices) v.add(w.fromBufferAttribute(normal, i));
    v.normalize();
    for (const i of indices) normal.setXYZ(i, v.x, v.y, v.z);
  };
  for (let iy = 1; iy < heightSegments; iy++) average([iy * row, iy * row + widthSegments]);
  for (const iy of [0, heightSegments]) average(Array.from({ length: row }, (_, ix) => iy * row + ix));
  normal.needsUpdate = true;
}

// Render only while on screen: several WebGL figures share the page.
export function whileVisible(target, frame) {
  let visible = true;
  let running = false;
  function loop() {
    if (!visible) {
      running = false;
      return;
    }
    frame();
    requestAnimationFrame(loop);
  }
  function start() {
    if (!running) {
      running = true;
      requestAnimationFrame(loop);
    }
  }
  if ("IntersectionObserver" in window) {
    new IntersectionObserver((entries) => {
      visible = entries.some((e) => e.isIntersecting);
      if (visible) start();
    }).observe(target);
  }
  start();
}
