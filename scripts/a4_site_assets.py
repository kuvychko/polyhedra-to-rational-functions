"""A4: precompute the coordinated views shown on each object page.

Run:  uv run python scripts/a4_site_assets.py                # every catalog piece
      uv run python scripts/a4_site_assets.py -p tetrahedral-dual

For each piece, five views from one camera, written to ``docs/assets/pieces/<id>/`` (committed
JPEGs):

1. ``geometry``: the solid, with zeros (blue) and poles (red) on the sphere;
2. ``plane``: the domain-colored portrait of ``f`` in the chart;
3. ``sphere``: ``f``'s phase on the unit sphere;
4. ``relief``: the printed shape, colored by phase;
5. ``neutral``: the printed shape, uncolored.

The reliefs come from `meshes.closed_relief`, the same path as the STLs, so the picture is the
object. Every view uses the fitted orthographic framing (``rendering._camera``), so no spike
leaves the frame. ``docs/assets/pieces/manifest.json`` records the configuration, the code
commit and every file's hash. Expensive generation is kept out of the site build
(``PROGRAM.md`` §14): the site only reads these files.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import complexplorer as cp  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pyvista as pv  # noqa: E402
from PIL import Image  # noqa: E402

from polyhedral_functions import catalog, fixtures, meshes  # noqa: E402
from polyhedral_functions.evaluation import as_function  # noqa: E402
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    environment,
    git_state,
    relative,
    sha256,
    write_json,
)
from polyhedral_functions.rendering import (  # noqa: E402
    DisplaySettings,
    _camera,
    render_geometry,
    render_relief,
)

CONFIG = REPO_ROOT / "configs" / "site" / "piece-assets.json"
OUT = REPO_ROOT / "docs" / "assets" / "pieces"
VIEWS = ("geometry", "plane", "sphere", "relief", "neutral")


def to_jpeg(png: Path, jpg: Path, config) -> Path:
    image = Image.open(png).convert("RGB")
    width = config["image_width"]
    if image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    jpg.parent.mkdir(parents=True, exist_ok=True)
    image.save(jpg, quality=config["jpeg_quality"], optimize=True)
    return jpg


def render_printed_relief(piece, path: Path, view, config, colored: bool) -> Path:
    cmap = cp.OklabPhase(phase_sectors=config["phase_sectors"], auto_scale_r=True)
    mesh = meshes.closed_relief(piece, cmap=cmap if colored else None)
    pl = pv.Plotter(off_screen=True, window_size=(config["window"], config["window"]))
    pl.set_background("white")
    if colored:
        pl.add_mesh(
            mesh,
            scalars="RGB",
            rgb=True,
            smooth_shading=True,
            specular=0.3,
            diffuse=0.85,
            ambient=0.25,
        )
    else:
        pl.add_mesh(mesh, color="#e8e4da", smooth_shading=True, specular=0.3, diffuse=0.85)
    _camera(pl, view, fit_points=mesh.points)
    pl.screenshot(str(path))
    pl.close()
    return path


def render_plane(piece, path: Path, config) -> Path:
    half = config["plane_half_width"]
    fig, ax = plt.subplots(figsize=(5, 5), dpi=140)
    cp.plot(
        cp.Rectangle(2 * half, 2 * half),
        as_function(piece.divisor()),
        resolution=config["plane_resolution"],
        cmap=cp.OklabPhase(phase_sectors=config["phase_sectors"], auto_scale_r=True),
        ax=ax,
    )
    ax.set_xlabel("Re z")
    ax.set_ylabel("Im z")
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


KIND_OF_LABEL = {"vertex": "vertex", "face": "face", "edge": "edge"}


def geometry_data(piece, view) -> dict:
    """What the interactive viewer draws: the solid at circumradius 1, with zeros and poles.

    Each marker carries its order and the cell it stands for, for the viewer's labels. Points
    are unit directions; the viewer draws them just outside the unit sphere, as the static
    render does.
    """
    poly = fixtures.load(piece.polyhedron)
    d = piece.divisor()

    def marker(point, order, label):
        kinds = sorted({part.split()[0] for part in label.split("+")})
        return {
            "p": [round(float(x), 6) for x in point],
            "order": abs(int(order)),
            "cell": " and ".join(KIND_OF_LABEL.get(k, k) for k in kinds),
        }

    return {
        "piece": piece.id,
        "title": piece.title,
        "solid": poly.name,
        "view": [float(x) for x in view],
        "vertices": [[round(float(x), 6) for x in v] for v in poly.vertices / poly.scale],
        "faces": [list(f) for f in poly.faces],
        "zeros": [
            marker(p, o, lab)
            for p, o, lab in zip(d.points, d.orders, d.labels, strict=True)
            if o > 0
        ],
        "poles": [
            marker(p, o, lab)
            for p, o, lab in zip(d.points, d.orders, d.labels, strict=True)
            if o < 0
        ],
    }


def write_geometry_json(piece, config) -> dict:
    view = config["views"].get(piece.polyhedron, config["views"]["default"])
    path = OUT / piece.id / "geometry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(geometry_data(piece, view), fh, separators=(",", ":"))
        fh.write("\n")
    return {"path": relative(path), "sha256": sha256(path)}


def piece_assets(piece, config) -> dict:
    view = config["views"].get(piece.polyhedron, config["views"]["default"])
    tmp = REPO_ROOT / "out" / "site-assets" / piece.id
    tmp.mkdir(parents=True, exist_ok=True)
    settings = DisplaySettings(
        window=config["window"],
        relief_resolution=config["sphere_resolution"],
        phase_sectors=config["phase_sectors"],
        framing="fit",
    )
    d = piece.divisor()
    pngs = {
        "geometry": render_geometry(
            fixtures.load(piece.polyhedron), d, tmp / "geometry.png", view, settings
        ),
        "plane": render_plane(piece, tmp / "plane.png", config),
        "sphere": render_relief(d, tmp / "sphere.png", view, settings, "sphere"),
        "relief": render_printed_relief(piece, tmp / "relief.png", view, config, colored=True),
        "neutral": render_printed_relief(piece, tmp / "neutral.png", view, config, colored=False),
    }
    files = {}
    for name in VIEWS:
        jpg = to_jpeg(pngs[name], OUT / piece.id / f"{name}.jpg", config)
        files[name] = {"path": relative(jpg), "sha256": sha256(jpg)}
    files["geometry_data"] = write_geometry_json(piece, config)
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-p", "--piece", action="append", help="only this piece (repeatable)")
    ap.add_argument(
        "--data-only",
        action="store_true",
        help="only (re)write each piece's geometry.json for the interactive viewer",
    )
    args = ap.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    pieces = catalog.load()
    if args.piece:
        pieces = [p for p in pieces if p.id in args.piece]

    manifest_path = OUT / "manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"pieces": {}}
    )
    code = git_state()
    for piece in pieces:
        print(f"{piece.id} ...", flush=True)
        if args.data_only:
            entry = manifest["pieces"].setdefault(piece.id, {"files": {}})
            entry["files"]["geometry_data"] = write_geometry_json(piece, config)
            entry["data_code"] = {"commit": code["commit"], "dirty": code["dirty"]}
            continue
        manifest["pieces"][piece.id] = {
            "code": {"commit": code["commit"], "dirty": code["dirty"]},
            "files": piece_assets(piece, config),
        }
    manifest.update(
        {
            "config": config,
            "config_file": {"path": relative(CONFIG), "sha256": sha256(CONFIG)},
            "environment": environment(),
            "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    manifest["pieces"] = dict(sorted(manifest["pieces"].items()))
    write_json(manifest_path, manifest)
    print(f"wrote {relative(OUT)}")


if __name__ == "__main__":
    main()
