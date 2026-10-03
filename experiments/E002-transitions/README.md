# E002-transitions: recipes across combinatorial transitions

- **Question:** which recipes change continuously when the combinatorics change, that is, when a
  small face or short edge shrinks to nothing?
- **Hypothesis:** no recipe is continuous under every transition.
  - Truncating a valence-`q` vertex adds `+3q` in new vertices and `−2q` in new edges, a net
    `+q`, which is the old vertex's order. So R4ve should be continuous under vertex truncation.
  - By polarity, R4fe should be continuous under raising a flat pyramid on a face.
  - R1, R2 and flag should jump under all three transitions, and R4ve should jump under an edge
    bevel.
- **Changed factor:** the transition parameter `s`, one family at a time:
  - `truncated_corner_cube`: a triangle face of side `s√2`;
  - `bevelled_edge_cube`: a thin rectangle with short sides `s√2`;
  - `raised_face_cube`: a flat pyramid of height `s`.

  `s` runs from 0.3 to 1e-4. The comparison target is the same recipe on the cube, the family's
  `s = 0` limit.
- **Method:**
  - Comparisons use **unreduced** divisors, because gcd reduction is itself discontinuous.
  - Residuals are absolute `log|f|` differences on 20,000 Fibonacci samples, with 0.05 caps
    excluded.
  - Jump divisors are exact: the divisor at `s = 1e-6`, with its collapsing features clustered
    within 1e-3, minus the cube's.
- **Status:** complete. Run from clean commit `7c929c7`.
  Reproduce with `uv run python scripts/e002_transitions.py --publish`.
- **Files:**
  - `convergence.csv`: residuals, degrees and the closest zero–pole distance per family × recipe
    × `s`;
  - `jumps.json`: the exact jump divisors;
  - `transitions.jpg`: geometry and convergence curves;
  - `manifest.json`.

## Result: the hypothesis holds exactly

| recipe | corner truncation | edge bevel | raised face |
|---|---|---|---|
| R1 | jump | jump | jump |
| R2 | jump: `+3` corner, `−1` on each of 3 faces | jump: `+3` at both ends, `−1` on the two capped faces, `−4` mid-edge | jump: `+1` at 4 corners, `−4` at the face |
| **R4ve** | **continuous**, residual ∝ `s^2.11` | jump: `+1` at both ends, `−2` mid-edge | jump |
| R4fe | jump | jump | **continuous**, residual ∝ `s^2.01` |
| flag | jump (= R4fe's jump) | jump | jump (= R4ve's jump) |

Four of these are also exact tests in `tests/test_families_and_transitions.py`: the R2 corner
jump, the R4ve bevel jump and both continuous cases. The rest are recorded in `jumps.json`.

- **Jumps add.** The jumps obey the incidence lattice: `J_R2 = J_R4ve − J_R4fe` and
  `J_flag = J_R4ve + J_R4fe`. So **no member of the incidence family is continuous under an
  edge bevel**, where the R4ve and R4fe jumps are not proportional.
- **R1 jumps everywhere and globally.** `V` and `F` change, so every order changes. Its residual
  plateaus 2–7× above R2's.
- **Quadratic convergence.** Convergence is quadratic, not linear: the collapsing cluster has
  total order equal to the old feature's, and its first moment vanishes by the local three-fold
  or four-fold symmetry.
- **Degree is not continuous even when the function is.** R4ve has unreduced degree 30 for every
  `s > 0` against the cube's 24, while its function converges. The extra degree is carried by
  nearly cancelling zero–pole pairs. The closest-pair distance in `convergence.csv` falls in
  proportion to `s`.

## What this changes

- **E001 reinterpreted:** the R4 "near pairs" on irregular-9 are the mechanism of R4's
  continuity under truncation, not only a liability. They are small cells that are close to
  collapsing. For printing they remain a spike beside a pit.
- **Stability favours R4 here:** among the recipes compared, only R4 has any transition-continuity
  (for the transitions polar to its edge pairing). R2 jumps in all three tested classes, and under
  vertex truncation in general. This is a real point in
  R4's favour on the stability criterion of `PROGRAM.md` §5.
- **Degree needs care in reporting:** degree economy must be reported with that caveat. A
  recipe's degree can be inflated by near-cancelling structure that is invisible in the field.
