# 2026-10-16: the stellation analogy

The R2 reliefs look like stellated solids: spikes rise over the faces. This note sets out what is
shared and what is not. Its verified parts are on the site page
`docs/research/stellation.md`; the checks are in `tests/test_stellation_claims.py`.

Labels: **[B]** established background, **[D]** derived here, **[N]** numerical observation,
**[C]** conjecture, **[P]** design preference.

## The constructions

- **Classical face stellation [B]** extends a solid's face planes until they meet again and
  takes a new solid bounded by pieces of those same planes. Every face of a stellation lies in a
  plane of the original. G. W. Hart, *Virtual Polyhedra*, gives the plane-preserving definition
  clearly.
- **Kis [B]** (Conway notation) raises a pyramid over each face. On a regular solid the pyramid
  tips point along the face normals.
- **R2** puts zeros at vertex directions and poles at face normals, and the relief is the radial
  graph of the logistic of `u = log|f| = Σ m log χ(x, a)`. No face plane constrains the surface.

So R2 is not a stellation, nor a smooth version of one. At most it shares tip directions with
some stellations, and those are what the questions below test.

## Three separate questions

### (a) Do the tip directions coincide?

The test enumerates every point where three face planes meet. The outer points of a stellation's
diagram fall into shells by radius, and each shell's directions are compared with the solid's
face normals (the R2 poles) and vertex directions (the R2 zeros). Fixtures as in `data/polyhedra/`;
radii as a fraction of the circumradius:

| solid | shells beyond the vertices (count, radius, direction) |
|---|---|
| tetrahedron | none |
| cube | none |
| octahedron | 8 at 1.732, along the face normals |
| dodecahedron | 12 at 1.777, along the face normals; 20 at 4.236, along the vertex directions |
| icosahedron | 20 at 1.066 and 20 at 2.384, along the face normals; 30 at 1.376, along the edge feet; 12 at 4.236, along the vertex directions; three shells of 60 in none of these directions |

**[N]** for these five fixtures, from the enumeration in the test.

- **Octahedron [D]:** its only stellation, the stella octangula (a compound of two tetrahedra),
  has its 8 tips at the cube's vertices. These are the octahedron's face normals, so they are
  exactly the R2 spike directions. This is the clean positive example.
- **Cube and tetrahedron [D]:** no finite stellation. On the cube, opposite face planes are
  parallel and adjacent ones already meet at edges. On the tetrahedron, any three face planes
  meet at a vertex. R2 still gives 6 (cube) and 4 (tetrahedron) spikes. So these are
  counterexamples to "R2 is a stellation".
- **Dodecahedron [N]:** it depends on which stellation you take. The 12-point shell (the tips
  of the small stellated dodecahedron [B]) lies along the R2 spike directions. The 20-point shell
  (the tips of the great stellated dodecahedron [B]) lies along the vertex directions, which are
  the R2 *pits*.
- **Icosahedron [N]:** its many stellations have tips in face, edge, vertex and other
  directions. The 30-point edge shell is suggestive for R4, which puts points on the edge feet,
  but no comparison has been made.

### (b) Does the ridge structure correspond?

**Open.** It would need a definition of "ridge" on a smooth relief, for example the ridge lines
of `u` on the sphere, compared with the projected edges of the stellation. Nothing has been
computed.

### (c) Is there a limiting relation between the surfaces?

**Open; [C] at most.** One could ask whether some family of display transfers, or some
sharpening of the divisor, tends to a stellation's surface. The cube shows that no such limit
can exist in general, because there is no stellation for it to tend to. Whether one exists on
solids that do have stellations is unexamined.

## A reading that explains the organic look

`u(x) = Σ m_i log χ(x, a_i)` is a balanced logarithmic potential on the sphere: every zero and
pole contributes at every point. The curves between spikes and pits come from the sum of all of
them, not from a local operation on each face. That is a likely reason the reliefs look grown
rather than built. Treat it as an interpretation of the formula, not a measured finding.

## Duality, the stronger statement

**[D]** For R2, polarity negates the divisor (recipes page), so `u_{P*} = -u_P` exactly under
chordal normalization. The relief radius is `r = d + (1 - d) σ(u / k)`. Since
`σ(-t) = 1 - σ(t)`, the same `d` and `k` give `r_{P*} = (1 + d) - r_P`: highs and lows swap about
the midpoint radius `(1 + d) / 2`. Under the order-tuned display, a solid and its polar dual get
the same `k`, since both have the same orders with signs exchanged. The printed pieces use
per-piece transfer settings, so their prints need not be exact reflections.

## Naming

**[P]** Do not call R2 "analytic stellation". That name would claim (b) or (c), and only part of
(a) is established. On the site the comparison is presented as an analogy, with the octahedron as
the example and the cube as the counterexample.
