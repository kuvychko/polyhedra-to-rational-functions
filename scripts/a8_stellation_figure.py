"""A8: the stellation comparison figure (research/stellation.md).

Run:  uv run python scripts/a8_stellation_figure.py

From one shared view:

- ``octahedron.jpg``: the octahedron with its R2 divisor: zeros at the 6 vertices, poles at the
  8 face normals;
- ``stella-octangula.jpg``: the octahedron's stellation, two tetrahedra on alternate cube
  vertices, with the same 8 pole directions marked at its tips;
- ``relief-octahedron.jpg``: the R2 relief of the octahedron, with the order-tuned display;
- ``relief-cube.jpg``: the R2 relief of its polar dual, the cube, with the same settings. Its
  log-modulus is the negative of the octahedron's (``tests/test_stellation_claims.py``).

Output: ``docs/assets/stellation/`` and a ``manifest.json`` with the code commit, the settings
and every file's hash.
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from PIL import Image

from polyhedral_functions import fixtures
from polyhedral_functions.geometry import Polyhedron
from polyhedral_functions.manifests import REPO_ROOT, git_state, relative, sha256, write_json
from polyhedral_functions.recipes import R2, apply
from polyhedral_functions.rendering import (
    DisplaySettings,
    render_geometry,
    render_relief,
    render_solids,
)

OUT = REPO_ROOT / "docs" / "assets" / "stellation"
VIEW = (3.0, 1.3, 0.8)  # oblique, so no tip points straight at the viewer
WIDTH = 480


def stella_octangula() -> list[Polyhedron]:
    """The octahedron's only stellation: two tetrahedra on alternate vertices of the cube. For
    the octahedron with vertices at ``±e_i``, its face planes ``±x ± y ± z = 1`` meet three at a
    time at ``(±1, ±1, ±1)``."""
    corners = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
    return [
        Polyhedron.from_points(corners, "tetrahedron"),
        Polyhedron.from_points(-corners, "tetrahedron"),
    ]


def main() -> None:
    # Read the tree state before writing anything, or the outputs themselves make it dirty.
    code = git_state()
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = REPO_ROOT / "out" / "stellation-figure"
    tmp.mkdir(parents=True, exist_ok=True)
    octahedron = fixtures.load("octahedron")
    divisor = apply(R2, octahedron).unreduced
    dual = apply(R2, octahedron.polar_dual()).unreduced
    geometry = DisplaySettings(window=700, framing="fit")
    relief = geometry.tuned_for(divisor)
    pngs = {
        "octahedron": render_geometry(octahedron, divisor, tmp / "octahedron.png", VIEW, geometry),
        "stella-octangula": render_solids(
            stella_octangula(), divisor.poles, tmp / "stella-octangula.png", VIEW, geometry
        ),
        "relief-octahedron": render_relief(divisor, tmp / "relief-octahedron.png", VIEW, relief),
        "relief-cube": render_relief(dual, tmp / "relief-cube.png", VIEW, relief),
    }
    files = {}
    for name, png in pngs.items():
        jpg = OUT / f"{name}.jpg"
        im = Image.open(png).convert("RGB")
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        im.save(jpg, quality=86, optimize=True)
        files[name] = {"path": relative(jpg), "sha256": sha256(jpg)}
    write_json(
        OUT / "manifest.json",
        {
            "id": "site-stellation-figure",
            "solid": "octahedron",
            "recipe": "R2",
            "divisors": "unreduced",
            "view": list(VIEW),
            "display": {"geometry": geometry.config(), "relief": relief.config()},
            "display_note": "relief views order-tuned (sharpness = 2 x max |order|), shared by "
            "the octahedron and its polar dual",
            "code": {"commit": code["commit"], "dirty": code["dirty"]},
            "files": files,
            "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    print(f"wrote {relative(OUT)}")


if __name__ == "__main__":
    main()
