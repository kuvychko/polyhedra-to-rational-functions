# Polyhedra as Complex Functions

**Riemann relief maps** turn complex functions into objects you can hold: poles become spikes,
and zeros become pits. This project makes the functions from convex polyhedra.

![The printed collection: thirteen white and pale blue PLA prints of the eleven designs, some at two sizes](docs/assets/photos/collection.jpg)

- **Site:** <https://kuvychko.github.io/polyhedra-to-rational-functions/>: the objects, a
  gentle introduction, the research narrative and an interactive recipe comparison.
- **Print files:** every printed design is on Printables, gathered in one
  [collection](https://www.printables.com/@Igor_2829688/collections/3812430) and linked from its
  page on the site.

## The question

How can a convex polyhedron be encoded in a rational function on the Riemann sphere so that
its geometry and combinatorics stay recognizable in the function and its pictures?

This repository compares recipes for placing zeros and poles on the sphere, using a polyhedron's
vertices, its polar dual and their incidences. It checks what each recipe preserves
(symmetry, duality, rotation consistency) and what it costs (degree, numerical conditioning,
lost information). The functions are explored with
[complexplorer](https://github.com/kuvychko/complexplorer) through domain coloring and radial
relief.

The full research program, scope and exit criteria are in [`PROGRAM.md`](PROGRAM.md).

## Status

- **Phase 1 (investigation) is complete:** every exit criterion in [`PROGRAM.md`](PROGRAM.md)
  §13 is met.
- **Phase 2 (explanation and exhibition, [`PHASE2.md`](PHASE2.md)):** the site is live and the
  exhibition is printed. Eleven designs are printed, thirteen prints in all, since some designs
  were printed at two sizes. A twelfth design, the hexagonal pyramid, is planned.

Current findings ([decision 0005](docs/decisions/0005-phase1-recipe-selection.md),
[narrative draft](docs/research/narrative.md)):

- **Default recipe, R2:** zeros at vertex directions with order equal to the valence, and poles at
  the polar face directions with order equal to the number of sides. It has exact reciprocal
  duality, a relief as symmetric as the solid, and the lowest degree on most tested solids.
- **Alternative, R4:** vertices or faces against edges. In the tested transitions it is the only
  recipe that stays continuous, under the transition matching its pairing (for R4ve, any vertex
  truncation). It reproduces the existing crown and star ornaments.
- **An exact family:** for unreduced divisors, `f_R2 = C · f_R4ve / f_R4fe`. The existing
  Klein-invariant ornaments are all outputs of these recipes on Platonic solids.
- **An exact normalization:** `log|f| = Σ m log χ` (chordal distance). It is self-dual and has
  geometric mean 1, with no sampling.

How the reliefs relate to stellated solids (shared tip directions on the octahedron; the cube has
no stellation at all) is on the site's [stellation page](docs/research/stellation.md).

The evidence is in [`experiments/`](experiments/README.md): the comparison atlas (E001),
transitions (E002), deformation and placement (E003) and display (E004).

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
