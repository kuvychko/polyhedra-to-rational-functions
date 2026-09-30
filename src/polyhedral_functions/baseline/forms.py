"""Klein's relative invariants, as used by the baseline ornaments.

Frozen copy -- see the package docstring for provenance. Source lines 33-122 of
``ornaments.py``, verbatim.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

# --- Klein's relative invariants for the polyhedral groups -------------------------
#
# A degree-d rational map has exactly d zeros and d poles on the sphere, so "poles at
# the 6 octahedron vertices and nothing else" is impossible. For the relief to carry the
# full polyhedral rotation symmetry, f must be a ratio of relative invariants of equal
# *binary-form* degree: the automorphy factors then cancel and |f| descends to a genuine
# invariant function on the sphere. `verify_math.py` checks every claim below.


def PHI(z):
    """Tetrahedral vertex form, binary degree 4. Roots: 4 tetrahedron vertices."""
    return z**4 + 2j * np.sqrt(3) * z**2 + 1


def PSI(z):
    """The dual (antipodal) tetrahedron, binary degree 4.

    PHI * PSI == F exactly: the two tetrahedra together are the cube.
    """
    return z**4 - 2j * np.sqrt(3) * z**2 + 1


def V(z):
    """Octahedral vertex form, binary degree 6.

    Only degree 5 as a polynomial -- the sixth root is the vertex at infinity.
    """
    return z * (z**4 - 1)


def F(z):
    """Octahedral face form = cube vertex form, binary degree 8."""
    return z**8 + 14 * z**4 + 1


def E(z):
    """Octahedral edge form, binary degree 12. Roots: the 12 cuboctahedron vertices."""
    return z**12 - 33 * z**8 - 33 * z**4 + 1


# The icosahedral trio. `ICO_` prefixed so as not to collide with the octahedral V/F/E
# above; the classical names for these are V (or f), H (the Hessian) and T.
#
# These coefficients were DERIVED, not copied, and that matters. The forms quoted in the
# literature only cohere as a set for one particular orientation of the icosahedron, and
# the commonly-remembered signs mix orientations: taking
# `V = z(z^10 + 11z^5 - 1)` together with `H = -(z^20 + 228z^15 + ...)` gives three root
# sets that are each individually a perfect icosahedron, dodecahedron and edge set, yet
# are rotated relative to one another. |V^5/H^3| then fails rotation invariance by a
# factor of 1e3 to 1e5 and Klein's syzygy does not hold at all -- a failure that is
# invisible if you only check the geometry of each form separately.
#
# The set below comes from building an explicit icosahedron (vertex at the north pole,
# rings at z = +-1/sqrt(5)), projecting stereographically and taking the monic polynomial
# over the finite roots. The coefficients land on integers to 1e-10, the syzygy
# `ICO_H^3 - ICO_T^2 = 1728 * ICO_V^5` holds exactly, and all three ratios are invariant
# to ~1e-13. `verify_math.py` re-checks every one of those claims.


def ICO_V(z):
    """Icosahedral vertex form, binary degree 12.

    Degree 11 as a polynomial -- the twelfth root is the vertex at infinity. Note the
    **minus** 11; the +11 variant belongs to a different orientation.
    """
    return z * (z**10 - 11 * z**5 - 1)


def ICO_H(z):
    """Icosahedral Hessian, degree 20. Roots: the 20 dodecahedron vertices."""
    return z**20 + 228 * z**15 + 494 * z**10 - 228 * z**5 + 1


def ICO_T(z):
    """Icosahedral edge form, degree 30. Roots: the 30 edge midpoints.

    Note the signs on the 522 terms run minus then plus, the reverse of the variant
    usually quoted.
    """
    return z**30 - 522 * z**25 - 10005 * z**20 - 10005 * z**10 + 522 * z**5 + 1


def _ratio(num: Callable, den: Callable, npow: int = 1, dpow: int = 1) -> Callable:
    """f(z) = num(z)**npow / den(z)**dpow, with division warnings suppressed."""

    def f(z):
        with np.errstate(all="ignore"):
            return num(z) ** npow / den(z) ** dpow

    return f
