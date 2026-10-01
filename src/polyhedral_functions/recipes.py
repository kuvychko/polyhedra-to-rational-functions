"""Recipes: rules that turn a polyhedron into a divisor (``PROGRAM.md`` §7).

Two kinds of rule:

- **R1, uniform:** order ``F`` at every vertex direction and order ``V`` at every face direction
  (zeros on vertices). Reduced by the common gcd.
- **The incidence family** ``a D_ve + b D_fe``, where

      D_ve = sum_v valence(v) [v] - 2 sum_e [e]
      D_fe = sum_f sides(f)   [f] - 2 sum_e [e]

  are both balanced (each totals ``2E``). Members:

  ======  =========  =============================================
  (a, b)  name       divisor
  ======  =========  =============================================
  (1, -1) R2         valence at vertices, sides at faces (edges cancel)
  (1, 0)  R4ve       valence at vertices, 2 at edges
  (0, 1)  R4fe       sides at faces, 2 at edges
  (1, 1)  flag       vertices and faces against edges of order 4
  ======  =========  =============================================

  Implemented once, so the identity ``R2 = R4ve - R4fe`` holds by construction rather than by
  coincidence. See ``notes/2026-10-01-recipe-separation.md``.

**Placement** is a separate setting: faces at polar directions (default) or projected area
centroids, and edges at the perpendicular foot from the origin (default) or projected
midpoints. With the defaults every recipe commutes with polarity:

- R1 and R2 on the polar dual give the reciprocal function;
- incidence ``(a, b)`` on the dual equals ``(b, a)`` on the primal, so R4ve and R4fe swap and the
  flag recipe is the **same** function for a polyhedron and its dual.

The centroid and midpoint placements are not polarity-invariant, so they break these relations
(``tests/test_recipes.py``).

Orientation: the reciprocal of any recipe is equally valid. Negate the result, or use
``Recipe.reciprocal()``.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import numpy as np

from .divisors import Divisor
from .geometry import Polyhedron

FACE_PLACEMENTS = ("polar", "centroid")
EDGE_PLACEMENTS = ("foot", "midpoint")


@dataclass(frozen=True)
class Recipe:
    """A point-placement and multiplicity rule.

    ``kind`` is ``"uniform"`` (R1) or ``"incidence"``, with integer coefficients ``a`` and ``b``.
    ``sign = -1`` takes the reciprocal.
    """

    name: str
    kind: str = "incidence"
    a: int = 1
    b: int = -1
    sign: int = 1
    face_placement: str = "polar"
    edge_placement: str = "foot"
    version: int = 1

    def __post_init__(self) -> None:
        if self.kind not in ("uniform", "incidence"):
            raise ValueError(f"unknown recipe kind {self.kind!r}")
        if self.kind == "incidence" and self.a == 0 and self.b == 0:
            raise ValueError("incidence recipe needs (a, b) != (0, 0)")
        if self.sign not in (1, -1):
            raise ValueError("sign is +1 or -1")
        if self.face_placement not in FACE_PLACEMENTS:
            raise ValueError(f"face placement must be one of {FACE_PLACEMENTS}")
        if self.edge_placement not in EDGE_PLACEMENTS:
            raise ValueError(f"edge placement must be one of {EDGE_PLACEMENTS}")

    def reciprocal(self) -> Recipe:
        return replace(self, name=f"1/{self.name}", sign=-self.sign)

    def placed(self, face: str | None = None, edge: str | None = None) -> Recipe:
        """The same multiplicities with different point placement."""
        face = face or self.face_placement
        edge = edge or self.edge_placement
        suffix = "" if (face, edge) == ("polar", "foot") else f"[{face},{edge}]"
        base = self.name.split("[")[0]
        return replace(self, name=base + suffix, face_placement=face, edge_placement=edge)

    def config(self) -> dict:
        """The recipe's settings, for run manifests."""
        return {
            "name": self.name,
            "kind": self.kind,
            "a": self.a,
            "b": self.b,
            "sign": self.sign,
            "face_placement": self.face_placement,
            "edge_placement": self.edge_placement,
            "version": self.version,
        }

    def apply(self, poly: Polyhedron) -> RecipeResult:
        return apply(self, poly)


R1 = Recipe("R1", kind="uniform")
R2 = Recipe("R2", a=1, b=-1)
R4VE = Recipe("R4ve", a=1, b=0)
R4FE = Recipe("R4fe", a=0, b=1)
FLAG = Recipe("flag", a=1, b=1)
PRESETS = {r.name: r for r in (R1, R2, R4VE, R4FE, FLAG)}


@dataclass(frozen=True, eq=False)
class RecipeResult:
    """The divisor a recipe gives on one polyhedron, with how it was obtained.

    ``divisor`` is coalesced and gcd-reduced. ``unreduced_degree`` and ``gcd`` record the
    reduction, and ``cancellations`` lists every zero-pole cancellation of coincident points.
    """

    recipe: Recipe
    polyhedron: str
    divisor: Divisor
    gcd: int
    unreduced_degree: int
    cancellations: list = field(default_factory=list)

    @property
    def degree(self) -> int:
        return self.divisor.degree

    def record(self) -> dict:
        """Manifest entry: the recipe's settings plus the resulting divisor's summary."""
        return {
            "recipe": self.recipe.config(),
            "polyhedron": self.polyhedron,
            "divisor": self.divisor.summary(),
            "gcd": self.gcd,
            "unreduced_degree": self.unreduced_degree,
            "n_cancellations": len(self.cancellations),
        }


def _face_points(poly: Polyhedron, placement: str) -> np.ndarray:
    return poly.face_directions() if placement == "polar" else poly.face_centroid_directions()


def _edge_points(poly: Polyhedron, placement: str) -> np.ndarray:
    if placement == "foot":
        return poly.edge_tangency_directions()
    return poly.edge_midpoint_directions()


def _cells(poly: Polyhedron, kind: str, recipe: Recipe) -> Divisor:
    """Each cell of one type as a positive divisor with its incidence order."""
    if kind == "v":
        pts, orders = poly.vertex_directions(), poly.valences
        labels = tuple(f"vertex {i}" for i in range(poly.n_vertices))
    elif kind == "f":
        pts, orders = _face_points(poly, recipe.face_placement), poly.face_sizes
        labels = tuple(f"face {j}" for j in range(poly.n_faces))
    else:
        pts, orders = _edge_points(poly, recipe.edge_placement), np.full(poly.n_edges, 2)
        labels = tuple(f"edge {k}" for k in range(poly.n_edges))
    return Divisor(pts, orders, labels)


def apply(recipe: Recipe, poly: Polyhedron) -> RecipeResult:
    """The recipe's divisor on ``poly``: coalesced, cancellations recorded, gcd-reduced."""
    if recipe.kind == "uniform":
        vertices = Divisor(
            poly.vertex_directions(),
            np.full(poly.n_vertices, poly.n_faces),
            tuple(f"vertex {i}" for i in range(poly.n_vertices)),
        )
        faces = Divisor(
            _face_points(poly, recipe.face_placement),
            np.full(poly.n_faces, poly.n_vertices),
            tuple(f"face {j}" for j in range(poly.n_faces)),
        )
        raw = vertices - faces
    else:
        edges = _cells(poly, "e", recipe)
        d_ve = _cells(poly, "v", recipe) - edges
        d_fe = _cells(poly, "f", recipe) - edges
        raw = Divisor.empty()
        if recipe.a:
            raw = raw + recipe.a * d_ve
        if recipe.b:
            raw = raw + recipe.b * d_fe
    raw = recipe.sign * raw
    raw.require_balanced()

    merged, cancellations = raw.coalesced()
    # Cancellation of a cell against itself (the edges in R2, where +a and +b meet) is
    # bookkeeping, not geometry. Only report zero-pole meetings between *different* cells.
    cancellations = [c for c in cancellations if len(set(c["labels"])) > 1]
    reduced, g = merged.reduced()
    return RecipeResult(
        recipe=recipe,
        polyhedron=poly.name,
        divisor=reduced,
        gcd=g,
        unreduced_degree=merged.degree,
        cancellations=cancellations,
    )
