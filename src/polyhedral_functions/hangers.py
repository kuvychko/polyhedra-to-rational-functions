"""Hanging-ornament variants: a thread hole bored through one spike (decision 0008).

The hole is a cylinder along the approved cut plane's normal ``n``, through a point on a spike's
axis a few millimetres in from its tip. In print pose each half lies cut face down, so the hole is
vertical and needs no bridging. When the chosen spike lies in the cut plane, the hole runs through
both halves and lines up when they are glued.

Choosing the spike:

1. Prefer spikes (poles) bisected by the cut plane (``|n . p| < sin 5 deg``), then spikes within
   35 degrees of it. The hole axis must cross the spike's axis roughly at right angles.
2. Among those, take the most prominent: the largest tip radius, measured by ray-casting the
   closed mesh.

Placing the hole: start ``distance_mm`` in from the tip. Measure the spike's width beside the
hole, along ``w = p x n``. Move inward in 0.5 mm steps until both sides keep at least ``wall_mm``
of material. The final distance is reported, so a thin spike shows up as a larger number rather
than a weak print.

Booleans and the plane split use ``manifold3d``, which is exact on closed meshes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import manifold3d as mf
import numpy as np
import pyvista as pv

from .divisors import Divisor

BISECTED_SIN = np.sin(np.radians(5.0))
EXIT_MARGIN_MM = 2.0  # the bore continues this far past the spike surface on each side
REMOVED_TOLERANCE = 0.15  # removed volume may exceed the spike crossing by this fraction
NEAR_PLANE_SIN = np.sin(np.radians(35.0))


@dataclass
class Hole:
    spike_direction: list
    spike_order: int
    bisected: bool
    tip_radius_mm: float
    distance_from_tip_mm: float
    side_wall_mm: float
    diameter_mm: float
    length_mm: float
    centre_mm: list
    reach_plus_mm: float  # solid along +n from the centre
    reach_minus_mm: float  # solid along -n

    def record(self) -> dict:
        return asdict(self)


def to_manifold(mesh: pv.PolyData) -> mf.Manifold:
    tri = mesh.triangulate().clean()
    faces = tri.faces.reshape(-1, 4)[:, 1:].astype(np.uint32)
    m = mf.Manifold(mf.Mesh(vert_properties=np.asarray(tri.points, np.float32), tri_verts=faces))
    if m.status() != mf.Error.NoError:
        raise RuntimeError(f"mesh is not a valid closed manifold: {m.status()}")
    return m


def from_manifold(m: mf.Manifold) -> pv.PolyData:
    mesh = m.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3].astype(float)
    tris = np.asarray(mesh.tri_verts)
    faces = np.hstack([np.full((len(tris), 1), 3), tris]).ravel()
    return pv.PolyData(verts, faces)


def radius_along(mesh: pv.PolyData, direction) -> float:
    """Distance from the centre to the surface along a ray (the relief is star-shaped)."""
    d = np.asarray(direction, dtype=float)
    d = d / np.linalg.norm(d)
    far = 4.0 * float(np.linalg.norm(mesh.points, axis=1).max())
    points, _ = mesh.ray_trace((0.0, 0.0, 0.0), tuple(d * far), first_point=False)
    return float(np.linalg.norm(points, axis=1).max()) if len(points) else 0.0


def inside(mesh: pv.PolyData, x) -> bool:
    r = float(np.linalg.norm(x))
    return r < radius_along(mesh, x) if r > 1e-9 else True


def extent(mesh, centre, direction, step=0.05, limit=60.0) -> float:
    """How far from ``centre`` along ``direction`` the solid continues."""
    s = 0.0
    while s < limit and inside(mesh, centre + (s + step) * direction):
        s += step
    return s


def choose_spike(mesh_mm: pv.PolyData, divisor: Divisor, normal) -> tuple[np.ndarray, int, bool]:
    n = np.asarray(normal, dtype=float)
    poles = divisor.poles
    candidates = []
    for p, order in zip(poles.points, -poles.orders, strict=True):
        s = abs(float(n @ p))
        if s > NEAR_PLANE_SIN:
            continue
        candidates.append((s < BISECTED_SIN, radius_along(mesh_mm, p), p, int(order)))
    if not candidates:
        raise RuntimeError("no spike within 35 degrees of the cut plane")
    bisected, _, p, order = max(candidates, key=lambda c: (c[0], c[1]))
    return p, order, bisected


def place_hole(
    mesh_mm, divisor, normal, diameter_mm=1.5, distance_mm=9.0, wall_mm=1.0, max_distance_mm=16.0
) -> Hole:
    n = np.asarray(normal, dtype=float) / np.linalg.norm(normal)
    p, order, bisected = choose_spike(mesh_mm, divisor, n)
    tip = radius_along(mesh_mm, p)
    w = np.cross(p, n)
    w /= np.linalg.norm(w)
    r_hole = diameter_mm / 2
    d = distance_mm
    while True:
        centre = p * (tip - d)
        wall = min(extent(mesh_mm, centre, w), extent(mesh_mm, centre, -w)) - r_hole
        if wall >= wall_mm or d >= max_distance_mm:
            break
        d += 0.5
    if wall < wall_mm:
        raise RuntimeError(
            f"spike too thin for a {diameter_mm} mm hole within {max_distance_mm} mm"
        )
    plus, minus = extent(mesh_mm, centre, n), extent(mesh_mm, centre, -n)
    return Hole(
        spike_direction=[round(float(x), 4) for x in p],
        spike_order=order,
        bisected=bool(bisected),
        tip_radius_mm=round(tip, 2),
        distance_from_tip_mm=d,
        side_wall_mm=round(wall, 2),
        diameter_mm=diameter_mm,
        length_mm=round(plus + minus + 2 * EXIT_MARGIN_MM, 2),
        centre_mm=[round(float(x), 3) for x in centre],
        reach_plus_mm=round(plus, 2),
        reach_minus_mm=round(minus, 2),
    )


def bore(solid: mf.Manifold, hole: Hole, normal) -> mf.Manifold:
    """Subtract the hole cylinder from the solid.

    The cylinder runs along ``normal`` from ``EXIT_MARGIN_MM`` beyond the spike surface on one
    side to the same beyond it on the other. The removed volume is checked against the cylinder
    crossing the spike. A bore that also cut into another part of the object raises, rather than
    making a hole somewhere unintended.
    """
    n = np.asarray(normal, dtype=float) / np.linalg.norm(normal)
    r = hole.diameter_mm / 2
    cyl = mf.Manifold.cylinder(hole.length_mm, r, r, 48)
    cyl = cyl.translate([0.0, 0.0, -(hole.reach_minus_mm + EXIT_MARGIN_MM)])
    z = np.array([0.0, 0.0, 1.0])
    axis, c = np.cross(z, n), float(z @ n)
    s = np.linalg.norm(axis)
    if s < 1e-12:
        R = np.eye(3) if c > 0 else np.diag([1.0, -1.0, -1.0])
    else:
        k = axis / s
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        R = np.eye(3) + s * K + (1 - c) * K @ K
    affine = np.hstack([R, np.asarray(hole.centre_mm, dtype=float).reshape(3, 1)])
    bored = solid - cyl.transform(affine.tolist())
    removed = solid.volume() - bored.volume()
    crossing = np.pi * r**2 * (hole.reach_plus_mm + hole.reach_minus_mm)
    if removed > crossing * (1 + REMOVED_TOLERANCE) or removed <= 0:
        raise RuntimeError(
            f"bore removed {removed:.1f} mm3, expected about {crossing:.1f}: the hole cut into "
            "more than its spike"
        )
    return bored


def split(solid: mf.Manifold, normal) -> tuple[pv.PolyData, pv.PolyData]:
    """(the ``+n`` half, the ``-n`` half), each closed."""
    n = np.asarray(normal, dtype=float) / np.linalg.norm(normal)
    a, b = solid.split_by_plane(n.tolist(), 0.0)
    a, b = from_manifold(a), from_manifold(b)
    if a.n_points and float(a.points.mean(axis=0) @ n) < 0:
        a, b = b, a
    return a, b
