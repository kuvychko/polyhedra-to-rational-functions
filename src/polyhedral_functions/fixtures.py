"""The geometry corpus: explicit constructions, and loading their stored copies.

Each fixture is defined by a construction function here, which is its provenance, and stored as
JSON in ``data/polyhedra/``. ``scripts/make_fixtures.py`` writes the JSON, and the tests check
that the stored copy matches a fresh construction. Everything is constructed rather than
transcribed, so no third-party coordinate data is involved.

Conventions:

- **Origin.** Every fixture is centred by construction, except ``irregular-9``, whose origin
  is simply a point strictly inside it. Nothing is recentered on load.
- **Scale.** Platonic solids have circumradius 1, so their vertex directions are their
  vertices. The rhombicuboctahedron has midradius 1, so its polar dual, the deltoidal
  icositetrahedron, also has midradius 1 and is the canonical one: both are tangent to the
  unit sphere at shared edge points.
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


CONSTRUCTIONS: dict[str, Callable[[], Polyhedron]] = {
    "tetrahedron": tetrahedron,
    "cube": cube,
    "octahedron": octahedron,
    "icosahedron": icosahedron,
    "dodecahedron": dodecahedron,
    "rhombicuboctahedron": rhombicuboctahedron,
    "deltoidal-icositetrahedron": deltoidal_icositetrahedron,
    "irregular-9": irregular_9,
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
