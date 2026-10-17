"""The stellation comparison (notes/2026-10-16-stellation-analogy.md, research/stellation.md).

Stellation tips are points where face planes meet again outside the solid. Each check
enumerates every point where three face planes meet and compares the shells of those points
with the R2 spike directions (face normals) and pit directions (vertices).
"""

import itertools

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.evaluation import log_modulus_on_sphere
from polyhedral_functions.normalization import fibonacci_sphere
from polyhedral_functions.recipes import R2, apply
from polyhedral_functions.rendering import DisplaySettings, relief_radius


def plane_meets(poly) -> np.ndarray:
    """Every point where three of the solid's face planes meet, without repeats."""
    normals, offsets = poly.face_planes
    points = []
    for triple in itertools.combinations(range(len(offsets)), 3):
        a = normals[list(triple)]
        if abs(np.linalg.det(a)) > 1e-9:
            points.append(np.linalg.solve(a, offsets[list(triple)]))
    return np.unique(np.round(points, 9), axis=0)


def shells(poly) -> dict[float, np.ndarray]:
    """``plane_meets`` grouped by radius (as a fraction of the circumradius), as unit vectors."""
    points = plane_meets(poly)
    radii = np.round(np.linalg.norm(points, axis=1) / poly.scale, 6)
    return {
        float(r): points[radii == r] / np.linalg.norm(points[radii == r], axis=1)[:, None]
        for r in np.unique(radii)
    }


def same_directions(a: np.ndarray, b: np.ndarray) -> bool:
    gaps = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
    return len(a) == len(b) and bool(np.all(gaps.min(axis=1) < 1e-6))


@pytest.mark.parametrize("name", ["cube", "tetrahedron"])
def test_no_finite_stellation(name):
    """Three face planes meet only at the solid's own vertices."""
    poly = fixtures.load(name)
    found = shells(poly)
    assert list(found) == [1.0]
    assert same_directions(found[1.0], poly.vertex_directions())


def test_octahedron_stellation_tips_are_its_r2_spike_directions():
    poly = fixtures.load("octahedron")
    found = shells(poly)
    assert sorted(found) == [1.0, pytest.approx(np.sqrt(3))]
    tips = found[max(found)]
    poles = apply(R2, poly).unreduced.poles
    assert same_directions(tips, poles.points)
    assert set(poles.orders.tolist()) == {-3}
    # The tips are the cube's vertices, i.e. the stella octangula's.
    assert same_directions(tips, fixtures.load("cube").vertex_directions())


def test_dodecahedron_shells_point_at_spikes_then_pits():
    poly = fixtures.load("dodecahedron")
    found = shells(poly)
    assert [len(found[r]) for r in sorted(found)] == [20, 12, 20]
    middle, outer = sorted(found)[1:]
    assert middle == pytest.approx(1.776901, abs=1e-6)
    assert outer == pytest.approx(4.236068, abs=1e-6)
    assert same_directions(found[middle], poly.face_directions())
    assert same_directions(found[outer], poly.vertex_directions())


def test_icosahedron_shell_directions():
    poly = fixtures.load("icosahedron")
    found = shells(poly)
    feet, _ = poly.edge_feet()
    kinds = {
        "face": poly.face_directions(),
        "edge": feet / np.linalg.norm(feet, axis=1)[:, None],
        "vertex": poly.vertex_directions(),
    }
    labels = []
    for r in sorted(found)[1:]:
        kind = next((k for k, d in kinds.items() if same_directions(found[r], d)), "other")
        labels.append((len(found[r]), kind))
    assert labels == [
        (20, "face"),
        (30, "edge"),
        (60, "other"),
        (60, "other"),
        (20, "face"),
        (12, "vertex"),
        (60, "other"),
    ]


def test_polar_dual_negates_the_log_modulus_and_reflects_the_relief():
    poly = fixtures.load("octahedron")
    divisor = apply(R2, poly).unreduced
    dual = apply(R2, poly.polar_dual()).unreduced
    x = fibonacci_sphere(500)
    u, u_dual = log_modulus_on_sphere(divisor, x), log_modulus_on_sphere(dual, x)
    assert np.allclose(u_dual, -u, atol=1e-9)
    # The order-tuned display gives both the same sharpness, so radii swap about (1 + d) / 2.
    settings = DisplaySettings().tuned_for(divisor)
    assert DisplaySettings().tuned_for(dual) == settings
    r = relief_radius(u, settings.sharpness, settings.depth)
    r_dual = relief_radius(u_dual, settings.sharpness, settings.depth)
    assert np.allclose(r + r_dual, 1 + settings.depth)
