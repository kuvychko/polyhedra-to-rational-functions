"""Convex polyhedra with genuine polygonal faces, polarity, and the point sets recipes use.

The geometry contract (``PROGRAM.md`` §6):

- A `Polyhedron` is full-dimensional and convex, with **genuine** polygonal faces. Coplanar
  hull facets are merged, and no two adjacent faces are coplanar. Faces are listed
  counterclockwise as seen from outside, and every edge lies on exactly two faces.
- The origin must lie **strictly inside**. Nothing is ever recentered implicitly. Moving the
  origin is an explicit `translated` call, because it changes the polar dual and every point
  set derived from it.
- For a face plane ``n . x = h`` with unit outward normal ``n`` and ``h > 0``, the unit-sphere
  polar dual has the vertex ``n / h``, whose spherical direction is ``n``. `polar_dual` keeps
  index correspondences: dual vertex ``j`` is primal face ``j``, and dual face ``i`` surrounds
  primal vertex ``i``.

Point sets are returned as unit vectors in index order, so multiplicities from incidence counts
line up with them. This module depends on numpy and scipy only, never on plotting code.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import cached_property

import numpy as np
from scipy.spatial import ConvexHull

# Default tolerance, relative to the polyhedron's circumradius: planarity, coplanarity of
# adjacent faces, convexity and the interior-origin margin are all measured against
# `DEFAULT_TOL * scale`. Fixtures are built from exact constructions, so their residuals sit
# near 1e-15. Anything above 1e-9 is a genuinely different face, not rounding.
DEFAULT_TOL = 1e-9


class GeometryError(ValueError):
    """The input violates the geometry contract. The message lists every violation found."""


def _unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def _newell_normal(points: np.ndarray) -> np.ndarray:
    """Area-weighted normal of a polygon (unnormalized; length = twice the area)."""
    nxt = np.roll(points, -1, axis=0)
    return np.cross(points, nxt).sum(axis=0)


def _polygon_centroid(points: np.ndarray) -> np.ndarray:
    """Area centroid of a planar convex polygon, by fanning triangles from its first vertex."""
    a = points[0]
    tri_b, tri_c = points[1:-1], points[2:]
    areas = np.linalg.norm(np.cross(tri_b - a, tri_c - a), axis=1)
    centroids = (a + tri_b + tri_c) / 3.0
    return (areas[:, None] * centroids).sum(axis=0) / areas.sum()


def _canonical_cycle(face: tuple[int, ...]) -> tuple[int, ...]:
    """Rotate a cyclic sequence so that it starts at its smallest index (orientation kept)."""
    k = face.index(min(face))
    return face[k:] + face[:k]


@dataclass(frozen=True, eq=False)
class Polyhedron:
    """A convex polyhedron: vertex coordinates plus faces as cyclic lists of vertex indices.

    Construct it with `from_faces` or `from_points`. Both validate the result. The direct
    constructor does not validate, so call `validate` if you use it.
    """

    vertices: np.ndarray
    faces: tuple[tuple[int, ...], ...]
    name: str = ""
    tol: float = field(default=DEFAULT_TOL, repr=False)

    def __post_init__(self) -> None:
        vertices = np.array(self.vertices, dtype=float)
        vertices.setflags(write=False)
        object.__setattr__(self, "vertices", vertices)
        object.__setattr__(self, "faces", tuple(tuple(int(i) for i in f) for f in self.faces))

    # --- construction ------------------------------------------------------------------

    @classmethod
    def from_faces(cls, vertices, faces, name: str = "", tol: float = DEFAULT_TOL) -> Polyhedron:
        """Build from explicit faces and validate against the contract."""
        poly = cls(vertices, faces, name=name, tol=tol)
        poly.validate()
        return poly

    @classmethod
    def from_points(cls, points, name: str = "", tol: float = DEFAULT_TOL) -> Polyhedron:
        """Convex hull of ``points``, with coplanar hull facets merged into genuine faces.

        Every input point must be a vertex of the hull. A point inside the hull, or on a face
        or edge without being a corner, raises instead of being silently dropped, so vertex
        indices always match the input order.
        """
        points = np.asarray(points, dtype=float)
        hull = ConvexHull(points)
        not_extreme = sorted(set(range(len(points))) - set(hull.vertices.tolist()))
        if not_extreme:
            raise GeometryError(f"points {not_extreme} are not vertices of their convex hull")

        scale = np.linalg.norm(points, axis=1).max()
        normals, offsets = hull.equations[:, :3], -hull.equations[:, 3]

        # Union adjacent facets whose planes agree. In a convex polyhedron, coplanar facets
        # are always one face, and walking adjacency keeps that face connected by construction.
        parent = list(range(len(hull.simplices)))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i, neighbours in enumerate(hull.neighbors):
            for j in neighbours:
                if (
                    np.linalg.norm(normals[i] - normals[j]) <= tol
                    and abs(offsets[i] - offsets[j]) <= tol * scale
                ):
                    parent[find(i)] = find(j)

        groups: dict[int, set[int]] = {}
        for i, simplex in enumerate(hull.simplices):
            groups.setdefault(find(i), set()).update(simplex.tolist())

        faces = []
        for root, members in groups.items():
            idx = np.array(sorted(members))
            n = normals[root]
            centre = points[idx].mean(axis=0)
            # An orthonormal basis (u, w) of the face plane with u x w = n, so increasing angle
            # is counterclockwise seen from outside.
            u = _unit(points[idx[0]] - centre)
            w = np.cross(n, u)
            rel = points[idx] - centre
            angle = np.arctan2(rel @ w, rel @ u)
            # Start each face at its smallest vertex index. The angle sort's starting point
            # depends on rounding when two vertices sit at angle +-pi (e.g. a regular hexagon),
            # and that varied between platforms.
            faces.append(_canonical_cycle(tuple(idx[np.argsort(angle)].tolist())))

        faces.sort(key=lambda f: _canonical_cycle(f))
        return cls.from_faces(points, faces, name=name, tol=tol)

    # --- combinatorics -----------------------------------------------------------------

    @property
    def n_vertices(self) -> int:
        return len(self.vertices)

    @property
    def n_faces(self) -> int:
        return len(self.faces)

    @property
    def n_edges(self) -> int:
        return len(self.edges)

    @cached_property
    def _half_edges(self) -> dict[tuple[int, int], int]:
        """Directed edge (a, b), in face order, mapped to the face that contains it."""
        return {
            (f[k], f[(k + 1) % len(f)]): i for i, f in enumerate(self.faces) for k in range(len(f))
        }

    @cached_property
    def edges(self) -> tuple[tuple[int, int], ...]:
        """Undirected edges as sorted vertex pairs, in sorted order."""
        return tuple(sorted({(min(a, b), max(a, b)) for a, b in self._half_edges}))

    @cached_property
    def edge_faces(self) -> tuple[tuple[int, int], ...]:
        """Faces on each edge ``(a, b)``: (the one where it runs a -> b, the one where b -> a)."""
        he = self._half_edges
        return tuple((he[(a, b)], he[(b, a)]) for a, b in self.edges)

    @cached_property
    def vertex_faces(self) -> tuple[tuple[int, ...], ...]:
        """Faces around each vertex, counterclockwise as seen from outside.

        This is the dual face of that vertex, in `polar_dual`'s orientation.
        """
        he = self._half_edges
        # For the face containing a -> v, the face across the edge v -> a (face order) is the
        # next one counterclockwise around v seen from outside.
        next_out = {}
        for (a, b), f in he.items():
            next_out.setdefault(b, {})[f] = he[(b, a)]
        rings = []
        for v in range(self.n_vertices):
            succ = next_out[v]
            start = min(succ)
            ring = [start]
            while (nxt := succ[ring[-1]]) != start:
                ring.append(nxt)
            rings.append(tuple(ring))
        return tuple(rings)

    @property
    def valences(self) -> np.ndarray:
        """Number of edges (equivalently faces) at each vertex."""
        return np.array([len(r) for r in self.vertex_faces])

    @property
    def face_sizes(self) -> np.ndarray:
        """Number of sides of each face."""
        return np.array([len(f) for f in self.faces])

    def summary(self) -> dict:
        """Counts for manifests: V, E, F, and the valence and face-size distributions."""
        return {
            "V": self.n_vertices,
            "E": self.n_edges,
            "F": self.n_faces,
            "valences": dict(sorted(Counter(self.valences.tolist()).items())),
            "face_sizes": dict(sorted(Counter(self.face_sizes.tolist()).items())),
        }

    def same_combinatorics(self, other: Polyhedron) -> bool:
        """True if both have the same face lattice under the **identity** vertex labelling.

        Use this for deformations that move vertices but keep their labels. It is not an
        isomorphism test.
        """
        if self.n_vertices != other.n_vertices:
            return False
        return {_canonical_cycle(f) for f in self.faces} == {
            _canonical_cycle(f) for f in other.faces
        }

    # --- metric data -------------------------------------------------------------------

    @property
    def scale(self) -> float:
        """Circumradius about the origin; tolerances are relative to it."""
        return float(np.linalg.norm(self.vertices, axis=1).max())

    @cached_property
    def face_planes(self) -> tuple[np.ndarray, np.ndarray]:
        """``(normals, offsets)``: unit outward normals ``n`` and ``h`` with ``n . x = h``."""
        normals = _unit(np.array([_newell_normal(self.vertices[list(f)]) for f in self.faces]))
        offsets = np.array(
            [
                n @ self.vertices[list(f)].mean(axis=0)
                for n, f in zip(normals, self.faces, strict=True)
            ]
        )
        return normals, offsets

    # --- validation --------------------------------------------------------------------

    def validate(self) -> None:
        """Check the full geometry contract, raising `GeometryError` that lists every failure."""
        problems: list[str] = []
        V = self.vertices
        tol = self.tol * max(self.scale, 1e-300)

        if V.ndim != 2 or V.shape[1] != 3 or len(V) < 4:
            raise GeometryError("need at least 4 vertices in 3D")
        if np.linalg.matrix_rank(V - V.mean(axis=0), tol=tol) < 3:
            raise GeometryError("vertices are not full-dimensional")

        used = set()
        for i, f in enumerate(self.faces):
            if len(f) < 3 or len(set(f)) != len(f):
                problems.append(f"face {i} needs at least 3 distinct vertices: {f}")
            if any(not 0 <= k < len(V) for k in f):
                raise GeometryError(f"face {i} has a vertex index out of range: {f}")
            used.update(f)
        if unused := sorted(set(range(len(V))) - used):
            problems.append(f"vertices {unused} are on no face")
        if problems:
            raise GeometryError("; ".join(problems))

        # Closed, consistently oriented 2-manifold: each directed edge exactly once, together
        # with its reverse.
        directed = Counter((f[k], f[(k + 1) % len(f)]) for f in self.faces for k in range(len(f)))
        if repeated := [e for e, c in directed.items() if c > 1]:
            problems.append(f"directed edges used twice (inconsistent orientation): {repeated}")
        if open_edges := [e for e in directed if (e[1], e[0]) not in directed]:
            problems.append(f"edges on only one face (surface not closed): {open_edges}")
        if problems:
            raise GeometryError("; ".join(problems))

        normals, offsets = self.face_planes
        for i, f in enumerate(self.faces):
            pts = V[list(f)]
            if (off := np.abs(pts @ normals[i] - offsets[i]).max()) > tol:
                problems.append(f"face {i} is not planar (max deviation {off:.3g})")
            # Strictly convex polygon, counterclockwise about the outward normal: every turn is
            # left. A zero turn is a vertex in the middle of a straight side, not a corner.
            # Measured as the sine of the turning angle, so the test is scale-free.
            side = np.roll(pts, -1, axis=0) - pts
            nxt = np.roll(side, -1, axis=0)
            sines = (np.cross(side, nxt) @ normals[i]) / (
                np.linalg.norm(side, axis=1) * np.linalg.norm(nxt, axis=1)
            )
            if sines.min() <= self.tol:
                problems.append(f"face {i} is not a strictly convex polygon in face order")

        # Convexity (and outward orientation): every vertex on or behind every face plane.
        excess = V @ normals.T - offsets
        if (worst := excess.max()) > tol:
            f = int(np.unravel_index(excess.argmax(), excess.shape)[1])
            problems.append(
                f"not convex or faces point inward: a vertex is {worst:.3g} outside face {f}"
            )

        # Genuine faces: no two faces sharing an edge lie in one plane.
        for (a, b), (f, g) in zip(self.edges, self.edge_faces, strict=True):
            if np.linalg.norm(normals[f] - normals[g]) <= self.tol:
                problems.append(f"faces {f} and {g} are coplanar across edge ({a}, {b})")

        if (h_min := offsets.min()) <= tol:
            problems.append(f"origin is not strictly inside (smallest face offset {h_min:.3g})")

        if (chi := self.n_vertices - self.n_edges + self.n_faces) != 2:
            problems.append(f"Euler characteristic is {chi}, not 2")

        if problems:
            raise GeometryError("; ".join(problems))

    # --- polarity and transformations -------------------------------------------------

    def polar_dual(self) -> Polyhedron:
        """The polar dual with respect to the unit sphere about the origin.

        Vertex ``j`` of the dual is ``n_j / h_j`` for face ``j`` here. Face ``i`` of the dual
        lists the dual vertices around primal vertex ``i``. Applying it twice returns this
        polyhedron's vertices in the same order, up to rounding.
        """
        normals, offsets = self.face_planes
        return Polyhedron.from_faces(
            normals / offsets[:, None],
            self.vertex_faces,
            name=f"polar dual of {self.name}" if self.name else "",
            tol=self.tol,
        )

    def rotated(self, rotation) -> Polyhedron:
        """Apply a proper rotation matrix. Labels and combinatorics are unchanged."""
        R = np.asarray(rotation, dtype=float)
        if not (np.allclose(R @ R.T, np.eye(3), atol=1e-12) and np.linalg.det(R) > 0):
            raise GeometryError("rotation must be a proper orthogonal 3x3 matrix")
        return Polyhedron.from_faces(self.vertices @ R.T, self.faces, name=self.name, tol=self.tol)

    def translated(self, offset) -> Polyhedron:
        """Move the solid by ``offset`` relative to the origin; validation rechecks the origin."""
        return Polyhedron.from_faces(
            self.vertices + np.asarray(offset, dtype=float), self.faces, self.name, self.tol
        )

    def with_vertices(self, vertices) -> Polyhedron:
        """Same labelled faces on new coordinates, e.g. a fixed-combinatorics deformation.

        Raises `GeometryError` if the new coordinates break the contract. A generic vertex
        motion makes faces non-planar, which means the face lattice would change.
        """
        return Polyhedron.from_faces(vertices, self.faces, self.name, self.tol)

    # --- symmetry ---------------------------------------------------------------------

    def symmetry_group(self) -> list[np.ndarray]:
        """All orthogonal maps fixing the origin that carry the polyhedron onto itself.

        These are the rotations and reflections (proper and improper elements) **about the
        origin**, which is the group a recipe can preserve. An off-centre origin reduces it.
        Found by mapping one frame of three independent vertices onto every compatible frame,
        then keeping the maps that are orthogonal and permute the faces.
        """
        V = self.vertices
        tol = self.tol * max(self.scale, 1e-300) * 1e3
        norms = np.linalg.norm(V, axis=1)
        dist = np.linalg.norm(V[:, None, :] - V[None, :, :], axis=-1)
        valence = self.valences

        i0 = 0
        i1 = next(j for a, b in self.edges for j in (a, b) if i0 in (a, b) and j != i0)
        i2 = next(
            k
            for k in range(len(V))
            if abs(np.linalg.det(V[[i0, i1, k]])) > 1e-6 * max(self.scale, 1e-300) ** 3
        )
        frame_inv = np.linalg.inv(V[[i0, i1, i2]].T)
        faces = {frozenset(f) for f in self.faces}

        def compatible(j: int, i: int) -> bool:
            return abs(norms[j] - norms[i]) <= tol and valence[j] == valence[i]

        group: list[np.ndarray] = []
        for j0 in range(len(V)):
            if not compatible(j0, i0):
                continue
            for j1 in range(len(V)):
                if not compatible(j1, i1) or abs(dist[j0, j1] - dist[i0, i1]) > tol:
                    continue
                for j2 in range(len(V)):
                    if (
                        not compatible(j2, i2)
                        or abs(dist[j0, j2] - dist[i0, i2]) > tol
                        or abs(dist[j1, j2] - dist[i1, i2]) > tol
                    ):
                        continue
                    M = V[[j0, j1, j2]].T @ frame_inv
                    if not np.allclose(M @ M.T, np.eye(3), atol=1e-9):
                        continue
                    image = V @ M.T
                    d = np.linalg.norm(image[:, None, :] - V[None, :, :], axis=-1)
                    perm = d.argmin(axis=1)
                    if d[np.arange(len(V)), perm].max() > tol or len(set(perm.tolist())) != len(V):
                        continue
                    if {frozenset(perm[list(f)].tolist()) for f in self.faces} != faces:
                        continue
                    if not any(np.allclose(M, g, atol=1e-9) for g in group):
                        group.append(M)
        return group

    # --- point sets on the sphere -----------------------------------------------------

    def vertex_directions(self) -> np.ndarray:
        """Radial projections of the vertices."""
        return _unit(self.vertices)

    def face_directions(self) -> np.ndarray:
        """Unit outward face normals: the directions of the polar dual's vertices."""
        return self.face_planes[0].copy()

    def face_centroid_directions(self) -> np.ndarray:
        """Radial projections of the faces' area centroids.

        This is a separate candidate from `face_directions`. The two agree only when the foot
        of the perpendicular from the origin is the face's centroid.
        """
        return _unit(np.array([_polygon_centroid(self.vertices[list(f)]) for f in self.faces]))

    def edge_feet(self) -> tuple[np.ndarray, np.ndarray]:
        """Foot of the perpendicular from the origin to each edge's line, with its parameter.

        Returns ``(points, t)``, where the foot is ``(1 - t) a + t b`` for edge ``(a, b)``. The
        foot lies on the edge segment itself when ``0 <= t <= 1``.
        """
        a = self.vertices[[e[0] for e in self.edges]]
        b = self.vertices[[e[1] for e in self.edges]]
        d = b - a
        t = -np.einsum("ij,ij->i", a, d) / np.einsum("ij,ij->i", d, d)
        return a + t[:, None] * d, t

    def edge_tangency_directions(self) -> np.ndarray:
        """Directions of the edge feet (see `edge_feet`).

        These are self-dual under polarity: an edge and its polar-dual edge have feet in the
        same direction. For a canonical polyhedron they are the midsphere tangency points.
        """
        return _unit(self.edge_feet()[0])

    def edge_midpoint_directions(self) -> np.ndarray:
        """Radial projections of the edge midpoints: a separate candidate from the feet."""
        a = self.vertices[[e[0] for e in self.edges]]
        b = self.vertices[[e[1] for e in self.edges]]
        return _unit((a + b) / 2.0)

    def dual_edge_index(self) -> np.ndarray:
        """For each edge here, the index of its polar-dual edge in ``self.polar_dual().edges``.

        Primal edge ``(a, b)`` separates faces ``f`` and ``g``, and its dual edge joins dual
        vertices ``f`` and ``g``.
        """
        dual_edges = {e: k for k, e in enumerate(self.polar_dual().edges)}
        return np.array([dual_edges[(min(f, g), max(f, g))] for f, g in self.edge_faces])
