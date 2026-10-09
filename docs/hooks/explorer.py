"""Generate the interactive pages' data at build time.

- ``assets/explorer/recipes.json`` (``research/compare.md``): every fixture under every preset
  recipe (`polyhedral_functions.viewer_data.explorer_data`).
- ``assets/explorer/primer.json`` (``research/primer.md``): the introduction's functions
  (`viewer_data.primer_data`), plus the display settings the page draws them with: the site's
  phase palette, sampled from complexplorer, and the relief transfer's depth and order-tuned
  sharpness (`rendering.DisplaySettings`).

Applying a recipe takes milliseconds, so the data is computed from the package on every build
rather than committed: it cannot go stale.
"""

from __future__ import annotations

import json
import logging

import complexplorer as cp
import numpy as np

from polyhedral_functions import viewer_data
from polyhedral_functions.manifests import REPO_ROOT
from polyhedral_functions.rendering import DisplaySettings

log = logging.getLogger("mkdocs.hooks.explorer")

PATH = "assets/explorer/recipes.json"
PRIMER_PATH = "assets/explorer/primer.json"
SITE_CONFIG = REPO_ROOT / "configs" / "site" / "piece-assets.json"
PALETTE_SIZE = 256


def phase_palette(phase_sectors: int) -> list[list[int]]:
    """The renders' phase colors at ``PALETTE_SIZE`` equal steps of ``arg f`` from ``-pi``, as
    0-255 RGB. Entry ``k`` is the color at the middle of step ``k``."""
    theta = -np.pi + 2 * np.pi * (np.arange(PALETTE_SIZE) + 0.5) / PALETTE_SIZE
    cmap = cp.OklabPhase(phase_sectors=phase_sectors, auto_scale_r=True)
    rgb = cmap.rgb(np.exp(1j * theta))
    return np.clip(np.round(rgb * 255), 0, 255).astype(int).tolist()


def primer_json() -> dict:
    data = viewer_data.primer_data()
    config = json.loads(SITE_CONFIG.read_text(encoding="utf-8"))
    base = DisplaySettings()
    for entry in data["functions"].values():
        # The order-tuned display (decision 0005): every example gets the same tip exponent, so
        # an order-1 pole is as visible as the cube's order-4 ones.
        divisor = viewer_data.unreduced_from_markers(entry)
        entry["sharpness"] = base.tuned_for(divisor).sharpness
    data["display"] = {
        "depth": base.depth,
        "plane_half_width": config["plane_half_width"],
        "palette": phase_palette(config["phase_sectors"]),
    }
    return data


def on_files(files, config):
    # Imported here, not at the top: the tests call primer_json() without the docs dependencies.
    from mkdocs.structure.files import File

    data = viewer_data.explorer_data()
    content = json.dumps(data, separators=(",", ":")) + "\n"
    files.append(File.generated(config, PATH, content=content))
    log.info(
        "explorer: %d solids x %d recipes -> %s", len(data["solids"]), len(data["recipes"]), PATH
    )
    primer = primer_json()
    content = json.dumps(primer, separators=(",", ":")) + "\n"
    files.append(File.generated(config, PRIMER_PATH, content=content))
    log.info("explorer: %d introduction functions -> %s", len(primer["functions"]), PRIMER_PATH)
    return files
