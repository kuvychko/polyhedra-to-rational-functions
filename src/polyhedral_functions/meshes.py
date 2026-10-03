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

from .baseline import meshtools, ornaments
from .catalog import Piece
from .evaluation import as_function
from .manifests import sha256

DEPTH = 0.2
DEFAULT_RESOLUTION = 300


def relief_generator(piece: Piece, cmap=None) -> tuple[OrnamentGenerator, str]:
    """complexplorer's generator for a piece, and a one-line description of its display."""
    if piece.origin == "baseline":
        gen, info = ornaments.generator(ornaments.BY_SLUG[piece.baseline_slug], cmap=cmap)
        return gen, f"baseline settings ({info['scaling']}, k = {info['sharpness']})"
    d = piece.divisor()
    gen = OrnamentGenerator(
        as_function(d),
        resolution=piece.resolution or DEFAULT_RESOLUTION,
        cmap=cmap,
        normalize=None,
        pole_order=int(np.abs(d.orders).max()),
        scaling_params={"r_min": DEPTH, "r_max": 1.0},
    )
    return gen, f"order-tuned (k = {gen.sharpness:g})"


def closed_relief(piece: Piece, cmap=None):
    """The piece's relief as a watertight, consistently oriented solid in unit coordinates."""
    gen, _ = relief_generator(piece, cmap=cmap)
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
