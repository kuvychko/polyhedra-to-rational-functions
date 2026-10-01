"""The chordal convention: geometric mean 1, and identity with the baseline's normalization.

Also pins the R0 divisors: each baseline ornament, scaled by the closed-form constant, has
exactly the chordal modulus of the recipe divisor named here. That establishes both the
divisor (audit findings 2 and 3, decision 0002) and the normalization claim.
"""

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.baseline import ornaments
from polyhedral_functions.chart import to_sphere
from polyhedral_functions.evaluation import log_modulus_on_sphere
from polyhedral_functions.normalization import (
    MEAN_LOG_CHORDAL,
    fibonacci_sphere,
    polynomial_ratio_constant,
)

from .incidence import incidence, uniform

X = fibonacci_sphere(400_000)


def test_mean_log_chordal_distance():
    a = np.array([0.36, -0.48, 0.8])
    mean = np.log(np.linalg.norm(X - a, axis=1)).mean()
    assert mean == pytest.approx(MEAN_LOG_CHORDAL, abs=1e-4)


@pytest.mark.parametrize("fixture_id", ["cube", "irregular-mixed", "hexagonal-pyramid"])
def test_geometric_mean_is_one(fixture_id):
    """Sea level |f| = 1 is the sphere's geometric mean, with no constant fitted."""
    for d in (uniform(fixtures.load(fixture_id)), incidence(fixtures.load(fixture_id), "v", "e")):
        d = d.reduced()[0]
        log_mod = log_modulus_on_sphere(d, X)
        assert log_mod.mean() / d.degree == pytest.approx(0.0, abs=2e-4)


ICO, DOD = fixtures.load("icosahedron"), fixtures.load("dodecahedron")
OCT, TET = fixtures.load("octahedron"), fixtures.load("tetrahedron")

# Each baseline piece as a recipe divisor. Baseline pieces put poles on the vertex side of the
# crowns, so those are negated recipes.
R0_AS_RECIPES = {
    "tetrahedral-dual": incidence(TET, "v", "f"),  # = R1 = R2 of the tetrahedron
    "cube-octahedron-dual": incidence(OCT, "v", "f"),  # = R1 = R2 of the octahedron
    "dodecahedron-icosahedron-dual": incidence(ICO, "v", "f"),  # = R1 = R2 of the icosahedron
    "octahedral-crown": -incidence(OCT, "v", "e"),  # R4ve of the octahedron, reciprocal
    "icosahedral-crown": -incidence(ICO, "v", "e"),  # R4ve of the icosahedron, reciprocal
    "icosidodecahedral-star": incidence(DOD, "v", "e"),  # R4ve of the dodecahedron
}


@pytest.mark.parametrize("slug", R0_AS_RECIPES)
def test_baseline_piece_is_the_recipe_function(slug):
    divisor = R0_AS_RECIPES[slug].reduced()[0]
    finite, orders, _ = divisor.chart_form()
    c = polynomial_ratio_constant(
        np.repeat(finite[orders > 0], orders[orders > 0]),
        np.repeat(finite[orders < 0], -orders[orders < 0]),
    )
    rng = np.random.default_rng(2)
    z = rng.normal(size=300) + 1j * rng.normal(size=300)
    z = z[np.abs(z) < 8]  # degree-60 pieces lose precision far out (baseline README)
    with np.errstate(all="ignore"):
        baseline = np.log(np.abs(c * ornaments.BY_SLUG[slug].raw(z)))
    chordal = log_modulus_on_sphere(divisor, to_sphere(z))
    assert np.allclose(baseline, chordal, atol=1e-8)


def test_star_is_also_face_edge_on_the_icosahedron():
    assert R0_AS_RECIPES["icosidodecahedral-star"].same_as(incidence(ICO, "f", "e"))


@pytest.mark.parametrize(
    "slug, solid",
    [
        ("tetrahedral-dual", TET),
        ("cube-octahedron-dual", OCT),
        ("dodecahedron-icosahedron-dual", ICO),
    ],
)
def test_baseline_duals_are_r1_and_r2(slug, solid):
    r2 = incidence(solid, "v", "f").reduced()[0]
    assert r2.same_as(uniform(solid).reduced()[0])
    assert r2.same_as(R0_AS_RECIPES[slug].reduced()[0])


def test_cube_octahedron_dual_constant_is_exact():
    """The baseline sampled 183.25; the closed form is 729/4 (baseline audit, finding 1)."""
    divisor = R0_AS_RECIPES["cube-octahedron-dual"].reduced()[0]
    finite, orders, _ = divisor.chart_form()
    c = polynomial_ratio_constant(
        np.repeat(finite[orders > 0], orders[orders > 0]),
        np.repeat(finite[orders < 0], -orders[orders < 0]),
    )
    assert c == pytest.approx(729 / 4, rel=1e-12)
