# 2026-10-01: Divisors, evaluation and normalization (M3)

This covers `PROGRAM.md` §8. Code is in `chart.py`, `divisors.py`, `evaluation.py` and
`normalization.py`, with tests in `tests/test_divisors.py`, `test_evaluation.py` and
`test_normalization.py`. The conventions are recorded in decision 0003.

## Choices [I]

- **Divisor first.** A `Divisor` holds unit vectors and nonzero integer orders, with labels for
  provenance.
  - **Group operations:** add, subtract, negate, scale by integers, divide by gcd.
  - **Infinity:** balance includes the north pole, which the chart reports as the order at `∞`.
- **Cancellation is explicit.** `coalesced` merges points within a chordal distance of `1e-9`
  and reports every zero–pole meeting (the labels, the orders, what remains). `near_pairs`
  reports zero–pole pairs that are close but distinct, and never merges them.
- **Chart precision.** `to_chart` uses `w (1 + z) / |w|²` in the northern hemisphere. The
  textbook `w / (1 − z)` lost about 1e-10 relative precision at `|z| = 10³` (found by the round-trip
  test).
- **Homogeneous evaluation (`PROGRAM.md` §8):** the chordal magnitude *is* the chart-free
  evaluation of the modulus. The phase needs a chart in any case, because a homogeneous ratio has
  no chart-free argument. So there is no separate homogeneous path.

## Verified [N, by tests]

| claim | where it was first made | test |
|---|---|---|
| The three baseline "dual" pieces are R1 = R2 of the tetrahedron, octahedron and icosahedron | audit finding 2 | `test_baseline_duals_are_r1_and_r2`, `test_baseline_piece_is_the_recipe_function` |
| The crowns are reciprocal R4ve of the octahedron and icosahedron; the star is R4ve of the dodecahedron = R4fe of the icosahedron | decision 0002 | same, plus `test_star_is_also_face_edge_on_the_icosahedron` |
| The chordal-product magnitude equals the baseline's normalization at its exact constant | audit §2 (sketch) | `test_baseline_piece_is_the_recipe_function` (1e-8) |
| `D_R2 = D_R4ve − D_R4fe`, with all `E` edge points cancelling exactly | recipe-separation note | `test_incidence_lattice_identity` (all 11 fixtures) |
| Geometric mean of the chordal `|f|` is 1 | decision 0003 | `test_geometric_mean_is_one` |
| `PROGRAM.md` §7 degree table, plus the hexagonal pyramid (7 vs 8) | spec, separation note | `test_degree_table_from_the_program` |
| Local orders equal the phase winding; `−D` gives `1/f`; rotation covariance; no overflow at degree 312 | `PROGRAM.md` §9 checks | `test_evaluation.py` |

The baseline function test is restricted to `|z| < 8` because the source's expanded degree-60
polynomials lose precision farther out (baseline README). The divisor route has no such limit.

## Open

- **Phase comparisons across rotations.** Rotating the divisor changes the chart phase by more
  than a constant. `diagnostics.py` will need to compare phase in a rotated chart, or only
  compare magnitudes.
- **Reflection symmetry.** Audit finding 4 is still unchecked. It now has the tools it needs (a
  reflected divisor plus `log_modulus_on_sphere`).
