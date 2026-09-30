"""The six polyhedral Riemann-relief ornaments: presets, normalization and relief settings.

Frozen copy -- see the package docstring for provenance. An excerpt of ``ornaments.py``;
the only edits are:

- the seven non-polyhedral pieces, their view constants and the filter gain constants are
  omitted, so the registry is `POLYHEDRAL` rather than ``COLLECTION``;
- the Klein forms live in `forms` and are imported from there;
- the output-path helpers (``FAMILY_DIRS``, ``output_dir``), the ``family`` field and the
  command-line lookups (``get``, ``select``) are dropped: every piece here is polyhedral,
  this package writes no files, and `BY_SLUG` serves lookups;
- ruff reformatting.

Everything else -- values, docstrings, comments -- is as in the source. Comments that
mention ``verify_math.py`` refer to the source's check script, whose checks now live in
``tests/baseline/``.

Geometry conventions inherited from complexplorer 3.1:

- The relief is the modulus |f| painted on the Riemann sphere and pushed radially.
  `complexplorer.core.field.sample_sphere` uses the canonical projection, so ``z = 0``
  sits at the SOUTH pole, ``z = inf`` at the NORTH pole and ``|z| = 1`` at the equator.
- The radius depends on |f| alone, through a transfer whose midpoint is |f| = 1. So the
  *absolute* magnitude of f changes the shape and not just its zero/pole pattern, which
  is why most pieces are normalized first. See `normalization`.
- The relief transfer itself -- the `logarithmic` / `log_mixture` modes, `pole_order`,
  `sharpness`, `contrast` and the cap on the derived scale -- is complexplorer's own since
  3.1, which upstreamed what this file first worked out. What stays here is the
  per-piece choice of those settings, and the normalization constant. See `generator`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from .forms import ICO_H, ICO_T, ICO_V, PHI, PSI, E, F, V, _ratio

# --- relief shaping ----------------------------------------------------------------

DEFAULT_DEPTH = 0.20

# How pointy the features are is set by complexplorer: with
# `r = r_min + (r_max - r_min) * logistic(log|f| / k)` the surface approaches a feature of
# order `mu` like `distance ** (mu / k)`, and the library derives `k = 2 * pole_order`, capped
# at 6. So the tip exponent -- not k -- is fixed at 1/2 for every piece, and a double pole is
# as sharp as a simple one. Fitting k to each piece's log-modulus spread instead -- the
# obvious thing, and what this file did first -- gives exponents from 1 to 8 and turns half
# the collection into rounded blobs. The cap only bites on `icosahedral-crown` (order 5),
# whose uncapped k = 10 asks for more dynamic range than a resolution-400 grid delivers.

# Named print sizes, as **tip-to-tip extent** in millimetres -- the true maximum width of
# the object, not a bounding-box dimension. See complexplorer's `max_extent`: the box
# depends on how a piece happens to sit in the coordinate frame, which silently made
# `cube-octahedron-dual` 1.73x larger than everything else while every piece reported the
# same nominal "80 mm".
#
# 80 matches the icosahedral pieces as first printed; 130 is within 5% of the
# cube-octahedron dual as first printed. Both of those came out well.
SIZES = {"small": 80.0, "large": 130.0}


# Viewing direction (not a position -- `renders_pv.py` fits the distance to the mesh's
# own bounds, so pieces of very different shapes are framed at the same apparent size).
DEFAULT_VIEW = (2.2, 2.2, 1.6)
# Down a 3-fold axis, which shows a polyhedral piece's symmetry most directly.
POLYHEDRAL_VIEW = (1.0, 1.0, 1.0)
# For the icosahedral pieces: just off the 5-fold axis, which this orientation puts along
# z. Reads as a fivefold rosette with the polar feature at the centre. (1,1,1) would be
# wrong here -- that is a 3-fold axis of the *cube*, not of this icosahedron. Straight
# down the axis is flatter and makes VTK reset the view-up.
ICOSAHEDRAL_VIEW = (0.6, 0.0, 2.4)


@dataclass(frozen=True)
class Ornament:
    """One piece of the collection.

    `raw` is the mathematical function. What actually gets meshed is
    ``c * raw(pre_scale * z)``, where `c` is `gain` when that is given and the
    sphere-wide geometric-mean constant otherwise -- see `prepare`.
    """

    slug: str
    name: str
    latex: str
    raw: Callable
    story: str
    zeros: str
    poles: str
    symmetry: str
    cut_plane: str
    pre_scale: float = 1.0
    # Explicit normalization constant. None means "compute the sphere-wide geometric
    # mean" (`normalization`), which is right for a piece whose features are spread
    # over the sphere. Set it when that average is the wrong one -- see the pole
    # flowers and the two filters.
    gain: float | None = None
    pole_order: int = 1  # order of the highest-order pole; drives the tip sharpness
    sharpness: float | None = None  # None: the library's capped 2 * pole_order
    # (boost, weight) for complexplorer's `log_mixture` transfer, or None for a single
    # logistic. Set it on a piece whose few features leave the rest of the body a
    # featureless sphere. See "Contrast" in the README for the trade.
    contrast: tuple[float, float] | None = None
    depth: float = DEFAULT_DEPTH
    resolution: int = 250
    view: tuple[float, float, float] = DEFAULT_VIEW
    portrait_half_width: float = 2.0


# --- sphere statistics -------------------------------------------------------------

# log|f| has log singularities at every zero and pole, so this lat/long Riemann sum
# converges only as O(1/N): 400 lands the constants within ~0.4% of their exact closed
# form (see `verify_math.py`), which moves sea level by under 0.5% of relief height --
# far below anything a nozzle can resolve. Higher is pointless; lower starts to show.
STATS_RESOLUTION = 400


def sphere_log_modulus(func: Callable, resolution: int = STATS_RESOLUTION):
    """Area-weighted samples of ``log|func|`` over the Riemann sphere.

    Sampling goes through complexplorer's own `sample_sphere`, so the statistics are
    computed on exactly the points the relief is built from. Those points lie on a
    latitude/longitude grid, which crowds the poles, so each sample carries a weight
    proportional to ``sin(theta)``. Without that weight a function with a high-order zero
    or pole at infinity is badly mis-measured -- the constant for `pole-flower-10` comes
    out ten times too large.
    """
    from complexplorer.core.field import sample_sphere

    field = sample_sphere(func, resolution=resolution)
    with np.errstate(all="ignore"):
        modulus = np.asarray(field.modulus, dtype=float).ravel()
    z_coord = np.asarray(field.sphere_xyz, dtype=float)[..., 2].ravel()
    weight = np.sqrt(np.clip(1.0 - z_coord**2, 0.0, None))

    good = np.isfinite(modulus) & (modulus > 0) & (weight > 0)
    return np.log(modulus[good]), weight[good]


def normalization(func: Callable) -> float:
    """Constant c making the geometric mean of |c * func| over the sphere equal to 1.

    The geometric mean is the right average because it is self-dual: normalizing 1/f
    gives the reciprocal of the constant that normalizes f. Together with
    ``logistic(-x) = 1 - logistic(x)``, that makes peaks and pits exact mirror images
    about sea level -- the relief of 1/f is the relief of f turned inside out, and
    nothing else changes.

    It also has a closed form. For ``f = A * prod(z - z_j) / prod(z - p_k)`` over the
    finite zeros and poles,

        c = (1/|A|) * prod (1 + |p_k|^2)^(1/2) / prod (1 + |z_j|^2)^(1/2)

    because the log of the chordal distance to a fixed point integrates to -1/2 over the
    sphere whatever that point is. `verify_math.py` checks the sampled constants against
    that formula.
    """
    log_modulus, weight = sphere_log_modulus(func)
    if log_modulus.size == 0:
        return 1.0
    return float(np.exp(-np.average(log_modulus, weights=weight)))


# --- preparing a piece for meshing --------------------------------------------------

_PREPARED: dict[str, tuple] = {}


def prepare(orn: Ornament) -> tuple[Callable, dict]:
    """Resolve one ornament to ``(func, info)``.

    `func` is ``c * raw(pre_scale * z)``, already normalized, so the STL, the render and
    the phase portrait all see the same function. `info` records the constants for the
    manifest and the README. Cached, because fitting the constant costs a sphere sample.
    """
    if orn.slug in _PREPARED:
        return _PREPARED[orn.slug]

    a = orn.pre_scale
    base_func = orn.raw if a == 1.0 else (lambda z, a=a: orn.raw(a * z))

    constant = orn.gain if orn.gain is not None else normalization(base_func)

    def func(z, c=constant, g=base_func):
        with np.errstate(all="ignore"):
            return c * g(z)

    info = {
        "pre_scale": a,
        "pole_order": orn.pole_order,
        "normalization_constant": round(constant, 6),
        "depth": orn.depth,
        "contrast": (
            None if orn.contrast is None else {"boost": orn.contrast[0], "weight": orn.contrast[1]}
        ),
    }
    _PREPARED[orn.slug] = (func, info)
    return _PREPARED[orn.slug]


def generator(orn: Ornament, resolution: int | None = None, cmap=None):
    """complexplorer's `OrnamentGenerator` for one piece, plus the manifest `info`.

    Normalization is done here rather than by the library, so ``normalize=None`` is
    essential: 3.1 normalizes by default, which would silently renormalize the pole
    flowers and the filters, whose constants are deliberately not the sphere-wide mean.
    Our own constant also comes from a finer, fixed grid than the piece's mesh, and is
    what `verify_math.py` checks against the closed form.

    The transfer settings are read back off the generator, so the manifest records what
    the library actually used rather than what this file expected it to.
    """
    from complexplorer.export.stl import OrnamentGenerator

    func, info = prepare(orn)
    gen = OrnamentGenerator(
        func,
        resolution=resolution if resolution is not None else orn.resolution,
        cmap=cmap,
        normalize=None,
        pole_order=orn.pole_order,
        sharpness=orn.sharpness,
        contrast=orn.contrast,
        scaling_params={"r_min": orn.depth, "r_max": 1.0},
    )
    info = {
        **info,
        "sharpness": round(gen.sharpness, 4),
        "scaling": gen.scaling,
        "scaling_params": {k: round(float(v), 4) for k, v in gen.scaling_params.items()},
    }
    return gen, info


# --- the polyhedral pieces ---------------------------------------------------------

POLYHEDRAL: list[Ornament] = [
    Ornament(
        slug="tetrahedral-dual",
        # Eight features, but a large smooth body between them.
        contrast=(4.0, 0.6),
        name="Tetrahedral Dual",
        latex=r"f(z)=\frac{\Phi(z)}{\Psi(z)},\quad "
        r"\Phi=z^{4}+2i\sqrt{3}\,z^{2}+1,\ \ \Psi=z^{4}-2i\sqrt{3}\,z^{2}+1",
        raw=_ratio(PHI, PSI),
        story="A ratio of the two dual tetrahedral forms -- and $\\Phi\\Psi=F$, the "
        "cube form, because the two tetrahedra together are the cube. Four spikes at "
        "the vertices of one regular tetrahedron, four pits at its antipode. The relief "
        "is chiral: every mirror of the tetrahedron turns it inside out instead of "
        "fixing it, exchanging the spikes with the pits.",
        zeros="4 simple zeros at one regular tetrahedron",
        poles="4 simple poles at the dual (antipodal) tetrahedron",
        symmetry="$T$ (order 12, rotations only) -- no mirror plane fixes it",
        cut_plane="perpendicular to a 2-fold axis; the halves are NOT congruent, which "
        "is the point of the piece",
        view=POLYHEDRAL_VIEW,
        portrait_half_width=2.5,
    ),
    Ornament(
        slug="octahedral-crown",
        name="Octahedral Crown",
        latex=r"f(z)=\frac{E(z)}{V(z)^{2}}",
        raw=_ratio(E, V, npow=1, dpow=2),
        story="Klein's octahedral edge form over the square of the vertex form. Six "
        "double poles at the octahedron's vertices, twelve simple zeros at its edge "
        "midpoints -- which are themselves the vertices of a cuboctahedron.",
        zeros="12 simple zeros at the octahedron's edge midpoints",
        poles="6 double poles at the octahedron's vertices",
        symmetry="full $O_h$ (order 48), including all nine mirror planes",
        cut_plane="any coordinate plane; the two halves are identical, so one printed "
        "file twice makes the whole piece",
        pole_order=2,
        resolution=300,
        view=POLYHEDRAL_VIEW,
    ),
    Ornament(
        slug="cube-octahedron-dual",
        name="Cube-Octahedron Dual",
        latex=r"f(z)=\frac{V(z)^{4}}{F(z)^{3}}",
        raw=_ratio(V, F, npow=4, dpow=3),
        story="The showpiece: a degree-24 Klein invariant. Eight triple poles at the "
        "cube's vertices and six quadruple zeros at the octahedron's -- peaks on one "
        "Platonic solid, pits on its dual, in a single smooth surface. Its spikes sit "
        "exactly where the Octahedral Crown has its pits.",
        zeros="6 zeros of order 4 at the octahedron's vertices",
        poles="8 poles of order 3 at the cube's vertices",
        symmetry="full $O_h$ (order 48), including all nine mirror planes",
        cut_plane="any coordinate plane; the halves are identical. Build with $z$ up -- "
        "the order-4 zero at the north pole gives a genuinely flat first layer",
        pole_order=3,
        resolution=300,
        view=POLYHEDRAL_VIEW,
    ),
    Ornament(
        slug="icosahedral-crown",
        name="Icosahedral Crown",
        latex=r"f(z)=\frac{\mathcal{T}(z)^{2}}{\mathcal{V}(z)^{5}}",
        raw=_ratio(ICO_T, ICO_V, npow=2, dpow=5),
        story="The icosahedral answer to the Octahedral Crown, and a jump from degree 12 "
        "to degree 60 -- the icosahedral rotation group has order 60, so 60 is the "
        "lowest degree any invariant ratio can have. Twelve spikes of order 5 at the "
        "icosahedron's vertices, thirty pits at its edge midpoints.",
        zeros="30 double zeros at the icosahedron's edge midpoints",
        poles="12 poles of order 5 at the icosahedron's vertices",
        symmetry="full $I_h$ (order 120), the largest symmetry group in the collection",
        cut_plane="any mirror plane of the icosahedron; the halves are identical",
        pole_order=5,
        resolution=400,
        view=ICOSAHEDRAL_VIEW,
    ),
    Ornament(
        slug="dodecahedron-icosahedron-dual",
        name="Dodecahedron-Icosahedron Dual",
        latex=r"f(z)=\frac{\mathcal{V}(z)^{5}}{\mathcal{H}(z)^{3}}",
        raw=_ratio(ICO_V, ICO_H, npow=5, dpow=3),
        story="The icosahedral twin of the Cube-Octahedron Dual, built the same way: the "
        "vertex form of one solid over the vertex form of its dual, at matching degree. "
        "Twenty triple spikes on the dodecahedron, twelve order-5 pits on the "
        "icosahedron. Its spikes sit exactly where the Icosahedral Crown has its pits.",
        zeros="12 zeros of order 5 at the icosahedron's vertices",
        poles="20 triple poles at the dodecahedron's vertices",
        symmetry="full $I_h$ (order 120)",
        cut_plane="any mirror plane of the icosahedron; the halves are identical",
        pole_order=3,
        resolution=400,
        view=ICOSAHEDRAL_VIEW,
    ),
    Ornament(
        slug="icosidodecahedral-star",
        name="Icosidodecahedral Star",
        latex=r"f(z)=\frac{\mathcal{H}(z)^{3}}{\mathcal{T}(z)^{2}}",
        raw=_ratio(ICO_H, ICO_T, npow=3, dpow=2),
        story="The third degree-60 ratio, and the one with no counterpart elsewhere in "
        "the set: thirty double spikes at the icosahedron's edge midpoints -- the "
        "vertices of an icosidodecahedron -- over twenty triple pits on the "
        "dodecahedron. The densest piece here, and the most sea-urchin-like.",
        zeros="20 triple zeros at the dodecahedron's vertices",
        poles="30 double poles at the icosahedron's edge midpoints",
        symmetry="full $I_h$ (order 120)",
        cut_plane="any mirror plane of the icosahedron; the halves are identical",
        pole_order=2,
        resolution=400,
        view=ICOSAHEDRAL_VIEW,
    ),
]

BY_SLUG = {o.slug: o for o in POLYHEDRAL}
