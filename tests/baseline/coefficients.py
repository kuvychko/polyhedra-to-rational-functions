"""Monic coefficient lists (highest power first) of the baseline Klein forms.

Written out independently of `polyhedral_functions.baseline.forms`, so the root checks do
not merely evaluate the code under test against itself.
"""

import numpy as np

PHI = [1, 0, 2j * np.sqrt(3), 0, 1]
PSI = [1, 0, -2j * np.sqrt(3), 0, 1]
V = [1, 0, 0, 0, -1, 0]  # plus a root at infinity
F = [1, 0, 0, 0, 14, 0, 0, 0, 1]
E = [1, 0, 0, 0, -33, 0, 0, 0, -33, 0, 0, 0, 1]
ICO_V = [1, 0, 0, 0, 0, -11, 0, 0, 0, 0, -1, 0]  # plus a root at infinity
ICO_H = [1, 0, 0, 0, 0, 228, 0, 0, 0, 0, 494, 0, 0, 0, 0, -228, 0, 0, 0, 0, 1]
ICO_T = [1, 0, 0, 0, 0, -522, 0, 0, 0, 0, -10005, *[0] * 9, -10005, 0, 0, 0, 0, 522, 0, 0, 0, 0, 1]


def to_sphere(z):
    """Inverse stereographic projection matching complexplorer: 0 -> south, inf -> north."""
    z = np.asarray(z, dtype=complex)
    x, y = z.real, z.imag
    d = x * x + y * y + 1.0
    return np.stack([2 * x / d, 2 * y / d, (x * x + y * y - 1) / d], axis=-1)


def to_plane(points):
    """Stereographic projection from the north pole, inverse of `to_sphere`."""
    return (points[:, 0] + 1j * points[:, 1]) / (1 - points[:, 2])


NORTH = np.array([[0.0, 0.0, 1.0]])


def roots_on_sphere(coeffs, with_infinity=False):
    points = to_sphere(np.roots(coeffs))
    return np.vstack([points, NORTH]) if with_infinity else points
