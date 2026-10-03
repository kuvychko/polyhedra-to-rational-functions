"""Alignment dowel holes: pin choice by size, a blind hole in each cut face, watertight halves."""

import numpy as np
import pytest
from complexplorer.export.stl import scale_to_size

from polyhedral_functions import catalog, cuts, dowels, fixtures, hangers, meshes

PIECES = {p.id: p for p in catalog.load()}


def prepared(piece_id, size):
    piece = PIECES[piece_id]
    group = fixtures.load(piece.polyhedron).symmetry_group()
    normal, _ = cuts.snap_normal(piece.cut["normal"], group)
    mesh = scale_to_size(meshes.closed_relief(piece, resolution=120), float(size), "extent")
    return normal, mesh


@pytest.mark.parametrize("size, pin, depth", [(80, "M5 x 10", 6.0), (130, "M5 x 20", 11.0)])
def test_pin_and_depth_follow_the_print_size(size, pin, depth):
    normal, mesh = prepared("icosidodecahedral-star", size)
    dowel = dowels.plan(mesh, normal, size)
    assert dowel.pin.startswith(pin) and "fallback" not in dowel.pin
    assert dowel.depth_each_side_mm == depth
    assert min(dowel.floor_plus_mm, dowel.floor_minus_mm) >= dowels.MIN_FLOOR_MM


@pytest.mark.parametrize("piece_id", ["tetrahedral-dual", "r2-irregular-separated"])
def test_dowel_is_a_blind_hole_in_each_half(piece_id):
    normal, mesh = prepared(piece_id, 130)
    dowel = dowels.plan(mesh, normal, 130)
    solid = hangers.to_manifold(mesh)
    bored = dowels.bore(solid, dowel, normal)
    cylinder = np.pi * (dowel.diameter_mm / 2) ** 2 * 2 * dowel.depth_each_side_mm
    # Blind on both sides: exactly the cylinder is removed, nothing breaks through.
    assert solid.volume() - bored.volume() == pytest.approx(cylinder, rel=0.02)
    upper, lower = hangers.split(bored, normal)
    for half, build in ((upper, normal), (lower, -normal)):
        posed = cuts.to_print_pose(half, build)
        assert cuts.watertight(posed)
        # The hole opens on the cut face (z = 0) around the centre of that face.
        assert posed.bounds[4] == pytest.approx(0.0, abs=1e-6)


def test_no_pin_fits_a_tiny_solid():
    normal, mesh = prepared("tetrahedral-dual", 80)
    tiny = mesh.scale(0.15, inplace=False)
    with pytest.raises(RuntimeError, match="no dowel pin fits"):
        dowels.plan(tiny, normal, 80)
