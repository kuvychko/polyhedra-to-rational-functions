"""Evaluation: chart against sphere, infinity, local orders, duality, rotation, high degree."""

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.chart import to_chart, to_sphere
from polyhedral_functions.divisors import Divisor
from polyhedral_functions.evaluation import (
    as_function,
    evaluate,
    log_modulus_and_phase,
    log_modulus_on_sphere,
)
from polyhedral_functions.normalization import fibonacci_sphere

from .incidence import incidence, uniform

RNG = np.random.default_rng(5)
Z = np.concatenate(
    [
        RNG.normal(size=300) + 1j * RNG.normal(size=300),
        (RNG.normal(size=50) + 1j * RNG.normal(size=50)) * 1e3,  # near the north pole
        (RNG.normal(size=50) + 1j * RNG.normal(size=50)) * 1e-3,  # near the south pole
    ]
)
CASES = {
    "R2 octahedron (vertex at inf)": incidence(fixtures.load("octahedron"), "v", "f"),
    "R4ve icosahedron (vertex at inf)": incidence(fixtures.load("icosahedron"), "v", "e"),
    "R2 irregular-mixed": incidence(fixtures.load("irregular-mixed"), "v", "f"),
    "R1 deltoidal icositetrahedron (deg 312)": uniform(
        fixtures.load("deltoidal-icositetrahedron")
    ).reduced()[0],
}


def test_chart_round_trip():
    assert np.allclose(to_chart(to_sphere(Z)), Z, rtol=1e-12)
    assert np.isinf(to_chart([[0.0, 0.0, 1.0]])[0])


@pytest.mark.parametrize("name", CASES)
def test_chart_and_sphere_agree(name):
    d = CASES[name]
    chart_log, _ = log_modulus_and_phase(d, Z)
    sphere_log = log_modulus_on_sphere(d, to_sphere(Z))
    assert np.allclose(chart_log, sphere_log, rtol=1e-10, atol=1e-8)


def test_value_at_infinity():
    north, south, east = [0.0, 0.0, 1.0], [0.0, 0.0, -1.0], [1.0, 0.0, 0.0]
    assert evaluate(Divisor.from_sets([north], 2, [south], 2), np.inf) == 0
    assert np.isinf(evaluate(Divisor.from_sets([south], 2, [north], 2), np.inf))
    # Regular at infinity: zero at z = 0, pole at z = 1, so f = C z / (z - 1) with
    # C = (1 + 0)^(-1/2) (1 + 1)^(+1/2) = sqrt(2), and f(inf) = sqrt(2).
    d = Divisor.from_sets([south], 1, [east], 1)
    assert evaluate(d, np.inf) == pytest.approx(np.sqrt(2.0))
    assert evaluate(d, 1e9) == pytest.approx(np.sqrt(2.0), rel=1e-8)


def winding(d, centre, radius=1e-4, n=400):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    _, phase = log_modulus_and_phase(d, centre + radius * np.exp(1j * t))
    return int(
        round(np.sum(np.angle(np.exp(1j * np.diff(np.append(phase, phase[0]))))) / (2 * np.pi))
    )


@pytest.mark.parametrize("name", CASES)
def test_local_orders_by_winding(name):
    """The phase winds m times around a feature of order m (finite features only)."""
    d = CASES[name]
    for point, order in zip(d.points, d.orders, strict=True):
        z0 = to_chart([point])[0]
        if np.isfinite(z0) and abs(z0) < 50:
            assert winding(d, z0, radius=1e-4 * (1 + abs(z0) ** 2)) == order


@pytest.mark.parametrize("name", CASES)
def test_negated_divisor_is_reciprocal(name):
    d = CASES[name]
    with np.errstate(all="ignore"):
        product = evaluate(d, Z) * evaluate(-d, Z)
    assert np.allclose(product, 1.0, rtol=1e-8)


@pytest.mark.parametrize("name", CASES)
def test_rotation_moves_the_magnitude_field(name):
    d = CASES[name]
    q, r = np.linalg.qr(RNG.normal(size=(3, 3)))
    R = q * np.sign(np.diag(r))
    R = R if np.linalg.det(R) > 0 else -R
    x = fibonacci_sphere(2000)
    assert np.allclose(log_modulus_on_sphere(d.rotated(R), x @ R.T), log_modulus_on_sphere(d, x))


def test_degree_312_does_not_overflow():
    d = CASES["R1 deltoidal icositetrahedron (deg 312)"]
    z = np.array([1e3 + 1e3j, -2e2 + 5j])
    with np.errstate(all="ignore"):
        finite_pts, orders, _ = d.chart_form()
        naive = np.prod((z[:, None] - finite_pts[None, :]) ** orders, axis=1)
    assert not np.all(np.isfinite(naive))  # the direct product does overflow ...
    assert np.all(np.isfinite(evaluate(d, z)))  # ... the log-domain route does not


def test_as_function_keeps_array_shape():
    f = as_function(CASES["R2 irregular-mixed"])
    grid = Z[:12].reshape(3, 4)
    assert f(grid).shape == (3, 4)
