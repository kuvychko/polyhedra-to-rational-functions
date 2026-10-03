"""The interactive viewer data (docs/assets/pieces/*/geometry.json) matches each divisor."""

import json
from pathlib import Path

import numpy as np
import pytest

from polyhedral_functions import catalog
from polyhedral_functions.divisors import Divisor

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
