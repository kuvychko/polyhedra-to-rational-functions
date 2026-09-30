"""The geometry contract: construction, validation failures, polarity and point sets."""

import itertools

import numpy as np
import pytest

from polyhedral_functions import fixtures
from polyhedral_functions.geometry import GeometryError, Polyhedron

IDS = list(fixtures.CONSTRUCTIONS)
CUBE_POINTS = np.array(list(itertools.product([-1.0, 1.0], repeat=3)))


def angle_between(a, b):
    return np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", a, b), -1, 1)))


def random_rotation(seed):
    q, r = np.linalg.qr(np.random.default_rng(seed).normal(size=(3, 3)))
    q = q * np.sign(np.diag(r))
    return q if np.linalg.det(q) > 0 else -q


# --- construction ----------------------------------------------------------------------


def test_hull_merges_coplanar_facets_into_genuine_faces():
    cube = Polyhedron.from_points(CUBE_POINTS)
    assert cube.n_faces == 6
    assert set(cube.face_sizes) == {4}


def test_hull_rejects_points_that_are_not_corners():
    with pytest.raises(GeometryError, match="not vertices"):
        Polyhedron.from_points(np.vstack([CUBE_POINTS, [[1.0, 0.0, 0.0]]]))  # face centre


def test_faces_are_counterclockwise_from_outside():
    for fixture_id in IDS:
        poly = fixtures.load(fixture_id)
        normals, _ = poly.face_planes
        for f, n in zip(poly.faces, normals, strict=True):
            a, b, c = poly.vertices[list(f[:3])]
            assert np.cross(b - a, c - b) @ n > 0


# --- validation failures ------------------------------------------------------------------

CUBE = Polyhedron.from_points(CUBE_POINTS)


def test_split_face_is_rejected_as_not_genuine():
    faces = [f for f in CUBE.faces]
    a, b, c, d = faces[0]
    faces[0:1] = [(a, b, c), (a, c, d)]
    with pytest.raises(GeometryError, match="coplanar"):
        Polyhedron.from_faces(CUBE.vertices, faces)


def test_inward_face_is_rejected():
    faces = list(CUBE.faces)
    faces[0] = tuple(reversed(faces[0]))
    with pytest.raises(GeometryError, match="orientation|twice"):
        Polyhedron.from_faces(CUBE.vertices, faces)


def test_all_faces_reversed_is_rejected():
    faces = [tuple(reversed(f)) for f in CUBE.faces]
    with pytest.raises(GeometryError, match="inward"):
        Polyhedron.from_faces(CUBE.vertices, faces)


def test_open_surface_is_rejected():
    with pytest.raises(GeometryError, match="not closed|no face"):
        Polyhedron.from_faces(CUBE.vertices, CUBE.faces[1:])


def test_non_planar_face_is_rejected():
    moved = CUBE.vertices.copy()
    moved[CUBE.faces[0][0]] *= 1.1
    with pytest.raises(GeometryError, match="not planar"):
        CUBE.with_vertices(moved)


def test_origin_outside_or_on_boundary_is_rejected():
    with pytest.raises(GeometryError, match="strictly inside"):
        CUBE.translated([2.0, 0.0, 0.0])
    with pytest.raises(GeometryError, match="strictly inside"):
        CUBE.translated([1.0, 0.0, 0.0])


def test_non_convex_is_rejected():
    # Push the top face of the cube down through the middle: every face stays planar, but the
    # solid is no longer convex.
    moved = CUBE.vertices.copy()
    top = [i for i, v in enumerate(moved) if v[2] > 0]
    moved[top, 2] = -0.5
    moved[top, :2] *= 0.5
    with pytest.raises(GeometryError):
        CUBE.with_vertices(moved)


# --- polarity ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture_id", IDS)
def test_double_dual_returns_the_polyhedron(fixture_id):
    poly = fixtures.load(fixture_id)
    dual = poly.polar_dual()
    assert (dual.n_vertices, dual.n_edges, dual.n_faces) == (
        poly.n_faces,
        poly.n_edges,
        poly.n_vertices,
    )
    assert np.array_equal(dual.valences, poly.face_sizes)
    assert np.array_equal(dual.face_sizes, poly.valences)
    back = dual.polar_dual()
    assert back.same_combinatorics(poly)
    assert np.allclose(back.vertices, poly.vertices, atol=1e-12)


@pytest.mark.parametrize("fixture_id", IDS)
def test_dual_vertex_directions_are_face_normals(fixture_id):
    poly = fixtures.load(fixture_id)
    assert np.allclose(poly.polar_dual().vertex_directions(), poly.face_directions())


@pytest.mark.parametrize("fixture_id", IDS)
def test_edge_tangency_directions_are_self_dual(fixture_id):
    """An edge and its polar-dual edge have their perpendicular feet in the same direction."""
    poly = fixtures.load(fixture_id)
    dual = poly.polar_dual()
    matched = dual.edge_tangency_directions()[poly.dual_edge_index()]
    assert np.allclose(matched, poly.edge_tangency_directions(), atol=1e-12)


# --- point sets -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture_id", ["tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron"]
)
def test_candidate_point_sets_coincide_on_platonic_solids(fixture_id):
    poly = fixtures.load(fixture_id)
    assert np.allclose(poly.face_centroid_directions(), poly.face_directions())
    assert np.allclose(poly.edge_midpoint_directions(), poly.edge_tangency_directions())


def test_candidate_point_sets_differ_on_less_regular_solids():
    """Where the controlled point-placement comparisons have something to measure.

    On the canonical deltoidal icositetrahedron, centroid and polar directions differ by the
    same small angle on every kite (0.896 degrees), so the placement comparison there will be
    subtle. On irregular-9 they differ by 7 to 20 degrees.
    """
    dit = fixtures.load("deltoidal-icositetrahedron")
    kites = angle_between(dit.face_centroid_directions(), dit.face_directions())
    assert np.allclose(kites, 0.896, atol=1e-3)
    irregular = fixtures.load("irregular-9")
    faces = angle_between(irregular.face_centroid_directions(), irregular.face_directions())
    assert faces.min() > 6.0 and faces.max() < 21.0
    edges = angle_between(
        irregular.edge_midpoint_directions(), irregular.edge_tangency_directions()
    )
    assert edges.max() > 1.0


@pytest.mark.parametrize("fixture_id", IDS)
def test_rotation_rotates_every_point_set(fixture_id):
    poly = fixtures.load(fixture_id)
    R = random_rotation(11)
    turned = poly.rotated(R)
    assert turned.same_combinatorics(poly)
    for name in (
        "vertex_directions",
        "face_directions",
        "face_centroid_directions",
        "edge_tangency_directions",
        "edge_midpoint_directions",
    ):
        assert np.allclose(getattr(turned, name)(), getattr(poly, name)() @ R.T), name


def test_improper_rotation_is_rejected():
    with pytest.raises(GeometryError, match="proper"):
        CUBE.rotated(np.diag([1.0, 1.0, -1.0]))


# --- deformation ------------------------------------------------------------------------


def test_parallel_face_shift_keeps_combinatorics():
    """Moving one face plane outward is a fixed-combinatorics deformation of the cube."""
    moved = CUBE.vertices.copy()
    moved[moved[:, 0] > 0, 0] = 1.3
    deformed = CUBE.with_vertices(moved)
    assert deformed.same_combinatorics(CUBE)


def test_generic_vertex_perturbation_changes_combinatorics():
    """A generic vertex motion splits the planar faces it touches (PROGRAM.md §6)."""
    moved = CUBE.vertices.copy()
    moved[0] += [0.01, -0.02, 0.015]
    hull = Polyhedron.from_points(moved)
    assert not hull.same_combinatorics(CUBE)
    assert hull.n_faces > CUBE.n_faces
