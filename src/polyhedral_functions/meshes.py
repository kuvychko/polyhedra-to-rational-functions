"""Printable meshes for catalog pieces: one meshing path for the print screen and the STL export.

- **Baseline pieces** are meshed with their own printed settings (`baseline.ornaments`), so a
  screened or exported baseline mesh is the same object as the printed one, up to the STL
  provenance question recorded in the catalog.
- **New pieces** use the order-tuned display (decision 0005) through complexplorer's
  ``pole_order``: scale ``k = min(2 mu_max, 6)``, depth 0.2, no normalization (the chordal
  convention already sets sea level).

Meshes are closed into watertight solids by `baseline.meshtools.close_relief`. Sizes are tip to
tip (``scale_to_size(axis="extent")``), the baseline convention.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from complexplorer.export.stl import OrnamentGenerator, center_mesh, scale_to_size

from . import cuts
from .baseline import meshtools, ornaments
from .catalog import Piece
from .evaluation import as_function
from .manifests import sha256

DEPTH = 0.2
DEFAULT_RESOLUTION = 300


def relief_generator(
    piece: Piece, cmap=None, resolution: int | None = None
) -> tuple[OrnamentGenerator, str]:
    """complexplorer's generator for a piece, and a one-line description of its display.

    ``resolution`` overrides the piece's own (a coarser mesh for screening cut planes); exports
    always use the piece's resolution.
    """
    if piece.origin == "baseline":
        orn = ornaments.BY_SLUG[piece.baseline_slug]
        gen, info = ornaments.generator(orn, resolution=resolution, cmap=cmap)
        return gen, f"baseline settings ({info['scaling']}, k = {info['sharpness']})"
    d = piece.divisor()
    gen = OrnamentGenerator(
        as_function(d),
        resolution=resolution or piece.resolution or DEFAULT_RESOLUTION,
        cmap=cmap,
        normalize=None,
        pole_order=int(np.abs(d.orders).max()),
        scaling_params={"r_min": DEPTH, "r_max": 1.0},
    )
    return gen, f"order-tuned (k = {gen.sharpness:g})"


def closed_relief(piece: Piece, cmap=None, resolution: int | None = None):
    """The piece's relief as a watertight, consistently oriented solid in unit coordinates."""
    gen, _ = relief_generator(piece, cmap=cmap, resolution=resolution)
    return meshtools.close_relief(gen.generate_ornament(verbose=False))


def export_stl(piece: Piece, sizes_mm, out_dir: Path) -> dict:
    """Write ``<id>-<size>mm.stl`` for each size. Returns the per-size facts and hashes."""
    mesh = closed_relief(piece)
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = {}
    for size in sizes_mm:
        scaled = scale_to_size(mesh, float(size), axis="extent")
        facts = meshtools.inspect_mesh(scaled)
        path = out_dir / f"{piece.id}-{size}mm.stl"
        center_mesh(scaled).save(str(path), binary=True)
        entries[str(size)] = {
            "name": path.name,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "extent_mm": facts["extent_mm"],
            "waist_mm": round(2 * facts["min_radius_mm"], 1),
            "volume_cm3": facts["volume_cm3"],
            "triangles": facts["n_triangles"],
            "watertight": facts["n_boundary_edges"] == 0 and facts["n_non_manifold_edges"] == 0,
        }
    return entries


def export_cuts(piece: Piece, sizes_mm, out_dir: Path) -> dict:
    """Cut STLs for the piece's approved plane, in print pose (cut face on z = 0), per size.

    Identical halves (a proper symmetry swaps the sides) are exported once, to be printed twice.
    Mirror-image or different halves are exported as ``-half-a`` (the ``+n`` side) and
    ``-half-b``. Each half must be watertight, or this raises.
    """
    if not piece.cut_approved():
        raise ValueError(f"{piece.id}: no approved cut plane in the catalog")
    from . import fixtures

    group = fixtures.load(piece.polyhedron).symmetry_group()
    normal, snapped = cuts.snap_normal(piece.cut["normal"], group)
    relation = cuts.halves_relation(normal, group)
    mesh = closed_relief(piece)
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = {}
    for size in sizes_mm:
        scaled = scale_to_size(mesh, float(size), axis="extent")
        upper, lower = cuts.cut(scaled, normal)
        halves = (
            [("half", upper, normal, 2)]
            if relation == "identical"
            else [
                ("half-a", upper, normal, 1),
                ("half-b", lower, -normal, 1),
            ]
        )
        files = []
        for label, half, build, copies in halves:
            posed = cuts.to_print_pose(half, build)
            if not cuts.watertight(posed):
                raise RuntimeError(f"{piece.id} {size} mm {label}: cut half is not watertight")
            path = out_dir / f"{piece.id}-{size}mm-{label}.stl"
            posed.save(str(path), binary=True)
            files.append(
                {
                    "name": path.name,
                    "sha256": sha256(path),
                    "copies": copies,
                    "bytes": path.stat().st_size,
                }
            )
        entries[str(size)] = {
            "normal": [round(float(x), 4) + 0.0 for x in piece.cut["normal"]],
            "exact_normal": [float(x) + 0.0 for x in normal],
            "snapped_to_symmetry_plane": snapped,
            "halves": relation,
            "files": files,
        }
    return entries
