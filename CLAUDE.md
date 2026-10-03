# CLAUDE.md

Guidance for Claude Code (and human contributors) working in this repository.

## Purpose and status

**Polyhedra as Complex Functions**: develop, compare and explain recipes that turn a convex
polyhedron into a rational function on the Riemann sphere, study the results with
[complexplorer](https://github.com/kuvychko/complexplorer) (domain coloring, radial relief), and
eventually turn selected results into printed objects and a public exhibition.

`PROGRAM.md` is the source of truth for scope, phases, criteria and exit conditions. Read the
relevant section before starting a milestone. Current status: **Phase 1 (investigation)**.
Phase 2 (narrative + exhibition site) starts only once a recipe is understood well enough to
explain. Decisions that change conventions go in `docs/decisions/`.

## Public from day one

The repository is private for now but is kept **public-ready at every commit**. Releasing it
means flipping visibility; there is no scrub step. So:

- No absolute local paths, usernames, machine names or drive letters in committed files. Refer
  to other repos by name and commit (e.g. "figures_repo @ 292bec4"), not by local path.
- Bring in code from the owner's other repos only as explicitly approved (currently: the
  polyhedral subset of the riemann-ornaments generator, as a frozen baseline with a provenance
  header). Never copy unrelated private work.
- No credentials, tokens or personal data beyond the author attribution already in
  `pyproject.toml` / `LICENSE`.
- No large or regenerable binaries: STL, 3MF, gcode, animation frames and bulk renders are
  gitignored. Commit only small, selected evidence (downscaled PNGs, manifests, JSON/CSV
  summaries).
- Every committed file falls under a declared license: code is MIT (`LICENSE`); media, meshes,
  documentation and prose are CC BY 4.0 (`LICENSE-media`). Third-party data (e.g. polyhedron
  coordinates) needs a recorded source and compatible terms.
- Never change repository visibility, enable/deploy GitHub Pages, push tags or publish to
  Printables without an explicit request at that time.
- Write notes and docs for an outside reader: no "as discussed" references to conversations.

## Mathematical conventions

- **Chart**: complexplorer's stereographic projection. `z = 0` is the **south** pole,
  `z = ∞` the **north** pole, `|z| = 1` the equator. Distinguish rotating the object from
  changing the chart.
- **Divisor first**: a recipe produces signed points on the sphere with **integer**
  multiplicities; the rational function is determined up to a nonzero constant. Total zero and
  pole orders balance across the whole sphere, including `∞`. Cancellation of coincident points
  is explicit and reported; nearby distinct points are never silently merged.
- **Unreduced by convention**: a recipe is its unreduced divisor. gcd reduction is a separate,
  reported, per-solid step. Identities, duality and transition comparisons use unreduced
  divisors (`RecipeResult.unreduced`).
- **Say which symmetry**: a preserved divisor means a symmetric relief `|f|`. The function itself
  may pick up a phase character `e^{iθ_g}`. Never write "full symmetry" without saying which
  is meant.
- **Polarity**: for a face plane `n · x = h` (unit outward `n`, `h > 0`), the unit-sphere polar
  dual vertex is `n / h` and its spherical direction is `n`. Projected face centroids are a
  separate candidate point set. Use the same origin for a polyhedron and its dual.
- **Faces stay polygonal**: render-only triangulation must never change valences, face sizes or
  multiplicities.
- **Default normalization** (decision 0003): `log|f| = Σ m log χ`, with χ the chordal
  distance. It is self-dual, rotation-covariant, of geometric mean 1, and never sampled. Phase
  is the chart's, with `C > 0`. Never fit constants by sampling; use sphere quadrature only to
  check.
- **Keep independent knobs independent**: magnitude normalization, phase convention, display
  compression (e.g. `|f|^(1/d)`) and radial transfer function are separately configured and
  separately recorded. A display mapping is not a change of recipe.
- **Label claims** as established background, derived result, numerical observation,
  conjecture, or design preference. A finding from the corpus is "in the tested examples" unless
  it is derived; name the transition classes or solids it covers. No novelty claims without a targeted literature review.
- "Klein duals" is a historical label for existing assets only. Attribute to Klein only
  classical constructions whose formulas and attribution have been checked.

Inherited from the baseline ornaments (verify before relying on them): the relief uses
complexplorer's logistic `logarithmic` / `log_mixture` transfer with sea level at `|f| = 1`;
tip sharpness is governed by the exponent `μ/k`; sizes are measured tip to tip; the
sphere-wide geometric mean normalization is self-dual.

## Architecture

Python package `polyhedral_functions` under `src/`. Layout and responsibilities follow
`PROGRAM.md` §10; modules are added when a milestone needs them, not in advance.

- Geometry, recipes, divisors, evaluation and normalization must **not** import plotting,
  rendering or site code. Renderers consume the same mathematical result.
- Reusable logic lives in `src/`; notebooks explore and interpret only.
- The frozen baseline (R0) lives in `src/polyhedral_functions/baseline/` and is not
  edited except to fix imports; new work goes in new modules and compares against it.
- Configuration is JSON/YAML under `configs/`; no databases or services.

## Experiment discipline

- Every experiment has a stable ID, a question or hypothesis, and **one** controlled factor.
- Keep fixed-display comparisons separate from individually tuned views, and label the latter.
- Run manifests record what `PROGRAM.md` §11 lists, including code commit and dirty-tree status,
  and a snapshot of the configuration used (`manifests.py`). Commit code *before* a run that will
  be published, so the manifest records a clean tree; then commit the published evidence.
- Checks before aesthetics: balance, local orders, rotation and duality residuals, numerical
  behavior near singularities and `∞`.
- Negative results and dead ends are recorded in `notes/` (dated files), not deleted.

## Commands

```bash
uv sync                                         # environment from uv.lock
uv run pytest                                   # tests (includes the baseline checks)
uv run pytest -m "not slow"                     # skip full mesh rebuilds
uv run python scripts/make_fixtures.py          # rewrite data/polyhedra/ after changing a construction
uv run python scripts/make_atlas.py --publish   # E001 atlas -> out/E001-atlas/, evidence -> experiments/
uv run python scripts/e00N_*.py --publish       # E002-E004; commit each one's evidence before the next run
uv run python scripts/catalog_status.py         # validate catalog/pieces.yaml, regenerate CHECKLIST.md
uv run python scripts/p001_print_screen.py      # printability screen of catalog pieces (80/130 mm)
uv run python scripts/p002_cut_proposals.py     # cut-plane proposals for owner approval
uv run python scripts/b2_export_stls.py         # whole + approved cut STLs -> out/stls/, hashes -> catalog/exports.json
uv run python scripts/a4_site_assets.py         # precompute each piece's five views -> docs/assets/pieces/ (commit code first)
uv run --group docs mkdocs serve                # the site (strict build in CI); object pages come from the catalog
uv run ruff check . && uv run ruff format --check .
```

Before any commit, run `pytest` on its own and check its exit status. Don't pipe it into
`tail` in an `&&` chain without `set -o pipefail`, which hides failures. After any edit to
`catalog/pieces.yaml`, regenerate `CHECKLIST.md`; a test enforces it.

## Style

Mirror complexplorer: PEP 8, type hints, numpy-style docstrings with the math written out,
descriptive names that follow the mathematics. ruff is pinned to `>=0.16.7,<0.17`; upgrading it
is a deliberate commit. Comments explain *why* (conventions, traps, derivations), not what.
Commit messages are imperative and scoped (e.g. `geometry: validate face orientation`).
