"""Run manifests record provenance; the render adapters consume a divisor without changing it."""

import json

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.evaluation import log_modulus_on_sphere
from polyhedral_functions.manifests import (
    REPO_ROOT,
    git_state,
    new_manifest,
    output_entry,
    relative,
    write_json,
)
from polyhedral_functions.recipes import R2, apply
from polyhedral_functions.rendering import (
    DisplaySettings,
    per_degree_field,
    render_geometry,
    render_relief,
)


def test_git_state_and_manifest_skeleton():
    state = git_state()
    assert set(state) == {"commit", "dirty", "changed_paths"}
    manifest = new_manifest({"id": "T", "question": "q", "hypothesis": "h", "changed_factor": "c"})
    assert manifest["experiment"]["id"] == "T"
    assert manifest["environment"]["packages"]["complexplorer"] == "3.1.0"


def test_paths_are_repository_relative_and_json_is_lf(tmp_path):
    assert relative(REPO_ROOT / "data" / "polyhedra" / "cube.json") == "data/polyhedra/cube.json"
    path = write_json(REPO_ROOT / "out" / "test-manifest" / "m.json", {"x": np.float64(1.5)})
    assert b"\r\n" not in path.read_bytes()
    assert json.loads(path.read_text())["x"] == 1.5
    entry = output_entry(path)
    assert entry["path"] == "out/test-manifest/m.json" and len(entry["sha256"]) == 64


def test_per_degree_field_matches_evaluation():
    d = apply(R2, fixtures.load("irregular-mixed")).divisor
    field = per_degree_field(d, resolution=20)
    assert field.shape == (20, 40)
    # The grid's first sample: lowest latitude row, first longitude.
    lat, lon = -np.pi / 2 + np.pi / 40, -np.pi + np.pi / 40
    x = np.array([[np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]])
    assert np.isclose(field[0, 0], log_modulus_on_sphere(d, x)[0] / d.degree)


@pytest.mark.render
def test_offscreen_renders(tmp_path):
    poly = fixtures.load("cube")
    d = apply(R2, poly).divisor
    settings = DisplaySettings(relief_resolution=40, window=120)
    for path in (
        render_geometry(poly, d, tmp_path / "g.png", (1, 1, 1), settings),
        render_relief(d, tmp_path / "r.png", (1, 1, 1), settings),
        render_relief(d, tmp_path / "s.png", (1, 1, 1), settings, "sphere"),
    ):
        assert path.stat().st_size > 1000


def test_order_tuned_display_sets_tip_exponent_one_half():
    d = apply(R2, fixtures.load("deltoidal-icositetrahedron")).divisor
    tuned = DisplaySettings().tuned_for(d)
    assert tuned.sharpness == 8.0  # max order 4
    assert DisplaySettings().sharpness == 4.0  # the controlled view is unchanged


def test_fit_framing_contains_the_silhouette():
    """Site views use an orthographic camera sized to the silhouette, so no tip is cropped."""
    import pyvista as pv

    from polyhedral_functions.rendering import FIT_MARGIN, _camera

    pts = np.array([[1.0, 1.0, 1.0], [-2.0, 0.5, 0.0], [0.0, 0.0, -1.0]])
    view = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
    pl = pv.Plotter(off_screen=True)
    pl.add_mesh(pv.PolyData(pts))
    _camera(pl, view, fit_points=pts)
    radial = pts - np.outer(pts @ view, view)
    assert pl.camera.parallel_projection
    assert pl.camera.parallel_scale == pytest.approx(
        np.linalg.norm(radial, axis=1).max() * FIT_MARGIN
    )
    pl.close()
