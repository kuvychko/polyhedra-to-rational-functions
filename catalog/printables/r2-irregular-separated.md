**A complex function you can hold.**

This sculpture is a picture of a single mathematical function. A rational function on the Riemann sphere is pinned down by its zeros and poles. Here they come from an irregular convex polyhedron with 9 vertices and 11 faces and no symmetry at all: zeros sit at its vertices, and poles at its face directions. The surface rises where the function's size grows, so **poles become spikes and zeros become pits**. The result has 11 spikes and 9 pits, of different sizes, because the vertices and faces differ.

The other pieces in this series come from highly symmetric solids. This one shows that the recipe needs no symmetry: it turns any convex polyhedron into a function. The solid was chosen by a seeded random search for one whose spikes and pits stay well apart (at least 24.7° on the sphere), so every feature prints as its own shape.

## The math

- The recipe (R2): a zero at each vertex, of order equal to the number of edges meeting there, and a pole at each face direction, of order equal to the face's number of sides.
- Here: 9 triangular faces, one quadrilateral and one pentagon give 11 poles of orders 3, 4 and 5. The vertices give 9 zeros: 7 of order 4, one of order 3 and one of order 5. Degree 36.
- The function is f(z) = C · ∏ (z − aᵢ)^mᵢ, one factor for each zero or pole aᵢ with its order mᵢ (negative for poles). The quadrilateral's pole sits at infinity, the north pole of the sphere, and contributes no factor.
- The radius at each point of the sphere follows |f|. The constant is fixed so that |f| has geometric mean 1 over the sphere, which puts "sea level" midway between the spikes and the pits.

## Files

Two sizes, measured tip to tip: **80 mm** and **130 mm**. The tested print is 80 mm.

- **Whole model:** one piece for each size.
- **Cut halves:** the model is cut through its centre into halves **a** and **b**. The solid has no symmetry, so the two halves are different: print each once. Each half lies flat on its cut face.
- **Hanging ornament:** halves **a** and **b** with a 1.5 mm thread hole through the spike over the pentagonal face, 9 mm from its tip. No spike lies in the cut plane, so the hole sits entirely within one half. Thread it, tie a loop, and hang it on a tree.

## Assembly

- Every half has a 5.2 mm alignment hole in the middle of its cut face, for an **M5 dowel pin (5.00 mm diameter)**:
  - 80 mm: M5 × 10 pin, 6 mm holes;
  - 130 mm: M5 × 20 pin, 11 mm holes.
- With the settings below, the pin gives a light friction fit. Glue the pin into one half, then glue the halves together; the pin keeps them aligned. If your printer makes holes tighter or looser, ream the hole lightly. You can also glue the halves without a pin.
- Glue: a budget cyanoacrylate (super glue) for plastics works well with PLA. I used LOOCTOT glue for plastic.
- Ornament hole: run a 1.5 mm drill bit through it by hand in a pin vise to clean it up. Monofilament (fishing line) makes a good hanging loop. Keep glue away from the hole while assembling.

## Print settings (tested)

- PLA, 0.4 mm nozzle
- 0.20 mm layers ("QUALITY" profile)
- 15% gyroid infill
- Halves print cut face down. No supports are needed.

Part of **[Polyhedra as Complex Functions](https://kuvychko.github.io/polyhedra-to-rational-functions/)**: how this piece is made, an interactive 3D view of its zeros and poles, and the [object's own page](https://kuvychko.github.io/polyhedra-to-rational-functions/objects/r2-irregular-separated/). Code and data: [GitHub](https://github.com/kuvychko/polyhedra-to-rational-functions).
