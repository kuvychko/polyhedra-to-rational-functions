# 0001: Public-ready repository conventions

Date: 2026-09-30. Status: accepted.

## Context

`PROGRAM.md` v2.0 assumed Phase 1 would run in a private repository, with a later choice
between publishing the reviewed repository and extracting a clean public subset. The owner
chose instead to develop in a repository that starts private but is treated as public from its
first commit.

## Decisions

1. **Public-ready from day one.** No commit should need scrubbing before release. Releasing
   means flipping visibility, and that flip stays an explicit owner action. `PROGRAM.md` was
   revised to v2.1 to match. The operating rules are in `CLAUDE.md`.
2. **Licenses.** Code is MIT (`LICENSE`). Documentation, prose, images, meshes and other
   non-code content are CC BY 4.0 (`LICENSE-media`). This deliberately differs from
   complexplorer's artwork license (CC BY-NC 4.0): here, derived prints and images may be
   used commercially, with attribution.
3. **Existing generator.** Only the polyhedral subset of the riemann-ornaments generator
   (figures_repo @ 292bec4, `2026/09-20-riemann-ornaments/`) will be brought in. That subset is
   the Klein forms, the normalization, the six polyhedral presets and their checks. It will be a
   frozen baseline with a provenance header, relicensed under this repository's licenses by
   its author. The non-polyhedral pieces, meshes, slicer projects and gcode stay out.
4. **Site stack.** The Phase 2 site uses MkDocs Material, matching complexplorer: strict builds,
   MathJax math, rendered (not executed) notebooks, deployment via `mkdocs gh-deploy` from a
   manual or tag-triggered workflow. The site source lives under `docs/`, and the built output
   (`site/`) is not committed. That differs from the `site/` source directory proposed in
   `PROGRAM.md` §10.
5. **No OpenSpec.** complexplorer manages library changes with OpenSpec. Here, experiment
   manifests, `notes/` and these decision records fill that role, and a parallel spec system
   would duplicate them.

## Reopen if

- An asset needs a license other than MIT or CC BY 4.0 (for example, third-party photos).
- The narrative needs executable cross-referenced documents that MkDocs cannot support. In
  that case, reconsider Quarto.
