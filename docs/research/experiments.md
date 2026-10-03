# Experiments

Each experiment changes one controlled factor. Each records its configuration, code commit,
package versions and output hashes in a manifest under `experiments/<id>/`, and can be rerun
from the repository with one command. The figures below are the published evidence.

## E001: the comparison atlas

Eleven solids and five recipes, under one fixed display. Every recipe passes the exact checks:

- local orders;
- duality;
- symmetry of the relief;
- rotation.

What differs is degree, the shape of the field, and readability.

![Atlas sheet for the deltoidal icositetrahedron: each recipe as geometry, plane portrait, sphere, colored relief, neutral relief and per-degree map](../experiments/E001-atlas/sheets/deltoidal-icositetrahedron-recipes.jpg)

*The deltoidal icositetrahedron. R1 and R2 have nearly identical per-degree maps (right). The R1
relief looks rounded only because its local orders are higher under the same display.*

## E002: when a face or edge shrinks to nothing

Three transitions were tested on the cube: a corner cut away, an edge bevelled, and a flat
pyramid raised on a face.

- **R4ve** is continuous as a corner truncation vanishes, and **R4fe** as a raised face
  flattens. Both converge as the square of the feature size.
- The other recipes **jump** to a different limit. The jumps were tested on the cube; for vertex
  truncation, R2's jump is derived in general.

![Convergence of each recipe as the new feature shrinks, for the three transitions](../experiments/E002-transitions/transitions.jpg)

## E003: deformation and placement

The pyramid's height varies, and so does a box's shear, with the combinatorics fixed throughout.

- Every recipe changes continuously.
- On the sheared box, the polar placement puts a face's pole **outside its own face** from shear
  1 onwards. A centroid placement never leaves the face, but it breaks exact duality.

![Continuity, separation and placement curves against pyramid height and box shear](../experiments/E003-deformation/deformation.jpg)

## E004: what the display does

The same functions are shown under three relief displays. Most of the visible difference between
R1 and R2 is display: tuning the sharpness to each recipe's highest order largely removes it. The
difference between R2 and R4 remains under every display.

![Neutral reliefs of R1, R2 and R4ve on the deltoidal icositetrahedron under three displays](../experiments/E004-display/reliefs-deltoidal-icositetrahedron.jpg)

## For printing: P001 and P002

These two runs screen the catalog for printability. **P001** measures waist, volume and the
closest feature gaps at 80 and 130 mm. **P002** proposes cut planes for two-part prints.

![Printability screen of every catalog piece](../experiments/P001-print-screen/screen.jpg)
