"""The stereographic chart between the unit sphere and the extended complex plane.

complexplorer's convention, used throughout: projection from the **north** pole, so the south
pole ``(0, 0, -1)`` is ``z = 0``, the north pole ``(0, 0, 1)`` is ``z = inf``, and the equator
is ``|z| = 1``.
"""

from __future__ import annotations

import numpy as np

# Within this distance of the north pole a point is treated as infinity rather than given a huge
# finite coordinate. At 1e-12 the coordinate would already have modulus about 1e12.
NORTH_POLE_TOL = 1e-12


def to_chart(points) -> np.ndarray:
    """Unit vectors to complex coordinates. The north pole maps to ``complex(inf, 0)``."""
    p = np.asarray(points, dtype=float).reshape(-1, 3)
    out = np.full(len(p), complex(np.inf, 0.0))
    finite = p[:, 2] < 1.0 - NORTH_POLE_TOL
    q = p[finite]
    w = q[:, 0] + 1j * q[:, 1]
    # 1 - z cancels catastrophically near the north pole, where |w| is large. In the northern
    # hemisphere use the equivalent form w (1 + z) / (x^2 + y^2), since 1 - z^2 = x^2 + y^2.
    north = q[:, 2] > 0
    denom = np.where(north, 1.0, 1.0 - q[:, 2])
    out_f = w / denom
    out_f[north] = w[north] * (1.0 + q[north, 2]) / (np.abs(w[north]) ** 2)
    out[finite] = out_f
    return out


def to_sphere(z) -> np.ndarray:
    """Complex coordinates to unit vectors. Any non-finite value maps to the north pole."""
    z = np.atleast_1d(np.asarray(z, dtype=complex))
    out = np.tile([0.0, 0.0, 1.0], (len(z), 1))
    finite = np.isfinite(z)
    w = z[finite]
    d = 1.0 + np.abs(w) ** 2
    out[finite] = np.stack([2 * w.real / d, 2 * w.imag / d, (np.abs(w) ** 2 - 1) / d], axis=1)
    return out


def chordal_distance(x, y) -> np.ndarray:
    """Euclidean distance between unit vectors. Pairwise ``(len(x), len(y))``."""
    x = np.asarray(x, dtype=float).reshape(-1, 3)
    y = np.asarray(y, dtype=float).reshape(-1, 3)
    # |x - y|^2 = 2 - 2 x.y for unit vectors, but the difference form keeps precision near 0.
    return np.linalg.norm(x[:, None, :] - y[None, :, :], axis=-1)
