"""Stable evaluation of the rational function a balanced divisor defines.

The function is pinned down by the **chordal convention** (see `normalization`):

    log|f(x)| = sum_i m_i log chi(x, a_i)

where ``chi`` is the chordal (Euclidean) distance between unit vectors. This magnitude needs no
chart and no choice of constant, and it is exactly rotation-covariant. In the chart it is the
modulus of

    f(z) = C * prod_{finite a_i} (z - a_i)^{m_i},    C = prod_{finite a_i} (1 + |a_i|^2)^{-m_i/2}

because balance cancels every ``(1 + |z|^2)`` factor and every factor of 2. A point at the north
pole contributes no factor: it is encoded by the drop in polynomial degree.

The phase is ``sum m_i arg(z - a_i)``, with ``C > 0``. That is a **chart convention**: rotating
the sphere changes the phase by more than a rotation of the palette, so compare phases only
between functions written in the same chart, and only up to a global shift.

Everything is accumulated in the log domain, in chunks. Degrees in the hundreds never form a
product, so nothing overflows before the final `exp`.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .chart import to_sphere
from .divisors import Divisor
from .normalization import log_chart_constant

_CHUNK = 20_000


def log_modulus_on_sphere(divisor: Divisor, x) -> np.ndarray:
    """``log|f|`` at unit vectors ``x`` (shape ``(k, 3)``). It is ``-inf`` at zeros, ``+inf`` at
    poles, and NaN where a zero and a pole coincide (coalesce the divisor first)."""
    divisor.require_balanced()
    x = np.asarray(x, dtype=float).reshape(-1, 3)
    out = np.empty(len(x))
    orders = divisor.orders.astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        for s in range(0, len(x), _CHUNK):
            d = np.linalg.norm(x[s : s + _CHUNK, None, :] - divisor.points[None, :, :], axis=-1)
            out[s : s + _CHUNK] = np.log(d) @ orders
    return out


def log_modulus_and_phase(divisor: Divisor, z) -> tuple[np.ndarray, np.ndarray]:
    """``(log|f|, arg f)`` at chart coordinates ``z`` of any shape, phase in ``(-pi, pi]``.

    Infinite ``z`` takes the value at the north pole. If ``f`` is finite and nonzero there,
    that value is ``C``, with phase 0.
    """
    divisor.require_balanced()
    z = np.asarray(z, dtype=complex)
    shape = z.shape
    z = z.reshape(-1)
    finite_pts, finite_orders, order_at_inf = divisor.chart_form()
    log_c = log_chart_constant(divisor)
    orders = finite_orders.astype(float)

    log_mod = np.empty(len(z))
    phase = np.zeros(len(z))
    finite = np.isfinite(z)
    zf = z[finite]
    lm = np.empty(len(zf))
    ph = np.empty(len(zf))
    with np.errstate(divide="ignore", invalid="ignore"):
        for s in range(0, len(zf), _CHUNK):
            diff = zf[s : s + _CHUNK, None] - finite_pts[None, :]
            lm[s : s + _CHUNK] = np.log(np.abs(diff)) @ orders + log_c
            ph[s : s + _CHUNK] = np.angle(diff) @ orders
    log_mod[finite] = lm
    phase[finite] = np.angle(np.exp(1j * ph))  # wrap
    log_mod[~finite] = -np.inf if order_at_inf > 0 else (np.inf if order_at_inf < 0 else log_c)
    return log_mod.reshape(shape), phase.reshape(shape)


def evaluate(divisor: Divisor, z) -> np.ndarray:
    """``f(z)`` as complex values. It is 0 at zeros and ``inf`` at poles."""
    log_mod, phase = log_modulus_and_phase(divisor, z)
    with np.errstate(over="ignore", invalid="ignore"):
        out = np.exp(log_mod) * np.exp(1j * phase)
    out = np.where(np.isposinf(log_mod), complex(np.inf, 0.0), out)
    return out


def as_function(divisor: Divisor) -> Callable:
    """A plain ``f(z)`` callable, e.g. for complexplorer's plotting and meshing functions."""

    def f(z):
        return evaluate(divisor, z)

    return f


def log_modulus_at(divisor: Divisor, z) -> np.ndarray:
    """``log|f|`` at chart coordinates, through the sphere, as a chart-free cross-check."""
    z = np.asarray(z, dtype=complex)
    return log_modulus_on_sphere(divisor, to_sphere(z.reshape(-1))).reshape(z.shape)
