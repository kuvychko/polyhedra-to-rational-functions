"""The six baseline presets: normalization, pole orders, and agreement with the recorded run.

The first two groups are ported from ``verify_math.py`` (figures_repo @ 292bec4). The
regression group compares against ``experiments/R0-baseline/manifest.json``, the manifest the
source wrote when it built the printed meshes.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from polyhedral_functions.baseline import ornaments

from . import coefficients as C

MANIFEST = json.loads(
    (Path(__file__).parents[2] / "experiments" / "R0-baseline" / "manifest.json").read_text(
        encoding="utf-8"
    )
)
SLUGS = list(ornaments.BY_SLUG)


def finite_roots(coeffs, order=1):
    return list(np.roots(coeffs)) * order


# Finite divisor of each raw function: (zeros, poles), with multiplicity by repetition.
DIVISORS = {
    "tetrahedral-dual": (finite_roots(C.PHI), finite_roots(C.PSI)),
    "octahedral-crown": (finite_roots(C.E), finite_roots(C.V, 2)),
    "cube-octahedron-dual": (finite_roots(C.V, 4), finite_roots(C.F, 3)),
    "icosahedral-crown": (finite_roots(C.ICO_T, 2), finite_roots(C.ICO_V, 5)),
    "dodecahedron-icosahedron-dual": (finite_roots(C.ICO_V, 5), finite_roots(C.ICO_H, 3)),
    "icosidodecahedral-star": (finite_roots(C.ICO_H, 3), finite_roots(C.ICO_T, 2)),
}


def test_registry_is_the_six_polyhedral_pieces():
    assert set(SLUGS) == set(DIVISORS) == set(MANIFEST)


def closed_form_normalization(zeros, poles, leading=1.0):
    """c = (1/|A|) prod (1+|p|^2)^(1/2) / prod (1+|z|^2)^(1/2), over finite zeros and poles.

    Holds because log of the chordal distance to any fixed point integrates to -1/2 over the
    sphere. Roots at infinity correctly do not appear.
    """
    num = np.prod([np.sqrt(1 + abs(p) ** 2) for p in poles])
    den = np.prod([np.sqrt(1 + abs(z) ** 2) for z in zeros])
    return float(num / den / abs(leading))


# Relative error of the sampled constant at STATS_RESOLUTION. 0.5%, not machine precision:
# log|f| is log-singular at every zero and pole, so the lat/long Riemann sum converges only as
# O(1/N). The source's check script never covered cube-octahedron-dual, and it is the
# exception: order-4 zeros sit at BOTH grid poles, where the lat/long grid is worst, and the
# constant used for the printed piece (183.25) is 0.55% above the exact 729/4. Measured
# error at resolution 200/400/800/1600: 1.18% / 0.55% / 0.23% / 0.07%, so it is convergence,
# not a wrong formula. See notes/2026-09-30-baseline-audit.md.
NORMALIZATION_RTOL = {"cube-octahedron-dual": 6e-3}


@pytest.mark.parametrize("slug", SLUGS)
def test_sampled_normalization_matches_closed_form(slug):
    sampled = ornaments.normalization(ornaments.BY_SLUG[slug].raw)
    exact = closed_form_normalization(*DIVISORS[slug])
    assert sampled == pytest.approx(exact, rel=NORMALIZATION_RTOL.get(slug, 5e-3))


def test_cube_octahedron_dual_closed_form_is_729_over_4():
    """Derived: over the 8 cube vertices prod sqrt(1+|p|^2) = 36; over the 5 finite
    octahedron vertices (0 and four on the unit circle) prod sqrt(1+|z|^2) = 4. With poles of
    order 3 and zeros of order 4, c = 36^3 / 4^4 = 46656 / 256 = 729/4."""
    assert closed_form_normalization(*DIVISORS["cube-octahedron-dual"]) == pytest.approx(729 / 4)


# One pole of each piece; symmetry makes the others equivalent.
ONE_POLE = {
    "tetrahedral-dual": np.roots(C.PSI)[0],
    "octahedral-crown": 1.0,
    "cube-octahedron-dual": np.roots(C.F)[0],
    "icosahedral-crown": np.roots(C.ICO_V)[0],
    "dodecahedron-icosahedron-dual": np.roots(C.ICO_H)[0],
    "icosidodecahedral-star": np.roots(C.ICO_T)[0],
}


@pytest.mark.parametrize("slug", SLUGS)
def test_declared_pole_order_is_measured_order(slug):
    """`pole_order` sets the tip sharpness, so a wrong value silently reshapes the object.

    Near a pole of order mu, |f| ~ C / d^mu, so log|f| against log(1/d) has slope mu.
    """
    orn = ornaments.BY_SLUG[slug]
    func, _ = ornaments.prepare(orn)
    eps = np.array([1e-4, 1e-5, 1e-6, 1e-7])
    with np.errstate(all="ignore"):
        modulus = np.abs(func(ONE_POLE[slug] + eps))
    slope = np.polyfit(-np.log(eps), np.log(modulus), 1)[0]
    assert slope == pytest.approx(orn.pole_order, abs=0.02)


# --- regression against the recorded run ----------------------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_relief_settings_match_recorded_run(slug):
    gen, info = ornaments.generator(ornaments.BY_SLUG[slug])
    recorded = MANIFEST[slug]
    assert gen.resolution == recorded["resolution"]
    for key in ("pre_scale", "pole_order", "depth", "contrast", "sharpness", "scaling"):
        assert info[key] == recorded[key], key
    assert info["scaling_params"] == pytest.approx(recorded["scaling_params"])
    assert info["normalization_constant"] == pytest.approx(
        recorded["normalization_constant"], rel=1e-6
    )


@pytest.mark.slow
def test_cube_octahedron_dual_mesh_matches_recorded_run():
    """Rebuild the reference piece and compare the printability facts recorded for it."""
    from complexplorer.export.stl import scale_to_size

    from polyhedral_functions.baseline import meshtools

    gen, _ = ornaments.generator(ornaments.BY_SLUG["cube-octahedron-dual"])
    mesh = meshtools.close_relief(gen.generate_ornament(verbose=False))
    recorded = MANIFEST["cube-octahedron-dual"]
    assert mesh.n_cells == recorded["n_triangles"]
    assert mesh.n_points == recorded["n_points"]

    facts = meshtools.inspect_mesh(scale_to_size(mesh, 80.0, axis="extent"))
    small = recorded["sizes"]["80"]
    assert facts["n_boundary_edges"] == facts["n_non_manifold_edges"] == 0
    for key in ("extent_mm", "min_radius_mm", "max_radius_mm", "volume_cm3", "surface_area_cm2"):
        assert facts[key] == pytest.approx(small[key], abs=0.11), key
