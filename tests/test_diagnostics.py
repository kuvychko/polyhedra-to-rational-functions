"""Diagnostics: winding orders, symmetry groups and preservation, field comparison.

Includes audit finding 4: the mirror symmetry of the baseline pieces, checked both on their
divisors and directly on the baseline functions.
"""

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.baseline import ornaments
from polyhedral_functions.chart import to_chart, to_sphere
from polyhedral_functions.diagnostics import (
    character_report,
    field_comparison,
    symmetry_report,
    winding_orders,
)
from polyhedral_functions.recipes import PRESETS, R1, R2, R4VE, apply

IDS = list(fixtures.CONSTRUCTIONS)


@pytest.mark.parametrize("fixture_id", IDS)
def test_winding_matches_declared_orders(fixture_id):
    """Every feature, including any at infinity, has the declared local order."""
    poly = fixtures.load(fixture_id)
    for recipe in PRESETS.values():
        for w in winding_orders(apply(recipe, poly).divisor):
            assert w["measured"] == w["declared"], (recipe.name, w)


GROUP_ORDERS = {
    "tetrahedron": (24, 12),
    "cube": (48, 24),
    "octahedron": (48, 24),
    "icosahedron": (120, 60),
    "dodecahedron": (120, 60),
    "rhombicuboctahedron": (48, 24),
    "deltoidal-icositetrahedron": (48, 24),
    "irregular-9": (1, 1),
    "hexagonal-pyramid": (12, 6),
    "triakis-tetrahedron": (24, 12),
    "irregular-mixed": (1, 1),
}


@pytest.mark.parametrize("fixture_id", IDS)
def test_symmetry_group_orders(fixture_id):
    group = fixtures.load(fixture_id).symmetry_group()
    assert (len(group), sum(np.linalg.det(g) > 0 for g in group)) == GROUP_ORDERS[fixture_id]


@pytest.mark.parametrize("fixture_id", IDS)
@pytest.mark.parametrize("name", list(PRESETS))
def test_every_recipe_preserves_the_full_symmetry_group(fixture_id, name):
    """All placements are equivariant, so every symmetry of P survives in the divisor."""
    poly = fixtures.load(fixture_id)
    group = poly.symmetry_group()
    for recipe in (PRESETS[name], PRESETS[name].placed("centroid", "midpoint")):
        report = symmetry_report(apply(recipe, poly).divisor, group)
        assert report["preserved"] == len(group), recipe.name


# --- audit finding 4: mirror symmetry of the baseline pieces --------------------------------

R0_RECIPES = {
    "tetrahedral-dual": (R2, "tetrahedron"),
    "octahedral-crown": (R4VE.reciprocal(), "octahedron"),
    "cube-octahedron-dual": (R2, "octahedron"),
    "icosahedral-crown": (R4VE.reciprocal(), "icosahedron"),
    "dodecahedron-icosahedron-dual": (R2, "icosahedron"),
    "icosidodecahedral-star": (R4VE, "dodecahedron"),
}


@pytest.mark.parametrize("slug", R0_RECIPES)
def test_baseline_pieces_have_their_full_symmetry_group_including_mirrors(slug):
    recipe, fixture_id = R0_RECIPES[slug]
    poly = fixtures.load(fixture_id)
    group = poly.symmetry_group()
    report = symmetry_report(apply(recipe, poly).divisor, group)
    assert report["preserved"] == len(group)
    assert report["preserved_improper"] == len(group) // 2


def modulus_ratio_under(raw, matrix):
    z = np.random.default_rng(0).normal(size=500) + 1j * np.random.default_rng(1).normal(size=500)
    moved = to_chart(to_sphere(z) @ np.asarray(matrix, dtype=float).T)
    with np.errstate(all="ignore"):
        return np.abs(raw(moved)) / np.abs(raw(z)), np.abs(raw(z))


def test_tetrahedral_dual_is_not_chiral():
    """The baseline README calls tetrahedral-dual chiral ("no mirror plane fixes it"). It is not:
    the six mirrors of the tetrahedron (planes such as x = y) fix |f|. Only the cube's coordinate
    mirrors, which are not symmetries of the tetrahedron, turn it inside out."""
    raw = ornaments.BY_SLUG["tetrahedral-dual"].raw
    ratio, _ = modulus_ratio_under(raw, [[0, 1, 0], [1, 0, 0], [0, 0, 1]])  # mirror x = y
    assert np.allclose(ratio, 1.0, rtol=1e-10)
    ratio, base = modulus_ratio_under(raw, np.diag([-1.0, 1.0, 1.0]))  # mirror x = 0
    assert np.allclose(ratio * base**2, 1.0, rtol=1e-10)


def test_tetrahedral_dual_halves_are_congruent():
    """Its suggested cut is perpendicular to a 2-fold axis (the plane z = 0). The half-turn about
    the x-axis is a symmetry and swaps the two sides of that plane, so the halves are congruent,
    contrary to the baseline README."""
    raw = ornaments.BY_SLUG["tetrahedral-dual"].raw
    ratio, _ = modulus_ratio_under(raw, np.diag([1.0, -1.0, -1.0]))
    assert np.allclose(ratio, 1.0, rtol=1e-10)


# --- field comparison -----------------------------------------------------------------------


def test_field_comparison_reproduces_the_separation_screen():
    cube, pyramid = fixtures.load("cube"), fixtures.load("hexagonal-pyramid")
    same = field_comparison(apply(R1, cube).divisor, apply(R2, cube).divisor)
    assert same["correlation"] == pytest.approx(1.0) and same["max_abs_difference"] < 1e-12
    apart = field_comparison(apply(R1, pyramid).divisor, apply(R2, pyramid).divisor)
    assert apart["correlation"] < 0.9
    assert 0 < apart["excluded_fraction"] < 0.2


# --- symmetry of the complex function, not only of the relief ---------------------------


@pytest.mark.parametrize("slug", R0_RECIPES)
def test_symmetries_act_on_f_by_a_constant_phase(slug):
    """A divisor-preserving rotation multiplies f by e^{i theta}; a reflection conjugates the
    phase and shifts it. The relation holds exactly (spread ~1e-13) on every baseline piece."""
    recipe, fixture_id = R0_RECIPES[slug]
    poly = fixtures.load(fixture_id)
    report = character_report(apply(recipe, poly).divisor, poly.symmetry_group())
    assert report["checked"] == len(poly.symmetry_group())
    assert report["max_spread"] < 1e-9


def test_tetrahedral_dual_phase_rotates_under_three_fold_rotations():
    """|f| is invariant under T_d, but f is not: the 8 three-fold rotations multiply it by
    e^{+-2 pi i / 3}. The relief is symmetric and the phase coloring is not."""
    poly = fixtures.load("tetrahedron")
    report = character_report(apply(R2, poly).divisor, poly.symmetry_group())
    assert report["proper_trivial"] == 4  # identity and the three half-turns
    assert report["proper_nontrivial_theta_over_pi"] == [-0.666667, 0.666667]


def test_octahedral_pieces_are_invariant_as_functions():
    poly = fixtures.load("octahedron")
    report = character_report(apply(R2, poly).divisor, poly.symmetry_group())
    assert report["proper_trivial"] == 24 and report["improper_trivial"] == 24
