# 2026-10-01: Recipes and diagnostics (M4)

This covers `PROGRAM.md` §5, §7 and §9. Code is in `recipes.py`, `diagnostics.py` and
`Polyhedron.symmetry_group`. Tests are in `tests/test_recipes.py` and
`tests/test_diagnostics.py`. `tests/incidence.py` stays as an independent construction that the
recipes are checked against.

## What is implemented [I]

- **R1 (uniform)**, and the **incidence family** `a·D_ve + b·D_fe`, with the presets R2 (1,−1),
  R4ve (1,0), R4fe (0,1) and flag (1,1). R3 is not implemented, since no weakness has called
  for it yet (`PROGRAM.md` §9, step 6).
- **Placement** is a recipe setting: faces `polar | centroid`, edges `foot | midpoint`.
- `apply` coalesces and reports any zero–pole meeting between different cells. There are none
  anywhere in the corpus. It then reduces by the gcd and returns a manifest `record()`.
- **Diagnostics:**
  - local orders by winding, including the point at ∞;
  - symmetry preservation over the polyhedron's full group (rotations and reflections about
    the origin);
  - duality against the predicted partner, with magnitude and phase residuals;
  - rotation residual;
  - per-degree field comparison with reported exclusion caps.

## Results [N, all by tests]

**Polarity.** With polar/foot placement, incidence `(a, b)` on `P*` equals `(b, a)` on `P`
**[D]**. This holds exactly on all 11 fixtures for all five presets, with log-magnitude residual
about 1e-14:

| recipe | on the polar dual |
|---|---|
| R1, R2 | the reciprocal function. Phase is also exact (`arg f* = −arg f`, about 1e-13) |
| R4ve, R4fe | each other |
| flag | **the same function** |

So only R1 and R2 meet the §5 duality criterion literally. R4 has a "variant swap" duality, and
the flag recipe cannot tell a polyhedron from its dual at all. That is a real loss of
information, to weigh in the comparison.

**Placement and polarity.** Centroid placement breaks R2's duality on every fixture where the
centroid differs from the polar direction. Midpoint placement breaks R4's duality unless edge
endpoints are equidistant from the origin in **both** `P` and `P*`. That means `P` must be
inscribed *and* have equidistant adjacent faces, which only the Platonic solids satisfy here.
I first predicted that "inscribed" was enough. The pyramid and the rhombicuboctahedron
disproved that: their duals are not inscribed.

**Symmetry.** All five presets, in both placements, preserve the full symmetry group of every
fixture, including reflections. Every construction is equivariant. Symmetry therefore cannot
discriminate between these recipes; only recipes that break equivariance (e.g. R3 tie-breaking)
could fail it.

**Local orders.** Phase winding matches the declared order for every feature (11 fixtures × 5
recipes), including features at ∞.

**Rotation.** Rebuilding a recipe on a rotated input gives the rotated divisor (exactly) and
field (residual below 1e-9) for R1, R2 and R4ve in both placements.

## Audit finding 4: the baseline's mirror claims

All six R0 pieces have their **full** groups, with half of the elements improper:

| piece | group |
|---|---|
| tetrahedral-dual | T_d (24) |
| octahedral-crown, cube-octahedron-dual | O_h (48) |
| icosahedral-crown, dodecahedron-icosahedron-dual, icosidodecahedral-star | I_h (120) |

**The baseline README is wrong about tetrahedral-dual.** It calls the piece chiral ("T, order
12, rotations only -- no mirror plane fixes it") and says its halves are not congruent.
Instead:

- **It has six mirror planes**, the tetrahedron's own (e.g. `x = y`). Checked directly on the
  baseline function: `|f|` is invariant to 1e-15.
- **Only the cube's coordinate mirrors turn it inside out.** Those mirrors (e.g. `x = 0`) are
  not symmetries of the tetrahedron, and they map `|f|` to `1/|f|`. This is probably what the
  README generalized from.
- **Its halves are congruent.** For the suggested cut (`z = 0`, perpendicular to a 2-fold
  axis), the half-turn about the x-axis is a symmetry that swaps the halves. One file printed
  twice makes the piece.

The frozen baseline keeps its original text. This note and `experiments/R0-baseline/README.md`
record the correction.

## Consequences

- Decision 0004: polar/foot placement is the default because it is the only one that commutes
  with polarity. Centroid/midpoint stay available as controlled comparisons.
- Symmetry preservation is not a discriminating criterion among the current candidates.
  Duality, degree, interpretability and the field comparisons are.
- Next is M5: the comparison atlas (rendering adapters, run manifests, standard panels).
