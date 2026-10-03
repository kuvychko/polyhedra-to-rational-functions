"""Cut planes: watertight halves in print pose, how halves relate, and the proposals."""

import numpy as np
import pytest

from polyhedral_functions import catalog, cuts, fixtures, meshes

PIECES = {p.id: p for p in catalog.load()}


@pytest.fixture(scope="module")
def tetra_mesh():
    return meshes.closed_relief(PIECES["tetrahedral-dual"], resolution=80)


def test_halves_are_watertight_and_posed_on_the_bed(tetra_mesh):
    n = np.array([0.0, 1.0, 1.0]) / np.sqrt(2)
    upper, lower = cuts.cut(tetra_mesh, n)
    for half, build in ((upper, n), (lower, -n)):
        posed = cuts.to_print_pose(half, build)
        assert cuts.watertight(posed)
        assert posed.bounds[4] == pytest.approx(0.0, abs=1e-9)
    assert upper.volume + lower.volume == pytest.approx(tetra_mesh.volume, rel=1e-3)


def test_tetrahedral_mirror_plane_gives_identical_halves():
    """Each mirror plane of the tetrahedron contains a 2-fold axis's perpendicular: a proper
    half-turn swaps the two sides, so one file printed twice makes the piece."""
    group = fixtures.load("tetrahedron").symmetry_group()
    mirror = np.array([0.0, 1.0, 1.0]) / np.sqrt(2)
    three_fold = np.ones(3) / np.sqrt(3)
    assert cuts.halves_relation(mirror, group) == "identical"
    assert cuts.halves_relation(three_fold, group) == "different"


def test_asymmetric_solid_has_different_halves():
    group = fixtures.load("irregular-separated").symmetry_group()
    assert cuts.halves_relation(np.array([0.0, 0.0, 1.0]), group) == "different"


def test_proposals_are_distinct_classes_ranked_best_first(tetra_mesh):
    group = fixtures.load("tetrahedron").symmetry_group()
    proposals = cuts.propose(tetra_mesh, PIECES["tetrahedral-dual"].divisor(), group)
    assert proposals[0].halves == "identical"
    keys = [p.rank_key() for p in proposals]
    assert keys == sorted(keys)
    for a in proposals:
        for b in proposals:
            if a is not b:
                assert all(abs(g @ a.normal @ b.normal) < 1 - 1e-6 for g in group)


def test_unapproved_cut_blocks_export(tmp_path):
    piece = PIECES["r2-triakis-tetrahedron"]
    if not piece.cut_approved():
        with pytest.raises(ValueError, match="approved"):
            meshes.export_cuts(piece, (80,), tmp_path)
