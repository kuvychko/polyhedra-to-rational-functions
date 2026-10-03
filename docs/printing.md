# Printing

Every object is a solid that is star-shaped about its centre: each ray from the centre crosses
the surface once. There are no thin walls. The fine geometry is all in the tips.

## Sizes

Each object comes in two sizes, **80 mm** and **130 mm**, measured **tip to tip**: the object's
true maximum width, not a bounding-box side. Objects with few, broad features gain little from
the larger size.

## Cut halves

Spiky objects print best in two halves, each lying on its flat cut face. Every object's files
include cut halves alongside the whole model.

- The cut plane passes through the centre and was chosen for each object.
- Where a symmetry swaps the two sides, the halves are **identical**: print the half file twice.
  This applies to every symmetric object here.
- The irregular objects have two different halves, **a** and **b**.
- Glue the halves together. No connectors are built in; add pins or dowels in your slicer if you
  like.

## Settings

The baseline prints used the settings below. Settings for the new pieces will be added as they
are printed.

| setting | value | status |
|---|---|---|
| layer height | 0.2 mm | used for the baseline prints |
| perimeters | 3 | used for the baseline prints |
| infill | 15% gyroid | used for the baseline prints |
| supports | tree supports for downward spikes, if any | depends on the cut |

Each object's page links to its files once they are published.
