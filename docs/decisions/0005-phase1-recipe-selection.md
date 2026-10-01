# 0005: Phase 1 selection: R2 by default, R4 as the alternative

Date: 2026-10-01. Status: accepted by the owner.

This is the Phase 1 decision record that `PROGRAM.md` §2 and §13 ask for. It selects a default
recipe and one alternative, records the trade-offs that decided them, the failure cases, and what
remains open. It builds on decisions 0002 (R4 as a candidate), 0003 (chordal normalization) and
0004 (polar/foot placement).

## Decision

1. **Default recipe: R2**, the incidence recipe. Each vertex direction gets a zero of order equal
   to its valence, and each polar face direction a pole of order equal to its number of sides.
   Orders are reduced by their gcd.
2. **Alternative: R4**, the edge-incidence family. Use **R4ve** (vertices against edges) or
   **R4fe** (faces against edges); they are swapped by polarity. Present R4 as a genuinely
   different construction, not a variant of R2.
3. **Placement: polar face directions and edge feet** (decision 0004). Centroid and midpoint
   placement is a **labelled option** for strongly oblique solids, where a polar point can leave
   its own cell (`diagnostics.placement_report`).
4. **Display for comparing recipes: order-tuned sharpness**,
   `k = 2 × max |order|` (`DisplaySettings.tuned_for`), labelled as tuned. Fixed-sharpness panels
   remain the controlled view and are kept alongside.
5. **Not selected:** R1 (uniform) stays as a baseline in comparisons. The flag recipe is
   recorded but not pursued. R3 (small orbit weights) was not needed: no weakness of R2 or R4
   that it would address turned up.

## Why: the criteria of `PROGRAM.md` §5, reported separately

| criterion | R1 | **R2** | **R4** | evidence |
|---|---|---|---|---|
| geometric correspondence | each zero a vertex, each pole a face | same, weighted by incidence | each pole an **edge**; vertices or faces as zeros | E001 |
| rotation consistency | exact | exact | exact | M4 tests, `rotation_report` |
| symmetry preservation | full group, mirrors included | full group | full group | M4, E001 (55/55) |
| duality (polar dual) | reciprocal function | **reciprocal function** | R4ve ↔ R4fe swap | decision 0004, E001 |
| degree economy | equal to R2 on Platonic solids, 2–3.25× R2 elsewhere, but lower on the hexagonal pyramid (7 vs 8) | **never above R1 except on the hexagonal pyramid**: equal on the 5 Platonic solids, lower on the 5 other solids | varies: 12–96, sometimes below R2, sometimes 3× | E001 |
| stability: deformation | continuous | continuous | continuous | E003 |
| stability: combinatorial transitions | jumps (globally) | jumps at every transition | **continuous under its matching transition** (vertex truncation for R4ve, the polar one for R4fe), jumps otherwise | E002 |
| numerical reliability | fine to degree 312 | fine | fine; near zero–pole pairs at short edges | M3 tests, E001 |
| interpretability, display | the R1/R2 relief gap is mostly display; phase winds 3× as often | readable phase | different field (correlation with R2 0.55–0.92) | E004 |

R2 wins on degree economy, exact reciprocal duality and the absence of near pairs. After dividing
by the degree, R1 and R2 have nearly the same shape, so R1 offers nothing R2 lacks except on rare
low-degree inputs such as the hexagonal pyramid (7 against 8).

R4 is kept because it is the only recipe with any transition continuity. It also reproduces three
of the six baseline pieces, and its field differs from R2's in a way no display removes.

## Failure cases and costs

- **R2 jumps at every combinatorial transition** (E002). A tiny face or a short edge changes the
  function by a fixed, nonzero divisor, for example `+3` at a cut corner and `−1` on each adjacent
  face.
- **No member of the incidence family is continuous under an edge bevel** (E002). The R4ve and
  R4fe jumps there are not proportional.
- **R4 makes tight zero–pole pairs** at short edges and small faces (E001: chordal distances
  0.04–0.09 on irregular-9). They are what makes it continuous, but in a print they are a spike
  beside a pit.
- **Polar placement can put a pole outside the face it stands for** on oblique solids: at shear
  `σ > 1` on the sheared box (E003), and on 2 of irregular-9's faces. Centroid placement avoids
  that, but breaks duality.
- **Degree is not continuous.** It counts nearly cancelling structure that is invisible in the
  field (E002), so degree economy must always be reported with that caveat.
- **Fixed-display comparisons overstate differences between recipes of different local order**
  (E004).

## Open questions

- **Full-function symmetry.** Magnitude symmetry is settled. Whether `f` itself is invariant
  (not just `|f|`) under the symmetry group, and how phase behaves under rotation of the chart, is
  unexplored. The chart phase is a convention (decision 0003).
- **Continuity under edge bevels.** Is there any natural recipe outside the incidence lattice
  that is continuous there, and under all three transitions?
- **Edge placement when the foot leaves its edge** (irregular-9, the sheared box). Is a midpoint
  fallback rule better, at the cost of duality?
- **Non-geometric-mean sea levels.** The baseline's pole flowers normalized along the equator.
  If a recipe ever needs that, decision 0003 says to add a named convention.
- **Novelty.** No literature review has been done yet. Nothing here claims that R2 or R4 is new
  (`PROGRAM.md` §12).
- **Physical evidence.** Photos of the four printed baseline pieces are deferred. No piece has
  been printed from R2 or R4 on a non-Platonic solid.

## Reopen if

- Phase 2 printing shows R4's near pairs to be unprintable at practical sizes.
- A review finds prior work that settles the choice.
- A recipe outside the incidence lattice turns out to be continuous across transitions.
