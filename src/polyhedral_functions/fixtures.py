"""The geometry corpus: explicit constructions, and loading their stored copies.

Each fixture is defined by a construction function here, which is its provenance, and stored as
JSON in ``data/polyhedra/``. ``scripts/make_fixtures.py`` writes the JSON, and the tests check
that the stored copy matches a fresh construction. Everything is constructed rather than
transcribed, so no third-party coordinate data is involved.

Conventions:

- **Origin.** Every fixture is centred by construction, except the two irregular ones and the
  pyramid: their origin is an interior point (for the pyramid, the circumcentre). Nothing is
  recentered on load.
- **Scale.** Platonic solids have circumradius 1, so their vertex directions are their
  vertices. The rhombicuboctahedron has midradius 1, so its polar dual, the deltoidal
  icositetrahedron, also has midradius 1 and is the canonical one: both are tangent to the
  unit sphere at shared edge points. The triakis tetrahedron is canonical in the same way.
- **Orientation.** The Platonic solids use the orientation of complexplorer 3.1's Klein forms,
  which is also the baseline's (R0). The tetrahedron's vertices are the roots of
  ``tetrahedral_vertex``, the octahedron has a vertex at each pole, and the icosahedron has a
  vertex at the north pole with rings at ``z = +-1/sqrt(5)``. The cube and the dodecahedron are
  the face directions of the octahedron and the icosahedron. So recipe divisors can be compared
  with R0's directly.
"""

from __future__ import annotations

import itertools
import json
from collections.abc import Callable
from pathlib import Path

import numpy as np
from scipy.spatial import HalfspaceIntersection

from .geometry import Polyhedron

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "polyhedra"


def _sorted_points(points) -> np.ndarray:
    """Lexicographic order, so vertex labels do not depend on how a set was generated."""
    points = np.asarray(points, dtype=float)
    return points[np.lexsort(np.round(points, 12).T[::-1])]


def tetrahedron() -> Polyhedron:
    """Regular tetrahedron, circumradius 1: the zeros of complexplorer's ``tetrahedral_vertex``."""
    pts = np.array([[-1, -1, -1], [-1, 1, 1], [1, -1, 1], [1, 1, -1]]) / np.sqrt(3)
    return Polyhedron.from_points(pts, "tetrahedron")


def octahedron() -> Polyhedron:
    """Regular octahedron, circumradius 1, with vertices on the coordinate axes."""
    return Polyhedron.from_points(_sorted_points(np.vstack([np.eye(3), -np.eye(3)])), "octahedron")


def cube() -> Polyhedron:
    """Cube, circumradius 1: the octahedron's face directions ``(+-1, +-1, +-1)/sqrt(3)``."""
    pts = np.array(list(itertools.product([-1, 1], repeat=3))) / np.sqrt(3)
    return Polyhedron.from_points(_sorted_points(pts), "cube")


def icosahedron() -> Polyhedron:
    """Regular icosahedron, circumradius 1: a vertex at each pole, rings at ``z = +-1/sqrt(5)``."""
    height, radius = 1 / np.sqrt(5), 2 / np.sqrt(5)
    turn = 2 * np.pi * np.arange(5) / 5
    upper = np.stack([radius * np.cos(turn), radius * np.sin(turn), np.full(5, height)], axis=1)
    lower = np.stack(
        [radius * np.cos(turn + np.pi / 5), radius * np.sin(turn + np.pi / 5), np.full(5, -height)],
        axis=1,
    )
    pts = np.vstack([[[0, 0, 1]], upper, lower, [[0, 0, -1]]])
    return Polyhedron.from_points(_sorted_points(pts), "icosahedron")


def dodecahedron() -> Polyhedron:
    """Regular dodecahedron, circumradius 1: the icosahedron's face directions."""
    return Polyhedron.from_points(_sorted_points(icosahedron().face_directions()), "dodecahedron")


def rhombicuboctahedron() -> Polyhedron:
    """Rhombicuboctahedron, midradius 1: permutations of ``(+-1, +-1, +-(1 + sqrt 2))``, scaled.

    Every edge midpoint has norm ``sqrt(4 + 2 sqrt 2)`` before scaling.
    """
    big = 1 + np.sqrt(2)
    pts = {
        tuple(s * x for s, x in zip(signs, perm, strict=True))
        for signs in itertools.product([-1, 1], repeat=3)
        for perm in set(itertools.permutations([1.0, 1.0, big]))
    }
    pts = np.array(sorted(pts)) / np.sqrt(4 + 2 * np.sqrt(2))
    return Polyhedron.from_points(_sorted_points(pts), "rhombicuboctahedron")


def deltoidal_icositetrahedron() -> Polyhedron:
    """Canonical deltoidal icositetrahedron, midradius 1: the rhombicuboctahedron's polar dual.

    Its vertices are relabelled in lexicographic order, so its labels do not follow the dual's
    face indices. Recover correspondences geometrically if needed.
    """
    dual = rhombicuboctahedron().polar_dual()
    return Polyhedron.from_points(_sorted_points(dual.vertices), "deltoidal icositetrahedron")


# Half-spaces n . x <= h (n not yet normalized). Chosen by hand so that every plane is a face,
# the faces have 3 to 6 sides, and there is no symmetry. The last three planes cut a corner, an
# edge and another edge of an off-centre box.
IRREGULAR_9_PLANES = [
    ((1, 0, 0), 1.1),
    ((-1, 0, 0), 0.9),
    ((0, 1, 0), 0.8),
    ((0, -1, 0), 1.0),
    ((0, 0, 1), 1.2),
    ((0, 0, -1), 0.7),
    ((1, 1, 1), 1.5),
    ((-1, 0, 1), 1.2),
    ((0, -1, -1), 1.05),
]


def irregular_9() -> Polyhedron:
    """An asymmetric solid with 9 faces, cut from half-spaces by `IRREGULAR_9_PLANES`.

    The origin is interior, with the smallest face distance 0.7. Two of its edges have their
    perpendicular foot from the origin **outside** the edge segment, which is relevant to R4's
    edge placement.
    """
    halfspaces = []
    for n, h in IRREGULAR_9_PLANES:
        n = np.asarray(n, dtype=float)
        norm = np.linalg.norm(n)
        halfspaces.append([*(n / norm), -h])
    corners = HalfspaceIntersection(np.array(halfspaces), np.zeros(3)).intersections
    return Polyhedron.from_points(_sorted_points(corners), "irregular-9")


def hexagonal_pyramid() -> Polyhedron:
    """Regular hexagonal pyramid inscribed in the unit sphere: apex at the north pole, base at
    ``z = -1/3`` with radius ``2 sqrt(2) / 3``.

    One vertex of valence 6 among six of valence 3, and one hexagon among six triangles. That
    spread is what separates R1 from R2. Its polar dual is again a hexagonal pyramid, inverted.
    """
    turn = 2 * np.pi * np.arange(6) / 6
    radius = 2 * np.sqrt(2) / 3
    base = np.stack([radius * np.cos(turn), radius * np.sin(turn), np.full(6, -1 / 3)], axis=1)
    return Polyhedron.from_points(
        _sorted_points(np.vstack([[[0, 0, 1]], base])), "hexagonal pyramid"
    )


def truncated_tetrahedron() -> Polyhedron:
    """Truncated tetrahedron, midradius 1: permutations of ``(3, 1, 1)`` with an even number of
    minus signs, scaled. Used only to build `triakis_tetrahedron`; it is not a fixture itself.
    """
    pts = {
        tuple(s * x for s, x in zip(signs, perm, strict=True))
        for signs in itertools.product([1, -1], repeat=3)
        if np.prod(signs) > 0
        for perm in set(itertools.permutations([3.0, 1.0, 1.0]))
    }
    # Every edge midpoint of the unscaled solid has norm 3: (2, 2, 1) between (3, 1, 1) and
    # (1, 3, 1) on a triangle, (3, 0, 0) between (3, 1, 1) and (3, -1, -1) between hexagons.
    pts = np.array(sorted(pts)) / 3.0
    return Polyhedron.from_points(_sorted_points(pts), "truncated tetrahedron")


def triakis_tetrahedron() -> Polyhedron:
    """Canonical triakis tetrahedron, midradius 1: the truncated tetrahedron's polar dual.

    Four vertices of valence 6, along the tetrahedron fixture's vertices, and four of valence
    3, with full tetrahedral symmetry. It keeps the symmetry while separating R1 from R2.
    """
    dual = truncated_tetrahedron().polar_dual()
    return Polyhedron.from_points(_sorted_points(dual.vertices), "triakis tetrahedron")


# An irregular pentagon (z = -0.6) below an irregular quadrilateral (z = 0.7). The hull joins
# them with nine triangles, which gives mixed valences (3, 4, 5) and mixed face sizes (3, 4, 5).
IRREGULAR_MIXED_BASE = [
    (1.0, 0.1, -0.6),
    (0.35, 0.95, -0.6),
    (-0.8, 0.7, -0.6),
    (-0.9, -0.45, -0.6),
    (0.2, -1.05, -0.6),
]
IRREGULAR_MIXED_TOP = [(0.45, 0.25, 0.7), (-0.15, 0.55, 0.7), (-0.55, -0.1, 0.7), (0.1, -0.5, 0.7)]


def irregular_mixed() -> Polyhedron:
    """An asymmetric solid that is neither simple nor simplicial: the hull of the points in
    `IRREGULAR_MIXED_BASE` and `IRREGULAR_MIXED_TOP`.

    Unlike irregular-9, whose vertices all have valence 3, both its valences and its face sizes
    vary, so neither side of the R2 divisor is uniform. Smallest face distance 0.555.
    """
    pts = np.array(IRREGULAR_MIXED_BASE + IRREGULAR_MIXED_TOP, dtype=float)
    return Polyhedron.from_points(_sorted_points(pts), "irregular-mixed")


CONSTRUCTIONS: dict[str, Callable[[], Polyhedron]] = {
    "tetrahedron": tetrahedron,
    "cube": cube,
    "octahedron": octahedron,
    "icosahedron": icosahedron,
    "dodecahedron": dodecahedron,
    "rhombicuboctahedron": rhombicuboctahedron,
    "deltoidal-icositetrahedron": deltoidal_icositetrahedron,
    "irregular-9": irregular_9,
    "hexagonal-pyramid": hexagonal_pyramid,
    "triakis-tetrahedron": triakis_tetrahedron,
    "irregular-mixed": irregular_mixed,
}


def to_record(fixture_id: str, poly: Polyhedron) -> dict:
    """The JSON form of a fixture: provenance, summary, coordinates and faces."""
    construct = CONSTRUCTIONS[fixture_id]
    return {
        "id": fixture_id,
        "name": poly.name,
        "construction": f"polyhedral_functions.fixtures.{construct.__name__}",
        "description": " ".join(construct.__doc__.split()),
        "summary": poly.summary(),
        "vertices": poly.vertices.tolist(),
        "faces": [list(f) for f in poly.faces],
    }


def load(fixture_id: str) -> Polyhedron:
    """Load a stored fixture from ``data/polyhedra/<id>.json`` and validate it."""
    path = DATA_DIR / f"{fixture_id}.json"
    if not path.exists():
        raise KeyError(f"no fixture {fixture_id!r}; available: {', '.join(CONSTRUCTIONS)}")
    record = json.loads(path.read_text(encoding="utf-8"))
    return Polyhedron.from_faces(record["vertices"], record["faces"], name=record["name"])
