"""R0: the existing Klein-invariant ornaments, frozen as a baseline.

Provenance
----------
Copied from the author's ``figures_repo`` at commit
``292bec4cdb5c52aa08ec777773fe2e4d367d6307`` (2026-09-30), folder
``2026/09-20-riemann-ornaments/``, and relicensed under this repository's licenses by
their author:

- `forms` -- the Klein forms, from ``ornaments.py``;
- `ornaments` -- the six polyhedral presets, normalization and relief settings, from
  ``ornaments.py``;
- `meshtools` -- closing and measuring the relief mesh, from ``meshtools.py``.

The checks from that folder's ``verify_math.py`` that concern these pieces are ported
to ``tests/baseline/``. The regression reference (the source's manifest and renders) is
in ``experiments/R0-baseline/``. The audit of what this code does, and how it relates to
the recipes under investigation, is ``notes/2026-09-30-baseline-audit.md``.

Rules
-----
This package is **frozen**: edit it only to keep it importable. New work goes in new
modules and compares against it. Results built on it are only comparable under the
pinned complexplorer 3.1.0, whose relief transfer, sampling and defaults it relies on.
"""
