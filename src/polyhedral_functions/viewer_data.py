"""What the site's interactive 3D viewers draw: solids, zeros and poles, as plain JSON data.

Two viewers use it:

- each object page's viewer (``docs/assets/pieces/<id>/geometry.json``, written by
  ``scripts/a4_site_assets.py``);
- the recipe comparison page (``assets/explorer/recipes.json``, generated at build time by
  ``docs/hooks/explorer.py``): every fixture under every preset recipe;
- the introduction page (``assets/explorer/primer.json``, from the same hook): a few textbook
  functions, written as divisors, and one recipe divisor.

Solids are scaled to circumradius 1, and markers are unit directions; the viewers draw them just
outside the unit sphere. Nothing here renders, so the data and the mathematics cannot drift
apart: a marker is a point of the recipe's divisor, with its order.
"""

from __future__ import annotations

import numpy as np

from . import fixtures
from .chart import to_sphere
from .divisors import Divisor
from .geometry import Polyhedron
from .recipes import PRESETS, apply

#: The recipes the comparison page offers, in menu order, with a one-line description each.
EXPLORER_RECIPES = {
    "R2": "zeros at vertices (order = valence), poles at faces (order = sides)",
    "R4ve": "zeros at vertices (order = valence), poles at edges (order 2)",
    "R4fe": "zeros at faces (order = sides), poles at edges (order 2)",
    "R1": "zeros at vertices (order = F), poles at faces (order = V)",
    "flag": "zeros at vertices and faces, poles at edges (order 4)",
}

#: Fixtures in menu order: regular solids and their duals first, then the rest of the corpus.
EXPLORER_SOLIDS = (
    "tetrahedron",
    "cube",
    "octahedron",
    "dodecahedron",
    "icosahedron",
    "rhombicuboctahedron",
    "deltoidal-icositetrahedron",
    "triakis-tetrahedron",
    "hexagonal-pyramid",
    "irregular-9",
    "irregular-mixed",
    "irregular-separated",
)


def _round(values) -> list:
    return [round(float(x), 6) for x in values]


def solid(poly: Polyhedron) -> dict:
    """The solid at circumradius 1: vertices and polygonal faces (the viewer triangulates)."""
    return {
        "name": poly.name,
        "vertices": [_round(v) for v in poly.vertices / poly.scale],
        "faces": [list(f) for f in poly.faces],
    }


def _cell(label: str) -> str:
    """``"vertex 3+face 1"`` -> ``"face and vertex"``: the kinds of cell a point stands for."""
    return " and ".join(sorted({part.split()[0] for part in label.split("+")}))


def markers(divisor: Divisor) -> dict:
    """Zeros and poles, each with its unit direction, (positive) order and cell kind."""

    def marker(point, order, label):
        return {"p": _round(point), "order": abs(int(order)), "cell": _cell(label)}

    entries = list(zip(divisor.points, divisor.orders, divisor.labels, strict=True))
    return {
        "zeros": [marker(p, o, lab) for p, o, lab in entries if o > 0],
        "poles": [marker(p, o, lab) for p, o, lab in entries if o < 0],
    }


def explorer_data() -> dict:
    """Every explorer solid under every explorer recipe.

    The markers are the **unreduced** divisor, the recipe's own (see `RecipeResult`). ``gcd`` is
    recorded so the viewer can also show the reduced orders; the points are the same.
    """
    solids = {}
    for fixture_id in EXPLORER_SOLIDS:
        poly = fixtures.load(fixture_id)
        record = solid(poly)
        record["counts"] = {"V": poly.n_vertices, "E": poly.n_edges, "F": poly.n_faces}
        record["recipes"] = {}
        for name in EXPLORER_RECIPES:
            result = apply(PRESETS[name], poly)
            record["recipes"][name] = {
                "degree": int(result.unreduced.degree),
                "gcd": int(result.gcd),
                **markers(result.unreduced),
            }
        solids[fixture_id] = record
    return {"recipes": EXPLORER_RECIPES, "solids": solids}


def unreduced_from_markers(entry: dict) -> Divisor:
    """Rebuild a divisor from viewer markers (for tests): zeros positive, poles negative."""
    zeros, poles = entry["zeros"], entry["poles"]
    return Divisor(
        np.array([m["p"] for m in zeros + poles]),
        np.array([m["order"] for m in zeros] + [-m["order"] for m in poles]),
    )


# --- the introduction page (research/primer.md) ------------------------------------------------

_OMEGA = np.exp(2j * np.pi / 3)

#: Textbook functions for the introduction, in menu order: (label, divisor as
#: ``[(chart point, order), ...]``). ``inf`` is the north pole. The chordal normalization gives
#: each of them exactly up to a positive constant, which is 1 for the first four.
PRIMER_FUNCTIONS = {
    "z": ("f(z) = z", [(0, 1), (np.inf, -1)]),
    "z2": ("f(z) = z²", [(0, 2), (np.inf, -2)]),
    "inv": ("f(z) = 1/z", [(0, -1), (np.inf, 1)]),
    "mobius": ("f(z) = (z − 1)/(z + 1)", [(1, 1), (-1, -1)]),
    "z3m1": ("f(z) = z³ − 1", [(1, 1), (_OMEGA, 1), (_OMEGA**2, 1), (np.inf, -3)]),
}

#: The recipe example closing the introduction's menu: a solid and a recipe from the explorer.
PRIMER_RECIPE = ("cube", "R2")


def primer_divisor(function_id: str) -> Divisor:
    """The divisor of one of `PRIMER_FUNCTIONS`, at points of the unit sphere."""
    _, entries = PRIMER_FUNCTIONS[function_id]
    z = np.array([complex(a) for a, _ in entries])
    return Divisor(to_sphere(z), np.array([m for _, m in entries]), ("point",) * len(entries))


def primer_data() -> dict:
    """The introduction's functions: label, degree and markers (zeros and poles), in menu order.

    Display settings (palette, relief sharpness) are added by the site hook, since they belong to
    rendering, not to the mathematics.
    """
    functions = {}
    for function_id, (label, _) in PRIMER_FUNCTIONS.items():
        d = primer_divisor(function_id)
        functions[function_id] = {"label": label, "degree": int(d.degree), **markers(d)}
    solid_id, recipe = PRIMER_RECIPE
    poly = fixtures.load(solid_id)
    d = apply(PRESETS[recipe], poly).unreduced
    functions[f"{solid_id}-{recipe}"] = {
        "label": f"{recipe} on the {poly.name}",
        "degree": int(d.degree),
        **markers(d),
    }
    return {"functions": functions}
