"""Generate the recipe comparison data at build time (``research/compare.md``).

``assets/explorer/recipes.json`` holds every fixture under every preset recipe
(`polyhedral_functions.viewer_data.explorer_data`). Applying a recipe takes milliseconds, so the
data is computed from the package on every build rather than committed: it cannot go stale.
"""

from __future__ import annotations

import json
import logging

from mkdocs.structure.files import File

from polyhedral_functions import viewer_data

log = logging.getLogger("mkdocs.hooks.explorer")

PATH = "assets/explorer/recipes.json"


def on_files(files, config):
    data = viewer_data.explorer_data()
    content = json.dumps(data, separators=(",", ":")) + "\n"
    files.append(File.generated(config, PATH, content=content))
    log.info(
        "explorer: %d solids x %d recipes -> %s", len(data["solids"]), len(data["recipes"]), PATH
    )
    return files
