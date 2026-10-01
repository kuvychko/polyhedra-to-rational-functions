# 2026-10-01: Do the candidate constructions actually differ?

Prompted by the deltoidal icositetrahedron (DI), which barely separated the face-placement
candidates (0.896°). That raised the question of whether the recipes produce genuinely
different functions, or only different divisors.

The tables come from `scripts/explore_recipe_separation.py`. That script is a quick screen,
not an experiment: its recipes are written inline and will be superseded by `recipes.py`, and
the only metric is a correlation.

**Method.** For a balanced divisor, log|f| equals
`L(x) = Σ mᵢ log χ(x, aᵢ) − Σ nⱼ log χ(x, bⱼ)` up to a constant, where `χ` is the chordal
distance. Each recipe is reduced to `L / degree` and the fields are compared by Pearson
correlation over 40,000 Fibonacci points, with 3° caps around all candidate features
excluded. Correlation 1 means the same field up to scale and offset. In that case the recipes
differ only in degree, which a display mapping can absorb.

## Results [N]

Placement is polar face directions and edge feet unless stated. Zeros go on the first named set.

| fixture | degree R1 / R2 / R4ve / R4fe | R1~R2 | R2~R4ve | R2~R4fe | R4ve~R4fe |
|---|---|---|---|---|---|
| tetrahedron | 4 / 4 / 12 / 12 | 1.000 | 0.659 | -0.659 | 0.131 |
| cube | 24 / 24 / 24 / 12 | 1.000 | 0.550 | -0.821 | 0.026 |
| octahedron | 24 / 24 / 12 / 24 | 1.000 | 0.821 | -0.550 | 0.026 |
| icosahedron | 60 / 60 / 60 / 60 | 1.000 | 0.905 | -0.481 | -0.062 |
| dodecahedron | 60 / 60 / 60 / 60 | 1.000 | 0.481 | -0.905 | -0.062 |
| rhombicuboctahedron | 312 / 96 / 48 / 96 | 0.989 | 0.741 | -0.722 | -0.071 |
| deltoidal-icositetrahedron | 312 / 96 / 96 / 48 | 0.989 | 0.737 | -0.738 | -0.087 |
| irregular-9 | 126 / 42 / 42 / 42 | 0.982 | 0.761 | -0.920 | -0.445 |
| hexagonal-pyramid | 7 / 8 / 24 / 24 | **0.831** | 0.746 | -0.776 | -0.159 |
| triakis-tetrahedron | 24 / 12 / 36 / 36 | 0.956 | 0.924 | -0.274 | 0.114 |
| irregular-mixed | 99 / 36 / 36 / 36 | 0.955 | 0.877 | -0.749 | -0.339 |

| fixture | R2: polar~centroid | R4ve: foot~midpoint |
|---|---|---|
| Platonic solids, rhombicuboctahedron | 1.000 | 1.000 |
| deltoidal-icositetrahedron | 0.992 | 0.895 |
| irregular-9 | **0.518** | 0.651 |
| hexagonal-pyramid | 0.595 | 1.000 |
| triakis-tetrahedron | 0.947 | **0.584** |
| irregular-mixed | **0.460** | **0.553** |

## What it means

1. **R1 and R2 are the same field up to valence weighting [D, confirmed N].** Divided by its
   degree, each recipe is the potential of "vertex points minus face points". R1 gives every
   point equal weight (`1/V`, `1/F`). R2 gives incidence weight (`q_v/2E`, `p_f/2E`). The
   relative weights therefore differ by `q_v / mean(q)` and `p_f / mean(p)`, so the fields
   separate only as much as valences and face sizes vary.
   - The two divisors are identical exactly when all valences are equal and all faces have the
     same size. By Euler's formula, that means the combinatorially Platonic polyhedra.
   - Everywhere else the main difference is **degree economy**. The shape differs little unless
     the valence spread is large: 0.83 on the hexagonal pyramid (valence 6 among 3s), and
     0.96–0.99 on all the other non-Platonic fixtures.
2. **R2 is not always the more economical recipe [N].** On the hexagonal pyramid R1 has degree 7
   (`V = F = 7`) and R2 has degree 8. `PROGRAM.md` §7 implied R2 is cheaper, from its example
   table; it is not in general.
3. **The incidence recipes form a lattice [D, confirmed N to 2e-16].** With unreduced incidence
   orders, all totalling `2E`, and shared placements:

   `D_R2 = D_R4ve − D_R4fe`, i.e. `f_R2 = C · f_R4ve / f_R4fe`.

   So R2, R4ve and R4fe span a two-parameter family, `f_ve^a · f_fe^b`. The "three-set" variant
   listed as an open question in `PROGRAM.md` §7 is simply `a = b = 1`: vertices and faces
   against edges of order 4. On the octahedron, this is how the baseline pieces fit together:
   `V⁴/E² ÷ F³/E² = V⁴/F³`. The crown and the cube-octahedron dual are two members of one
   family.
4. **R4 is genuinely different from R2.** The correlation is 0.48–0.92 even on Platonic inputs,
   because edges and faces are different point sets. R4ve and R4fe are nearly uncorrelated with
   each other.
5. **Placement candidates coincide under explicit geometric conditions [D, confirmed N]:**
   - The edge foot equals the edge midpoint iff the endpoints are equidistant from the origin.
     This always holds for inscribed polyhedra: Platonic solids, rhombicuboctahedron, the
     pyramid.
   - The polar face direction equals the face centroid direction iff the foot of the
     perpendicular is the face's area centroid. For an inscribed polyhedron that foot is the
     face's circumcentre, so the condition fails on the pyramid's isosceles triangles (0.595).
   - Canonical duals of inscribed solids (DI, triakis tetrahedron) reverse the roles: their
     vertices sit at two radii, so edge placement separates (triakis 0.584).
   - Irregular solids separate both.

## Consequences

- Corpus extended with **hexagonal-pyramid** (R1/R2 and face-placement separator,
  combinatorially self-dual), **triakis-tetrahedron** (symmetric but separating, and an edge
  placement separator), and **irregular-mixed** (varied valences *and* face sizes). The
  rhombicuboctahedron/DI pair stays as the symmetric dual pair from the spec.
- R1 vs R2 is mainly a question of degree economy and display. Report it that way rather than
  as a difference in shape, except on high-spread inputs.
- M4 should implement the incidence lattice (`f_ve^a f_fe^b`) directly, not three separate
  recipes. That makes R2 and the three-set variant special cases, and the identity a test.
- The correlation metric hides *where* fields differ. The atlas (M5) should show difference
  maps, not only scalars.
