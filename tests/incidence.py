"""Incidence divisors written out independently of ``recipes.py``, as a cross-check on it.

Unreduced orders throughout: valence at vertices, number of sides at faces, 2 at edges.
Placement is polar face directions and edge feet.
"""

import numpy as np

from polyhedral_functions.divisors import Divisor


def points(poly, kind):
    return {
        "v": poly.vertex_directions(),
        "f": poly.face_directions(),
        "e": poly.edge_tangency_directions(),
    }[kind]


def orders(poly, kind):
    return {
        "v": poly.valences,
        "f": poly.face_sizes,
        "e": np.full(poly.n_edges, 2),
    }[kind]


def incidence(poly, zeros: str, poles: str) -> Divisor:
    """Zeros on one cell type and poles on another, e.g. ``incidence(P, "v", "f")`` is R2."""
    return Divisor.from_sets(
        points(poly, zeros),
        orders(poly, zeros),
        points(poly, poles),
        orders(poly, poles),
        zero_label=zeros,
        pole_label=poles,
    )


def uniform(poly) -> Divisor:
    """R1, unreduced: order F at every vertex, order V at every face direction."""
    return Divisor.from_sets(
        poly.vertex_directions(), poly.n_faces, poly.face_directions(), poly.n_vertices, "v", "f"
    )
