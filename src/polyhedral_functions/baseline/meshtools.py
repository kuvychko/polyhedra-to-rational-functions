"""Closing the relief into a printable solid, and measuring it.

complexplorer builds the relief on a latitude/longitude grid with three open boundaries:
the duplicated `phi = 0 / 2*pi` seam, and a small cap missing at each pole. Its
`repair_mesh_simple` closes all three, and since 3.1 its edge counts and its `max_extent`
are honest, so this module is thin: `close_relief` repairs, orients the normals and
*raises* if anything is left open -- which the library's `save_stl` only reports -- and
`inspect_mesh` collects the printability facts the manifest records.

The STL path goes through here rather than `save_stl` because each piece is meshed once
and saved at several sizes, and the renders need the same closed solid.

Frozen copy of ``meshtools.py`` -- see the package docstring for provenance. Verbatim
apart from this paragraph and ruff reformatting.
"""

from __future__ import annotations

import numpy as np
import pyvista as pv
from complexplorer.export.stl import count_edges, max_extent, repair_mesh_simple


def close_relief(mesh: pv.PolyData, verbose: bool = False) -> pv.PolyData:
    """Return a watertight, consistently oriented copy of a relief mesh.

    Raises
    ------
    RuntimeError
        If the mesh is still open or non-manifold afterwards -- better to stop here than
        to hand a slicer something it will silently reinterpret.
    """
    surf = mesh.extract_surface(algorithm="dataset_surface")
    closed = repair_mesh_simple(surf, fill_holes=True, verbose=False)

    # Make the surface consistently outward-facing so the STL's facet normals mean
    # something. The library's repair leaves winding alone.
    closed = closed.compute_normals(
        consistent_normals=True, auto_orient_normals=True, inplace=False
    )

    n_boundary = count_edges(closed, boundary_edges=True)
    n_nonmanifold = count_edges(closed, non_manifold_edges=True)

    if verbose:
        print(
            f"  closed relief: {surf.n_points} -> {closed.n_points} points, "
            f"{surf.n_cells} -> {closed.n_cells} faces "
            f"(boundary {n_boundary}, non-manifold {n_nonmanifold})"
        )

    if n_boundary or n_nonmanifold:
        raise RuntimeError(
            f"relief did not close: {n_boundary} boundary edges, {n_nonmanifold} non-manifold edges"
        )
    if closed.volume <= 0:
        raise RuntimeError(f"relief has non-positive volume ({closed.volume:.4g})")

    return closed


def inspect_mesh(mesh: pv.PolyData) -> dict:
    """Printability facts about a millimetre-scaled ornament, measured from the origin.

    Call this *before* centring the mesh. The relief is a star-shaped solid about the
    origin, so radii from the origin are the meaningful ones -- the thinnest
    cross-section through the body is twice the minimum. Measuring from the bounding-box
    centre instead badly understates the range on a lopsided piece like the dipole,
    whose star centre and box centre are far apart.

    What no single number captures is the ridge between two adjacent pits;
    `min_radius_mm` is the honest proxy, and the README calls out the one piece where
    the ridge, not the radius, is the binding constraint.
    """
    radii = np.linalg.norm(mesh.points, axis=1)
    bounds = mesh.bounds
    return {
        "n_points": int(mesh.n_points),
        "n_triangles": int(mesh.n_cells),
        "n_boundary_edges": count_edges(mesh, boundary_edges=True),
        "n_non_manifold_edges": count_edges(mesh, non_manifold_edges=True),
        "dimensions_mm": [
            round(bounds[1] - bounds[0], 2),
            round(bounds[3] - bounds[2], 2),
            round(bounds[5] - bounds[4], 2),
        ],
        "extent_mm": round(max_extent(mesh), 2),
        "min_radius_mm": round(float(radii.min()), 2),
        "max_radius_mm": round(float(radii.max()), 2),
        "volume_cm3": round(float(mesh.volume) / 1000.0, 1),
        "surface_area_cm2": round(float(mesh.area) / 100.0, 1),
    }
