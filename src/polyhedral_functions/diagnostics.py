"""Mathematical and numerical checks on recipes (``PROGRAM.md`` §5 and §9).

Every check returns plain numbers or dicts suitable for a run manifest, and states its
tolerance or exclusion radius. Under the chordal convention (decision 0003) ``|f|`` is a
function of the divisor alone. So symmetry and duality of the **magnitude** are decided exactly
by divisor comparisons, and the sampled residuals here are independent confirmations rather than
the definition. Phase is chart-dependent and is reported separately where it is meaningful.
"""

from __future__ import annotations

import numpy as np

from .chart import to_chart
from .divisors import Divisor
from .evaluation import log_modulus_and_phase, log_modulus_on_sphere
from .geometry import Polyhedron
from .normalization import fibonacci_sphere
from .recipes import Recipe, apply

DEFAULT_SAMPLES = 20_000
# Radius (chordal, about radians) of the caps excluded around zeros and poles when comparing
# fields. Behaviour inside the caps is checked separately, by `winding_orders`.
DEFAULT_EXCLUSION = 0.05


def exclusion_mask(x: np.ndarray, points: np.ndarray, radius: float) -> np.ndarray:
    """True where ``x`` is farther than ``radius`` from every point in ``points``."""
    if radius <= 0 or not len(points):
        return np.ones(len(x), dtype=bool)
    d = np.linalg.norm(x[:, None, :] - np.asarray(points)[None, :, :], axis=-1)
    return d.min(axis=1) > radius


def field_comparison(
    d1: Divisor,
    d2: Divisor,
    n: int = DEFAULT_SAMPLES,
    exclusion: float = DEFAULT_EXCLUSION,
    per_degree: bool = True,
) -> dict:
    """Compare two magnitude fields on matched Fibonacci samples.

    With ``per_degree``, each ``log|f|`` is divided by its degree, so recipes of different degree
    are compared by shape. Reports the Pearson correlation, the RMS and maximum absolute
    difference, and the excluded fraction. Caps of radius ``exclusion`` around every feature
    of either divisor are excluded.
    """
    x = fibonacci_sphere(n)
    keep = exclusion_mask(x, np.vstack([d1.points, d2.points]), exclusion)
    a = log_modulus_on_sphere(d1, x[keep])
    b = log_modulus_on_sphere(d2, x[keep])
    if per_degree:
        a, b = a / max(d1.degree, 1), b / max(d2.degree, 1)
    ac, bc = a - a.mean(), b - b.mean()
    denom = np.sqrt((ac @ ac) * (bc @ bc))
    return {
        "correlation": float(ac @ bc / denom) if denom > 0 else float("nan"),
        "rms_difference": float(np.sqrt(np.mean((a - b) ** 2))),
        "max_abs_difference": float(np.max(np.abs(a - b))),
        "per_degree": per_degree,
        "samples": int(n),
        "exclusion_radius": exclusion,
        "excluded_fraction": float(1 - keep.mean()),
    }


def winding_orders(d: Divisor, radius: float = 1e-5, n: int = 256) -> list[dict]:
    """Local order of every feature, measured as phase winding on a small loop.

    Finite features use a loop in the chart. The point at infinity uses the loop
    ``z = 1/(r e^{it})``, on which the phase winds by the order at infinity. Finite loop radii are
    scaled by ``1 + |z|^2``, so loops are about the same size on the sphere everywhere.
    """
    t = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
    loop = np.exp(1j * t)
    out = []
    for point, order, label in zip(d.points, d.orders, d.labels, strict=True):
        z0 = to_chart([point])[0]
        if np.isfinite(z0):
            z = z0 + radius * (1 + abs(z0) ** 2) * loop
        else:
            z = 1.0 / (radius * loop)
        _, phase = log_modulus_and_phase(d, z)
        steps = np.angle(np.exp(1j * np.diff(np.append(phase, phase[0]))))
        # At infinity, f ~ c z^(-m) for a zero of order m, and on z = 1/(r e^{it}) that is
        # c r^m e^{imt}: the loop already winds +m, with no sign change.
        winding = steps.sum() / (2 * np.pi)
        out.append({"label": label, "declared": int(order), "measured": int(round(winding))})
    return out


def symmetry_report(d: Divisor, group: list[np.ndarray], tol: float = 1e-8) -> dict:
    """Which elements of ``group`` preserve the divisor, and which turn it inside out.

    Under the chordal convention, the divisor is preserved iff ``|f|`` is invariant, and it
    maps to its negative iff ``|f|`` maps to ``1/|f|``. Elements are split into proper
    (rotations) and improper (reflections and rotoreflections).
    """
    report = {
        "group_order": len(group),
        "preserved_proper": 0,
        "preserved_improper": 0,
        "inverted_proper": 0,
        "inverted_improper": 0,
    }
    for g in group:
        kind = "proper" if np.linalg.det(g) > 0 else "improper"
        image = d.rotated(g)
        if image.same_as(d, tol):
            report[f"preserved_{kind}"] += 1
        elif image.same_as(-d, tol):
            report[f"inverted_{kind}"] += 1
    report["preserved"] = report["preserved_proper"] + report["preserved_improper"]
    return report


def dual_partner(recipe: Recipe) -> Recipe:
    """The recipe whose result on ``P*`` should be compared with ``recipe`` on ``P``.

    With polar and foot placement, incidence ``(a, b)`` on ``P*`` equals ``(b, a)`` on ``P``. R1
    and R2 are therefore reciprocal (``(1, -1) -> (-1, 1)``), R4ve and R4fe swap, and the flag
    recipe is self-dual. The prediction is the same recipe applied to the dual. This function
    names the *primal* recipe that the dual result should equal.
    """
    if recipe.kind == "uniform":
        return recipe.reciprocal()
    return Recipe(
        f"dual of {recipe.name}",
        a=recipe.b,
        b=recipe.a,
        sign=recipe.sign,
        face_placement=recipe.face_placement,
        edge_placement=recipe.edge_placement,
    )


def duality_report(
    recipe: Recipe, poly: Polyhedron, n: int = DEFAULT_SAMPLES, exclusion: float = DEFAULT_EXCLUSION
) -> dict:
    """Apply ``recipe`` to the polar dual and compare with the predicted primal recipe.

    For R1 and R2 the prediction is the reciprocal function, as ``PROGRAM.md`` §5 asks. Reports
    whether the divisors are equal, the per-point log-magnitude residual away from features,
    and, when the prediction is a reciprocal, the phase residual ``arg f + arg f*`` in the
    chart, wrapped to ``(-pi, pi]``.
    """
    on_dual = apply(recipe, poly.polar_dual()).divisor
    predicted = apply(dual_partner(recipe), poly).divisor
    x = fibonacci_sphere(n)
    keep = exclusion_mask(x, np.vstack([on_dual.points, predicted.points]), exclusion)
    residual = log_modulus_on_sphere(on_dual, x[keep]) - log_modulus_on_sphere(predicted, x[keep])
    report = {
        "divisors_equal": on_dual.same_as(predicted),
        "max_log_modulus_residual": float(np.max(np.abs(residual))),
        "exclusion_radius": exclusion,
    }
    if recipe.kind == "uniform" or (recipe.a, recipe.b) == (-recipe.b, -recipe.a):
        z = to_chart(x[keep])
        z = z[np.isfinite(z)]
        _, phase_dual = log_modulus_and_phase(on_dual, z)
        _, phase_primal = log_modulus_and_phase(-predicted, z)
        report["max_phase_residual"] = float(
            np.max(np.abs(np.angle(np.exp(1j * (phase_dual + phase_primal)))))
        )
    return report


def rotation_report(recipe: Recipe, poly: Polyhedron, rotation, n: int = DEFAULT_SAMPLES) -> dict:
    """Rotate the input, rebuild the recipe, and compare with the rotated original field.

    The residual is ``log|f_{R P}|(R x) - log|f_P|(x)``, with no exclusion: the samples avoid
    the features. A recipe that depends on anything but the geometry (for example labels or
    axes) would show up here.
    """
    R = np.asarray(rotation, dtype=float)
    original = apply(recipe, poly).divisor
    turned = apply(recipe, poly.rotated(R)).divisor
    x = fibonacci_sphere(n)
    residual = log_modulus_on_sphere(turned, x @ R.T) - log_modulus_on_sphere(original, x)
    finite = np.isfinite(residual)
    return {
        "divisors_equal": turned.same_as(original.rotated(R)),
        "max_log_modulus_residual": float(np.max(np.abs(residual[finite]))),
    }
