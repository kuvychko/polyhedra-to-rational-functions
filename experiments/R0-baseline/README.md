# R0-baseline: the existing Klein-invariant ornaments

- **Question:** what exactly do the existing polyhedral ornaments compute, and can they be
  reproduced here?
- **Status:** reference, complete.
- **Source:** figures_repo @ `292bec4`, `2026/09-20-riemann-ornaments/polyhedral/`, built on
  complexplorer 3.1.0.
- **Code:** `src/polyhedral_functions/baseline/`. **Checks:** `tests/baseline/`.
  **Audit:** `notes/2026-09-30-baseline-audit.md`.

## Contents

| file | what it is |
|---|---|
| `manifest.json` | the source's STL manifest, verbatim: resolution, transfer, normalization constant and per-size printability facts for all six pieces |
| `renders/*.png` | the source's relief renders, downscaled from 2000 px to 800 px |
| `portraits/*.png` | the source's phase portraits, downscaled to 800 px wide |

The meshes are not committed. To rebuild the reference piece and compare it with the manifest,
run `uv run pytest -m slow`.

## Result

All six pieces reproduce: settings and normalization constants match the manifest, and the
cube-octahedron-dual mesh matches its recorded triangle count, volume and radii. See the
audit for findings, including the 0.55% normalization sampling error on cube-octahedron-dual
and the fact that the three "dual" pieces are exactly recipes R1/R2 on Platonic inputs.
