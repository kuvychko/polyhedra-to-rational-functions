// Interactive view of a piece's geometry: the solid, the unit sphere, and the zeros (blue) and
// poles (red) of its function. Drag to rotate, scroll or pinch to zoom, hover or tap a marker
// for its order and the cell it stands for.
//
// Progressive enhancement: each `.geometry-viewer` holds a static render, which stays in place
// if WebGL, the network or this script is unavailable. The data comes from
// docs/assets/pieces/<id>/geometry.json, written by scripts/a4_site_assets.py. The drawing is
// shared with the recipe comparison page (viewer-core.js).
import { createView } from "./viewer-core.js";

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

  const stage = container.querySelector(".geometry-viewer__stage") || container;
  let view;
  try {
    view = createView(stage, {
      ariaLabel: fallback ? fallback.alt : `Geometry of ${data.title}`,
      view: data.view,
    });
  } catch (error) {
    console.warn("geometry viewer: no WebGL, keeping the static image:", error);
    return;
  }
  view.show(data, data.zeros, data.poles);
  if (fallback) fallback.hidden = true;
  container.classList.add("is-interactive");

  function frame() {
    view.controls.update();
    view.render();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
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
