"""Alignment dowel holes in the cut faces (decision 0009).

Every cut plane passes through the relief's centre. One cylinder along the plane normal, centred
there, is bored into the whole solid before it is split. Each half then gets a blind hole in the
middle of its cut face, and the two line up by construction when glued. Holes are 5.2 mm across,
for M5 dowel pins, and as deep as half the pin plus 1 mm of slack for glue (`PINS`):

- 130 mm prints: a 20 mm pin, 11 mm deep each side;
- 80 mm prints: a 10 mm pin, 6 mm deep each side.

If the preferred pin does not fit, the shorter one is used, and the choice is recorded.

Checks, all recorded in ``catalog/exports.json``:

- **Floor:** the solid continues at least `MIN_FLOOR_MM` beyond each hole's bottom, measured
  along the axis. If it does not, both depths shrink to fit.
- **Pin:** the two depths together hold the pin plus `PIN_SLACK_MM`. Otherwise the export fails.
- **Side walls:** a cylinder `MIN_SIDE_MM` wider than the hole, over the hole's length plus the
  floor, lies inside the solid (``manifold3d`` intersection).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import manifold3d as mf
import numpy as np
import pyvista as pv

from . import hangers

PIN_DIAMETER_MM = 5.00  # M5 dowel pins, measured
# The modelled hole is 0.2 mm larger than the pin. Printed holes come out undersized, and with the
# owner's material and print settings a 5.2 mm hole gives a light friction fit on a 5.00 mm pin
# (tested 2026-10-03). Other printers may need a different value.
DIAMETER_MM = 5.2
# pin length (mm) -> hole depth on each side (mm): half the pin plus 1 mm slack.
PINS = {20.0: 11.0, 10.0: 6.0}
# print size (mm) -> preferred pin length (mm); the owner has M5 x 20 and M5 x 10 pins.
PREFERRED_PIN = {130: 20.0, 80: 10.0}
PIN_SLACK_MM = 0.5  # the two holes together must exceed the pin by at least this
MIN_FLOOR_MM = 1.2
MIN_SIDE_MM = 1.5
INSIDE_FRACTION = 0.999  # of the side-wall envelope; the remainder allows for faceting


@dataclass
class Dowel:
    diameter_mm: float
    depth_each_side_mm: float
    floor_plus_mm: float
    floor_minus_mm: float
    side_wall_mm: float
    pin: str

    def record(self) -> dict:
        return asdict(self)


def fits(mesh_mm, solid, n, pin_mm, reach_plus, reach_minus) -> float | None:
    """The hole depth for this pin if it fits with floor and side walls, else None."""
    depth = min(PINS[pin_mm], reach_plus - MIN_FLOOR_MM, reach_minus - MIN_FLOOR_MM)
    if 2 * depth < pin_mm + PIN_SLACK_MM:
        return None
    reach = depth + MIN_FLOOR_MM
    envelope = hangers.axis_cylinder(n, DIAMETER_MM / 2 + MIN_SIDE_MM, -reach, reach)
    if (envelope ^ solid).volume() < INSIDE_FRACTION * envelope.volume():
        return None
    return depth


def plan(mesh_mm: pv.PolyData, normal, size_mm: int) -> Dowel:
    """The dowel for a print of ``size_mm``: the preferred pin if it fits, else a shorter one."""
    n = np.asarray(normal, dtype=float) / np.linalg.norm(normal)
    reach_plus = hangers.radius_along(mesh_mm, n)
    reach_minus = hangers.radius_along(mesh_mm, -n)
    solid = hangers.to_manifold(mesh_mm)
    preferred = PREFERRED_PIN[int(size_mm)]
    for pin in sorted((p for p in PINS if p <= preferred), reverse=True):
        depth = fits(mesh_mm, solid, n, pin, reach_plus, reach_minus)
        if depth is not None:
            return Dowel(
                diameter_mm=DIAMETER_MM,
                depth_each_side_mm=round(depth, 2),
                floor_plus_mm=round(reach_plus - depth, 2),
                floor_minus_mm=round(reach_minus - depth, 2),
                side_wall_mm=MIN_SIDE_MM,
                pin=f"M5 x {pin:g} dowel pin" + ("" if pin == preferred else " (fallback)"),
            )
    raise RuntimeError(f"no dowel pin fits a {size_mm} mm print along this cut")


def bore(solid: mf.Manifold, dowel: Dowel, normal) -> mf.Manifold:
    d = dowel.depth_each_side_mm
    return solid - hangers.axis_cylinder(normal, dowel.diameter_mm / 2, -d, d)
