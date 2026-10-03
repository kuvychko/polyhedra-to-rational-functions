"""Provenance for the ``irregular-separated`` fixture: the seeded search that chose its points.

Run:  uv run python scripts/search_irregular_separated.py

irregular-mixed has two adjacent faces only 3.4 degrees from coplanar, so R2 fuses their poles
into one double spike (P001). For a printable "any convex solid", this searches frustum-like
point sets (an irregular pentagon below an irregular quadrilateral, coordinates rounded to 0.01)
for one that keeps mixed valences and face sizes, has no symmetry, keeps every face at least 0.4
from the origin, and maximizes the smallest angle between any two R2 features. The winner is
hard-coded in ``fixtures.irregular_separated``.
"""

import numpy as np

from polyhedral_functions.geometry import GeometryError, Polyhedron
from polyhedral_functions.recipes import R2, apply

SEED, TRIALS = 20261003, 4000


def smallest_feature_angle(poly) -> float:
    d = apply(R2, poly).divisor
    cos = np.clip(d.points @ d.points.T, -1, 1)
    np.fill_diagonal(cos, -1)
    return float(np.arccos(cos.max()))


def main() -> None:
    rng = np.random.default_rng(SEED)
    best = None
    for _ in range(TRIALS):
        tb = np.sort(rng.uniform(0, 2 * np.pi, 5))
        tt = np.sort(rng.uniform(0, 2 * np.pi, 4))
        rb, rt = rng.uniform(0.8, 1.15, 5), rng.uniform(0.45, 0.8, 4)
        zb, zt = -rng.uniform(0.5, 0.8), rng.uniform(0.6, 0.9)
        off = rng.uniform(-0.15, 0.15, 2)
        pts = np.vstack(
            [
                np.c_[rb * np.cos(tb), rb * np.sin(tb), np.full(5, zb)],
                np.c_[rt * np.cos(tt) + off[0], rt * np.sin(tt) + off[1], np.full(4, zt)],
            ]
        )
        pts = np.round(pts, 2)
        try:
            poly = Polyhedron.from_points(pts)
        except (GeometryError, ValueError, RuntimeError):
            continue
        s = poly.summary()
        if len(s["valences"]) < 2 or len(s["face_sizes"]) < 2:
            continue
        if len(poly.symmetry_group()) != 1 or poly.face_planes[1].min() < 0.4:
            continue
        angle = smallest_feature_angle(poly)
        if best is None or angle > best[0]:
            best = (angle, pts)
    print(f"smallest R2 feature angle {np.degrees(best[0]):.1f} deg")
    print(best[1].tolist())


if __name__ == "__main__":
    main()
