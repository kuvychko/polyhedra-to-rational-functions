"""Planar cuts of a closed relief into two flat-bottomed halves for printing (decision 0007).

Every cut is a plane through the relief's centre (the origin), with unit normal ``n``. Halves are
capped by ``pyvista``'s ``clip_closed_surface`` and printed cut face down: the half on the ``+n``
side is built along ``+n``, the other along ``-n``.

Candidate planes are proposed and scored here. The owner approves one per piece in the catalog;
nothing is exported from an unapproved plane.

- **Halves:** ``identical`` if a proper symmetry of the piece maps ``n`` to ``-n`` (one file,
  printed twice); ``mirror`` if only an improper one does; ``different`` otherwise. That is a
  property of the function, exact up to the mesh's triangulation.
- **Support:** the share of each half's outer surface that faces down more than 45 degrees in
  print orientation. The larger of the two halves is reported.
- **Slivers:** features (zeros and poles) lying in the plane are split cleanly. A feature just off
  the plane leaves a thin sliver at the cut edge. The clearance is the smallest angle from the
  plane among features not in it.
- **Cut area:** the area of the cut face (bed contact) at a given size.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pyvista as pv
from complexplorer.export.stl import count_edges, max_extent

from .divisors import Divisor
from .normalization import fibonacci_sphere

IN_PLANE_DEG = 0.5  # a feature this close to the plane counts as split, not slivered
OVERHANG_DEG = 45.0


@dataclass
class CutCandidate:
    normal: np.ndarray
    halves: str  # identical | mirror | different
    support_pct: float
    clearance_deg: float
    split_features: int
    cut_area_unit: float  # in the mesh's unit coordinates

    def rank_key(self):
        order = {"identical": 0, "mirror": 1, "different": 2}[self.halves]
        return (order, round(self.support_pct, 0), -self.clearance_deg, -self.cut_area_unit)


def _unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def candidate_normals(group: list[np.ndarray], sweep: int = 240) -> list[np.ndarray]:
    """Mirror normals and rotation axes of a nontrivial group, or a direction sweep otherwise.

    One representative per ``+-n`` pair.
    """
    normals = []
    if len(group) > 1:
        for g in group:
            w, v = np.linalg.eig(g)
            if np.linalg.det(g) < 0 and np.isclose(np.trace(g), 1.0):  # a reflection
                normals.append(np.real(v[:, np.argmin(np.abs(w + 1))]))
            elif np.linalg.det(g) > 0 and not np.allclose(g, np.eye(3)):  # a rotation axis
                normals.append(np.real(v[:, np.argmin(np.abs(w - 1))]))
    else:
        normals = list(fibonacci_sphere(2 * sweep))
    unique: list[np.ndarray] = []
    for n in normals:
        n = _unit(n)
        if n[np.argmax(np.abs(n))] < 0:
            n = -n
        if not any(abs(n @ u) > 1 - 1e-6 for u in unique):
            unique.append(n)
    return unique


def halves_relation(normal: np.ndarray, group: list[np.ndarray]) -> str:
    swaps = [g for g in group if np.allclose(g @ normal, -normal, atol=1e-6)]
    if any(np.linalg.det(g) > 0 for g in swaps):
        return "identical"
    return "mirror" if swaps else "different"


def cut(mesh: pv.PolyData, normal) -> tuple[pv.PolyData, pv.PolyData]:
    """The ``+n`` and ``-n`` halves, each capped (watertight)."""
    n = _unit(normal)
    upper = mesh.clip_closed_surface(normal=tuple(n), origin=(0.0, 0.0, 0.0))
    lower = mesh.clip_closed_surface(normal=tuple(-n), origin=(0.0, 0.0, 0.0))
    return upper, lower


def to_print_pose(half: pv.PolyData, build_direction) -> pv.PolyData:
    """Rotate so ``build_direction`` is +z and put the cut face on ``z = 0``."""
    b = _unit(build_direction)
    z = np.array([0.0, 0.0, 1.0])
    axis = np.cross(b, z)
    s, c = np.linalg.norm(axis), float(b @ z)
    if s < 1e-12:
        R = np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    else:
        k = axis / s
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        R = np.eye(3) + s * K + (1 - c) * K @ K
    posed = half.copy()
    posed.points = half.points @ R.T
    posed.points[:, 2] -= posed.points[:, 2].min()
    return posed


def support_share(posed: pv.PolyData) -> float:
    """Percent of the outer surface facing down more than `OVERHANG_DEG` (cap excluded)."""
    tri = posed.triangulate().compute_normals(
        cell_normals=True, point_normals=False, auto_orient_normals=True
    )
    normals = tri.cell_data["Normals"]
    areas = tri.compute_cell_sizes(length=False, volume=False).cell_data["Area"]
    centers_z = tri.cell_centers().points[:, 2]
    outer = centers_z > 1e-6 * max(posed.bounds[5], 1e-12)  # drop the cap on the bed
    down = normals[:, 2] < -np.cos(np.radians(90 - OVERHANG_DEG))
    total = areas[outer].sum()
    return float(100 * areas[outer & down].sum() / total) if total > 0 else 0.0


def cut_face_area(mesh: pv.PolyData, normal) -> float:
    """Area enclosed by the cut contour, in the mesh's units (projected shoelace formula)."""
    n = _unit(normal)
    section = mesh.slice(normal=tuple(n), origin=(0.0, 0.0, 0.0))
    if section.n_points < 3:
        return 0.0
    u = _unit(np.cross(n, [1.0, 0.0, 0.0] if abs(n[0]) < 0.9 else [0.0, 1.0, 0.0]))
    w = np.cross(n, u)
    area = 0.0
    lines = section.lines.reshape(-1, 3)[:, 1:] if section.lines.size else np.empty((0, 2), int)
    for a, b in lines:  # sum of signed triangle areas from the origin, segment by segment
        pa, pb = section.points[a], section.points[b]
        area += 0.5 * ((pa @ u) * (pb @ w) - (pb @ u) * (pa @ w))
    return abs(float(area))


def feature_clearance(divisor: Divisor, normal) -> tuple[float, int]:
    """(smallest angle in degrees from the plane among features not in it, number in it)."""
    angles = np.degrees(np.arcsin(np.clip(np.abs(divisor.points @ _unit(normal)), 0, 1)))
    in_plane = angles < IN_PLANE_DEG
    off = angles[~in_plane]
    return (float(off.min()) if off.size else 90.0), int(in_plane.sum())


def evaluate(mesh: pv.PolyData, divisor: Divisor, normal, group) -> CutCandidate:
    n = _unit(normal)
    upper, lower = cut(mesh, n)
    support = max(support_share(to_print_pose(upper, n)), support_share(to_print_pose(lower, -n)))
    clearance, split = feature_clearance(divisor, n)
    return CutCandidate(
        normal=n,
        halves=halves_relation(n, group),
        support_pct=support,
        clearance_deg=clearance,
        split_features=split,
        cut_area_unit=cut_face_area(mesh, n),
    )


def watertight(mesh: pv.PolyData) -> bool:
    return (
        count_edges(mesh, boundary_edges=True) == 0
        and count_edges(mesh, non_manifold_edges=True) == 0
    )


def mm_per_unit(mesh: pv.PolyData, size_mm: float) -> float:
    """Scale from unit coordinates to millimetres at a tip-to-tip size."""
    return size_mm / max_extent(mesh)


def distinct_classes(candidates: list[CutCandidate], group) -> list[CutCandidate]:
    """One candidate per symmetry class (planes related by a symmetry give congruent cuts)."""
    kept: list[CutCandidate] = []
    for c in candidates:
        images = [g @ c.normal for g in group] or [c.normal]
        if not any(abs(k.normal @ im) > 1 - 1e-6 for k in kept for im in images):
            kept.append(c)
    return kept


def propose(mesh, divisor: Divisor, group, sweep: int = 240, top: int = 3) -> list[CutCandidate]:
    """The best `top` distinct cut planes, best first (see `CutCandidate.rank_key`)."""
    scored = [evaluate(mesh, divisor, n, group) for n in candidate_normals(group, sweep)]
    return distinct_classes(sorted(scored, key=CutCandidate.rank_key), group)[:top]
