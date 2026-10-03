"""Serve the experiment figures that live outside ``docs/``, without copying them into it.

The figures are produced by the experiment scripts and published to ``experiments/<id>/``
(``manifests.publish_evidence``). MkDocs only serves what is inside ``docs_dir``, so this hook
adds them to the build under their repository paths. Pages link to them as
``../../experiments/<id>/<file>``.

Registering real files keeps ``--strict`` useful: a link to a figure that doesn't exist still
fails the build. Nothing is written into the working tree. Adapted from complexplorer's hook of
the same name.
"""

from __future__ import annotations

import logging
from pathlib import Path

from mkdocs.structure.files import File

log = logging.getLogger("mkdocs.hooks.site_assets")

REPO_ROOT = Path(__file__).resolve().parents[2]

# (source directory relative to the repo, glob) pairs added to the site.
ASSET_SOURCES = [
    ("experiments", "**/*.jpg"),
    ("experiments", "**/*.png"),
]


def on_files(files, config):
    added = 0
    for relative_dir, pattern in ASSET_SOURCES:
        source_dir = REPO_ROOT / relative_dir
        for source in sorted(source_dir.glob(pattern)):
            files.append(
                File(
                    path=source.relative_to(REPO_ROOT).as_posix(),
                    src_dir=str(REPO_ROOT),
                    dest_dir=str(config["site_dir"]),
                    use_directory_urls=False,
                )
            )
            added += 1
    if not added:
        # A silent zero would mean every figure on the site is broken.
        raise RuntimeError("site_assets added no files; experiments/ has no published figures")
    log.info("site_assets: added %d experiment figure(s)", added)
    return files
