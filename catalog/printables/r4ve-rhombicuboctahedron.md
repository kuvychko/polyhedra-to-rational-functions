**A complex function you can hold.**

This sculpture is a picture of a single mathematical function. A rational function on the Riemann sphere is pinned down by its zeros and poles. Here they come from a rhombicuboctahedron, an Archimedean solid with 18 squares and 8 triangles: zeros sit at its 24 vertices, and poles at its 48 edges, each where the edge touches the sphere. The surface rises where the function's size grows, so **poles become spikes and zeros become pits**. The result is a sea urchin of 48 spikes, the most in the series, around 24 pits.

Unlike the classical pieces in this series, it isn't built from Klein's invariant forms. It comes from the project's general recipes, which turn any convex polyhedron into a function. Its companion piece, the Deltoidal Icositetrahedron, is built from this solid's dual with the default recipe; this one uses the alternative.

## The math

- The recipe (R4ve, vertices against edges): a zero at each vertex, of order equal to the number of edges meeting there, and a pole of order 2 at each edge.
- Here the raw orders are 4 at every vertex and 2 at every edge. They share a factor of 2, and dividing it out gives the function itself: 24 zeros of order 2 and 48 simple poles. Degree 48.
- The function is f(z) = C · ∏ (z − aᵢ)^mᵢ, one factor for each zero or pole aᵢ with its order mᵢ (negative for poles).
- The relief has the full symmetry of the octahedron, mirrors included: 48 symmetries.
- The radius at each point of the sphere follows |f|. The constant is fixed so that |f| has geometric mean 1 over the sphere, which puts "sea level" midway between the spikes and the pits.

## Files

Two sizes, measured tip to tip: **80 mm** and **130 mm**. The tested print is 80 mm; with 72 features, the 130 mm size shows them more boldly.

- **Whole model:** one piece for each size.
- **Cut halves:** the model is cut through its centre along a symmetry plane, so the two halves are identical. Print the half file **twice**. Each half lies flat on its cut face.
- **Hanging ornament:** halves **a** and **b** with a 1.5 mm thread hole through one spike. The spikes are slender, so the hole sits 9.5 mm from the tip (13 mm on the 130 mm version), where there is at least 1.5 mm of wall around it. The spike lies in the cut plane, so the hole runs through both halves and lines up when they are glued. Thread it, tie a loop, and hang it on a tree.

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

Part of **[Polyhedra as Complex Functions](https://kuvychko.github.io/polyhedra-to-rational-functions/)**: how this piece is made, an interactive 3D view of its zeros and poles, and the [object's own page](https://kuvychko.github.io/polyhedra-to-rational-functions/objects/r4ve-rhombicuboctahedron/). Code and data: [GitHub](https://github.com/kuvychko/polyhedra-to-rational-functions).
