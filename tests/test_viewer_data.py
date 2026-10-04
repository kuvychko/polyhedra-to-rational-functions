"""The interactive viewer data (docs/assets/pieces/*/geometry.json) matches each divisor."""

import json
from pathlib import Path

import numpy as np
import pytest

from polyhedral_functions import catalog, fixtures, viewer_data
from polyhedral_functions.divisors import Divisor
from polyhedral_functions.recipes import PRESETS, apply

DOCS = Path(__file__).resolve().parents[1] / "docs"
PIECES = catalog.load()


@pytest.mark.parametrize("piece", PIECES, ids=lambda p: p.id)
def test_geometry_json_is_the_pieces_divisor(piece):
    path = DOCS / "assets" / "pieces" / piece.id / "geometry.json"
    if not path.exists():
        pytest.skip("not generated yet: uv run python scripts/a4_site_assets.py --data-only")
    data = json.loads(path.read_text(encoding="utf-8"))
    stored = Divisor(
        np.array([m["p"] for m in data["zeros"] + data["poles"]]),
        np.array([m["order"] for m in data["zeros"]] + [-m["order"] for m in data["poles"]]),
    )
    assert stored.same_as(piece.divisor(), tol=1e-5)
    assert np.allclose(np.linalg.norm(data["vertices"], axis=1).max(), 1.0)
    assert all(m["cell"] for m in data["zeros"] + data["poles"])


# --- the recipe comparison page (docs/hooks/explorer.py) ---------------------------------------

EXPLORER = viewer_data.explorer_data()


@pytest.mark.parametrize("solid", viewer_data.EXPLORER_SOLIDS)
@pytest.mark.parametrize("recipe", list(viewer_data.EXPLORER_RECIPES))
def test_explorer_markers_are_the_unreduced_divisor(solid, recipe):
    entry = EXPLORER["solids"][solid]["recipes"][recipe]
    result = apply(PRESETS[recipe], fixtures.load(solid))
    stored = viewer_data.unreduced_from_markers(entry)
    assert stored.same_as(result.unreduced, tol=1e-5)
    assert entry["gcd"] == result.gcd
    assert entry["degree"] == result.unreduced.degree
    assert all(m["cell"] in ("vertex", "face", "edge") for m in entry["zeros"] + entry["poles"])


def test_explorer_solids_have_circumradius_one():
    for record in EXPLORER["solids"].values():
        assert np.isclose(np.linalg.norm(record["vertices"], axis=1).max(), 1.0)


def test_compare_page_claims():
    """The 'comparisons to try' on research/compare.md."""
    solids = EXPLORER["solids"]
    cube = {r: viewer_data.unreduced_from_markers(e) for r, e in solids["cube"]["recipes"].items()}
    # R2 = R4ve - R4fe (unreduced), and R1 = 2 R2 on the cube.
    assert cube["R2"].same_as(cube["R4ve"] - cube["R4fe"], tol=1e-5)
    assert cube["R1"].same_as(cube["R2"] * 2, tol=1e-5)
    # R2 on the octahedron is R2 on the cube, negated.
    octa = viewer_data.unreduced_from_markers(solids["octahedron"]["recipes"]["R2"])
    assert octa.same_as(-cube["R2"], tol=1e-5)
    # The irregular solid's valences and face sizes, and R4ve's edge poles.
    irregular = solids["irregular-separated"]["recipes"]
    assert {m["order"] for m in irregular["R2"]["zeros"]} == {3, 4, 5}
    assert {m["order"] for m in irregular["R2"]["poles"]} == {3, 4, 5}
    assert [m["order"] for m in irregular["R4ve"]["poles"]] == [2] * 18
    # The pyramid's apex has valence 6, its base vertices 3.
    pyramid = solids["hexagonal-pyramid"]["recipes"]["R2"]["zeros"]
    assert sorted(m["order"] for m in pyramid) == [3] * 6 + [6]
