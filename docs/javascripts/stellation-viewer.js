// The stellation page (research/stellation.md): three linked 3D views of one solid under R2.
//
// - the solid, with its zeros (blue) and poles (red);
// - its stellation, with the same pole directions marked at its tips, or, for a solid without
//   one, the pole directions alone;
// - the R2 relief, colored by phase.
//
// A menu switches between the octahedron and its polar dual, the cube, which has no stellation.
// The views share one orientation: dragging any one turns all three, as on the comparison page.
//
// The data, assets/explorer/stellation.json, is generated at build time by docs/hooks/explorer.py
// from polyhedral_functions.viewer_data.stellation_data. The relief uses the prints' transfer
// (rendering.relief_radius), r = depth + (1 - depth) / (1 + exp(-log|f| / k)), whose tips reach
// radius 1, so it fits the same framing as the solids. Sea level |f| = 1 is at (1 + depth) / 2.
import {
  THREE, createStage, createView, divisorOf, paletteIndex, toChart, unitSphere, weldNormals, whileVisible,
} from "./viewer-core.js";

const DATA_URL = new URL("../assets/explorer/stellation.json", import.meta.url);
const VIEW = [3.0, 1.3, 0.8]; // the static figure's, scripts/a8_stellation_figure.py
const RELIEF_W = 192;
const RELIEF_H = 96;
// The relief's body sits near sea level, (1 + depth) / 2 = 0.6, so at the solids' scale it looks
// small. Scaled up, its tips (radius 1) still stay inside the shared camera's frame.
const RELIEF_SCALE = 1.15;
const EMPTY = { vertices: [], faces: [] };
const LABELS = { octahedron: "Octahedron", cube: "Cube, its polar dual" };

function element(tag, attributes = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) {
    if (key === "text") el.textContent = value;
    else el.setAttribute(key, value);
  }
  el.append(...children);
  return el;
}

function panel(caption) {
  const stage = element("div", { class: "geometry-viewer__stage" });
  const text = element("figcaption", { "aria-live": "polite", text: caption });
  return { stage, text, figure: element("figure", { class: "stellation-viewer__panel" }, [stage, text]) };
}

// The R2 relief of one solid: a fine sphere mesh, pushed out by the transfer and colored by phase.
function createRelief(stage, data) {
  const view = createStage(stage, { ariaLabel: "The R2 relief", view: VIEW, aspect: 1 });
  const geometry = unitSphere(RELIEF_W, RELIEF_H);
  const directions = geometry.attributes.position.array.slice();
  const n = directions.length / 3;
  geometry.setAttribute("color", new THREE.Float32BufferAttribute(new Float32Array(3 * n), 3));
  const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75 }));
  mesh.scale.setScalar(RELIEF_SCALE);
  view.scene.add(mesh);
  const palette = data.display.palette.map(
    ([r, g, b]) => new THREE.Color().setRGB(r / 255, g / 255, b / 255, THREE.SRGBColorSpace),
  );
  const depth = data.display.depth;

  function show(entry) {
    const divisor = divisorOf(entry);
    const pos = geometry.attributes.position;
    const colors = geometry.attributes.color;
    for (let i = 0; i < n; i++) {
      const u = [directions[3 * i], directions[3 * i + 1], directions[3 * i + 2]];
      const x = Math.max(-700, Math.min(700, divisor.logModulus(u) / entry.sharpness));
      const r = depth + (1 - depth) / (1 + Math.exp(-x));
      pos.setXYZ(i, u[0] * r, u[1] * r, u[2] * r);
      const z = toChart(u);
      const c = palette[paletteIndex(z ? divisor.phase(z[0], z[1]) : 0, palette.length)];
      colors.setXYZ(i, c.r, c.g, c.b);
    }
    pos.needsUpdate = true;
    colors.needsUpdate = true;
    geometry.computeVertexNormals();
    weldNormals(geometry, RELIEF_W, RELIEF_H);
    geometry.computeBoundingSphere();
  }

  return { ...view, show };
}

async function mount(container) {
  if (container.dataset.mounted) return;
  container.dataset.mounted = "1";
  let data;
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) throw new Error(`${response.status} for ${DATA_URL}`);
    data = await response.json();
  } catch (error) {
    console.warn("stellation viewer: no data, keeping the still images:", error);
    return;
  }

  const ids = Object.keys(data.solids);
  let current = data.solids[container.dataset.solid] ? container.dataset.solid : ids[0];
  const picker = element("select");
  for (const id of ids) picker.append(element("option", { value: id, text: LABELS[id] || data.solids[id].name }));
  picker.value = current;
  const reset = element("button", { type: "button", class: "md-button", text: "Reset view" });
  const toolbar = element("div", { class: "stellation-viewer__toolbar" }, [
    element("label", {}, [element("span", { text: "Solid " }), picker]),
    reset,
  ]);

  const solidPanel = panel("");
  const stellationPanel = panel("");
  const reliefPanel = panel("");
  const grid = element("div", { class: "stellation-viewer__panels" },
    [solidPanel.figure, stellationPanel.figure, reliefPanel.figure]);

  const fallback = container.querySelector(".stellation-viewer__fallback");
  container.append(toolbar, grid);
  let views;
  try {
    views = [
      createView(solidPanel.stage, { ariaLabel: "The solid with its zeros and poles", view: VIEW, aspect: 1 }),
      createView(stellationPanel.stage, { ariaLabel: "The solid's stellation", view: VIEW, aspect: 1 }),
      createRelief(reliefPanel.stage, data),
    ];
  } catch (error) {
    console.warn("stellation viewer: no WebGL, keeping the still images:", error);
    toolbar.remove();
    grid.remove();
    return;
  }
  if (fallback) fallback.hidden = true;
  container.classList.add("is-interactive");
  const [solidView, stellationView, reliefView] = views;

  function show(id) {
    current = id;
    const entry = data.solids[id];
    const name = entry.name;
    // One marker scale for both marker views, so the same order looks the same in each.
    const maxOrder = Math.max(...[...entry.zeros, ...entry.poles].map((m) => m.order));
    const spikes = entry.poles.length;
    solidView.show(entry, entry.zeros, entry.poles, maxOrder);
    solidView.canvas.setAttribute("aria-label", `The ${name} with the zeros and poles of R2`);
    solidPanel.text.textContent =
      `The ${name} under R2: zeros (blue) at its ${entry.zeros.length} vertices, ` +
      `poles (red) at its ${spikes} face normals.`;
    if (entry.stellation) {
      stellationView.show(entry.stellation, [], entry.poles, maxOrder);
      stellationView.canvas.setAttribute("aria-label", `The ${entry.stellation.name}, with its tips marked`);
      stellationPanel.text.textContent =
        `Its stellation, the ${entry.stellation.name}. Its ${spikes} tips point in the same directions as the poles.`;
    } else {
      stellationView.show(EMPTY, [], entry.poles, maxOrder);
      stellationView.canvas.setAttribute("aria-label", `The ${name} has no stellation; the pole directions alone`);
      stellationPanel.text.textContent =
        `The ${name} has no stellation: its opposite face planes are parallel. ` +
        `The markers are where R2 still puts its ${spikes} spikes.`;
    }
    reliefView.show(entry);
    reliefView.canvas.setAttribute("aria-label", `The R2 relief of the ${name}, colored by phase`);
    reliefPanel.text.textContent =
      `The R2 relief: ${spikes} spikes at the poles, ${entry.zeros.length} pits at the zeros, colored by phase.`;
  }
  picker.addEventListener("change", () => show(picker.value));

  // Shared orientation, as in recipe-explorer.js: the view being dragged leads, and the others
  // copy its camera each frame. A view that stops leading first settles its damping.
  let leader = views[0];
  for (const v of views) {
    v.controls.addEventListener("start", () => {
      if (leader !== v) {
        const old = leader.controls;
        old.enableDamping = false;
        old.update();
        old.enableDamping = true;
        leader = v;
      }
    });
  }
  reset.addEventListener("click", () => {
    for (const v of views) v.resetCamera();
  });

  show(current);
  whileVisible(container, () => {
    leader.controls.update();
    for (const v of views) {
      if (v !== leader) {
        v.camera.position.copy(leader.camera.position);
        v.camera.quaternion.copy(leader.camera.quaternion);
      }
      v.render();
    }
  });
}

function mountAll() {
  document.querySelectorAll(".stellation-viewer").forEach((el) => mount(el));
}

// Material's instant navigation (if enabled) re-renders pages without a reload.
if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(mountAll);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountAll);
} else {
  mountAll();
}
