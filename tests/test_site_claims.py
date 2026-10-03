"""Numbers quoted on the site agree with the experiment records they come from (A5).

Each test reads a published data file under ``experiments/`` and checks that the prose in
``docs/`` states the same value, so the narrative cannot drift from the evidence.
"""

import csv
from pathlib import Path

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
