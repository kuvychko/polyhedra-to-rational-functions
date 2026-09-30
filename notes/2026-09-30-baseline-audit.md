# 2026-09-30: Audit of the existing polyhedral ornaments (R0)

This audit covers `PROGRAM.md` §4. Its subject is the riemann-ornaments generator in
figures_repo @ `292bec4` (folder `2026/09-20-riemann-ornaments/`, clean tree at that commit).
The polyhedral subset is now frozen in `src/polyhedral_functions/baseline/`, and its checks run
in `tests/baseline/`.

Claim labels: **[E]** established background, **[D]** derived here, **[N]** numerical
observation, **[I]** implementation or design choice, **[U]** unverified.

## 1. Inventory

| component | source file | now | role |
|---|---|---|---|
| Klein forms `PHI PSI V F E ICO_V ICO_H ICO_T` | `ornaments.py` | `baseline/forms.py` | the polynomials whose roots are the features |
| six polyhedral presets, normalization, `prepare`, `generator` | `ornaments.py` | `baseline/ornaments.py` | the functions, their constants and relief settings |
| closing and measuring the relief mesh | `meshtools.py` | `baseline/meshtools.py` | watertight solid, printability facts |
| math checks | `verify_math.py` | `tests/baseline/` | roots, syzygy, invariance, normalization, pole orders |
| STL driver, renders, portraits, README builder | `make_stl.py`, `renders_pv.py`, `portraits.py`, `build_readme.py` | not copied | drivers. Their settings are recorded below; to be re-created as `scripts/` when needed |
| seven non-polyhedral pieces (dipole, flowers, filters, ...) | `ornaments.py` | not copied | out of scope |
| STL, 3MF slicer cuts, gcode | `polyhedral/stl/` | not copied | large or hand-made. Cut files exist for 4 pieces, which suggests they were printed |

**Dependencies:** numpy, pyvista, matplotlib, and **complexplorer 3.1.0 from PyPI**. It is a public
release, so there is no unreleased dependency. complexplorer 3.1 ships the same eight forms in
`complexplorer.core.polyhedral`, and they agree with the baseline's to rounding
(`test_forms_match_complexplorer`).

**Coordinates [I]:** complexplorer's chart puts `z = 0` at the south pole and `∞` at the north
pole. The octahedron has vertices on the axes (one at `∞`). The icosahedron has a vertex at the
north pole with rings at `z = ±1/√5` on the sphere. The cube's vertices are `(±1,±1,±1)/√3`.

## 2. Divisors, infinity, normalization, radial mapping

| piece | f | zeros (order) | poles (order) | degree | at ∞ |
|---|---|---|---|---|---|
| tetrahedral-dual | Φ/Ψ | tetrahedron (1) | antipodal tetrahedron (1) | 4 | regular point |
| octahedral-crown | E/V² | 12 octahedron edge midpoints (1) | 6 octahedron vertices (2) | 12 | pole of order 2 (poly degrees 12 vs 10) |
| cube-octahedron-dual | V⁴/F³ | 6 octahedron vertices (4) | 8 cube vertices (3) | 24 | zero of order 4 (20 vs 24) |
| icosahedral-crown | T²/V⁵ | 30 edge midpoints (2) | 12 icosahedron vertices (5) | 60 | pole of order 5 (60 vs 55) |
| dodecahedron-icosahedron-dual | V⁵/H³ | 12 icosahedron vertices (5) | 20 dodecahedron vertices (3) | 60 | zero of order 5 (55 vs 60) |
| icosidodecahedral-star | H³/T² | 20 dodecahedron vertices (3) | 30 edge midpoints (2) | 60 | regular point |

- **Infinity [D]:** wherever a solid has a feature at the north pole, the drop in polynomial
  degree encodes exactly that feature (`V` and `ICO_V` have binary degree one more than their
  polynomial degree). So in every piece the chart's behavior at `∞` is a genuine vertex, never an
  accidental extra feature. This is the property `PROGRAM.md` §8 asks for, but it is achieved by
  choosing the orientation, not by homogeneous evaluation.
- **Symmetry [E]/[N]:** each ratio has equal binary degree, so `|f|` is invariant under the
  rotation group. That is checked numerically for generators of T, O and I (`test_*_invariance`).
  The degree-60 floor for icosahedral invariants follows from the quotient map
  `S² → S²/I` having degree 60 **[E, to cite]**. Klein's syzygy `H³ − T² = 1728 V⁵` holds
  **[E; checked N]**.
- **Normalization [I + D]:** by default, `f` is scaled by `c` so the area-weighted geometric mean
  of `|c f|` over the sphere is 1. It is computed by sampling on complexplorer's lat/long grid
  at resolution 400. It has the closed form
  `c = (1/|A|) ∏ √(1+|p|²) / ∏ √(1+|z|²)` over finite zeros and poles, and it is self-dual
  (`1/f` gets `1/c`).
  - **[D, sketch, verify in M3]:** for a balanced divisor this normalized modulus is exactly
    `∏ χ(z,aᵢ)^mᵢ / ∏ χ(z,bⱼ)^nⱼ`, where `χ` is the chordal distance. The `(1+|z|²)` factors cancel
    because the total orders agree, and so do the per-point averages of `log χ`. The
    chordal-product magnitude baseline in `PROGRAM.md` §8 is therefore the baseline's own
    normalization, which makes it a natural default to carry forward.
- **Radial mapping [I]:** complexplorer's `logarithmic` transfer is
  `r = r_min + (r_max − r_min)·logistic(log|f| / k)` with `r_min = 0.2`, `r_max = 1`, and sea level
  at `|f| = 1`. `k = 2·pole_order`, capped at 6, fixes the tip exponent `μ/k` at 1/2. Only
  tetrahedral-dual uses the two-scale `log_mixture` (boost 4, weight 0.6). Both transfers are
  odd in `log|f|`, so the relief of `1/f` is the relief of `f` turned inside out **[D]**.
- **Phase [I]:** renders use `OklabPhase(phase_sectors=12)`. The phase of `c·f` is untouched
  by normalization because `c > 0`. No phase convention is chosen beyond that.

## 3. Reusable components

- `baseline/forms.py` and `complexplorer.core.polyhedral.polyhedral_features`: exact
  Platonic point sets in the chart. These are fixtures for M2 and reference divisors for M3.
- The closed-form normalization is the model for `normalization.py`.
- `meshtools.close_relief` / `inspect_mesh`, together with complexplorer's `OrnamentGenerator`,
  `scale_to_size(axis="extent")` and `max_extent`, form the mesh and export path for
  `meshes.py`.
- Render settings to reproduce in `rendering.py`: `OklabPhase(12, auto_scale_r=True)`, a
  2000×2000 off-screen window, a white background, the view directions `POLYHEDRAL_VIEW` and
  `ICOSAHEDRAL_VIEW`, and framing ×1.25 after `reset_camera`.

## 4. Regression reference

`experiments/R0-baseline/` holds the source's `manifest.json` verbatim (all six pieces), and
800 px copies of the six renders and phase portraits.

- `test_relief_settings_match_recorded_run` re-derives resolution, transfer, sharpness and
  normalization constant for all six pieces and matches the manifest.
- `test_cube_octahedron_dual_mesh_matches_recorded_run` (marked `slow`, about 3 s) rebuilds
  the reference piece and matches its triangle and point counts, and its 80 mm extent, radii,
  volume and area, to 0.1.
- Photographs of the printed pieces: **not yet located.** 3MF and gcode cuts exist for
  tetrahedral-dual, cube-octahedron-dual, icosahedral-crown, dodecahedron-icosahedron-dual and
  icosidodecahedral-star. Ask the owner which pieces were printed and whether photos exist.

## 5. Findings

1. **Normalization accuracy [N].** The source says the sampled constants land "within ~0.4%" of
   the closed form. Its check script never covered cube-octahedron-dual, and that piece is at
   0.55%: sampled 183.25 against the exact 729/4 = 182.25 **[D]**. The error falls as O(1/N) with
   resolution (1.18%, 0.55%, 0.23%, 0.07% at 200, 400, 800, 1600). It is convergence, made worst by
   order-4 zeros at both grid poles, not a wrong formula. The effect on the printed piece is
   below print resolution. Lesson for new code: **use the closed form**, not sampling.
2. **R0 relates to R1/R2 [D, verify algebraically in M3].** For a regular polyhedron with
   Schläfli symbol {p, q}, R2 puts order q at vertices and order p at face directions. R1 uses
   orders `F/g` and `V/g`. Since `qV = 2E = pF`, the two ratios are equal, and after gcd
   reduction **R1 and R2 coincide on every Platonic solid.** The polar-dual face directions of
   a centred Platonic solid are its dual's vertex directions. So:
   - tetrahedral-dual = R1 = R2 of the tetrahedron;
   - cube-octahedron-dual `V⁴/F³` = R1 = R2 of the **octahedron** (valence 4, triangles), and
     the reciprocal of the recipe applied to the cube;
   - dodecahedron-icosahedron-dual `V⁵/H³` = R1 = R2 of the **icosahedron**, and the reciprocal
     of the recipe applied to the dodecahedron.

   So the R0 "duals" are exactly the R1/R2 recipe on Platonic inputs. **They cannot tell R1 and
   R2 apart.** The first corpus member that can is the deltoidal icositetrahedron (spec §7 table:
   312 vs 96), which makes it the key fixture for M4.
3. **Crowns and star are a different construction [D].** octahedral-crown, icosahedral-crown and
   icosidodecahedral-star place features at **edge midpoints**, which neither R1 nor R2 uses.
   They are a third family (vertex–edge or face–edge). `PROGRAM.md` §7 says to add point sets
   only to answer a specific question, so for now they stay as R0 references, not candidates.

   *Update (same day):* the owner decided to explore this family deliberately. It is now
   recipe **R4** (`PROGRAM.md` §7, decision 0002). The vertex–edge recipe reproduces all three
   pieces: octahedral crown = octahedron (4:2 → 2:1), icosahedral crown = icosahedron (5:2),
   star = dodecahedron (3:2), equivalently face–edge on the icosahedron **[D]**.
4. **Unverified symmetry claims [U].** The source's checks cover rotations only. The following
   are claimed but never checked:
   - "full O_h / I_h including mirror planes";
   - the tetrahedral-dual chirality claim that every mirror swaps spikes and pits.

   Reflections act antiholomorphically, so `|f|` invariance under them needs its own test. Add
   one when `diagnostics.py` exists.
5. **Orientation trap [E/N].** The commonly quoted icosahedral coefficient signs mix
   orientations. Each form is a correct solid on its own, but no ratio is invariant. The
   syzygy catches this. New recipes that build forms from geometry avoid it by construction,
   but the test should stay.

## 6. What is established, chosen or unverified

- **Established (citations still to be attached):** Klein's relative invariants and syzygy; the
  degree-60 minimum for icosahedral invariants; relative invariants of equal degree giving
  invariant `|f|`. The references in `PROGRAM.md` §16 (Nash) are the starting point.
- **Implementation choices:**
  - the orientation of each solid;
  - which form sits in the numerator;
  - geometric-mean normalization;
  - the logistic transfer with `k = 2·pole_order` capped at 6, `r_min = 0.2`, and the
    `log_mixture` boost;
  - tip-to-tip sizing at 80 and 130 mm;
  - views and colormap.
- **Unverified or historical:**
  - "Klein duals" as a name for the pieces;
  - the reflection-symmetry and chirality claims (finding 4);
  - the claim that the renders match the printed objects (no photos yet).
