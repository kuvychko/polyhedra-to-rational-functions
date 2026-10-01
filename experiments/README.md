# Experiments

An index of experiments plus their run manifests and small, selected outputs. Large and
regenerable outputs (full-resolution renders, meshes, frames) are written to `out/`, which is
not committed.

A manifest records the fields listed in `PROGRAM.md` §11: ID, question, changed factor,
geometry, recipe, normalization, evaluation settings, code commit and dirty-tree status,
dependency versions, display settings, outputs, and conclusion.

| ID | question | status |
|---|---|---|
| [R0-baseline](R0-baseline/README.md) | what do the existing Klein-invariant ornaments compute, and do they reproduce here? | reference, complete |
| [E001-atlas](E001-atlas/README.md) | how do R1, R2, R4 and flag differ across the corpus (degree, duality, symmetry, field shape)? | complete |
| [E002-transitions](E002-transitions/README.md) | which recipes are continuous when a small face or short edge vanishes? | complete |
| [E003-deformation](E003-deformation/README.md) | how do recipes and placements behave under fixed-combinatorics deformation; when does a feature leave its cell? | complete |
| [E004-display](E004-display/README.md) | how much of the visible difference between recipes is the display? | complete |
