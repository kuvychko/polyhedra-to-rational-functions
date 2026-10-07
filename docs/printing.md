# Printing

Every object is a solid that is star-shaped about its centre: each ray from the centre crosses
the surface once. There are no thin walls. The fine geometry is all in the tips.

The print files are on Printables, one listing per object, gathered in the collection
[Polyhedra as Complex Functions](https://www.printables.com/@Igor_2829688/collections/3812430).

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
- Each half has a **dowel hole** in the middle of its cut face, for an **M5 dowel pin, 5.00 mm in
  diameter**. The hole is modelled at 5.2 mm because printed holes come out undersized. On a
  test print it gave a light friction fit, which suits gluing. If your printer prints holes
  tighter or looser, scale the hole or ream it lightly.
    - 130 mm prints take a **20 mm** pin, in holes 11 mm deep;
    - 80 mm prints take a **10 mm** pin, in holes 6 mm deep.
- The holes line up by construction. Glue the pin into one half, then glue the halves together;
  the pin keeps them aligned. Without a pin, just glue the faces.
- **Glue:** a budget cyanoacrylate (super glue) made for plastics worked well with PLA. The one
  tested was LOOCTOT glue for plastic.

## Hanging ornaments

Every object also comes as a **hanging ornament**: cut halves with a 1.5 mm thread hole bored
through one spike. Pass a thread through, tie a loop, and it hangs on a tree. Monofilament
(fishing line) makes a good loop at this hole size.

- **Which spike:** the most prominent one the cut plane splits lengthwise, so the hole runs
  through both halves and lines up when they are glued. Where no spike lies in the plane, as on
  the irregular objects, the hole goes through the most prominent spike near the plane, entirely
  within one half.
- **Where on the spike:** about 9 mm in from the tip. It moves further in only where the spike
  is too thin to keep at least 1.5 mm of wall on both sides of the hole. Each object's record gives
  the exact distance.
- **Printing:** each half lies cut face down, so the hole is vertical and needs no support. The
  ornament halves are always two files, **a** and **b**: the hole makes them different.
- **Cleaning the hole:** a printed 1.5 mm hole comes out rough and slightly undersized. Run a
  1.5 mm drill bit through it by hand in a pin vise.
- **Gluing:** the ornament halves have the same dowel hole as the plain halves. Keep glue away
  from the thread hole, or clear it with a pin before it sets.

## Settings

These settings produced the prints so far, including the dowel-fit test. Notes for individual
pieces will be added as they are printed.

| setting | value | status |
|---|---|---|
| material | PLA | tested |
| nozzle | 0.4 mm | tested |
| layer height | 0.20 mm (the slicer's "QUALITY" profile) | tested |
| infill | 15% gyroid | tested |
| perimeters | 3 | used for the baseline prints |
| dowel fit | 5.2 mm hole on a 5.00 mm M5 pin: light friction fit | tested |
| supports | none: halves print cut face down | tested: no printed piece has needed them |

Each object's page links to its files once they are published.
