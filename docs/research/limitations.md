# Limitations and open questions

What the research shows, how far each result reaches, and what it does not show. Labels follow
[the exploration](narrative.md): **[E]** established, **[D]** derived, **[N]** numerical,
**[C]** conjecture, **[P]** design preference.

## How far the evidence reaches

The numerical evidence comes from:

- **eleven solids:** the five Platonic solids, the rhombicuboctahedron and its dual, the triakis
  tetrahedron, a hexagonal pyramid, and two irregular solids;
- **five one-parameter families:** three transitions on the cube, a pyramid height, and a box
  shear.

A third irregular solid was added for printing. Results fall into three groups.

**Derived, so they hold for every convex input with the origin inside:**

- the incidence identity \(D_{R2} = D_{R4ve} - D_{R4fe}\), for unreduced divisors;
- the polarity relations: R1 and R2 give the reciprocal function, R4ve and R4fe swap, and flag is
  self-dual;
- symmetry of the relief under every symmetry of the solid;
- the phase-character form \(f(gx) = e^{i\theta_g} f(x)\);
- continuity under fixed-combinatorics deformation;
- R4ve's continuity, and R2's jump, under truncating any vertex.

**Shown only for the cases tested:**

- the edge-bevel and raised-face results, on the cube;
- the values of the phase characters;
- every correlation, degree ratio and gap measurement.

**Observed in the corpus, not proved:**

- that R2 makes no close zero–pole pairs;
- that R4 is the only recipe with any transition continuity.

## What the construction gives up

- **Distances.** Points are placed by direction from the centre, so a solid and a radially
  rescaled copy with the same directions give the same function. Nothing here reconstructs the
  solid from the function.
- **The choice of centre.** Every result assumes the origin is strictly inside the solid. Moving
  it changes the polar dual and every placement.
- **Some information under reduction.** The gcd-reduced function is a root of the recipe's
  function. Identities and continuity statements refer to the unreduced one.

## Known weaknesses of the selected recipes

- **R2 jumps at combinatorial transitions.** A vanishing face changes the function by a fixed
  divisor. This is proved for vertex truncation and observed at the tested edge bevel and raised
  face.
- **No incidence recipe is continuous at the tested edge bevel.**
- **A pole can leave its face.** On strongly oblique solids the polar direction of a face falls
  outside the face (on a sheared box, from shear 1). Centroid placement avoids this, but breaks
  duality.
- **The phase is not as symmetric as the relief.** Under a symmetry the function picks up a factor
  \(e^{i\theta_g}\), so the colors of a symmetric relief can rotate.
- **R4 makes tight zero–pole pairs** at short edges and small faces. They are what makes R4
  continuous, but a print shows them as a spike beside a pit.
- **The flag recipe** gives the same function for a solid and its dual.

## Choices that are conventions, not findings **[P]**

- **The constant:** chordal normalization, with geometric mean 1.
- **The phase:** the stereographic chart with a positive leading constant.
- **The display:** relief sharpness. The order-tuned rule equalizes only the highest-order
  features.
- **Placement:** polar faces and edge feet, chosen for exact duality.
- **The printed shapes:** depth 0.2, the logistic transfer, and the sizes and cut planes.

## Printing

- **The printability reference is narrow.** It is the smallest feature gaps among four pieces
  already printed at 130 mm, scaled linearly to 80 mm. Nothing has yet been printed at 80 mm.
- **The gap measure is a proxy.** It is an arc length at sea level, and does not capture the
  ridge profile between a spike and a pit.
- **New-recipe pieces are not yet tested.** Until they are printed, their settings are proposals.
- **"Identical" halves are congruent only up to mesh resolution.** The latitude–longitude mesh is
  not exactly symmetric.

## Open questions

- Is any natural recipe continuous under every class of transition, or at least under edge
  bevels?
- What determines the phase characters \(\theta_g\)? Why do R1 and R2 pick up cube roots of unity
  on tetrahedral inputs, while R4 picks up signs? Can a recipe be chosen to make \(f\) itself
  invariant when a symmetric phase coloring matters?
- How should phases be compared across rotations of the solid? The phase depends on the chart.
- When an edge's foot falls off the edge, should the point fall back to the midpoint, at the cost
  of duality?
- What about solids beyond this corpus: non-simple solids with many small faces, or near-regular
  solids close to several transitions at once?
- **Prior work.** No literature review has been done, so nothing here claims novelty.
