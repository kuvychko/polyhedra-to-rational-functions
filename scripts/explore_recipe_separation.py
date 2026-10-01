"""Exploratory: how different are the recipes' fields once the degree is removed?

Run:  uv run python scripts/explore_recipe_separation.py

Produces the tables in ``notes/2026-10-01-recipe-separation.md``. It is a quick screen, not an
experiment. The recipes are written inline here and will be superseded by ``recipes.py`` (M4),
and the comparison metric is a single correlation.

For a balanced divisor, log|f| equals, up to an additive constant,
``L(x) = sum m_i log chi(x, a_i) - sum n_j log chi(x, b_j)``, where ``chi`` is the chordal
distance on the unit sphere. Two recipes are compared through ``L / degree``: the Pearson
correlation over 40,000 Fibonacci points, excluding a 3-degree cap around every candidate
feature so that the log singularities do not dominate. Correlation 1 means the same field up to
scale and offset, so the recipes differ only in degree, which a display mapping can absorb.
"""

from functools import reduce
from math import gcd

import numpy as np

from polyhedral_functions import fixtures

N_POINTS = 40_000
CAP_DEG = 3.0


def fibonacci_sphere(n: int) -> np.ndarray:
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    r = np.sqrt(1 - z * z)
    t = np.pi * (1 + 5**0.5) * i
    return np.stack([r * np.cos(t), r * np.sin(t), z], axis=1)


X = fibonacci_sphere(N_POINTS)


def log_chordal(points: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore"):
        return np.log(np.linalg.norm(X[:, None, :] - points[None, :, :], axis=-1))


def potential(zeros, zero_orders, poles, pole_orders) -> tuple[np.ndarray, int]:
    """``L / degree`` at the sample points, and the degree."""
    degree = int(zero_orders.sum())
    assert degree == int(pole_orders.sum()), "unbalanced divisor"
    return (log_chordal(zeros) @ zero_orders - log_chordal(poles) @ pole_orders) / degree, degree


def divisor(zeros, zero_orders, poles, pole_orders):
    """``(zeros, orders, poles, orders)`` with every order divided by their common gcd."""
    g = reduce(gcd, np.concatenate([zero_orders, pole_orders]).tolist())
    return zeros, zero_orders // g, poles, pole_orders // g


def recipes(poly, placement: str = "polar", edge: str = "foot") -> dict:
    """R1, R2 and both R4 variants. Zeros go on the first point set of each pair."""
    v = poly.vertex_directions()
    f = poly.face_directions() if placement == "polar" else poly.face_centroid_directions()
    e = poly.edge_tangency_directions() if edge == "foot" else poly.edge_midpoint_directions()
    nv, nf = poly.n_vertices, poly.n_faces
    two = np.full(poly.n_edges, 2)
    return {
        "R1": divisor(v, np.full(nv, nf), f, np.full(nf, nv)),
        "R2": divisor(v, poly.valences, f, poly.face_sizes),
        "R4ve": divisor(v, poly.valences, e, two),
        "R4fe": divisor(f, poly.face_sizes, e, two),
    }


def correlation(a: np.ndarray, b: np.ndarray, keep: np.ndarray) -> float:
    a, b = a[keep] - a[keep].mean(), b[keep] - b[keep].mean()
    return float(a @ b / np.sqrt((a @ a) * (b @ b)))


def main() -> None:
    rows, placement_rows, identity = [], [], []
    for fixture_id in fixtures.CONSTRUCTIONS:
        poly = fixtures.load(fixture_id)
        candidates = np.vstack(
            [
                poly.vertex_directions(),
                poly.face_directions(),
                poly.face_centroid_directions(),
                poly.edge_tangency_directions(),
                poly.edge_midpoint_directions(),
            ]
        )
        keep = (X @ candidates.T).max(axis=1) < np.cos(np.radians(CAP_DEG))

        fields = {k: potential(*r) for k, r in recipes(poly).items()}
        degrees = {k: d for k, (_, d) in fields.items()}
        L = {k: field for k, (field, _) in fields.items()}
        rows.append(
            (
                fixture_id,
                degrees,
                correlation(L["R1"], L["R2"], keep),
                correlation(L["R2"], L["R4ve"], keep),
                correlation(L["R2"], L["R4fe"], keep),
                correlation(L["R4ve"], L["R4fe"], keep),
            )
        )

        alt = {k: potential(*r)[0] for k, r in recipes(poly, "centroid", "midpoint").items()}
        placement_rows.append(
            (
                fixture_id,
                correlation(L["R2"], alt["R2"], keep),
                correlation(L["R4ve"], alt["R4ve"], keep),
            )
        )

        # D_R2 = D_R4ve - D_R4fe with unreduced incidence orders, all totalling 2E.
        v, f, e = poly.vertex_directions(), poly.face_directions(), poly.edge_tangency_directions()
        two = np.full(poly.n_edges, 2)
        r2 = potential(v, poly.valences, f, poly.face_sizes)[0]
        ve = potential(v, poly.valences, e, two)[0]
        fe = potential(f, poly.face_sizes, e, two)[0]
        ok = np.isfinite(r2) & np.isfinite(ve) & np.isfinite(fe)
        identity.append((fixture_id, float(np.abs(r2[ok] - (ve[ok] - fe[ok])).max())))

    print("| fixture | degree R1 / R2 / R4ve / R4fe | R1~R2 | R2~R4ve | R2~R4fe | R4ve~R4fe |")
    print("|---|---|---|---|---|---|")
    for fid, d, *c in rows:
        deg = f"{d['R1']} / {d['R2']} / {d['R4ve']} / {d['R4fe']}"
        print(f"| {fid} | {deg} | " + " | ".join(f"{x:.3f}" for x in c) + " |")
    print("\n| fixture | R2: polar~centroid | R4ve: foot~midpoint |")
    print("|---|---|---|")
    for fid, a, b in placement_rows:
        print(f"| {fid} | {a:.3f} | {b:.3f} |")
    print("\nmax |L_R2 - (L_R4ve - L_R4fe)| over fixtures:", f"{max(e for _, e in identity):.1e}")


if __name__ == "__main__":
    main()
