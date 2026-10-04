// The recipe comparison page (research/compare.md): two 3D views side by side, each showing one
// solid under one recipe, with zeros (blue) and poles (red). The views share one orientation:
// dragging either one turns both.
//
// The data, assets/explorer/recipes.json, is generated at build time by docs/hooks/explorer.py
// from polyhedral_functions.viewer_data, so it always matches the package. Markers carry the
// recipe's unreduced orders; "reduce by gcd" divides them by the solid's gcd for that recipe.
// The selection is kept in the URL hash, so a comparison can be linked.
import { createView, withArticle } from "./viewer-core.js";

const DATA_URL = new URL("../assets/explorer/recipes.json", import.meta.url);
const DEFAULT_VIEW = [2.2, 2.2, 1.6];
const DEFAULTS = [
  { solid: "cube", recipe: "R2" },
  { solid: "cube", recipe: "R4ve" },
];

function element(tag, attributes = {}, children = []) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(attributes)) {
    if (key === "text") el.textContent = value;
    else el.setAttribute(key, value);
  }
  el.append(...children);
  return el;
}

function select(label, options, value) {
  const control = element("select");
  for (const [key, text] of options) control.append(element("option", { value: key, text }));
  control.value = value;
  return { control, wrapper: element("label", {}, [element("span", { text: label }), control]) };
}

function plural(n, word) {
  return `${n} ${word}${n === 1 ? "" : "s"}`;
}

const CELL_PLURAL = { vertex: "vertices", face: "faces", edge: "edges" };

// "8 zeros of order 3 at vertices; 6 poles of order 4 at faces"
function groups(list, kind) {
  const counts = new Map();
  for (const m of list) {
    const key = `${m.order}|${m.cell}`;
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([key, n]) => {
      const [order, cell] = key.split("|");
      const where = n === 1 ? withArticle(cell) : CELL_PLURAL[cell] || `${cell} points`;
      return `${plural(n, kind)} of order ${order} at ${where}`;
    });
}

// "a=cube:R2&b=cube:R4ve&link=1&reduce=0", the format of the URL hash and of the
// data-compare attribute on the page's preset buttons.
function parseState(text) {
  const state = {};
  for (const part of (text || "").split("&")) {
    const [key, value] = part.split("=");
    if (key && value) {
      try {
        state[key] = decodeURIComponent(value);
      } catch (error) {
        // A malformed value is ignored.
      }
    }
  }
  return state;
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
    console.warn("recipe explorer: no data:", error);
    return;
  }

  const solidOptions = Object.entries(data.solids).map(([id, s]) => [id, s.name]);
  const recipeOptions = Object.keys(data.recipes).map((name) => [name, name]);
  const hash = parseState(window.location.hash.slice(1));

  const linkSolids = element("input", { type: "checkbox" });
  const reduce = element("input", { type: "checkbox" });
  const reset = element("button", { type: "button", class: "md-button", text: "Reset view" });
  const toolbar = element("div", { class: "recipe-explorer__toolbar" }, [
    element("label", {}, [linkSolids, " Same solid in both"]),
    element("label", {}, [reduce, " Reduce by gcd"]),
    reset,
  ]);

  const panels = [];
  const grid = element("div", { class: "recipe-explorer__panels" });
  for (const [index, side] of ["a", "b"].entries()) {
    const [solid, recipe] = (hash[side] || "").split(":");
    const state = {
      solid: data.solids[solid] ? solid : DEFAULTS[index].solid,
      recipe: data.recipes[recipe] ? recipe : DEFAULTS[index].recipe,
    };
    const solidSelect = select("Solid", solidOptions, state.solid);
    const recipeSelect = select("Recipe", recipeOptions, state.recipe);
    const stage = element("div", { class: "geometry-viewer__stage" });
    const summary = element("p", { class: "recipe-explorer__summary", "aria-live": "polite" });
    const panel = element("section", { class: "recipe-explorer__panel" }, [
      element("div", { class: "recipe-explorer__controls" }, [solidSelect.wrapper, recipeSelect.wrapper]),
      stage,
      summary,
    ]);
    grid.append(panel);
    panels.push({ side, state, solidSelect, recipeSelect, stage, summary });
  }
  linkSolids.checked = hash.link ? hash.link === "1" : panels[0].state.solid === panels[1].state.solid;
  reduce.checked = hash.reduce === "1";

  const fallback = container.querySelector(".recipe-explorer__fallback");
  container.append(toolbar, grid);
  try {
    for (const p of panels) {
      p.view = createView(p.stage, { ariaLabel: "zeros and poles", view: DEFAULT_VIEW, aspect: 0.9 });
    }
  } catch (error) {
    console.warn("recipe explorer: no WebGL:", error);
    toolbar.remove();
    grid.remove();
    return;
  }
  if (fallback) fallback.hidden = true;
  container.classList.add("is-interactive");

  function markersOf(p) {
    const entry = data.solids[p.state.solid].recipes[p.state.recipe];
    const g = reduce.checked ? entry.gcd : 1;
    const scaled = (list) => list.map((m) => ({ ...m, order: m.order / g }));
    return { entry, g, zeros: scaled(entry.zeros), poles: scaled(entry.poles) };
  }

  function refresh() {
    const shown = panels.map(markersOf);
    // One marker scale for both views, so equal orders look equal across the comparison.
    const maxOrder = Math.max(1, ...shown.flatMap((s) => [...s.zeros, ...s.poles].map((m) => m.order)));
    panels.forEach((p, i) => {
      const { entry, g, zeros, poles } = shown[i];
      const solid = data.solids[p.state.solid];
      p.view.show(solid, zeros, poles, maxOrder);
      p.view.canvas.setAttribute(
        "aria-label", `The ${solid.name} with the zeros and poles of recipe ${p.state.recipe}`,
      );
      const degree = entry.degree / g;
      const reduction = entry.gcd === 1
        ? "The orders have no common factor."
        : reduce.checked
          ? `Reduced by the gcd ${entry.gcd} (unreduced degree ${entry.degree}).`
          : `The orders share a factor ${entry.gcd}: reduced, the degree is ${entry.degree / entry.gcd}.`;
      p.summary.textContent =
        `${p.state.recipe} on the ${solid.name}: ${data.recipes[p.state.recipe]}. ` +
        `Degree ${degree}: ${[...groups(zeros, "zero"), ...groups(poles, "pole")].join("; ")}. ${reduction}`;
      p.solidSelect.control.value = p.state.solid;
      p.recipeSelect.control.value = p.state.recipe;
    });
    const hashValue = panels.map((p) => `${p.side}=${p.state.solid}:${p.state.recipe}`)
      .concat([`link=${linkSolids.checked ? 1 : 0}`, `reduce=${reduce.checked ? 1 : 0}`]).join("&");
    try {
      history.replaceState(null, "", `#${hashValue}`);
    } catch (error) {
      // Some embedded contexts refuse history changes; the page still works.
    }
  }

  for (const p of panels) {
    p.solidSelect.control.addEventListener("change", () => {
      p.state.solid = p.solidSelect.control.value;
      if (linkSolids.checked) for (const q of panels) q.state.solid = p.state.solid;
      refresh();
    });
    p.recipeSelect.control.addEventListener("change", () => {
      p.state.recipe = p.recipeSelect.control.value;
      refresh();
    });
  }
  linkSolids.addEventListener("change", () => {
    if (linkSolids.checked) panels[1].state.solid = panels[0].state.solid;
    refresh();
  });
  reduce.addEventListener("change", refresh);

  function apply(state) {
    for (const p of panels) {
      const [solid, recipe] = (state[p.side] || "").split(":");
      if (data.solids[solid]) p.state.solid = solid;
      if (data.recipes[recipe]) p.state.recipe = recipe;
    }
    if (state.link) linkSolids.checked = state.link === "1";
    if (state.reduce) reduce.checked = state.reduce === "1";
    refresh();
  }
  // Preset comparisons in the page text: <button data-compare="a=...&b=...">.
  document.querySelectorAll("[data-compare]").forEach((button) => {
    button.addEventListener("click", () => {
      apply(parseState(button.dataset.compare));
      container.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Shared orientation: the view being dragged leads, and the other copies its camera each
  // frame. A view that stops leading first settles its damping, so it cannot drift back.
  let leader = panels[0];
  for (const p of panels) {
    p.view.controls.addEventListener("start", () => {
      if (leader !== p) {
        const old = leader.view.controls;
        old.enableDamping = false;
        old.update();
        old.enableDamping = true;
        leader = p;
      }
    });
  }
  reset.addEventListener("click", () => {
    for (const p of panels) p.view.resetCamera();
  });

  refresh();
  function frame() {
    leader.view.controls.update();
    for (const p of panels) {
      if (p !== leader) {
        p.view.camera.position.copy(leader.view.camera.position);
        p.view.camera.quaternion.copy(leader.view.camera.quaternion);
      }
      p.view.render();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function mountAll() {
  document.querySelectorAll(".recipe-explorer").forEach((el) => mount(el));
}

if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(mountAll);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", mountAll);
} else {
  mountAll();
}
