"""The stored corpus matches its constructions, with the expected combinatorics and orientation."""

import json

import numpy as np
import pytest
from complexplorer.core import polyhedral as cpp

from polyhedral_functions import fixtures

IDS = list(fixtures.CONSTRUCTIONS)

# id: (V, E, F, {valence: count}, {face size: count})
EXPECTED = {
    "tetrahedron": (4, 6, 4, {3: 4}, {3: 4}),
    "cube": (8, 12, 6, {3: 8}, {4: 6}),
    "octahedron": (6, 12, 8, {4: 6}, {3: 8}),
    "icosahedron": (12, 30, 20, {5: 12}, {3: 20}),
    "dodecahedron": (20, 30, 12, {3: 20}, {5: 12}),
    "rhombicuboctahedron": (24, 48, 26, {4: 24}, {3: 8, 4: 18}),
    "deltoidal-icositetrahedron": (26, 48, 24, {3: 8, 4: 18}, {4: 24}),
    "irregular-9": (14, 21, 9, {3: 14}, {3: 1, 4: 3, 5: 3, 6: 2}),
    "hexagonal-pyramid": (7, 12, 7, {3: 6, 6: 1}, {3: 6, 6: 1}),
    "triakis-tetrahedron": (8, 18, 12, {3: 4, 6: 4}, {3: 12}),
    "irregular-mixed": (9, 18, 11, {3: 1, 4: 7, 5: 1}, {3: 9, 4: 1, 5: 1}),
}


def test_every_construction_has_expectations():
    assert set(IDS) == set(EXPECTED)


@pytest.mark.parametrize("fixture_id", IDS)
def test_stored_fixture_matches_construction(fixture_id):
    stored = fixtures.load(fixture_id)
    fresh = fixtures.CONSTRUCTIONS[fixture_id]()
    assert stored.faces == fresh.faces
    assert np.allclose(stored.vertices, fresh.vertices, atol=1e-14)
    record = json.loads((fixtures.DATA_DIR / f"{fixture_id}.json").read_text(encoding="utf-8"))
    assert record == json.loads(json.dumps(fixtures.to_record(fixture_id, fresh)))


@pytest.mark.parametrize("fixture_id", IDS)
def test_combinatorics(fixture_id):
    V, E, F, valences, face_sizes = EXPECTED[fixture_id]
    summary = fixtures.load(fixture_id).summary()
    assert summary == {"V": V, "E": E, "F": F, "valences": valences, "face_sizes": face_sizes}


def same_point_set(a, b, atol=1e-12):
    """Equal as unordered sets of points."""
    if len(a) != len(b):
        return False
    distance = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
    return bool(np.all(distance.min(axis=1) < atol) and np.all(distance.min(axis=0) < atol))


def to_sphere(z):
    z = np.asarray(z, dtype=complex)
    d = 1 + abs(z) ** 2
    return np.stack([2 * z.real / d, 2 * z.imag / d, (abs(z) ** 2 - 1) / d], axis=-1)


NORTH = np.array([[0.0, 0.0, 1.0]])


@pytest.mark.parametrize(
    "fixture_id, solid, kind",
    [
        ("tetrahedron", "tetrahedron", "vertices"),
        ("octahedron", "octahedron", "vertices"),
        ("cube", "octahedron", "faces"),
        ("icosahedron", "icosahedron", "vertices"),
        ("dodecahedron", "icosahedron", "faces"),
    ],
)
def test_platonic_orientation_matches_klein_forms(fixture_id, solid, kind):
    """Same orientation as complexplorer's forms and the baseline, so divisors compare directly."""
    finite = to_sphere(cpp.polyhedral_features(solid, kind))
    ours = fixtures.load(fixture_id).vertex_directions()
    expected = finite if len(finite) == len(ours) else np.vstack([finite, NORTH])
    assert same_point_set(ours, expected)


@pytest.mark.parametrize(
    "primal, dual",
    [
        ("cube", "octahedron"),
        ("octahedron", "cube"),
        ("icosahedron", "dodecahedron"),
        ("dodecahedron", "icosahedron"),
        ("tetrahedron", None),
        ("rhombicuboctahedron", "deltoidal-icositetrahedron"),
        ("deltoidal-icositetrahedron", "rhombicuboctahedron"),
    ],
)
def test_dual_pairs_share_directions(primal, dual):
    """A fixture's face directions are its partner's vertex directions (tetrahedron: antipodes)."""
    faces = fixtures.load(primal).face_directions()
    if dual is None:
        assert same_point_set(faces, -fixtures.load(primal).vertex_directions())
    else:
        assert same_point_set(faces, fixtures.load(dual).vertex_directions())


def test_deltoidal_icositetrahedron_is_the_canonical_polar_dual():
    """Rhombicuboctahedron and its polar dual are tangent to the unit sphere at shared points."""
    rco = fixtures.load("rhombicuboctahedron")
    dit = fixtures.load("deltoidal-icositetrahedron")
    assert same_point_set(rco.polar_dual().vertices, dit.vertices)
    for poly in (rco, dit):
        feet, t = poly.edge_feet()
        assert np.allclose(np.linalg.norm(feet, axis=1), 1.0)
        assert np.all((t > 0) & (t < 1))
    assert same_point_set(rco.edge_tangency_directions(), dit.edge_tangency_directions())


def test_irregular_origin_and_edge_feet():
    poly = fixtures.load("irregular-9")
    assert poly.face_planes[1].min() == pytest.approx(0.7)
    _, t = poly.edge_feet()
    assert int(np.sum((t < 0) | (t > 1))) == 2


def test_hexagonal_pyramid_is_combinatorially_self_dual():
    pyramid = fixtures.load("hexagonal-pyramid")
    assert pyramid.polar_dual().summary() == pyramid.summary()


def test_triakis_tetrahedron_is_canonical_and_aligned_with_the_tetrahedron():
    triakis = fixtures.load("triakis-tetrahedron")
    feet, t = triakis.edge_feet()
    assert np.allclose(np.linalg.norm(feet, axis=1), 1.0)
    assert np.all((t > 0) & (t < 1))
    apexes = triakis.vertex_directions()[triakis.valences == 6]
    assert same_point_set(apexes, fixtures.load("tetrahedron").vertex_directions())


def test_irregular_mixed_is_neither_simple_nor_simplicial():
    poly = fixtures.load("irregular-mixed")
    assert len(set(poly.valences)) > 1 and len(set(poly.face_sizes)) > 1
    assert poly.face_planes[1].min() == pytest.approx(0.555, abs=1e-3)
