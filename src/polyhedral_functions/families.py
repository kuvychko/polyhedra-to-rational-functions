"""One-parameter families of polyhedra for the controlled experiments (M6).

Each family is a function of one parameter, built from explicit half-spaces or points about a
fixed origin. Nothing is recentered, so a change of parameter changes only the geometry.

- `truncated_corner_cube(s)`: the cube ``[-1, 1]^3`` with the corner at ``(1, 1, 1)`` cut by
  ``x + y + z <= 3 - s``. It has a triangle face of side ``s sqrt 2`` that vanishes as
  ``s -> 0``: a **combinatorial transition** back to the cube.
- `bevelled_edge_cube(s)`: the cube with the edge along ``x = y = 1`` cut by ``x + y <= 2 - s``. A
  thin rectangle with two short sides of length ``s sqrt 2`` vanishes as ``s -> 0``.
- `raised_face_cube(t)`: the cube with a flat square pyramid of height ``t`` on its top face. Four
  triangles become coplanar as ``t -> 0``: the transition polar to a corner truncation.
- `sheared_box(sigma)`: the parallelepiped with vertices ``(x + sigma z, y, z)`` over the cube's.
  The combinatorics are fixed, and the top face's polar direction leaves the top face at
  ``|sigma| = 1``.
- `hexagonal_pyramid(h)`: apex at ``(0, 0, h)`` over the fixture pyramid's base (radius
  ``2 sqrt 2 / 3`` at ``z = -1/3``). The combinatorics are **fixed** for every ``h > 0``.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import HalfspaceIntersection

from .geometry import Polyhedron

CUBE_PLANES = [
    ((1, 0, 0), 1.0),
    ((-1, 0, 0), 1.0),
    ((0, 1, 0), 1.0),
    ((0, -1, 0), 1.0),
    ((0, 0, 1), 1.0),
    ((0, 0, -1), 1.0),
]


def from_halfspaces(planes, name: str) -> Polyhedron:
    """Intersection of half-spaces ``n . x <= h`` (n need not be unit) about the origin."""
    rows = []
    for n, h in planes:
        n = np.asarray(n, dtype=float)
        norm = np.linalg.norm(n)
        rows.append([*(n / norm), -h / norm])
    corners = HalfspaceIntersection(np.array(rows), np.zeros(3)).intersections
    # Corners met by more than three planes are reported once per triple; keep one copy each.
    unique = []
    for c in corners:
        if not any(np.linalg.norm(c - u) < 1e-9 for u in unique):
            unique.append(c)
    unique = np.array(unique)
    unique = unique[np.lexsort(np.round(unique, 12).T[::-1])]
    return Polyhedron.from_points(unique, name)


def cube() -> Polyhedron:
    """The family limit at ``s = 0``: the cube ``[-1, 1]^3``."""
    return from_halfspaces(CUBE_PLANES, "cube [-1,1]^3")


def truncated_corner_cube(s: float) -> Polyhedron:
    if not 0 < s < 3:
        raise ValueError("need 0 < s < 3")
    return from_halfspaces(CUBE_PLANES + [((1, 1, 1), 3 - s)], f"cube, corner cut s={s:g}")


def bevelled_edge_cube(s: float) -> Polyhedron:
    if not 0 < s < 2:
        raise ValueError("need 0 < s < 2")
    return from_halfspaces(CUBE_PLANES + [((1, 1, 0), 2 - s)], f"cube, edge bevel s={s:g}")


def raised_face_cube(t: float) -> Polyhedron:
    if not 0 < t < 1:
        raise ValueError("need 0 < t < 1")
    corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
    return Polyhedron.from_points(
        np.vstack([corners, [[0, 0, 1 + t]]]), f"cube, face raised t={t:g}"
    )


def hexagonal_pyramid(h: float) -> Polyhedron:
    if h <= 0:
        raise ValueError("apex must be above the origin (h > 0)")
    turn = 2 * np.pi * np.arange(6) / 6
    radius = 2 * np.sqrt(2) / 3
    base = np.stack([radius * np.cos(turn), radius * np.sin(turn), np.full(6, -1 / 3)], axis=1)
    return Polyhedron.from_points(np.vstack([[[0, 0, h]], base]), f"hexagonal pyramid h={h:g}")


def sheared_box(sigma: float) -> Polyhedron:
    corners = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
    corners[:, 0] += sigma * corners[:, 2]
    return Polyhedron.from_points(corners, f"sheared box sigma={sigma:g}")
