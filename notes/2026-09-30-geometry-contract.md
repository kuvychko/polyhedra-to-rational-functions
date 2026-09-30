# 2026-09-30: Geometry contract (M2)

This covers `PROGRAM.md` §6. Code is in `src/polyhedral_functions/geometry.py` and
`fixtures.py`. The corpus is in `data/polyhedra/`, and tests are in `tests/test_geometry.py` and
`tests/test_fixtures.py`.

## Choices [I]

- **Tolerance.** `1e-9` relative to circumradius is used for planarity, coplanarity of
  adjacent faces, convexity and the interior-origin margin. The turn test for strictly convex
  faces uses the sine of the turning angle, so it is scale-free. Fixture residuals are about
  1e-15.
- **Labels are stable, never implicit.** `from_points` keeps input order and raises when a point
  is not a corner, instead of silently dropping it. `polar_dual` keeps index correspondences:
  dual vertex `j` is face `j`, and dual face `i` surrounds vertex `i`. So the double dual
  returns the same labels, and `dual_edge_index` maps edges to dual edges.
- **No implicit centring.** `translated` is the only way to move the origin, and validation
  rechecks it.
- **Face centroid means the area centroid** of the polygon, not the vertex average. The two
  differ on irregular faces, and the area centroid is the more geometric choice. If a
  comparison ever depends on it, record it there.
- **Edge points.** `edge_feet` gives the foot of the perpendicular from the origin, and its
  parameter `t` along the edge. `edge_midpoint_directions` is the alternative. The feet are
  self-dual under polarity, which is verified on every fixture, so they are the natural
  default for R4.

## Observations [N]

- **Point-placement candidates coincide on the Platonic solids.** Face centroids equal polar
  directions and edge midpoints equal feet there. So Platonic inputs cannot inform the
  placement comparison either, just as they cannot separate R1 and R2 (baseline audit,
  finding 2).
- **They barely differ on the canonical deltoidal icositetrahedron.** Centroid and polar
  directions differ by 0.896° on every kite, and its edge feet are the tangency points. A
  placement comparison on it will be subtle. irregular-9 is where placement matters: 7–20° on
  faces and up to 13.5° on edges.
- **Edge feet can leave the edge.** On irregular-9, two of the 21 edges have their foot outside
  the segment (`t` outside [0, 1]). The direction is still well defined, but "the edge's point"
  then lies off the edge. R4 must decide whether that is acceptable, and the decision belongs in
  the R4 experiments.
- **A generic vertex perturbation changes the face lattice**, splitting the cube's quads into
  triangles, as `PROGRAM.md` §6 warns. Fixed-combinatorics deformations must move face planes
  (see `test_parallel_face_shift_keeps_combinatorics`), not individual vertices.

## Open

- Deformation and transition cases are M6 experiments built from these fixtures.
- Reflection-symmetry checks (baseline audit, finding 4) belong in `diagnostics.py`, not here.
