"""P001: printability screen for every printable piece in the catalog, at 80 and 130 mm.

Run:  uv run python scripts/p001_print_screen.py [--publish]

For each catalog piece that is not digital-only, this meshes the relief, closes it into a solid
and measures it at each size (tip-to-tip extent, the baseline's convention):

- closure: boundary and non-manifold edge counts, which must both be 0;
- waist (twice the smallest radius from the centre), volume and triangle count;
- **closest zero-pole gap** and **closest pole-pole gap**, as arc lengths in mm on the sea-level
  sphere (``|f| = 1``, radius ``depth + (1 - depth) / 2`` of the tip radius). A short zero-pole gap
  is a spike next to a pit; a short pole-pole gap is two spikes that may fuse.

Meshing goes through `polyhedral_functions.meshes`, the same path the STL export uses. Baseline
pieces keep their printed settings; new pieces use the order-tuned rule (``k = min(2 mu_max, 6)``).

The reference bar is the smallest gaps among pieces already printed successfully at 130 mm
(``reference_pieces``). The screen reports and compares; the owner chooses.

Outputs, in ``out/P001-print-screen/``: ``screen.csv`` (read by ``catalog_status.py``),
``screen.png`` and ``manifest.json``.
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
from complexplorer.export.stl import max_extent, scale_to_size  # noqa: E402

from polyhedral_functions import catalog, meshes  # noqa: E402
from polyhedral_functions.baseline import meshtools  # noqa: E402
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    new_manifest,
    output_entry,
    publish_evidence,
    relative,
    sha256,
    write_json,
)
from polyhedral_functions.rendering import DisplaySettings, _camera, phase_cmap  # noqa: E402

CONFIG = REPO_ROOT / "configs" / "experiments" / "P001-print-screen.json"


def feature_gaps(d) -> dict:
    """Smallest angles (radians) between a zero and a pole, and between two poles."""
    zeros, poles = d.zeros.points, d.poles.points

    def min_angle(a, b, same=False):
        if not len(a) or not len(b):
            return float("nan")
        cos = np.clip(a @ b.T, -1, 1)
        if same:
            np.fill_diagonal(cos, -1)
        return float(np.arccos(cos.max()))

    return {"zero_pole": min_angle(zeros, poles), "pole_pole": min_angle(poles, poles, True)}


def screen_piece(piece, config, out):
    gen, display = meshes.relief_generator(piece)
    mesh = meshtools.close_relief(gen.generate_ornament(verbose=False))
    unit_extent = max_extent(mesh)
    gaps = feature_gaps(piece.divisor())
    sea = config["depth"] + (1 - config["depth"]) / 2
    rows = []
    for size in config["sizes_mm"]:
        scaled = scale_to_size(mesh, float(size), axis="extent")
        facts = meshtools.inspect_mesh(scaled)
        mm_per_unit = size / unit_extent
        rows.append(
            {
                "piece": piece.id,
                "size_mm": size,
                "display": display,
                "closed": facts["n_boundary_edges"] == 0 and facts["n_non_manifold_edges"] == 0,
                "triangles": facts["n_triangles"],
                "waist_mm": round(2 * facts["min_radius_mm"], 1),
                "tip_radius_mm": facts["max_radius_mm"],
                "volume_cm3": facts["volume_cm3"],
                "zero_pole_gap_mm": round(gaps["zero_pole"] * sea * mm_per_unit, 1),
                "pole_pole_gap_mm": round(gaps["pole_pole"] * sea * mm_per_unit, 1),
            }
        )
    tiles = render(piece, config, out)
    return rows, tiles


def render(piece, config, out):
    view = config["views"].get(piece.polyhedron, config["views"]["default"])
    settings = DisplaySettings(window=config["window"])
    paths = {}
    for style in ("neutral", "colored"):
        mesh = meshes.closed_relief(piece, cmap=phase_cmap(settings))
        pl = pv.Plotter(off_screen=True, window_size=(config["window"], config["window"]))
        pl.set_background("white")
        if style == "neutral":
            pl.add_mesh(mesh, color="#e8e4da", smooth_shading=True, specular=0.3, diffuse=0.85)
        else:
            pl.add_mesh(
                mesh,
                scalars="RGB",
                rgb=True,
                smooth_shading=True,
                specular=0.3,
                diffuse=0.85,
                ambient=0.25,
            )
        _camera(pl, view)
        path = out / "tiles" / f"{piece.id}-{style}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.screenshot(str(path))
        pl.close()
        paths[style] = path
    return paths


def sheet(pieces, rows, tiles, reference, out):
    n = len(pieces)
    fig, axes = plt.subplots(
        n, 3, figsize=(11.5, 2.5 * n), gridspec_kw={"width_ratios": [1, 1, 2.4]}
    )
    for r, piece in enumerate(pieces):
        for c, style in enumerate(("neutral", "colored")):
            axes[r, c].imshow(plt.imread(str(tiles[piece.id][style])))
            axes[r, c].set_axis_off()
        ax = axes[r, 2]
        ax.set_axis_off()
        lines = [
            f"{piece.title}   [{piece.origin}, {piece.recipe}"
            f"{' reciprocal' if piece.reciprocal else ''} on {piece.polyhedron}]"
        ]
        mine = [x for x in rows if x["piece"] == piece.id]
        lines.append(mine[0]["display"] + ("" if mine[0]["closed"] else "   MESH NOT CLOSED"))
        for x in mine:
            flag = ""
            if x["zero_pole_gap_mm"] < reference[x["size_mm"]]["zero_pole_gap_mm"]:
                flag += "  < ref (zero–pole)"
            if x["pole_pole_gap_mm"] < reference[x["size_mm"]]["pole_pole_gap_mm"]:
                flag += "  < ref (pole–pole)"
            lines.append(
                f"{x['size_mm']:>3} mm: waist {x['waist_mm']} mm, {x['volume_cm3']} cm³, "
                f"gaps zero–pole {x['zero_pole_gap_mm']} / "
                f"pole–pole {x['pole_pole_gap_mm']} mm{flag}"
            )
        printed = ", ".join(f"{s} mm" for s in piece.printed_sizes()) or "not printed"
        planned = f"{piece.planned_size_mm} mm" if piece.planned_size_mm else "undecided"
        lines.append(f"printed: {printed}; planned: {planned}")
        ax.text(0, 0.5, "\n".join(lines), va="center", ha="left", fontsize=8, family="monospace")
    ref = reference[130]
    fig.suptitle(
        "P001 print screen. Reference (smallest among pieces printed at 130 mm): zero–pole "
        f"{ref['zero_pole_gap_mm']} mm, pole–pole {ref['pole_pole_gap_mm']} mm at 130 mm; "
        "scaled for 80 mm.",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    path = out / "screen.png"
    fig.savefig(path, dpi=100, facecolor="white")
    plt.close(fig)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    out = REPO_ROOT / "out" / config["id"]
    out.mkdir(parents=True, exist_ok=True)
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
        piece_rows, tiles[piece.id] = screen_piece(piece, config, out)
        rows += piece_rows

    # The reference bar: the smallest gaps among the pieces already printed at the reference size,
    # scaled linearly to the other size.
    ref_rows = [
        x
        for x in rows
        if x["piece"] in config["reference_pieces"] and x["size_mm"] == config["reference_size_mm"]
    ]
    reference = {}
    for size in config["sizes_mm"]:
        scale = size / config["reference_size_mm"]
        reference[size] = {
            key: round(min(x[key] for x in ref_rows) * scale, 1)
            for key in ("zero_pole_gap_mm", "pole_pole_gap_mm")
        }

    csv_path = out / "screen.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    sheet_path = sheet(pieces, rows, tiles, reference, out)
    manifest["runs"] = rows
    manifest["reference"] = reference
    manifest["outputs"] = [output_entry(p) for p in (csv_path, sheet_path)]
    write_json(out / "manifest.json", manifest)
    print(f"wrote {relative(out)}; reference {reference}")
    if args.publish:
        dest = publish_evidence(manifest, [csv_path, sheet_path], config["id"])
        print(f"published to {relative(dest)}")


if __name__ == "__main__":
    main()
