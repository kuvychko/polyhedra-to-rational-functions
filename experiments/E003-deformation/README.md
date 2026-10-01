# E003-deformation: fixed-combinatorics deformation and placement

The planned "E005 placement on irregular solids" is folded in here. The sheared box crosses the
placement threshold in a controlled way, which a fixed irregular fixture cannot.

- **Question:** under fixed-combinatorics deformation:
  - do the recipes change continuously?
  - how do the R1/R2 and placement separations evolve?
  - when does polar/foot placement stop putting a cell's feature over the cell?
- **Hypothesis:**
  - Every recipe is continuous.
  - R1~R2 separation is set by the combinatorics, so it is roughly constant.
  - Placement separation grows with distortion.
  - On the sheared box, polar and foot placement leave their face and edges exactly at `|σ| = 1`;
    centroid and midpoint never do.
- **Changed factor:** one parameter per family:
  - `hexagonal_pyramid(h)`: apex height `h` from 0.15 to 4, reference `h = 1`;
  - `sheared_box(σ)`: shear `σ` from 0 to 2.5, reference `σ = 0`.
- **Status:** complete. Run from clean commit `860b82e`; its code is identical to `7c929c7`.
  Reproduce with `uv run python scripts/e003_deformation.py --publish`.
- **Files:**
  - `deformation.csv`;
  - `deformation.jpg`: continuity, separations and placement margins against the parameter;
  - `geometry.jpg`: R2 poles at polar directions against centroids, at three parameters per
    family;
  - `manifest.json`.

## Results

**Continuity: confirmed.** Every recipe's residual against the reference is smooth and zero at
the reference, and the per-step ratios in the CSV stay bounded.

**R1~R2 is not constant at fixed combinatorics: hypothesis refuted [N].**

- **Pyramid:** R1~R2 falls from 0.96 (flat pyramid, `h = 0.15`) to 0.57 (`h = 4`).
- **Why:** the orders are fixed (R1: all 1; R2: apex and hexagon 2, the rest 1), but the
  reweighted features (the apex zero and the hexagon pole) move. Their influence on the field
  depends on where they sit relative to everything else.
- **Sheared box:** R1 = R2 for every `σ` (every valence 3, every face a quadrilateral), as
  expected.

**Placement separation is not monotone in distortion [N].**

- **Pyramid, R2 polar~centroid:** negative for flat pyramids (−0.60 at `h = 0.15`), peaking at
  0.965 near `h = 1.3`, then falling again (−0.12 at `h = 4`). Somewhere near that peak, each
  side triangle's perpendicular foot coincides with its centroid.
- **Pyramid, R4ve foot~midpoint:** exactly 1 at `h = 1`, where the pyramid is inscribed and foot
  = midpoint, and drops on both sides.
- **Sheared box:** placement separation reaches its minimum (≈0.15) near `σ = 1` and partly
  recovers beyond it.

**Placement threshold: confirmed exactly.**

- **Sheared box:** at `σ = 1.1` the two horizontal faces' polar directions leave their face cones
  and four edge feet leave their edges. At `σ = 0.9` none do.
- **Centroids and midpoints:** never leave their cells, by construction.
- **Pyramid:** never crosses the threshold over the tested range.
- **Corpus:** among the fixtures only irregular-9 crosses it (2 faces, 2 edges).

## What this means

- **Placement is a real trade-off.**
  - Polar/foot placement gives exact duality (decision 0004), but on strongly oblique solids it
    can put a face's pole outside the face it represents.
  - Centroid/midpoint placement always stays inside its cell, but breaks duality.

  Neither dominates. The choice depends on whether interpretability ("this spike *is* that
  face") or duality matters more. That is a design decision for the exit record.
- **R1 vs R2 depends on geometry too.** On a solid with uneven valences, how different R1 and R2
  look depends on the geometry as well as the combinatorics.
