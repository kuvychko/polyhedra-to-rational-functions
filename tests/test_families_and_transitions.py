"""Parametric families, exact jump divisors at combinatorial transitions, placement criteria,
and the relief-radius model used to compare displays (E002-E004)."""

import numpy as np
import pytest
from complexplorer.export.stl import OrnamentGenerator

from polyhedral_functions import families
from polyhedral_functions.diagnostics import placement_report
from polyhedral_functions.divisors import Divisor
from polyhedral_functions.evaluation import as_function, log_modulus_on_sphere
from polyhedral_functions.recipes import R2, R4FE, R4VE, apply
from polyhedral_functions.rendering import relief_radius

CUBE = families.cube()
CORNER = np.ones(3) / np.sqrt(3)
X, Y, Z = np.eye(3)


@pytest.mark.parametrize(
    "family, summary",
    [
        (families.truncated_corner_cube, (10, 15, 7)),
        (families.bevelled_edge_cube, (10, 15, 7)),
        (families.raised_face_cube, (9, 16, 9)),
    ],
)
def test_transition_families_change_combinatorics(family, summary):
    for s in (0.3, 1e-3):
        poly = family(s)
        assert (poly.n_vertices, poly.n_edges, poly.n_faces) == summary


@pytest.mark.parametrize("family", [families.hexagonal_pyramid, families.sheared_box])
def test_deformation_families_keep_combinatorics(family):
    summaries = {str(family(p).summary()) for p in (0.2, 0.9, 1.5, 2.5)}
    assert len(summaries) == 1


def unreduced(recipe, poly):
    result = apply(recipe, poly)
    return result.divisor * result.gcd


def jump(recipe, family):
    limit, _ = unreduced(recipe, family(1e-7)).coalesced(tol=1e-4)
    return (limit - unreduced(recipe, CUBE)).coalesced(tol=1e-4)[0]


def test_r4ve_is_continuous_under_vertex_truncation():
    assert len(jump(R4VE, families.truncated_corner_cube)) == 0


def test_r4fe_is_continuous_under_the_polar_transition():
    assert len(jump(R4FE, families.raised_face_cube)) == 0


def test_r2_jump_at_vertex_truncation_is_the_derived_divisor():
    """+3 at the cut corner (zeros 9, pole 3 vs the cube's 3) and -1 on each pentagon."""
    expected = Divisor([CORNER, X, Y, Z], [3, -1, -1, -1])
    assert jump(R2, families.truncated_corner_cube).same_as(expected, tol=1e-4)


def test_r4ve_jumps_under_an_edge_bevel():
    """+1 at each end of the bevelled edge, -2 at its middle: no member is continuous here."""
    ends = [np.array([1, 1, 1]) / np.sqrt(3), np.array([1, 1, -1]) / np.sqrt(3)]
    middle = np.array([1, 1, 0]) / np.sqrt(2)
    expected = Divisor([*ends, middle], [1, 1, -2])
    assert jump(R4VE, families.bevelled_edge_cube).same_as(expected, tol=1e-4)


def test_continuous_recipe_converges_quadratically():
    residual = []
    for s in (1e-2, 1e-3):
        d = unreduced(R4VE, families.truncated_corner_cube(s))
        x = np.random.default_rng(0).normal(size=(4000, 3))
        x /= np.linalg.norm(x, axis=1, keepdims=True)
        x = x[(x @ CORNER) < 0.95]
        diff = log_modulus_on_sphere(d, x) - log_modulus_on_sphere(unreduced(R4VE, CUBE), x)
        residual.append(np.sqrt(np.mean(diff**2)))
    assert residual[1] < residual[0] / 50  # about s^2: a factor ~100 per decade


def test_sheared_box_placement_threshold_at_sigma_one():
    below, above = (
        placement_report(families.sheared_box(0.9)),
        placement_report(families.sheared_box(1.1)),
    )
    assert below["faces_polar_outside"] == 0 and below["edges_foot_outside"] == 0
    assert above["faces_polar_outside"] == 2 and above["edges_foot_outside"] == 4
    for sigma in (0.5, 1.5, 2.5):
        assert placement_report(families.sheared_box(sigma))["faces_centroid_outside"] == 0


def test_relief_radius_matches_complexplorer_mesh():
    d = apply(R2, families.hexagonal_pyramid(1.0)).divisor
    k, depth = 6.0, 0.25
    mesh = OrnamentGenerator(
        as_function(d),
        resolution=60,
        normalize=None,
        sharpness=k,
        scaling_params={"r_min": depth, "r_max": 1.0},
    ).generate_ornament(verbose=False)
    r = np.linalg.norm(mesh.points, axis=1)
    keep = (r > depth + 1e-3) & (r < 1 - 1e-3)
    directions = mesh.points[keep] / r[keep, None]
    predicted = relief_radius(log_modulus_on_sphere(d, directions), k, depth)
    assert np.allclose(predicted, r[keep], atol=1e-6)
