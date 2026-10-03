"""Hanging-ornament holes: placement, wall, a bore confined to its spike, watertight halves."""

import numpy as np
import pytest
from complexplorer.export.stl import scale_to_size

from polyhedral_functions import catalog, cuts, fixtures, hangers, meshes

PIECES = {p.id: p for p in catalog.load()}


def prepared(piece_id, size=80, resolution=120):
    piece = PIECES[piece_id]
    group = fixtures.load(piece.polyhedron).symmetry_group()
    normal, _ = cuts.snap_normal(piece.cut["normal"], group)
    mesh = scale_to_size(meshes.closed_relief(piece, resolution=resolution), float(size), "extent")
    return piece, normal, mesh


@pytest.mark.parametrize("piece_id", ["tetrahedral-dual", "r2-irregular-separated"])
def test_hole_is_through_a_spike_with_a_wall(piece_id):
    piece, normal, mesh = prepared(piece_id)
    hole = hangers.place_hole(mesh, piece.divisor(), normal)
    assert 9.0 <= hole.distance_from_tip_mm <= 16.0
    assert hole.side_wall_mm >= 1.0
    assert abs(np.dot(hole.spike_direction, normal)) < np.sin(np.radians(35))
    solid = hangers.to_manifold(mesh)
    bored = hangers.bore(solid, hole, normal)
    removed = solid.volume() - bored.volume()
    crossing = np.pi * 0.75**2 * (hole.reach_plus_mm + hole.reach_minus_mm)
    assert removed == pytest.approx(crossing, rel=hangers.REMOVED_TOLERANCE)
    for half in hangers.split(bored, normal):
        assert cuts.watertight(half)


def test_symmetric_piece_hole_is_in_a_bisected_spike():
    piece, normal, mesh = prepared("tetrahedral-dual")
    assert hangers.place_hole(mesh, piece.divisor(), normal).bisected


def test_bore_that_hits_more_than_its_spike_is_refused():
    piece, normal, mesh = prepared("tetrahedral-dual")
    hole = hangers.place_hole(mesh, piece.divisor(), normal)
    hole.reach_plus_mm *= 0.1  # claim a far thinner spike than the cylinder actually crosses
    hole.reach_minus_mm *= 0.1
    with pytest.raises(RuntimeError, match="more than its spike"):
        hangers.bore(hangers.to_manifold(mesh), hole, normal)
