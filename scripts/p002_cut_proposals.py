"""P002: cut-plane proposals for every printable catalog piece, for the owner to approve.

Run:  uv run python scripts/p002_cut_proposals.py [--publish]

For each piece, the best three distinct planes through the centre (``cuts.propose``), ranked:

1. halves identical (one file printed twice), then mirror images, then different;
2. then less support;
3. then more clearance between the plane and the nearest feature not in it;
4. then a larger cut face.

Measures are given at the piece's planned size, or 130 mm if undecided. Each tile shows the two
halves in print pose (cut face down) on a shared bed.

To approve a plane, copy its normal into the piece's catalog entry::

    cut: {normal: [0.7071, 0.0, 0.7071], approved: true}

``scripts/b2_export_stls.py`` then writes the cut STLs. Outputs, in ``out/P002-cut-proposals/``:
``proposals.csv``, ``proposals.png``, ``manifest.json``.
"""

from __future__ import annotations

import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

from polyhedral_functions import catalog, cuts, fixtures, meshes  # noqa: E402
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    new_manifest,
    output_entry,
    publish_evidence,
    relative,
    sha256,
    write_json,
)

CONFIG = REPO_ROOT / "configs" / "experiments" / "P002-cut-proposals.json"


def render_halves(mesh, normal, path, window):
    upper, lower = cuts.cut(mesh, normal)
    a, b = cuts.to_print_pose(upper, normal), cuts.to_print_pose(lower, -normal)
    width = max(a.bounds[1] - a.bounds[0], b.bounds[1] - b.bounds[0])
    a.points[:, 0] -= (a.bounds[0] + a.bounds[1]) / 2 + 0.6 * width
    b.points[:, 0] -= (b.bounds[0] + b.bounds[1]) / 2 - 0.6 * width
    for half in (a, b):
        half.points[:, 1] -= (half.bounds[2] + half.bounds[3]) / 2
    pl = pv.Plotter(off_screen=True, window_size=(window, int(window * 0.6)))
    pl.set_background("white")
    bed = pv.Plane(center=(0, 0, 0), i_size=3.2 * width, j_size=1.6 * width)
    pl.add_mesh(bed, color="#d6dbe3")
    for half in (a, b):
        pl.add_mesh(half, color="#e8e4da", smooth_shading=True, specular=0.3, diffuse=0.85)
    pl.camera.position = (0.0, -3.2 * width, 1.6 * width)
    pl.camera.focal_point = (0.0, 0.0, 0.25 * width)
    pl.camera.up = (0.0, 0.0, 1.0)
    pl.reset_camera()
    pl.camera.zoom(1.75)
    path.parent.mkdir(parents=True, exist_ok=True)
    pl.screenshot(str(path))
    pl.close()
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    out = REPO_ROOT / "out" / config["id"]
    manifest = new_manifest(config)
    manifest["config_file"] = {"path": relative(CONFIG), "sha256": sha256(CONFIG)}
    manifest["catalog"] = {
        "path": relative(catalog.CATALOG_FILE),
        "sha256": sha256(catalog.CATALOG_FILE),
    }

    pieces = [p for p in catalog.load() if not p.digital_only]
    rows, tiles = [], {}
    for piece in pieces:
        print(f"{piece.id} ...", flush=True)
        mesh = meshes.closed_relief(piece, resolution=config["screening_resolution"])
        group = fixtures.load(piece.polyhedron).symmetry_group()
        proposals = cuts.propose(mesh, piece.divisor(), group, sweep=config["sweep"])
        size = piece.planned_size_mm or 130
        scale = cuts.mm_per_unit(mesh, size)
        sea = config["sea_level_radius"]
        tiles[piece.id] = []
        for rank, c in enumerate(proposals, start=1):
            row = {
                "piece": piece.id,
                "rank": rank,
                "normal": [round(float(x), 4) + 0.0 for x in c.normal],
                "halves": c.halves,
                "size_mm": size,
                "support_pct": round(c.support_pct, 2),
                "clearance_deg": round(c.clearance_deg, 1),
                "clearance_mm": round(np.radians(c.clearance_deg) * sea * scale, 1),
                "split_features": c.split_features,
                "cut_area_cm2": round(c.cut_area_unit * scale**2 / 100, 1),
                "approved_in_catalog": bool(
                    piece.cut_approved() and np.allclose(piece.cut["normal"], c.normal, atol=1e-3)
                ),
            }
            rows.append(row)
            tiles[piece.id].append(
                render_halves(
                    mesh, c.normal, out / "tiles" / f"{piece.id}-{rank}.png", config["window"]
                )
            )

    csv_path = out / "proposals.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "normal": " ".join(f"{x:g}" for x in row["normal"])})
    sheet = proposal_sheet(pieces, rows, tiles, out)
    manifest["runs"] = rows
    manifest["outputs"] = [output_entry(p) for p in (csv_path, sheet)]
    write_json(out / "manifest.json", manifest)
    print(f"wrote {relative(out)}")
    if args.publish:
        dest = publish_evidence(manifest, [csv_path, sheet], config["id"])
        print(f"published to {relative(dest)}")


def proposal_sheet(pieces, rows, tiles, out):
    fig, axes = plt.subplots(len(pieces), 3, figsize=(13, 2.9 * len(pieces)))
    for r, piece in enumerate(pieces):
        mine = [x for x in rows if x["piece"] == piece.id]
        for c in range(3):
            ax = axes[r, c]
            ax.set_axis_off()
            if c >= len(mine):
                continue
            x = mine[c]
            ax.imshow(plt.imread(str(tiles[piece.id][c])))
            n = ", ".join(f"{v:g}" for v in x["normal"])
            ax.set_title(
                f"{piece.title} #{x['rank']}: halves {x['halves']}"
                + ("  [APPROVED]" if x["approved_in_catalog"] else "")
                + f"\nnormal [{n}]\n"
                f"at {x['size_mm']} mm: support {x['support_pct']}%, clearance "
                f"{x['clearance_deg']}° ({x['clearance_mm']} mm), split {x['split_features']}, "
                f"cut face {x['cut_area_cm2']} cm²",
                fontsize=7,
            )
    fig.suptitle(
        "P002 cut proposals: approve one plane per piece in catalog/pieces.yaml", fontsize=10
    )
    fig.tight_layout(rect=[0, 0, 1, 0.99])
    path = out / "proposals.png"
    fig.savefig(path, dpi=100, facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    main()
