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
geometry contract and an eight-solid corpus are in place ([notes](notes/2026-09-30-geometry-contract.md)).
Next: divisors and stable evaluation, then a comparison of the uniform (R1), incidence-based (R2)
and edge-incidence (R4) recipes. The audit shows that on Platonic solids R1 and R2 coincide
with each other and with the baseline "dual" pieces, and R4 reproduces the baseline crowns and
star, so the recipes can only be told apart on less regular inputs. A public narrative
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
