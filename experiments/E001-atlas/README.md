# E001-atlas: standard comparison panels across the corpus

- **Question:** across the corpus, how do the candidate recipes differ: in degree, in duality
  and symmetry behaviour, and in the shape of their magnitude fields?
- **Hypothesis (from the M3/M4 screens):** R1 and R2 differ in shape only where valences or face
  sizes vary strongly; R4 differs from R2 everywhere; placement matters only on the irregular
  solids and the pyramid.
- **Changed factor:**
  - recipe (R1, R2, R4ve, R4fe, flag), with polar/foot placement;
  - placement, with multiplicities fixed (R2 centroid faces; R4ve midpoint edges).
- **Fixed:**
  - display settings (`configs/experiments/E001-atlas.json`): relief sharpness 4, depth 0.2,
    OkLab phase with 12 sectors;
  - chordal normalization;
  - views per fixture.

  This is a fixed-display comparison: no view is tuned per recipe.
- **Status:** complete. Run from clean commit `28645f0` (`manifest.json` → `code`).
- **Reproduce:** `uv run python scripts/make_atlas.py --publish`. It takes about three minutes.
  Full-resolution sheets and tiles go to `out/E001-atlas/`.

## Contents

| file | what it is |
|---|---|
| `manifest.json` | config snapshot, commit, package versions, fixture hashes, all 55 run records (recipe settings, divisor summary, windings, duality, symmetry, comparison against R2, near pairs) and every output's hash |
| `metrics.csv` | one row per fixture × recipe |
| `sheets/<fixture>-recipes.jpg` | per recipe: geometry with zeros and poles, plane portrait, colored sphere, colored relief, neutral relief, `log|f|/degree` map |
| `sheets/<fixture>-differences.jpg` | per-degree difference maps: each recipe against R2, and each placement variant against the default |

## Observations

**Exact checks (55/55 runs).** Every run passes all four:

- every local order matches its winding, including features at ∞;
- every recipe meets its predicted duality (residuals ≤ 1e-13);
- every recipe's divisor, and so its relief `|f|`, is invariant under the fixture's full
  symmetry group (the function itself can pick up a phase character; see the narrative, §6);
- no zero–pole cancellations occur anywhere.

These checks pass for all recipes alike, so none of them separates the recipes.

**Degree.**

| fixture | R1 | R2 | R4ve | R4fe | flag |
|---|---|---|---|---|---|
| Platonic (cube/oct, ico/dod) | = R2 | 24, 60 | 12–60 | 12–60 | 2× |
| rhombicuboctahedron / DI | 312 | 96 | 48 / 96 | 96 / 48 | 192 |
| triakis tetrahedron | 24 | 12 | 36 | 36 | 72 |
| hexagonal pyramid | **7** | 8 | 24 | 24 | 48 |
| irregular-9 | 126 | 42 | 42 | 42 | 84 |
| irregular-mixed | 99 | 36 | 36 | 36 | 72 |

R2 is the cheapest of R1/R2 everywhere except the pyramid. R4 can be cheaper than R2 (octahedron
R4ve 12, rhombicuboctahedron R4ve 48) or much dearer (pyramid, triakis tetrahedron).

**Shape (correlation with R2, per degree, 3° caps).**

- **R1 vs R2:** ≥ 0.98 except the pyramid (0.83) and the triakis tetrahedron and irregular-mixed
  (0.96). That confirms the screen.
- **R4ve vs R2:** 0.55–0.92.
- **R4fe vs R2:** negatively correlated (−0.29 to −0.92). It puts faces on the zero side.
- **flag:** roughly uncorrelated with R2.

**The visible R1/R2 difference is mostly display [N, design-relevant].** On the DI, the two
recipes' per-degree maps are nearly indistinguishable. Under the fixed display, though, R1
(orders 12–13) renders as rounded lobes and R2 (orders ≤ 4) as sharp spikes, because the tip
exponent is order/sharpness. A per-recipe sharpness (`k ∝ order`, the baseline's rule) would
largely remove that difference. That would be a tuned view, and has to be labelled as one.

What does **not** depend on the display is phase density. R1's portraits and spheres wind 3×
as often (312 vs 96 on the DI; 126 vs 42 on irregular-9), and the phase coloring becomes hard
to read. That is degree economy as a readability cost.

**R4 is sensitive to short edges and small faces [N, new].** On irregular-9, R4ve places 6
zero–pole pairs within chordal distance 0.1 (0.039–0.092): a short edge's foot sits close to its
endpoint vertices. R4fe has 3 such pairs (small faces near edge feet). irregular-mixed has 3
under R4fe. R2 has none anywhere. Each pair shows as a tight dipole in the portrait, and in a
print it would be a spike beside a pit. It is a stability question for M6: what happens to R4
as an edge shrinks to zero length, which is exactly a combinatorial transition.

**Placement.**

- **R2, centroid vs polar:** 0.53 on irregular-9, 0.60 on the pyramid, 0.99 on the DI. The
  differences are broad, regional shifts, not local ones.
- **R4ve, midpoint vs foot:** 0.66 on irregular-9, 0.58 on the triakis tetrahedron, 1.0 on
  inscribed solids.

This confirms the M4 conditions. Placement is a large effect exactly where the solid is far from
canonical.

## Conclusions

1. Among R1 and R2, the choice is **degree economy and phase readability**, not shape. R2 is
   the better default except in rare low-degree cases like the pyramid, where R1 is one degree
   cheaper.
2. **R4 is a genuinely different construction** (edges as features) with a variant-swap duality.
   It is attractive on symmetric inputs, as the baseline crowns and star show. On irregular
   inputs its short-edge dipoles are a liability worth studying in M6.
3. **The flag recipe** cannot distinguish a polyhedron from its dual and costs twice the degree.
   It is low priority.
4. **Fixed-display comparisons overstate the R1/R2 difference.** M6 should add explicitly tuned
   views (sharpness by order, or `|f|^(1/d)` display compression) next to the fixed ones.
5. **Display tweak for later runs:** `map_limit` 0.75 leaves the per-degree maps pale. Most
   values sit within ±0.3.

## Feeds into

M6 controlled experiments:

- R4 under edge shrinkage (combinatorial transition);
- fixed-combinatorics deformation (prism or pyramid height);
- tuned vs fixed display;
- R2 placement on irregular solids.
