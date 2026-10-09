// The introduction page (research/primer.md): three small interactive figures.
//
// - .stereo-demo: stereographic projection. A point z on the plane through the sphere's equator
//   is joined to the north pole; the line crosses the sphere at z's image. Drag z, or use the
//   sliders, and send it towards infinity.
// - .sphere-demo: one function drawn in the plane (domain coloring) and/or on the sphere, with an
//   optional relief slider that pushes the sphere in and out by |f|. Attributes:
//   data-function (initial choice), data-panels ("plane", "sphere" or "plane sphere"),
//   data-relief ("1" adds the slider).
//
// Every function is a divisor, from assets/explorer/primer.json (docs/hooks/explorer.py, from
// polyhedral_functions.viewer_data). The evaluation follows polyhedral_functions.evaluation:
//   log|f(x)| = sum m log chi(x, a)   (chordal distance; the site's normalization),
//   arg f(z)  = sum over finite a of m arg(z - a)   (the chart's phase, constant C > 0).
// The chart is the site's: z = 0 is the south pole, z = infinity the north pole.
import { THREE, createStage } from "./viewer-core.js";

const DATA_URL = new URL("../assets/explorer/primer.json", import.meta.url);
const ZERO = 0x2a5ea6;
const POLE = 0xb4312c;
const POINT_Z = 0xd9822b;
const IMAGE = 0x6b3fa0;
const REDUCED_MOTION = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let dataPromise = null;
function loadData() {
  dataPromise ||= fetch(DATA_URL).then((response) => {
    if (!response.ok) throw new Error(`${response.status} for ${DATA_URL}`);
    return response.json();
  });
  return dataPromise;
}

function element(tag, attributes = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) {
    if (key === "text") el.textContent = value;
    else el.setAttribute(key, value);
  }
  el.append(...children);
  return el;
}

function slider(label, { min, max, step, value }) {
  const input = element("input", { type: "range", min, max, step });
  input.value = value;
  return { input, wrapper: element("label", { class: "primer__slider" }, [element("span", { text: label }), input]) };
}

// --- the chart --------------------------------------------------------------------------------

// Unit vector -> chart coordinate [re, im], or null at the north pole (infinity).
function toChart([x, y, h]) {
  if (h > 1 - 1e-9) return null;
  // Near the north pole 1 - h cancels; use w (1 + h) / |w|^2 there (as chart.to_chart does).
  if (h > 0) {
    const s = (1 + h) / (x * x + y * y);
    return [x * s, y * s];
  }
  return [x / (1 - h), y / (1 - h)];
}

function toSphere(re, im) {
  const r2 = re * re + im * im;
  const d = 1 + r2;
  return [(2 * re) / d, (2 * im) / d, (r2 - 1) / d];
}

function formatNumber(x, digits = 2) {
  const text = Math.abs(x).toFixed(digits).replace(/\.?0+$/, "");
  return `${x < 0 && text !== "0" ? "−" : ""}${text}`;
}

function formatComplex(c, digits = 2) {
  if (!c) return "∞";
  const [re, im] = c.map((v) => (Math.abs(v) < 0.5 * 10 ** -digits ? 0 : v));
  if (im === 0) return formatNumber(re, digits);
  const imText = `${formatNumber(Math.abs(im), digits) === "1" ? "" : formatNumber(Math.abs(im), digits)}i`;
  if (re === 0) return `${im < 0 ? "−" : ""}${imText}`;
  return `${formatNumber(re, digits)} ${im < 0 ? "−" : "+"} ${imText}`;
}

// --- a function, from its divisor -------------------------------------------------------------

function divisorOf(entry) {
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

function paletteIndex(phase, size) {
  const turns = (phase + Math.PI) / (2 * Math.PI);
  return Math.floor((turns - Math.floor(turns)) * size) % size;
}

const CELL_PLURAL = { vertex: "vertices", face: "faces", edge: "edges" };

function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

// "a zero of order 2 at 0; a pole of order 2 at ∞", or grouped by cell for a recipe.
function describePoints(divisor) {
  const pts = divisor.points;
  if (pts.length <= 4) {
    return pts.map((a) => `a ${a.kind} of order ${Math.abs(a.m)} at ${formatComplex(a.z, 3)}`).join("; ");
  }
  const counts = new Map();
  for (const a of pts) {
    const key = `${a.kind}|${Math.abs(a.m)}|${a.cell}`;
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return [...counts.entries()].map(([key, n]) => {
    const [kind, order, cell] = key.split("|");
    return `${plural(n, kind)} of order ${order} at the ${CELL_PLURAL[cell] || `${cell}s`}`;
  }).join("; ");
}

// Render only while on screen: several WebGL figures share the page.
function whileVisible(target, frame) {
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

function label(text) {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 96;
  const ctx = canvas.getContext("2d");
  ctx.font = "600 52px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.lineWidth = 10;
  ctx.strokeStyle = "rgba(255,255,255,0.9)";
  ctx.strokeText(text, 128, 48);
  ctx.fillStyle = "#222";
  ctx.fillText(text, 128, 48);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, depthTest: false }));
  sprite.scale.set(0.6, 0.225, 1);
  sprite.renderOrder = 10;
  return sprite;
}

function line(points, color, opacity = 1) {
  const geometry = new THREE.BufferGeometry().setFromPoints(points.map((p) => new THREE.Vector3(...p)));
  return new THREE.Line(geometry, new THREE.LineBasicMaterial({ color, transparent: opacity < 1, opacity }));
}

function ball(radius, color) {
  return new THREE.Mesh(
    new THREE.SphereGeometry(radius, 24, 16),
    new THREE.MeshStandardMaterial({ color, roughness: 0.4, metalness: 0.1 }),
  );
}

// SphereGeometry, turned so its poles lie on the z axis (the chart's south and north poles).
function unitSphere(widthSegments, heightSegments) {
  const geometry = new THREE.SphereGeometry(1, widthSegments, heightSegments);
  geometry.rotateX(Math.PI / 2);
  return geometry;
}

// --- figure 1: stereographic projection ------------------------------------------------------

const PLANE_RADIUS = 3;
const LOG_MIN = -1.5;
const LOG_MAX = 2;

function mountStereo(container) {
  const stageEl = element("div", { class: "geometry-viewer__stage" });
  const modulus = slider("|z|", { min: LOG_MIN, max: LOG_MAX, step: 0.001, value: Math.log10(0.8) });
  const angle = slider("angle of z", { min: 0, max: 359, step: 1, value: 35 });
  const toInfinity = element("button", { type: "button", class: "md-button", text: "Send z towards ∞" });
  const reset = element("button", { type: "button", class: "md-button", text: "Reset" });
  const gridBox = element("input", { type: "checkbox" });
  gridBox.checked = true;
  const controls = element("div", { class: "primer__controls" }, [
    modulus.wrapper, angle.wrapper,
    element("label", {}, [gridBox, " Grid on the sphere"]),
    toInfinity, reset,
  ]);
  const readout = element("p", { class: "primer__readout", "aria-live": "polite" });

  let view;
  try {
    view = createStage(stageEl, {
      ariaLabel: "Stereographic projection: the unit sphere, the plane through its equator, and a point z joined to the north pole",
      view: [2.2, -3.0, 1.5], aspect: 0.75, distance: 8, maxDistance: 16,
    });
  } catch (error) {
    console.warn("stereographic projection: no WebGL, keeping the drawing:", error);
    return;
  }
  const fallback = container.querySelector(".primer__fallback");
  if (fallback) fallback.hidden = true;
  container.append(controls, stageEl, readout);
  const { scene, camera, canvas } = view;

  scene.add(new THREE.Mesh(
    unitSphere(64, 32),
    new THREE.MeshStandardMaterial({
      color: 0xc9d4e6, transparent: true, opacity: 0.35, depthWrite: false, side: THREE.DoubleSide,
    }),
  ));
  scene.add(new THREE.Mesh(
    new THREE.CircleGeometry(PLANE_RADIUS, 96),
    new THREE.MeshBasicMaterial({
      color: 0xe8e4da, transparent: true, opacity: 0.5, depthWrite: false, side: THREE.DoubleSide,
    }),
  ));

  const circle = (r, h = 0, n = 128) => Array.from({ length: n + 1 }, (_, k) => {
    const t = (2 * Math.PI * k) / n;
    return [r * Math.cos(t), r * Math.sin(t), h];
  });
  // The plane's grid: circles |z| = 1/2, 2, 3 and rays every 30 degrees. The unit circle is the
  // equator itself, drawn darker.
  for (const r of [0.5, 2, 3]) scene.add(line(circle(r), 0x8a8a8a, 0.8));
  for (let k = 0; k < 12; k++) {
    const t = (Math.PI * k) / 6;
    scene.add(line([[0, 0, 0], [PLANE_RADIUS * Math.cos(t), PLANE_RADIUS * Math.sin(t), 0]], 0x8a8a8a, 0.6));
  }
  scene.add(line(circle(1), 0x222222));

  // The images of that grid on the sphere: |z| = r is the circle of latitude at height
  // (r^2 - 1) / (r^2 + 1); a ray is a meridian from the south pole to the north pole.
  const sphereGrid = new THREE.Group();
  for (const r of [0.5, 2, 3]) {
    const h = (r * r - 1) / (r * r + 1);
    sphereGrid.add(line(circle(Math.sqrt(1 - h * h), h), 0x5a6f99));
  }
  for (let k = 0; k < 12; k++) {
    const t = (Math.PI * k) / 6;
    const arc = Array.from({ length: 65 }, (_, j) => {
      const a = (Math.PI * j) / 64;
      return [Math.sin(a) * Math.cos(t), Math.sin(a) * Math.sin(t), -Math.cos(a)];
    });
    sphereGrid.add(line(arc, 0x5a6f99, 0.7));
  }
  scene.add(sphereGrid);

  const north = ball(0.05, 0x222222);
  north.position.set(0, 0, 1);
  const south = ball(0.05, 0x222222);
  south.position.set(0, 0, -1);
  const origin = ball(0.035, 0x222222);
  const northLabel = label("N = ∞");
  northLabel.position.set(0, 0, 1.28);
  const southLabel = label("S = 0");
  southLabel.position.set(0, 0, -1.28);
  scene.add(north, south, origin, northLabel, southLabel);

  const zMarker = ball(0.075, POINT_Z);
  const handle = new THREE.Mesh(
    new THREE.SphereGeometry(0.22, 16, 12),
    new THREE.MeshBasicMaterial({ transparent: true, opacity: 0, depthWrite: false }),
  );
  const zLabel = label("z");
  const image = ball(0.065, IMAGE);
  const ray = new THREE.LineSegments(
    new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(12), 3)),
    new THREE.LineBasicMaterial({ color: 0x333333 }),
  );
  scene.add(zMarker, handle, zLabel, image, ray);

  const state = { logR: Number(modulus.input.value), deg: Number(angle.input.value) };

  function update() {
    const r = 10 ** state.logR;
    const t = (state.deg * Math.PI) / 180;
    const re = r * Math.cos(t);
    const im = r * Math.sin(t);
    const p = toSphere(re, im);
    zMarker.position.set(re, im, 0);
    handle.position.copy(zMarker.position);
    zLabel.position.set(re, im, 0.22);
    image.position.set(...p);
    const pos = ray.geometry.attributes.position;
    pos.setXYZ(0, 0, 0, 1);
    pos.setXYZ(1, ...p);
    pos.setXYZ(2, 0, 0, 1);
    pos.setXYZ(3, re, im, 0);
    pos.needsUpdate = true;
    ray.geometry.computeBoundingSphere();
    modulus.input.value = state.logR;
    angle.input.value = state.deg;

    let where;
    if (Math.abs(r - 1) < 0.01) where = "on the unit circle, so its image is on the equator";
    else if (r < 1) where = "inside the unit circle, so its image is in the southern hemisphere";
    else if (r < 20) where = "outside the unit circle, so its image is in the northern hemisphere";
    else where = "far out, so its image is close to the north pole, the point ∞";
    const height = p[2];
    readout.textContent =
      `z = ${formatComplex([re, im])}, |z| = ${formatNumber(r)}: ${where}` +
      ` (height ${formatNumber(height)} on a sphere of radius 1).` +
      (r > PLANE_RADIUS ? " z itself is beyond the edge of the drawn plane; follow the line." : "");
  }

  modulus.input.addEventListener("input", () => { state.logR = Number(modulus.input.value); update(); });
  angle.input.addEventListener("input", () => { state.deg = Number(angle.input.value); update(); });
  gridBox.addEventListener("change", () => { sphereGrid.visible = gridBox.checked; });

  let animation = null;
  toInfinity.addEventListener("click", () => {
    if (REDUCED_MOTION) {
      state.logR = LOG_MAX;
      update();
      return;
    }
    const from = state.logR;
    const start = performance.now();
    animation = (now) => {
      const s = Math.min(1, (now - start) / 2500);
      state.logR = from + (LOG_MAX - from) * (1 - (1 - s) ** 2);
      update();
      if (s >= 1) animation = null;
    };
  });
  reset.addEventListener("click", () => {
    animation = null;
    state.logR = Math.log10(0.8);
    state.deg = 35;
    view.resetCamera();
    update();
  });

  // Dragging z: the capture-phase listener runs before OrbitControls' own, so the controls can
  // be switched off before they start a rotation.
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  const hit = new THREE.Vector3();
  let dragging = false;
  function cast(event) {
    const rect = canvas.getBoundingClientRect();
    pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
  }
  stageEl.addEventListener("pointerdown", (event) => {
    cast(event);
    if (raycaster.intersectObject(handle).length) {
      dragging = true;
      animation = null;
      view.controls.enabled = false;
      canvas.setPointerCapture(event.pointerId);
      event.preventDefault();
    }
  }, { capture: true });
  canvas.addEventListener("pointermove", (event) => {
    cast(event);
    if (!dragging) {
      canvas.style.cursor = raycaster.intersectObject(handle).length ? "move" : "";
      return;
    }
    if (raycaster.ray.intersectPlane(plane, hit)) {
      const r = Math.min(Math.hypot(hit.x, hit.y), PLANE_RADIUS);
      state.logR = Math.max(LOG_MIN, Math.log10(Math.max(r, 1e-6)));
      state.deg = Math.round(((Math.atan2(hit.y, hit.x) * 180) / Math.PI + 360) % 360);
      update();
    }
  });
  const endDrag = () => {
    dragging = false;
    view.controls.enabled = true;
  };
  canvas.addEventListener("pointerup", endDrag);
  canvas.addEventListener("pointercancel", endDrag);

  update();
  container.classList.add("is-interactive");
  whileVisible(container, () => {
    if (animation) animation(performance.now());
    view.controls.update();
    view.render();
  });
}

// --- figures 2-4: a function on the plane and on the sphere ----------------------------------

const PLANE_PIXELS = 320;
const SPHERE_W = 192;
const SPHERE_H = 96;

function drawPlane(canvas, divisor, data) {
  const half = data.display.plane_half_width;
  const palette = data.display.palette;
  const ctx = canvas.getContext("2d");
  const n = PLANE_PIXELS;
  const img = ctx.createImageData(n, n);
  for (let j = 0; j < n; j++) {
    const im = half - ((j + 0.5) * 2 * half) / n;
    for (let i = 0; i < n; i++) {
      const re = -half + ((i + 0.5) * 2 * half) / n;
      const c = palette[paletteIndex(divisor.phase(re, im), palette.length)];
      const k = 4 * (j * n + i);
      img.data[k] = c[0];
      img.data[k + 1] = c[1];
      img.data[k + 2] = c[2];
      img.data[k + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  const px = (re) => ((re + half) / (2 * half)) * n;
  const py = (im) => ((half - im) / (2 * half)) * n;
  // The unit circle (dashed) and the axes, for orientation.
  ctx.lineWidth = 1.5;
  ctx.strokeStyle = "rgba(255,255,255,0.85)";
  ctx.setLineDash([5, 4]);
  ctx.beginPath();
  ctx.arc(px(0), py(0), n / (2 * half), 0, 2 * Math.PI);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.strokeStyle = "rgba(255,255,255,0.45)";
  ctx.beginPath();
  ctx.moveTo(0, py(0));
  ctx.lineTo(n, py(0));
  ctx.moveTo(px(0), 0);
  ctx.lineTo(px(0), n);
  ctx.stroke();
  for (const a of divisor.points) {
    if (!a.z || Math.abs(a.z[0]) > half || Math.abs(a.z[1]) > half) continue;
    ctx.beginPath();
    ctx.arc(px(a.z[0]), py(a.z[1]), 5, 0, 2 * Math.PI);
    ctx.fillStyle = a.kind === "zero" ? "#2a5ea6" : "#b4312c";
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#fff";
    ctx.stroke();
  }
}

// After computeVertexNormals, SphereGeometry's seam column and the pole rows are separate
// vertices at the same point; give each group one averaged normal so no crease shows.
function weldNormals(geometry) {
  const normal = geometry.attributes.normal;
  const row = SPHERE_W + 1;
  const v = new THREE.Vector3();
  const w = new THREE.Vector3();
  const average = (indices) => {
    v.set(0, 0, 0);
    for (const i of indices) v.add(w.fromBufferAttribute(normal, i));
    v.normalize();
    for (const i of indices) normal.setXYZ(i, v.x, v.y, v.z);
  };
  for (let iy = 1; iy < SPHERE_H; iy++) average([iy * row, iy * row + SPHERE_W]);
  for (const iy of [0, SPHERE_H]) average(Array.from({ length: row }, (_, ix) => iy * row + ix));
  normal.needsUpdate = true;
}

async function mountSphereDemo(container) {
  let data;
  try {
    data = await loadData();
  } catch (error) {
    console.warn("primer: no data, keeping the still images:", error);
    return;
  }
  const panels = (container.dataset.panels || "plane sphere").split(/\s+/);
  const withRelief = container.dataset.relief === "1";
  const options = Object.entries(data.functions);
  let current = data.functions[container.dataset.function] ? container.dataset.function : options[0][0];

  const picker = element("select");
  for (const [id, f] of options) picker.append(element("option", { value: id, text: f.label }));
  picker.value = current;
  const controlItems = [element("label", {}, [element("span", { text: "Function" }), picker])];
  const relief = withRelief ? slider("relief", { min: 0, max: 1, step: 0.01, value: 0 }) : null;
  const seaBox = element("input", { type: "checkbox" });
  seaBox.checked = true;
  if (relief) controlItems.push(relief.wrapper, element("label", {}, [seaBox, " Sea level |f| = 1"]));
  const controls = element("div", { class: "primer__controls" }, controlItems);
  const grid = element("div", { class: `primer__panels primer__panels--${panels.length}` });
  const summary = element("p", { class: "primer__readout", "aria-live": "polite" });

  let planeCanvas = null;
  if (panels.includes("plane")) {
    planeCanvas = element("canvas", { width: PLANE_PIXELS, height: PLANE_PIXELS, class: "primer__plane", role: "img" });
    const half = formatNumber(data.display.plane_half_width);
    grid.append(element("figure", { class: "primer__figure" }, [
      planeCanvas,
      element("figcaption", { text: `The plane, −${half} to ${half} each way; dashed: the unit circle.` }),
    ]));
  }

  let sphere = null;
  if (panels.includes("sphere")) {
    const stageEl = element("div", { class: "geometry-viewer__stage" });
    const figure = element("figure", { class: "primer__figure" }, [
      stageEl,
      element("figcaption", { text: "The sphere: drag to turn it, scroll or pinch to zoom." }),
    ]);
    grid.append(figure);
    try {
      sphere = createStage(stageEl, {
        ariaLabel: "The function drawn on the sphere",
        view: [2.2, -2.6, 1.2], aspect: 1, distance: withRelief ? 7.6 : 5, maxDistance: 14,
      });
    } catch (error) {
      console.warn("primer: no WebGL, the sphere view is left out:", error);
      figure.remove();
      grid.className = "primer__panels primer__panels--1";
      if (!planeCanvas) return;
    }
  }

  const fallback = container.querySelector(".primer__fallback");
  if (fallback) fallback.hidden = true;
  container.append(controls, grid, summary);
  container.classList.add("is-interactive");

  // The sphere: per-vertex directions, the function's log|f| and phase color at each.
  let surface = null;
  let markers = null;
  let sea = null;
  const n = (SPHERE_W + 1) * (SPHERE_H + 1);
  const directions = new Float32Array(3 * n);
  const logModulus = new Float32Array(n);
  if (sphere) {
    const geometry = unitSphere(SPHERE_W, SPHERE_H);
    directions.set(geometry.attributes.position.array);
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(new Float32Array(3 * n), 3));
    surface = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75 }));
    sea = new THREE.Mesh(
      unitSphere(64, 32),
      new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.35, depthWrite: false }),
    );
    sphere.scene.add(surface, sea);
  }

  const linear = data.display.palette.map(([r, g, b]) => new THREE.Color().setRGB(r / 255, g / 255, b / 255, THREE.SRGBColorSpace));
  let divisor = null;
  let entry = null;

  // Radius at relief t: sea level |f| = 1 stays at radius 1 while t moves the rest. The
  // transfer is complexplorer's logistic one (rendering.relief_radius):
  //   rho = depth + (1 - depth) / (1 + exp(-log|f| / k)),
  // divided by its sea-level value so the plain sphere (t = 0) has radius 1.
  function radius(L, t) {
    const depth = data.display.depth;
    const sea0 = depth + (1 - depth) / 2;
    const x = Math.max(-700, Math.min(700, L / entry.sharpness));
    const rho = depth + (1 - depth) / (1 + Math.exp(-x));
    return ((1 - t) * sea0 + t * rho) / sea0;
  }

  function shape() {
    if (!surface) return;
    const t = relief ? Number(relief.input.value) : 0;
    const pos = surface.geometry.attributes.position;
    for (let i = 0; i < n; i++) {
      const r = radius(logModulus[i], t);
      pos.setXYZ(i, directions[3 * i] * r, directions[3 * i + 1] * r, directions[3 * i + 2] * r);
    }
    pos.needsUpdate = true;
    surface.geometry.computeVertexNormals();
    weldNormals(surface.geometry);
    surface.geometry.computeBoundingSphere();
    // The markers belong to the plain sphere. Once the relief starts, the spikes and pits show
    // the points themselves, and a marker would float off a spike's tip (the mesh only reaches
    // the logistic's limit exactly at the pole).
    markers.visible = t < 0.02;
    for (const mesh of markers.children) mesh.position.set(...mesh.userData.p).multiplyScalar(1.04);
    sea.visible = relief ? t > 0.01 && seaBox.checked : false;
  }

  function choose(id) {
    current = id;
    entry = data.functions[id];
    divisor = divisorOf(entry);
    if (planeCanvas) {
      drawPlane(planeCanvas, divisor, data);
      planeCanvas.setAttribute("aria-label", `Domain coloring of ${entry.label} in the plane`);
    }
    if (surface) {
      const colors = surface.geometry.attributes.color;
      for (let i = 0; i < n; i++) {
        const u = [directions[3 * i], directions[3 * i + 1], directions[3 * i + 2]];
        logModulus[i] = divisor.logModulus(u);
        const z = toChart(u);
        const c = linear[paletteIndex(z ? divisor.phase(z[0], z[1]) : 0, linear.length)];
        colors.setXYZ(i, c.r, c.g, c.b);
      }
      colors.needsUpdate = true;
      if (markers) {
        sphere.scene.remove(markers);
        markers.traverse((o) => {
          if (o.geometry) o.geometry.dispose();
          if (o.material) o.material.dispose();
        });
      }
      markers = new THREE.Group();
      const top = Math.max(...divisor.points.map((a) => Math.abs(a.m)));
      for (const a of divisor.points) {
        const mesh = ball(0.035 + 0.035 * Math.sqrt(Math.abs(a.m) / top), a.kind === "zero" ? ZERO : POLE);
        mesh.userData = a;
        markers.add(mesh);
      }
      sphere.scene.add(markers);
      sphere.canvas.setAttribute("aria-label", `${entry.label} drawn on the sphere`);
      shape();
    }
    summary.textContent = `${entry.label}: ${describePoints(divisor)}. ` +
      `Counted with their orders, ${plural(entry.degree, "zero")} and ${plural(entry.degree, "pole")}.`;
  }

  picker.addEventListener("change", () => choose(picker.value));
  if (relief) {
    relief.input.addEventListener("input", shape);
    seaBox.addEventListener("change", shape);
  }
  choose(current);
  if (sphere) {
    whileVisible(container, () => {
      sphere.controls.update();
      sphere.render();
    });
  }
}

function mountAll() {
  for (const el of document.querySelectorAll(".stereo-demo")) {
    if (el.dataset.mounted) continue;
    el.dataset.mounted = "1";
    mountStereo(el);
  }
  for (const el of document.querySelectorAll(".sphere-demo")) {
    if (el.dataset.mounted) continue;
    el.dataset.mounted = "1";
    mountSphereDemo(el);
  }
}

if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(mountAll);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountAll);
} else {
  mountAll();
}
