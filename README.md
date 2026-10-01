# Polyhedra as Complex Functions

How can a convex polyhedron be encoded in a rational function on the Riemann sphere so that
its geometry and combinatorics stay recognizable in the function and its pictures?

This repository compares recipes for placing zeros and poles on the sphere, using a polyhedron's
vertices, its polar dual and their incidences. It checks what each recipe preserves
(symmetry, duality, rotation consistency) and what it costs (degree, numerical conditioning,
lost information). The functions are explored with
[complexplorer](https://github.com/kuvychko/complexplorer) through domain coloring and radial
relief, and selected results will become 3D-printable objects.

The full research program, scope and exit criteria are in [`PROGRAM.md`](PROGRAM.md).

## Status

**Phase 1: investigation, pre-release.** The existing Klein-invariant ornaments are
preserved and reproduced as baseline R0 ([audit](notes/2026-09-30-baseline-audit.md)). The
geometry contract and an eleven-solid corpus are in place ([notes](notes/2026-09-30-geometry-contract.md)).
Divisors, stable evaluation and an exact normalization are in place, and the baseline pieces are
confirmed to be instances of the recipes. Recipes R1, R2 and the edge-incidence family R4, with
diagnostics for local orders, duality, symmetry and rotation, are implemented and checked across
the corpus ([notes](notes/2026-10-01-recipes-and-diagnostics.md)). The first comparison atlas
([E001](experiments/E001-atlas/README.md)) covers 11 solids × 5 recipes. Next: controlled experiments
on deformation, combinatorial transitions and display. Early findings ([notes](notes/2026-10-01-recipe-separation.md)):
once the degree is divided out, R1 and R2 differ only by valence weighting, and R2 and the two R4
variants form a single multiplicative family, `f_R2 = f_R4ve / f_R4fe`. A public narrative
and exhibition site will follow in Phase 2.

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
```

## Repository layout

| path | contents |
|---|---|
| `src/polyhedral_functions/` | the Python package: geometry, recipes, divisors, evaluation |
| `data/polyhedra/` | small geometry fixtures, each with its source |
| `configs/` | recipe presets and experiment definitions |
| `experiments/` | experiment index, run manifests, selected diagnostic outputs |
| `notes/` | dated observations, derivations and negative results |
| `docs/decisions/` | why conventions and recipes were chosen or rejected |
| `docs/research/` | the curated exploration narrative |

## License

Code is released under the [MIT License](LICENSE). Documentation, images, meshes and other
non-code content are released under [CC BY 4.0](LICENSE-media).
