// Interactive view of a piece's geometry: the solid, the unit sphere, and the zeros (blue) and
// poles (red) of its function. Drag to rotate, scroll or pinch to zoom, hover or tap a marker
// for its order and the cell it stands for.
//
// Progressive enhancement: each `.geometry-viewer` holds a static render, which stays in place
// if WebGL, the network or this script is unavailable. The data comes from
// docs/assets/pieces/<id>/geometry.json, written by scripts/a4_site_assets.py. three.js 0.170.0
// is vendored under ./vendor/ (see its README), so the site loads nothing from third parties.
import * as THREE from "./vendor/three-0.170.0/three.module.min.js";
import { OrbitControls } from "./vendor/three-0.170.0/OrbitControls.js";

const ZERO = 0x2a5ea6;
const POLE = 0xb4312c;
const SOLID = 0xd9d4c7;
const EDGE = 0x4a4a4a;

function markerRadius(order, maxOrder) {
  return 0.035 + 0.035 * Math.sqrt(order / maxOrder);
}

function solidGeometry(data) {
  const positions = [];
  for (const face of data.faces) {
    // Faces are convex polygons; a fan from the first vertex triangulates them.
    for (let k = 1; k < face.length - 1; k++) {
      for (const i of [face[0], face[k], face[k + 1]]) positions.push(...data.vertices[i]);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  return geometry;
}

function edgeGeometry(data) {
  const seen = new Set();
  const positions = [];
  for (const face of data.faces) {
    for (let k = 0; k < face.length; k++) {
      const a = face[k];
      const b = face[(k + 1) % face.length];
      const key = a < b ? `${a}-${b}` : `${b}-${a}`;
      if (seen.has(key)) continue;
      seen.add(key);
      positions.push(...data.vertices[a], ...data.vertices[b]);
    }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  return geometry;
}

function describe(marker) {
  const kind = marker.kind === "zero" ? "zero (a pit)" : "pole (a spike)";
  return `${kind} of order ${marker.order}, at a ${marker.cell} direction`;
}

async function mount(container) {
  if (container.dataset.mounted) return;
  container.dataset.mounted = "1";
  const fallback = container.querySelector("img");
  // data-src names the data file relative to the fallback image, whose URL MkDocs rewrites for
  // the page's location (raw HTML attributes are not rewritten).
  const url = fallback
    ? new URL(container.dataset.src, fallback.currentSrc || fallback.src)
    : new URL(container.dataset.src, document.baseURI);
  let data;
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`${response.status} for ${url}`);
    data = await response.json();
  } catch (error) {
    console.warn("geometry viewer: keeping the static image:", error);
    return;
  }

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
  } catch (error) {
    console.warn("geometry viewer: no WebGL, keeping the static image:", error);
    return;
  }
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setClearColor(0xffffff, 1);
  const canvas = renderer.domElement;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", fallback ? fallback.alt : `Geometry of ${data.title}`);
  canvas.tabIndex = 0;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  const view = new THREE.Vector3(...data.view).normalize();
  camera.up.set(0, 0, 1);
  camera.position.copy(view.multiplyScalar(4.6));
  scene.add(camera);
  scene.add(new THREE.AmbientLight(0xffffff, 1.4));
  const headlight = new THREE.DirectionalLight(0xffffff, 1.6);
  headlight.position.set(1, 1, 2);
  camera.add(headlight);

  scene.add(
    new THREE.Mesh(
      solidGeometry(data),
      new THREE.MeshStandardMaterial({
        color: SOLID, transparent: true, opacity: 0.55, side: THREE.DoubleSide,
        depthWrite: false, roughness: 0.9,
      }),
    ),
  );
  scene.add(new THREE.LineSegments(edgeGeometry(data), new THREE.LineBasicMaterial({ color: EDGE })));
  scene.add(
    new THREE.Mesh(
      new THREE.SphereGeometry(1, 64, 32),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.12, depthWrite: false }),
    ),
  );

  const markers = [];
  const maxOrder = Math.max(1, ...data.zeros.map((m) => m.order), ...data.poles.map((m) => m.order));
  for (const [kind, list, color] of [["zero", data.zeros, ZERO], ["pole", data.poles, POLE]]) {
    for (const m of list) {
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(markerRadius(m.order, maxOrder), 24, 16),
        new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.1 }),
      );
      mesh.position.set(...m.p).multiplyScalar(1.04);
      mesh.userData = { ...m, kind };
      scene.add(mesh);
      markers.push(mesh);
    }
  }

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.enablePan = false;
  controls.minDistance = 2.2;
  controls.maxDistance = 9;

  const tooltip = document.createElement("div");
  tooltip.className = "geometry-viewer__tooltip";
  tooltip.hidden = true;

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let highlighted = null;
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

  function resize() {
    const width = container.clientWidth;
    const height = Math.round(width * 0.8);
    renderer.setSize(width, height, false);
    canvas.style.width = "100%";
    canvas.style.height = `${height}px`;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  const stage = container.querySelector(".geometry-viewer__stage") || container;
  if (fallback) fallback.hidden = true;
  stage.append(canvas, tooltip);
  container.classList.add("is-interactive");
  new ResizeObserver(resize).observe(container);
  resize();

  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
}

function mountAll() {
  document.querySelectorAll(".geometry-viewer[data-src]").forEach((el) => mount(el));
}

// Material's instant navigation (if enabled) re-renders pages without a reload.
if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(mountAll);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountAll);
} else {
  mountAll();
}
