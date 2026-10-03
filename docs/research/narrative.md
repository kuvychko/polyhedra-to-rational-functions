# Polyhedra as complex functions: an exploration

*Draft, 2026-10-01; revised 2026-10-03 after review. Phase 1 complete; to be revised for Phase 2.*

Claims are labelled **[E]** established background, **[D]** derived here, **[N]** numerical
observation, **[C]** conjecture, **[P]** design preference. Every numerical claim points to a
reproducible experiment in `experiments/`.

## 1. The question

A convex polyhedron is a finite, rigid object: points, edges, flat faces. A rational function on
the Riemann sphere is also determined by finitely many points: its zeros and poles, with integer
multiplicities, fix it up to a constant factor **[E]**. That suggests a translation. Place zeros
and poles according to the polyhedron, and study the function that results.

The function can be seen in two ways. Its phase colors the sphere (domain coloring). Its modulus
can push the sphere radially in and out, giving a relief: poles become spikes, zeros become pits.
That relief can be printed. Six such objects existed before this project started, built from
Klein's classical invariants of the Platonic groups.

The question is not whether this can be done, but how to do it well. Which recipe keeps the
polyhedron recognizable? What does each recipe cost? Where does each one fail?

## 2. The construction space

A recipe has two parts **[P]**:

- **placement:** which points on the sphere stand for which cells of the polyhedron;
- **multiplicities:** which integer order each point gets.

**Placement.** The natural points are:

- the directions of the vertices;
- the directions of the polar dual's vertices, i.e. the face normals;
- the projected face centroids;
- for edges, either the foot of the perpendicular from the origin or the projected midpoint.

**Duality.** Polar duality with respect to the unit sphere exchanges vertices and faces and maps
edges to edges **[E]**. The face normals and the edge feet are the two choices that commute with
it **[D]**.

**Normalization.** The constant in front of `f` matters for a relief, because it sets "sea
level". Using chordal distance on the unit sphere, a balanced divisor determines the modulus
exactly: `log|f| = Σ mᵢ log χ(x, aᵢ)` **[D]**. That modulus is:

- self-dual: the negated divisor gives `1/|f|`;
- rotation-covariant;
- of geometric mean 1 over the sphere, since the mean of `log χ(x, a)` is `log 2 − 1/2` for
  every `a`.

The existing ornaments had fixed the constant by sampling that geometric mean; this formula
reproduces their normalization exactly **[N]**, to 1e-8.

**Multiplicities: unreduced by convention.** A recipe is defined by its **unreduced** divisor:
valences, side counts and edge orders exactly as counted. Dividing every order by their gcd
lowers the degree, but it takes a `g`-th root of the function, and `g` depends on the solid.
Therefore:

- every identity between recipes is stated for unreduced divisors, as is every comparison
  across a combinatorial transition and between a solid and its dual;
- between independently reduced divisors, an identity holds only up to powers;
- reduction can also break continuity. Reduced R4fe jumps at the raised-face transition, because
  the cube's gcd is 2 and the raised cube's is 1, while the unreduced divisors converge **[N]**.

Degrees quoted in tables are reduced degrees, used as a measure of economy for one solid
(`RecipeResult.unreduced` gives the defining divisor).

**Information lost.** The radial projection discards distances. A cube and a stretched box with
the same face normals give the same face points. No recipe here claims to reconstruct the solid.

## 3. The first obstacle: balance

A rational function has as many zeros as poles, counted with multiplicity, including at infinity
**[E]**. Zeros at the 8 cube vertices and poles at the 6 face directions don't balance with equal
orders. Two simple fixes:

- **R1, uniform:** order `F` at every vertex and `V` at every face.
- **R2, incidence:** order = valence at each vertex and = number of sides at each face. Both sides
  total `2E`, because each count goes through edge incidences **[E]**.

On the cube, both give `V⁴/F³`-type degree-24 functions. They are exactly the existing
"cube–octahedron dual" ornament, up to which side is called zeros **[N]**.

## 4. Competing recipes

R2 counts vertex–face incidences. The existing crown and star ornaments suggested counting
**vertex–edge** and **face–edge** incidences instead: order = valence or sides, and 2 at each edge
point. That is **R4** (R4ve, R4fe). The three are linked by an exact identity between the
unreduced divisors:

`D_R2 = D_R4ve − D_R4fe`, i.e. `f_R2 = C · f_R4ve / f_R4fe` **[D, confirmed N on all 11 solids]**

After each side is reduced by its own gcd, this becomes a relation between powers,
`f_R2^g₂ = C · f_R4ve^g_ve / f_R4fe^g_fe`. So the incidence recipes form a two-parameter family
`f_ve^a · f_fe^b` of unreduced functions, with R2 at `(1, −1)`.
The "flag" recipe `(1, 1)`, vertices and faces against edges, is another member. Polarity maps
`(a, b)` on a solid to `(b, a)` on its dual **[D]**. Consequences:

- R1 and R2 give the reciprocal function on the dual;
- R4ve and R4fe swap;
- the flag recipe gives the *same* function for a solid and its dual, so it cannot tell them apart.

These hold for unreduced divisors, and also after reduction. In each case the dual's divisor is
the primal's, negated or relabelled, so the gcd is the same on both.

All six existing ornaments turned out to be recipe outputs **[N]**: R1 = R2 on the tetrahedron,
octahedron and icosahedron, and R4ve on the octahedron, icosahedron and dodecahedron.

## 5. Experiments that changed our view

**The Platonic solids cannot decide anything.** Every candidate coincides on them **[D]**:

- R1 = R2, because all valences are equal and all faces are the same size;
- face centroids sit on the face normals, and edge midpoints on the feet.

The corpus therefore had to grow with members chosen for what they separate:

- a hexagonal pyramid, for valence spread;
- a triakis tetrahedron, symmetric but with separated edge placements;
- two irregular solids.

The deltoidal icositetrahedron, the obvious next example, barely separates the placements:
0.9° on every kite **[N]**.

**R1 and R2 are nearly the same shape.** Divided by its degree, each is the potential of "vertex
points minus face points", weighted uniformly for R1 and by incidence for R2 **[D]**. They
correlate at 0.96–0.99 on most solids. Only strong valence spread separates them (0.83 on the
pyramid) **[N]** (E001). The real differences are reduced degree, which is up to 3.25× smaller
for R2 on the tested solids, and phase readability.

**The display had been exaggerating.** Under one fixed relief sharpness, high-order R1 renders as
rounded lobes and R2 as spikes. Tuning sharpness to each recipe's highest order removes most of
that: the deltoidal icositetrahedron's relief correlation rises from 0.950 to 0.991 **[N]**
(E004). Phase cannot be tuned away. R1 winds about three times as often, and its coloring becomes
hard to read.

**R4 is genuinely different.** Its correlation with R2 is 0.55–0.92, whatever the display **[N]**
(E001, E004). On irregular solids it places zeros and poles very close together at short edges
**[N]**. That first looked like a defect.

## 6. Symmetry and deformation

**Symmetry of the relief.** The test was:

- for every element `g`, proper or improper, of each solid's symmetry group about the origin,
  the recipe's divisor is mapped exactly onto itself;
- under the chordal normalization `|f|` depends only on the divisor, so that is the same as
  `|f(gx)| = |f(x)|`: the relief is symmetric.

It held for every recipe, in both placements, on every fixture **[N]** (E001, 55 of 55 runs). It
holds for any input, because every placement rule is equivariant under orthogonal maps that fix
the origin **[D]**. So relief symmetry cannot choose between the recipes.

It did correct a claim. The existing "tetrahedral dual" piece was described as chiral, and it is
not: it has the tetrahedron's six mirror planes, and its cut halves are congruent **[N]**.

**Symmetry of the function is weaker.** If a rotation `g` preserves the divisor, then `f(gx)/f(x)`
has no zeros or poles and modulus 1. So `f(gx) = e^{iθ_g} f(x)` exactly. For a reflection,
`f(gx) = e^{iθ_g} · conj f(x)` **[D]**. The relief is unchanged, but the phase colors can shift.
The angle `θ_g` does not depend on the chart or the constant. The measured values are exact to
about 1e-13 **[N]** (`diagnostics.character_report`):

| inputs | θ_g |
|---|---|
| icosahedron and dodecahedron, all recipes | `θ_g = 0`: `f` itself is invariant, as it must be, since the icosahedral rotation group has no nontrivial one-dimensional characters **[E]** |
| cube, octahedron, rhombicuboctahedron, deltoidal icositetrahedron, under R1 and R2 | 0 throughout |
| cube and octahedron, under one R4 variant each | signs (`θ = π`) on some elements |
| tetrahedron (including the existing tetrahedral dual) and triakis tetrahedron, under R2 | cube roots of unity (`θ = ±2π/3`) on rotations and reflections, e.g. on the tetrahedron's eight three-fold rotations; R1 does the same on the tetrahedron |
| tetrahedron and triakis tetrahedron, under R4 | signs, on reflections only |
| hexagonal pyramid | cube roots under R2; sixth roots under R1; R4 and flag invariant |
| flag recipe, every fixture | 0 throughout |

A symmetric relief can therefore carry phase coloring that is not symmetric.

**Continuous deformation.** With combinatorics fixed and the origin kept inside, every recipe
should change continuously. Orders stay fixed and every placement point moves continuously
**[D]**. Both tested families behaved this way **[N]** (E003). Two results went against
expectation:

- How far apart R1 and R2 look depends on geometry, not only on combinatorics (0.96 to 0.57
  along the pyramid family).
- Polar placement can put a face's pole **outside the face it represents**. On a sheared box this
  happens exactly at shear 1, together with edge feet leaving their edges **[D, N]**. Centroids
  never leave their faces, but they break duality.

**Combinatorial transitions.** Three transition classes were tested on the cube: a corner
truncated away, an edge bevel, and a flat pyramid on a face. All comparisons use unreduced
divisors (§2).

**Vertex truncation.** Here the results generalize to any vertex **[D]**. Truncating a valence-`q`
vertex adds `q` valence-3 vertices, `q` new edges and a `q`-gon, and each of the `q` adjacent
faces gains a side. The cut edges keep their lines, so their feet do not move. As the cut
shrinks:

- **R4ve is continuous:** `+3q` in vertices and `−2q` in edges collapse to the old vertex's `+q`.
- **R2 jumps by a fixed divisor:** `+q` at the corner and `−1` on each adjacent face. At the
  cube corner that is `+3` and three `−1`s, matching the measurement **[N]**.

**Raised face.** By polarity, R4fe is continuous as a raised face flattens, the dual of vertex
truncation **[D]**.

**Edge bevel.** In the cube case, no member of the incidence family is continuous, because the
R4ve and R4fe jumps there are not proportional **[D for that case, N]**.

R1 jumped in all three classes. The continuous cases converge as the square of the feature size
**[N]** (E002). R4's near zero–pole pairs are this mechanism at work: small cells about to
collapse.

Whether a recipe is continuous under the other classes of transition, or under an edge bevel in
general, is not established. One caveat: the degree jumps even when the function converges, so
degree is not a continuous measure **[N]**.

## 7. The selected recipe

**Default: R2, with polar placement** (decision 0005) **[P]**:

- vertex directions with order = valence, face normals with order = number of sides;
- normalize by the chordal formula;
- optionally reduce by the gcd for economy on a single solid, reporting `g`; comparisons use
  the unreduced divisor.

**Assumptions.** A convex solid with the origin strictly inside and genuine polygonal faces.

**Strengths.**

- exact reciprocal duality **[D]**;
- a symmetric relief for every symmetric input **[D]**;
- a reduced degree never above R1's on the tested solids, except the hexagonal pyramid **[N]**;
- no zero–pole pairs closer than chordal distance 0.1 anywhere in the tested corpus **[N]**.

Close pairs are not ruled out in general. A face whose polar direction lies near one of its own
vertices, on a strongly oblique solid, would create one.

**Limitations.**

- it jumps under every vertex truncation **[D]**, and at the edge bevel and raised face tested
  **[N]**;
- on strongly oblique solids a pole can leave its face **[D, N]**;
- the function, unlike the relief, can pick up phase characters under symmetries **[N]**.

**Alternative: R4** **[P]**. Of the recipes tested, it is the only one continuous across any of
the tested transitions, under the class matching its pairing. It reproduces the crowns and the
star, and its field is genuinely different. Its cost is tight zero–pole pairs, observed on
irregular inputs.

**Worked example.** R2 on the octahedron is the existing cube–octahedron dual `V⁴/F³`: degree 24,
with the exact constant `C = 729/4` in its classical chart form. R2 on the cube gives its
reciprocal, by duality. Reproduce it with
`apply(R2, fixtures.load("octahedron"))` and compare with `experiments/R0-baseline/`.

## 8. From analysis to object

The relief maps `log|f|` through a logistic: `r = r_min + (1 − r_min) · logistic(log|f| / k)`.
The tip exponent near a feature of order `μ` is `μ / k` **[E/D]**. That makes `k` a display
choice, separate from the function. The baseline's rule `k = 2 · μ_max` gives exponent 1/2 only
to each recipe's **highest-order** features. A feature of lower order `μ` keeps exponent
`μ / (2 μ_max)`, which is sharper. So the rule equalizes the strongest features across recipes,
not every feature. E004 shows it is enough to remove most of the visual gap between R1 and R2.

**Done.** Meshing, closing and sizing (tip-to-tip extent) are inherited from the baseline and
complexplorer 3.1. The baseline's reference mesh rebuilds exactly.

**Not done yet.** No new recipe has been printed. Phase 2 has to check R4's near pairs at
printable sizes, and choose the exhibition pieces.

## 9. Open questions

- Is any natural recipe continuous under all three transitions?
- How should phase be compared across rotations? It is a chart convention.
- What determines the phase characters `θ_g` in general? For example, why do R1 and R2 pick up
  cube roots of unity on tetrahedral inputs while R4 picks up signs? Can a recipe be chosen to
  make `f` itself invariant when that matters, for instance for a symmetric phase coloring?
- Are there transition classes beyond the three tested, or general edge bevels, under which some
  recipe is continuous?
- Should an edge foot that falls off its edge fall back to the midpoint, at the cost of duality?
- Prior work. No literature review has been done, so nothing here claims novelty.

## Reproduce

```bash
uv sync
uv run pytest                                  # the derived and numerical claims above
uv run python scripts/make_atlas.py            # E001
uv run python scripts/e002_transitions.py      # E002, and likewise e003, e004
```
