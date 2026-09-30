"""The Klein forms have the roots, the syzygy and the symmetry the baseline claims.

Ported from ``verify_math.py`` (figures_repo @ 292bec4); see the baseline package docstring.
"""

import itertools

import numpy as np
import pytest
from complexplorer.core import polyhedral as cpp

from polyhedral_functions.baseline import forms

from . import coefficients as C
from .coefficients import roots_on_sphere, to_plane

TOL = 1e-9


def pairwise(points):
    return np.array(
        [
            np.linalg.norm(points[i] - points[j])
            for i, j in itertools.combinations(range(len(points)), 2)
        ]
    )


def is_centred_unit_set(points, n, atol=1e-8):
    return (
        len(points) == n
        and np.allclose(np.linalg.norm(points, axis=1), 1.0, atol=atol)
        and np.allclose(points.sum(axis=0), 0.0, atol=atol)
    )


# --- roots ---------------------------------------------------------------------------

# (coefficients, root at infinity?, number of features, shortest edge on the unit sphere)
SOLIDS = {
    "PHI -> tetrahedron": (C.PHI, False, 4, np.sqrt(8 / 3)),
    "PSI -> tetrahedron": (C.PSI, False, 4, np.sqrt(8 / 3)),
    "V + inf -> octahedron": (C.V, True, 6, np.sqrt(2)),
    "F -> cube": (C.F, False, 8, 2 / np.sqrt(3)),
    "E -> cuboctahedron": (C.E, False, 12, 1.0),
    "ICO_V + inf -> icosahedron": (C.ICO_V, True, 12, 1.0514622),
    "ICO_H -> dodecahedron": (C.ICO_H, False, 20, 0.7136442),
    "ICO_T -> icosidodecahedron": (C.ICO_T, False, 30, 0.6180340),  # 1/phi
}


@pytest.mark.parametrize("label", SOLIDS)
def test_roots_form_the_claimed_solid(label):
    coeffs, at_infinity, n, edge = SOLIDS[label]
    points = roots_on_sphere(coeffs, with_infinity=at_infinity)
    assert is_centred_unit_set(points, n)
    assert pairwise(points).min() == pytest.approx(edge, abs=1e-6)


@pytest.mark.parametrize(
    "name, coeffs",
    [
        ("PHI", C.PHI),
        ("PSI", C.PSI),
        ("V", C.V),
        ("F", C.F),
        ("E", C.E),
        ("ICO_V", C.ICO_V),
        ("ICO_H", C.ICO_H),
        ("ICO_T", C.ICO_T),
    ],
)
def test_code_matches_written_coefficients(name, coeffs):
    rng = np.random.default_rng(3)
    z = rng.normal(size=50) + 1j * rng.normal(size=50)
    ours = getattr(forms, name)(z)
    assert np.allclose(ours, np.polyval(coeffs, z), rtol=1e-12)


def test_psi_tetrahedron_is_antipode_of_phi():
    phi, psi = roots_on_sphere(C.PHI), roots_on_sphere(C.PSI)
    nearest_antipode = np.linalg.norm(phi[:, None, :] + psi[None, :, :], axis=-1).min(axis=1)
    assert np.allclose(nearest_antipode, 0.0, atol=TOL)


def test_two_tetrahedra_make_the_cube():
    probe = np.array([0.3 + 0.7j, -1.4 + 0.2j, 2.1 - 1.1j, 0.05 + 0.05j])
    assert np.allclose(forms.PHI(probe) * forms.PSI(probe), forms.F(probe), atol=1e-10)


def test_klein_syzygy():
    """H^3 - T^2 = 1728 V^5: the check that catches a mixed-orientation icosahedral set."""
    probe = np.array([0.3 + 0.7j, -1.4 + 0.2j, 2.1 - 1.1j, 0.45 - 0.8j])
    ratio = (forms.ICO_H(probe) ** 3 - forms.ICO_T(probe) ** 2) / forms.ICO_V(probe) ** 5
    assert np.allclose(ratio, 1728.0, rtol=1e-9)


# --- modulus invariance --------------------------------------------------------------


def moebius_invariance_error(f, g):
    """max | |f(g(z))| / |f(z)| - 1 | over random sample points."""
    rng = np.random.default_rng(0)
    z = rng.normal(size=400) + 1j * rng.normal(size=400)
    with np.errstate(all="ignore"):
        base = np.abs(f(z))
        ratio = np.abs(f(g(z))) / base
    good = np.isfinite(ratio) & (base > 0)
    return float(np.max(np.abs(ratio[good] - 1.0)))


# Generators of the tetrahedral and octahedral rotation groups, for this orientation.
TETRAHEDRAL = {"z -> -z": lambda z: -z, "z -> i(z+1)/(z-1)": lambda z: 1j * (z + 1) / (z - 1)}
OCTAHEDRAL = {"z -> iz": lambda z: 1j * z, "z -> (z+i)/(iz+1)": lambda z: (z + 1j) / (1j * z + 1)}


@pytest.mark.parametrize(
    "ratio, group",
    [
        (forms._ratio(forms.PHI, forms.PSI), TETRAHEDRAL),
        (forms._ratio(forms.E, forms.V, dpow=2), OCTAHEDRAL),
        (forms._ratio(forms.V, forms.F, npow=4, dpow=3), OCTAHEDRAL),
    ],
    ids=["PHI/PSI", "E/V^2", "V^4/F^3"],
)
def test_tetrahedral_and_octahedral_invariance(ratio, group):
    for g in group.values():
        assert moebius_invariance_error(ratio, g) < TOL


def rotation(axis, angle):
    a = np.asarray(axis, dtype=float)
    a = a / np.linalg.norm(a)
    cross = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(angle) * cross + (1 - np.cos(angle)) * cross @ cross


@pytest.mark.parametrize(
    "ratio",
    [
        forms._ratio(forms.ICO_T, forms.ICO_V, npow=2, dpow=5),
        forms._ratio(forms.ICO_V, forms.ICO_H, npow=5, dpow=3),
        forms._ratio(forms.ICO_H, forms.ICO_T, npow=3, dpow=2),
    ],
    ids=["T^2/V^5", "V^5/H^3", "H^3/T^2"],
)
def test_icosahedral_invariance(ratio):
    # Generators as 3x3 rotations of sphere points rather than Moebius maps, which avoids
    # matching the SU(2) convention to this projection's handedness.
    ico = roots_on_sphere(C.ICO_V, with_infinity=True)
    generators = [
        rotation(ico[1], 2 * np.pi / 5),  # 5-fold about a vertex
        rotation(roots_on_sphere(C.ICO_H)[0], 2 * np.pi / 3),  # 3-fold about a face centre
        rotation(roots_on_sphere(C.ICO_T)[0], np.pi),  # 2-fold about an edge midpoint
    ]
    rng = np.random.default_rng(7)
    sample = rng.normal(size=(4000, 3))
    sample /= np.linalg.norm(sample, axis=1, keepdims=True)
    # Degree-60 maps: keep |w| modest so the ratios keep full precision.
    sample = sample[np.abs(to_plane(sample)) < 8.0][:500]
    with np.errstate(all="ignore"):
        base = np.abs(ratio(to_plane(sample)))
        for rot in generators:
            moved = to_plane(sample @ rot.T)
            rel = np.abs(ratio(moved)) / base
            good = np.isfinite(rel) & (base > 0) & (np.abs(moved) < 1e3)
            assert np.max(np.abs(rel[good] - 1.0)) < 1e-9


# --- agreement with complexplorer ----------------------------------------------------


@pytest.mark.parametrize(
    "ours, theirs",
    [
        (forms.PHI, cpp.tetrahedral_vertex),
        (forms.PSI, cpp.tetrahedral_dual_vertex),
        (forms.V, cpp.octahedral_vertex),
        (forms.F, cpp.cube_vertex),
        (forms.E, cpp.octahedral_edge),
        (forms.ICO_V, cpp.icosahedral_vertex),
        (forms.ICO_H, cpp.icosahedral_hessian),
        (forms.ICO_T, cpp.icosahedral_edge),
    ],
    ids=["PHI", "PSI", "V", "F", "E", "ICO_V", "ICO_H", "ICO_T"],
)
def test_forms_match_complexplorer(ours, theirs):
    """Two independent derivations agreeing is the strongest check on orientation."""
    rng = np.random.default_rng(1)
    z = rng.normal(size=200) + 1j * rng.normal(size=200)
    a, b = ours(z), theirs(z)
    assert np.max(np.abs(a - b) / np.maximum(np.abs(a), 1.0)) < TOL
