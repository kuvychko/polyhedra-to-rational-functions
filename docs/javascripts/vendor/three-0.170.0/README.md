# three.js 0.170.0 (vendored)

Used by `../../geometry-viewer.js`, the interactive zeros-and-poles viewer on the object pages.
It is bundled rather than loaded from a CDN, so the published site has no third-party runtime
dependency.

- **Source:** the npm package `three@0.170.0`
  (tarball sha256 `4a608a355dcaba72e0e5383cdc814303f5b6060b43c238cdf6932dceb699238d`).
- **Files:** `build/three.module.min.js` and `examples/jsm/controls/OrbitControls.js`.
- **Licence:** MIT, see `LICENSE`. Copyright 2010–2024 three.js authors.
- **One local change:** in `OrbitControls.js`, the import from the bare module name `'three'` is
  repointed to `'./three.module.min.js'`. Browsers cannot resolve a bare name without an import
  map.

To upgrade, replace both files from the new npm package, reapply the one-line import change, and
rename this folder.
