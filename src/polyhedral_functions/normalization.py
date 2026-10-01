"""Magnitude normalization: the chordal convention, and the baseline's closed form.

**Chordal convention.** A balanced divisor ``D = sum m_i [a_i]`` gets the function with
``log|f(x)| = sum m_i log chi(x, a_i)``, where ``chi`` is the Euclidean distance between unit
vectors. Three properties make this the default:

- *Self-dual:* the divisor ``-D`` gets exactly ``1/f``.
- *Rotation-covariant:* rotating ``D`` rotates ``|f|``, with no constant to refit.
- *Geometric mean 1 over the sphere [D]:* the area-average of ``log chi(x, a)`` is
  ``log 2 - 1/2`` for every ``a``, and the orders sum to zero. So sea level ``|f| = 1`` is the
  baseline's geometric-mean level, reached exactly, with no sampling.

The baseline normalized ``c * raw(z)`` by sampling the geometric mean. For
``raw = A prod(z - z_j) / prod(z - p_k)`` its closed form, `polynomial_ratio_constant`, gives
exactly the chordal function (``tests/test_normalization.py``). The two conventions are the same
modulus, reached without sampling error.

The phase is not normalized here: ``C > 0`` in the chart. See `evaluation`.
"""

from __future__ import annotations

import numpy as np

from .divisors import Divisor

# Area-average of log chi(x, a) over the unit sphere, for any fixed unit vector a [D]:
# with chi = 2 sin(theta / 2) and density sin(theta) / 2, the integral is log 2 - 1/2.
MEAN_LOG_CHORDAL = float(np.log(2.0) - 0.5)


def log_chart_constant(divisor: Divisor) -> float:
    """``log C`` with ``C = prod_{finite a_i} (1 + |a_i|^2)^{-m_i/2}``: the chart's positive
    leading constant under the chordal convention. Requires a balanced divisor."""
    divisor.require_balanced()
    pts, orders, _ = divisor.chart_form()
    return float(-0.5 * (orders * np.log1p(np.abs(pts) ** 2)).sum())


def polynomial_ratio_constant(zeros, poles, leading: complex = 1.0) -> float:
    """The baseline's closed-form constant for ``A prod(z - z_j) / prod(z - p_k)``.

    ``c = (1/|A|) prod sqrt(1 + |p_k|^2) / prod sqrt(1 + |z_j|^2)`` over **finite** zeros and
    poles, listed with multiplicity. ``c * raw`` is then the chordal-convention function.
    """
    zeros = np.asarray(zeros, dtype=complex)
    poles = np.asarray(poles, dtype=complex)
    log_c = 0.5 * (np.log1p(np.abs(poles) ** 2).sum() - np.log1p(np.abs(zeros) ** 2).sum())
    return float(np.exp(log_c) / abs(leading))


def fibonacci_sphere(n: int) -> np.ndarray:
    """``n`` nearly uniform points on the unit sphere, each standing for area ``4 pi / n``.

    Used to *check* sphere averages, not to define a normalization.
    """
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    r = np.sqrt(1 - z * z)
    t = np.pi * (1 + 5**0.5) * i
    return np.stack([r * np.cos(t), r * np.sin(t), z], axis=1)
