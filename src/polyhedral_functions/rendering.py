"""Diagnostic renders: thin adapters from a divisor to complexplorer, pyvista and matplotlib.

Every view consumes the same mathematical object, a `Divisor`, through `evaluation.as_function`.
The rendering never changes the function: display choices live in `DisplaySettings` and are
recorded in run manifests. Views:

- `render_geometry`: the polyhedron with its zero and pole directions marked;
- `plane_portrait`: domain coloring in the chart (complexplorer `plot`);
- `render_relief`: colored or neutral radial relief, or the plain colored sphere (complexplorer
  `OrnamentGenerator`, ``normalize=None``, because the chordal convention already sets sea level);
- `log_modulus_map` / `difference_map`: equirectangular maps of ``log|f| / degree``, which compare
  recipes by shape whatever their degree.

Nothing in the mathematical modules imports this one.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import complexplorer as cp
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
from complexplorer.export.stl import OrnamentGenerator

from .divisors import Divisor
from .evaluation import as_function, log_modulus_on_sphere
from .geometry import Polyhedron

ZERO_COLOR = "#2b6cb0"
POLE_COLOR = "#c53030"


@dataclass(frozen=True)
class DisplaySettings:
    """Rendering choices, kept separate from the mathematics and recorded with every run.

    ``sharpness`` is the relief transfer's log-modulus scale ``k`` in
    ``r = r_min + (r_max - r_min) logistic(log|f| / k)``. A single fixed value across a
    comparison keeps it a *fixed-display* comparison. Near a feature of order ``mu`` the tip
    exponent is then ``mu / k``, so high-order recipes come out blunter, which is a true property
    of the function under that display.
    """

    relief_resolution: int = 160
    depth: float = 0.2
    sharpness: float = 4.0
    phase_sectors: int = 12
    plane_half_width: float = 2.5
    plane_resolution: int = 300
    map_resolution: int = 180
    map_limit: float = 0.75
    window: int = 600

    def config(self) -> dict:
        return asdict(self)


def phase_cmap(settings: DisplaySettings):
    """The baseline renders' palette (OkLab phase), kept for continuity."""
    return cp.OklabPhase(phase_sectors=settings.phase_sectors, auto_scale_r=True)


def _camera(plotter: pv.Plotter, view) -> None:
    direction = np.asarray(view, dtype=float)
    direction = direction / np.linalg.norm(direction)
    plotter.camera.position = tuple(direction * 4.0)
    plotter.camera.focal_point = (0.0, 0.0, 0.0)
    plotter.camera.up = (0.0, 0.0, 1.0) if abs(direction[2]) < 0.99 else (0.0, 1.0, 0.0)
    plotter.reset_camera()
    plotter.camera.zoom(1.2)


def render_geometry(
    poly: Polyhedron, divisor: Divisor, path: Path, view, settings: DisplaySettings
) -> Path:
    """The solid, scaled to circumradius 1, with zeros (blue) and poles (red) on the sphere.

    Marker area grows with order, and markers sit slightly outside the unit sphere so they stay
    visible.
    """
    faces = np.concatenate([[len(f), *f] for f in poly.faces])
    mesh = pv.PolyData(poly.vertices / poly.scale, faces)
    pl = pv.Plotter(off_screen=True, window_size=(settings.window, settings.window))
    pl.set_background("white")
    pl.add_mesh(mesh, color="#d9d4c7", opacity=0.55, show_edges=True, edge_color="#4a4a4a")
    pl.add_mesh(
        pv.Sphere(radius=1.0, theta_resolution=48, phi_resolution=48), color="white", opacity=0.12
    )
    top = max(abs(int(divisor.orders.max())), abs(int(divisor.orders.min())), 1)
    for point, order in zip(divisor.points, divisor.orders, strict=True):
        radius = 0.035 + 0.035 * np.sqrt(abs(order) / top)
        pl.add_mesh(
            pv.Sphere(radius=radius, center=1.04 * point),
            color=ZERO_COLOR if order > 0 else POLE_COLOR,
            smooth_shading=True,
        )
    _camera(pl, view)
    path.parent.mkdir(parents=True, exist_ok=True)
    pl.screenshot(str(path))
    pl.close()
    return path


def render_relief(
    divisor: Divisor,
    path: Path,
    view,
    settings: DisplaySettings,
    style: str = "colored",
) -> Path:
    """Radial relief of ``|f|`` (``style`` ``colored`` or ``neutral``), or the unit sphere
    colored by phase (``style="sphere"``)."""
    if style == "sphere":
        gen = OrnamentGenerator(
            as_function(divisor),
            resolution=settings.relief_resolution,
            cmap=phase_cmap(settings),
            normalize=None,
            scaling="constant",
            scaling_params={"radius": 1.0},
        )
    else:
        gen = OrnamentGenerator(
            as_function(divisor),
            resolution=settings.relief_resolution,
            cmap=phase_cmap(settings),
            normalize=None,
            sharpness=settings.sharpness,
            scaling_params={"r_min": settings.depth, "r_max": 1.0},
        )
    mesh = gen.generate_ornament(verbose=False)
    pl = pv.Plotter(off_screen=True, window_size=(settings.window, settings.window))
    pl.set_background("white")
    if style == "neutral":
        pl.add_mesh(mesh, color="#e8e4da", smooth_shading=True, specular=0.3, diffuse=0.85)
    else:
        pl.add_mesh(
            mesh,
            scalars="RGB",
            rgb=True,
            smooth_shading=True,
            specular=0.3,
            diffuse=0.85,
            ambient=0.25,
        )
    _camera(pl, view)
    path.parent.mkdir(parents=True, exist_ok=True)
    pl.screenshot(str(path))
    pl.close()
    return path


def plane_portrait(divisor: Divisor, ax, settings: DisplaySettings) -> None:
    """Domain coloring of ``f`` on ``|Re z|, |Im z| <= plane_half_width``."""
    half = settings.plane_half_width
    cp.plot(
        cp.Rectangle(2 * half, 2 * half),
        as_function(divisor),
        resolution=settings.plane_resolution,
        cmap=phase_cmap(settings),
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(labelsize=6)


def _lat_long(resolution: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lon = np.linspace(-np.pi, np.pi, 2 * resolution, endpoint=False) + np.pi / (2 * resolution)
    lat = np.linspace(-np.pi / 2, np.pi / 2, resolution, endpoint=False) + np.pi / (2 * resolution)
    LON, LAT = np.meshgrid(lon, lat)
    x = np.stack([np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)], axis=-1)
    return x.reshape(-1, 3), lon, lat


def per_degree_field(divisor: Divisor, resolution: int) -> np.ndarray:
    """``log|f| / degree`` on an equirectangular grid (rows: latitude from south to north)."""
    x, lon, lat = _lat_long(resolution)
    return (log_modulus_on_sphere(divisor, x) / max(divisor.degree, 1)).reshape(len(lat), len(lon))


def _mark(ax, divisor: Divisor) -> None:
    lon = np.degrees(np.arctan2(divisor.points[:, 1], divisor.points[:, 0]))
    lat = np.degrees(np.arcsin(np.clip(divisor.points[:, 2], -1, 1)))
    pos = divisor.orders > 0
    ax.scatter(
        lon[pos],
        lat[pos],
        s=10,
        marker="o",
        facecolors="none",
        edgecolors=ZERO_COLOR,
        linewidths=0.8,
    )
    ax.scatter(lon[~pos], lat[~pos], s=10, marker="x", color=POLE_COLOR, linewidths=0.8)


def _map_axes(ax) -> None:
    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.set_yticks([-90, 0, 90])
    ax.tick_params(labelsize=6)


def log_modulus_map(divisor: Divisor, ax, settings: DisplaySettings):
    """``log|f| / degree`` with zeros (o) and poles (x). Fixed symmetric color limits."""
    field = per_degree_field(divisor, settings.map_resolution)
    lim = settings.map_limit
    image = ax.imshow(
        field,
        origin="lower",
        extent=[-180, 180, -90, 90],
        cmap="RdBu_r",
        vmin=-lim,
        vmax=lim,
        aspect="auto",
        interpolation="nearest",
    )
    _mark(ax, divisor)
    _map_axes(ax)
    return image


def difference_map(d1: Divisor, d2: Divisor, ax, settings: DisplaySettings, limit: float = 0.5):
    """``log|f1|/deg1 - log|f2|/deg2``: where two recipes differ in shape."""
    a = per_degree_field(d1, settings.map_resolution)
    b = per_degree_field(d2, settings.map_resolution)
    image = ax.imshow(
        a - b,
        origin="lower",
        extent=[-180, 180, -90, 90],
        cmap="PuOr_r",
        vmin=-limit,
        vmax=limit,
        aspect="auto",
        interpolation="nearest",
    )
    _mark(ax, d1)
    _map_axes(ax)
    return image


def show_image(ax, path: Path, title: str | None = None) -> None:
    ax.imshow(plt.imread(str(path)))
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=7)
