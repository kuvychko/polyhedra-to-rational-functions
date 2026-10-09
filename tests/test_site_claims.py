"""Numbers quoted on the site agree with the experiment records they come from (A5).

Each test reads a published data file under ``experiments/`` and checks that the prose in
``docs/`` states the same value, so the narrative cannot drift from the evidence.
"""

import csv
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
NARRATIVE = (DOCS / "research" / "narrative.md").read_text(encoding="utf-8")
EXPERIMENTS_PAGE = (DOCS / "research" / "experiments.md").read_text(encoding="utf-8")
RECIPES_PAGE = (DOCS / "research" / "recipes.md").read_text(encoding="utf-8")


def rows(path):
    with (ROOT / path).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


E001 = rows("experiments/E001-atlas/metrics.csv")
E003 = rows("experiments/E003-deformation/deformation.csv")
E004 = rows("experiments/E004-display/display.csv")


def e001(fixture, recipe, field):
    return next(r[field] for r in E001 if r["fixture"] == fixture and r["recipe"] == recipe)


def test_e001_is_55_runs_all_exact_checks_passing():
    assert len(E001) == 55
    assert all(r["winding_ok"] == "True" and r["dual_equal"] == "True" for r in E001)
    assert all(r["symmetry_preserved"] == r["group_order"] for r in E001)
    assert "55 of 55 runs" in NARRATIVE


def test_pyramid_r1_r2_correlation():
    assert float(e001("hexagonal-pyramid", "R1", "corr_vs_reference")) == pytest.approx(0.833)
    assert "0.83 on the" in NARRATIVE


def test_largest_r1_to_r2_degree_ratio():
    ratio = max(
        int(e001(f, "R1", "degree")) / int(e001(f, "R2", "degree"))
        for f in {r["fixture"] for r in E001}
    )
    assert ratio == pytest.approx(3.25)
    assert "up to 3.25×" in NARRATIVE


def test_r4ve_correlation_range_with_r2():
    corr = [float(r["corr_vs_reference"]) for r in E001 if r["recipe"] == "R4ve"]
    assert round(min(corr), 2) == 0.48 and round(max(corr), 2) == 0.92
    assert "0.48–0.92" in NARRATIVE


def test_display_correction_on_the_deltoidal_icositetrahedron():
    def corr(mode):
        return next(
            float(r["correlation"])
            for r in E004
            if r["fixture"] == "deltoidal-icositetrahedron"
            and r["display"] == mode
            and r["pair"] == "R1~R2"
        )

    assert corr("fixed") == pytest.approx(0.950, abs=5e-4)
    assert corr("order-tuned") == pytest.approx(0.991, abs=5e-4)
    assert "from 0.950 to 0.991" in NARRATIVE


def test_pyramid_family_r1_r2_range():
    pyramid = [r for r in E003 if r["family"] == "hexagonal_pyramid"]
    first, last = float(pyramid[0]["corr_R1_R2"]), float(pyramid[-1]["corr_R1_R2"])
    assert (round(first, 2), round(last, 2)) == (0.96, 0.56)
    assert "0.96 to 0.56" in NARRATIVE


def test_sheared_box_placement_threshold_at_shear_one():
    box = {
        float(r["parameter"]): int(r["faces_polar_outside"])
        for r in E003
        if r["family"] == "sheared_box"
    }
    assert box[1.0] == 0 and box[1.1] > 0
    assert "exactly at shear 1" in NARRATIVE
    assert "from shear\n  1 onwards" in EXPERIMENTS_PAGE or "from shear 1" in EXPERIMENTS_PAGE


def test_worked_example_constant_and_degree():
    from polyhedral_functions import fixtures
    from polyhedral_functions.recipes import R2, apply

    d = apply(R2, fixtures.load("octahedron")).divisor
    assert d.degree == 24
    assert "\\(C = 729/4\\)" in RECIPES_PAGE
    assert "6 \\cdot 4 = 8 \\cdot 3 = 24" in RECIPES_PAGE


def test_research_landing_summary_quotes_the_same_figures():
    """The short account on research/index.md repeats figures checked above."""
    landing = (DOCS / "research" / "index.md").read_text(encoding="utf-8")
    assert "all 55 runs" in landing
    assert "0.48–0.92" in landing
    assert "from 0.950 to 0.991" in landing


def test_printing_limitations_gap_figures():
    """Limitations quotes the P001 reference scaled to 80 mm and the two pieces below it."""
    screen = rows("experiments/P001-print-screen/screen.csv")
    baseline = {
        "cube-octahedron-dual",
        "dodecahedron-icosahedron-dual",
        "icosidodecahedral-star",
        "icosahedral-crown",
    }
    ref_80 = (
        min(
            float(r["pole_pole_gap_mm"])
            for r in screen
            if r["piece"] in baseline and r["size_mm"] == "130"
        )
        * 80
        / 130
    )
    below = {
        r["piece"]
        for r in screen
        if r["size_mm"] == "80"
        and float(r["pole_pole_gap_mm"]) < ref_80
        and r["piece"] in {"r4ve-rhombicuboctahedron", "r2-irregular-separated"}
    }
    assert round(ref_80, 1) == 16.7
    assert below == {"r4ve-rhombicuboctahedron", "r2-irregular-separated"}
    limitations = (DOCS / "research" / "limitations.md").read_text(encoding="utf-8")
    assert "16.7 mm" in limitations


PRIMER_PAGE = (DOCS / "research" / "primer.md").read_text(encoding="utf-8")


def test_primer_chart_facts():
    """Section 3 of the introduction: where the plane's points land on the sphere."""
    from polyhedral_functions.chart import to_sphere

    assert np.allclose(to_sphere(0), [[0, 0, -1]])
    unit_circle = np.exp(1j * np.linspace(0, 2 * np.pi, 13))
    assert np.allclose(to_sphere(unit_circle)[:, 2], 0)
    assert (to_sphere([0.3, 0.9j, -0.5 + 0.5j])[:, 2] < 0).all()
    assert (to_sphere([1.1, 3j, -2 - 2j])[:, 2] > 0).all()
    assert to_sphere(1e4)[0, 2] > 1 - 1e-7
    # The fallback drawing: circle of radius 100 centred at (200, 150), points z = 1.8, w = 0.5.
    for z, (sx, sy) in [(1.8, (284.9, 97.2)), (0.5, (280, 210))]:
        x, _, h = to_sphere(z)[0]
        assert np.isclose(200 + 100 * x, sx, atol=0.1) and np.isclose(150 - 100 * h, sy, atol=0.1)
    assert r"\(z = 0\) is the south pole, \(z = \infty\) the" + "\nnorth pole" in PRIMER_PAGE


def test_primer_relief_settings():
    """Section 5: the transfer, its depth, and the order-tuned sharpness the figure uses."""
    import sys

    from polyhedral_functions.rendering import DisplaySettings, relief_radius

    sys.path.insert(0, str(DOCS / "hooks"))
    import explorer

    data = explorer.primer_json()
    assert data["display"]["depth"] == DisplaySettings().depth == 0.2
    assert r"\(d = 0.2\)" in PRIMER_PAGE
    for entry in data["functions"].values():
        top = max(m["order"] for m in entry["zeros"] + entry["poles"])
        assert entry["sharpness"] == 2 * top
    assert "twice the highest order" in PRIMER_PAGE
    # Sea level |f| = 1 is halfway between the deepest pit d and the tips at 1.
    assert np.isclose(relief_radius(0.0, 4.0, 0.2), 0.2 + 0.8 / 2)
