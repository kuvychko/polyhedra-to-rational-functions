"""Recipes: agreement with the independent test construction, polarity, placement, records."""

import json

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.diagnostics import duality_report, rotation_report
from polyhedral_functions.recipes import FLAG, PRESETS, R1, R2, R4FE, R4VE, Recipe, apply

from .incidence import incidence, uniform

IDS = list(fixtures.CONSTRUCTIONS)


@pytest.mark.parametrize("fixture_id", IDS)
def test_presets_match_the_independent_construction(fixture_id):
    poly = fixtures.load(fixture_id)
    expected = {
        "R1": uniform(poly),
        "R2": incidence(poly, "v", "f"),
        "R4ve": incidence(poly, "v", "e"),
        "R4fe": incidence(poly, "f", "e"),
        "flag": incidence(poly, "v", "e") + incidence(poly, "f", "e"),
    }
    for name, recipe in PRESETS.items():
        result = apply(recipe, poly)
        assert result.divisor.same_as(expected[name].coalesced()[0].reduced()[0]), name
        assert result.divisor.is_balanced
        assert result.cancellations == []  # no coincident cells anywhere in the corpus


@pytest.mark.parametrize("fixture_id", IDS)
def test_r2_is_r4ve_over_r4fe_unreduced(fixture_id):
    poly = fixtures.load(fixture_id)
    lhs = apply(R2, poly)
    rhs = (
        apply(R4VE, poly).divisor * apply(R4VE, poly).gcd
        - apply(R4FE, poly).divisor * apply(R4FE, poly).gcd
    )
    assert (lhs.divisor * lhs.gcd).same_as(rhs)


@pytest.mark.parametrize("fixture_id", IDS)
@pytest.mark.parametrize("name", list(PRESETS))
def test_polarity(fixture_id, name):
    """R1, R2: reciprocal on the dual. R4ve and R4fe: swap. Flag: unchanged."""
    report = duality_report(PRESETS[name], fixtures.load(fixture_id), n=3000)
    assert report["divisors_equal"]
    assert report["max_log_modulus_residual"] < 1e-9
    if "max_phase_residual" in report:
        assert report["max_phase_residual"] < 1e-9


@pytest.mark.parametrize("fixture_id", IDS)
def test_flag_recipe_is_the_same_function_for_a_polyhedron_and_its_dual(fixture_id):
    poly = fixtures.load(fixture_id)
    assert apply(FLAG, poly.polar_dual()).divisor.same_as(apply(FLAG, poly).divisor)


# Where the alternative placements differ from the polar/foot defaults (recipe-separation note).
FACE_PLACEMENT_DIFFERS = [
    "deltoidal-icositetrahedron",
    "irregular-9",
    "hexagonal-pyramid",
    "triakis-tetrahedron",
    "irregular-mixed",
]
EDGE_PLACEMENT_DIFFERS = [
    "deltoidal-icositetrahedron",
    "irregular-9",
    "triakis-tetrahedron",
    "irregular-mixed",
]


@pytest.mark.parametrize("fixture_id", FACE_PLACEMENT_DIFFERS)
def test_centroid_placement_breaks_reciprocal_duality(fixture_id):
    report = duality_report(R2.placed(face="centroid"), fixtures.load(fixture_id), n=3000)
    assert not report["divisors_equal"]


@pytest.mark.parametrize("fixture_id", EDGE_PLACEMENT_DIFFERS)
def test_midpoint_placement_breaks_r4_duality(fixture_id):
    report = duality_report(R4VE.placed(edge="midpoint"), fixtures.load(fixture_id), n=3000)
    assert not report["divisors_equal"]


def test_midpoint_placement_keeps_r4_duality_only_when_inscribed_and_circumscribed():
    """Foot = midpoint on an edge iff its endpoints are equidistant from the origin. Duality
    compares P with P*, so it needs that in both: P inscribed, and adjacent faces of P
    equidistant (P* inscribed). The Platonic solids qualify. The pyramid and the
    rhombicuboctahedron are inscribed only, so their duals' midpoints move."""
    for fixture_id in ("tetrahedron", "cube", "icosahedron"):
        report = duality_report(R4VE.placed(edge="midpoint"), fixtures.load(fixture_id), n=2000)
        assert report["divisors_equal"], fixture_id
    for fixture_id in ("hexagonal-pyramid", "rhombicuboctahedron"):
        report = duality_report(R4VE.placed(edge="midpoint"), fixtures.load(fixture_id), n=2000)
        assert not report["divisors_equal"], fixture_id


@pytest.mark.parametrize("fixture_id", IDS)
@pytest.mark.parametrize("name", ["R1", "R2", "R4ve"])
def test_rotating_the_input_rotates_the_field(fixture_id, name):
    q, r = np.linalg.qr(np.random.default_rng(4).normal(size=(3, 3)))
    R = q * np.sign(np.diag(r))
    R = R if np.linalg.det(R) > 0 else -R
    for recipe in (PRESETS[name], PRESETS[name].placed("centroid", "midpoint")):
        report = rotation_report(recipe, fixtures.load(fixture_id), R, n=2000)
        assert report["divisors_equal"]
        assert report["max_log_modulus_residual"] < 1e-9


def test_reciprocal_and_placement_variants():
    poly = fixtures.load("irregular-mixed")
    assert apply(R2.reciprocal(), poly).divisor.same_as(-apply(R2, poly).divisor)
    assert R2.placed("centroid", "midpoint").name == "R2[centroid,midpoint]"
    assert R2.placed("centroid").placed("polar").name == "R2"


def test_invalid_recipes_are_rejected():
    with pytest.raises(ValueError):
        Recipe("x", a=0, b=0)
    with pytest.raises(ValueError):
        Recipe("x", face_placement="vertex")


def test_record_is_json_serializable():
    record = apply(R1, fixtures.load("hexagonal-pyramid")).record()
    assert json.loads(json.dumps(record))["divisor"]["degree"] == 7
