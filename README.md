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

**Phase 1: investigation, pre-release.** There are no findings yet. The first milestones are:
audit and preserve the existing Klein-invariant ornaments as a baseline, implement the geometry
contract, then compare the uniform (R1) and incidence-based (R2) recipes. A public narrative
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
