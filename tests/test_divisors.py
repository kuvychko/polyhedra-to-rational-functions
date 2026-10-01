"""Divisors: balance, group operations, explicit cancellation, the chart."""

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.divisors import Divisor

from .incidence import incidence, uniform

N, S = np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, -1.0])
E1, E2 = np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])


def test_rejects_bad_input():
    with pytest.raises(ValueError, match="integers"):
        Divisor([N], [1.5])
    with pytest.raises(ValueError, match="nonzero"):
        Divisor([N], [0])
    with pytest.raises(ValueError, match="unit"):
        Divisor([2 * N], [1])
    with pytest.raises(ValueError, match="positive"):
        Divisor.from_sets([N], -1, [S], 1)


def test_balance_and_degree():
    d = Divisor.from_sets([N, S], 2, [E1], 4)
    assert d.is_balanced and d.degree == 4
    assert not Divisor.from_sets([N], 1, [S], 2).is_balanced
    with pytest.raises(ValueError, match="unbalanced"):
        Divisor.from_sets([N], 1, [S], 2).require_balanced()


def test_group_operations_and_reduction():
    a = Divisor.from_sets([N], 2, [S], 2)
    b = Divisor.from_sets([E1], 4, [E2], 4)
    assert (a + b).degree == 6
    assert (-a).same_as(Divisor.from_sets([S], 2, [N], 2))
    assert (3 * a).degree == 6
    reduced, g = (a + b).reduced()
    assert g == 2 and reduced.same_as(Divisor.from_sets([N, E1], [1, 2], [S, E2], [1, 2]))


def test_coincident_zero_and_pole_cancel_and_are_reported():
    d = Divisor.from_sets([N, E1], [3, 1], [N, S], [1, 3])
    merged, cancellations = d.coalesced()
    assert merged.same_as(Divisor.from_sets([N, E1], [2, 1], [S], 3))
    assert merged.degree == 3
    assert cancellations == [{"labels": ["zero 0", "pole 0"], "orders": [3, -1], "remaining": 2}]


def test_same_sign_merge_is_not_a_cancellation():
    merged, cancellations = Divisor.from_sets([N, N], 1, [S], 2).coalesced()
    assert cancellations == [] and merged.orders.tolist() == [2, -2]


def test_near_points_are_reported_not_merged():
    tilt = np.array([np.sin(1e-4), 0.0, np.cos(1e-4)])  # 1e-4 rad from the north pole
    d = Divisor.from_sets([N], 1, [tilt], 1)
    merged, cancellations = d.coalesced()
    assert len(merged) == 2 and cancellations == []
    (pair,) = d.near_pairs(radius=1e-3)
    assert pair["chordal_distance"] == pytest.approx(1e-4, rel=1e-6)


def test_chart_form_carries_the_north_pole_as_infinity():
    finite, orders, at_infinity = Divisor.from_sets([N, E1], [4, 1], [S], 5).chart_form()
    assert at_infinity == 4
    assert np.allclose(sorted(finite, key=abs), [0.0, 1.0])


def test_same_as_ignores_order_and_labels_but_not_points():
    poly = fixtures.load("irregular-mixed")
    d = incidence(poly, "v", "f")
    perm = np.random.default_rng(0).permutation(len(d))
    shuffled = Divisor(d.points[perm], d.orders[perm])
    assert d.same_as(shuffled)
    assert not d.same_as(d.rotated(np.diag([-1.0, -1.0, 1.0])))


@pytest.mark.parametrize("fixture_id", list(fixtures.CONSTRUCTIONS))
def test_incidence_lattice_identity(fixture_id):
    """D_R2 = D_R4ve - D_R4fe: the edge points cancel exactly, and the cancellation is reported."""
    poly = fixtures.load(fixture_id)
    lhs = incidence(poly, "v", "f")
    rhs = incidence(poly, "v", "e") - incidence(poly, "f", "e")
    assert lhs.same_as(rhs)
    _, cancellations = rhs.coalesced()
    assert len(cancellations) == poly.n_edges
    assert all(c["remaining"] == 0 for c in cancellations)


@pytest.mark.parametrize("fixture_id", list(fixtures.CONSTRUCTIONS))
def test_incidence_and_uniform_recipes_balance(fixture_id):
    poly = fixtures.load(fixture_id)
    for d in (uniform(poly), incidence(poly, "v", "f"), incidence(poly, "v", "e")):
        assert d.is_balanced and d.degree == d.coalesced()[0].degree
    assert incidence(poly, "v", "f").degree == 2 * poly.n_edges


def test_degree_table_from_the_program():
    """PROGRAM.md §7: uniform and reduced incidence degrees (no coincident points here)."""
    table = {
        "tetrahedron": (4, 4),
        "cube": (24, 24),
        "icosahedron": (60, 60),
        "deltoidal-icositetrahedron": (312, 96),
        "hexagonal-pyramid": (7, 8),
    }
    for fixture_id, (r1, r2) in table.items():
        poly = fixtures.load(fixture_id)
        assert uniform(poly).reduced()[0].degree == r1, fixture_id
        assert incidence(poly, "v", "f").reduced()[0].degree == r2, fixture_id
