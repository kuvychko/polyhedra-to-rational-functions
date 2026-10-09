"""A7: static fallback for the recipe comparison page (research/compare.md).

Run:  uv run python scripts/a7_compare_fallback.py

Renders the page's default comparison, the cube under R2 and under R4ve, as two still images
from the interactive viewer's default direction. The page shows them when JavaScript or WebGL is
unavailable. Markers are the unreduced divisors, as in the interactive view, from
``viewer_data`` via the same recipes. Output: ``docs/assets/explorer/cube-<recipe>.jpg`` and a
``manifest.json`` with the code commit and every file's hash.
"""

from __future__ import annotations

from datetime import UTC, datetime

from PIL import Image

from polyhedral_functions import fixtures
from polyhedral_functions.manifests import REPO_ROOT, git_state, relative, sha256, write_json
from polyhedral_functions.recipes import PRESETS, apply
from polyhedral_functions.rendering import DisplaySettings, render_geometry

OUT = REPO_ROOT / "docs" / "assets" / "explorer"
SOLID = "cube"
RECIPES = ("R2", "R4ve")
VIEW = (2.2, 2.2, 1.6)  # DEFAULT_VIEW in docs/javascripts/recipe-explorer.js
WIDTH = 480


def main() -> None:
    # Read the tree state before writing anything, or the outputs themselves make it dirty.
    code = git_state()
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = REPO_ROOT / "out" / "compare-fallback"
    tmp.mkdir(parents=True, exist_ok=True)
    settings = DisplaySettings(window=700, framing="fit")
    poly = fixtures.load(SOLID)
    files = {}
    for name in RECIPES:
        divisor = apply(PRESETS[name], poly).unreduced
        png = render_geometry(poly, divisor, tmp / f"{SOLID}-{name}.png", VIEW, settings)
        jpg = OUT / f"{SOLID}-{name}.jpg"
        im = Image.open(png).convert("RGB")
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
        im.save(jpg, quality=86, optimize=True)
        files[name] = {"path": relative(jpg), "sha256": sha256(jpg)}
    write_json(
        OUT / "manifest.json",
        {
            "id": "site-compare-fallback",
            "solid": SOLID,
            "recipes": list(RECIPES),
            "divisors": "unreduced",
            "view": list(VIEW),
            "code": {"commit": code["commit"], "dirty": code["dirty"]},
            "files": files,
            "updated": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )
    print(f"wrote {relative(OUT)}")


if __name__ == "__main__":
    main()
