# The recipes

## From a polyhedron to a divisor

A rational function on the Riemann sphere is determined, up to a constant factor, by its
**divisor**: a finite set of points, each carrying a nonzero integer order. Positive orders are
zeros and negative orders are poles. The orders must sum to zero over the whole sphere, counting
infinity.

A **recipe** places such points according to a convex polyhedron with its centre at the origin:

- **vertices** at their directions from the centre;
- **faces** at their outward normals, which are the vertex directions of the polar dual;
- **edges** at the foot of the perpendicular from the centre, a direction shared with the dual
  edge.

**The default recipe, R2**, counts incidences:

$$
D_{R2} \;=\; \sum_{v} \operatorname{val}(v)\,[v] \;-\; \sum_{f} \operatorname{sides}(f)\,[f].
$$

Both sums equal \(2E\), so the divisor balances automatically. **The alternative, R4**, pairs
cells with edges instead:

$$
D_{R4ve} = \sum_v \operatorname{val}(v)\,[v] - 2\sum_e [e], \qquad
D_{R4fe} = \sum_f \operatorname{sides}(f)\,[f] - 2\sum_e [e].
$$

For these unreduced divisors, \(D_{R2} = D_{R4ve} - D_{R4fe}\). Polarity exchanges vertices and
faces, so R2 on the polar dual gives exactly the reciprocal function, and R4ve and R4fe swap.

## Fixing the constant

The relief needs an absolute modulus, not one defined up to a constant. With \(\chi\) the chordal
(straight-line) distance between points of the unit sphere, the modulus is

$$
\log|f(x)| \;=\; \sum_i m_i \log \chi(x, a_i).
$$

It has three useful properties:

- **self-dual:** the negated divisor gives \(1/|f|\);
- **rotation-covariant:** rotating the polyhedron rotates the relief;
- **geometric mean 1 over the sphere:** sea level, \(|f| = 1\), sits in the middle of the
  relief.

## Worked example: the octahedron

| step | result |
|---|---|
| polyhedron | regular octahedron: 6 vertices of valence 4, 8 triangular faces |
| R2 divisor | zeros of order 4 at the 6 vertices; poles of order 3 at the 8 face normals, which point to the cube's vertices |
| degree | \(6 \cdot 4 = 8 \cdot 3 = 24\) |
| function | \(f(z) = C\, V(z)^4 / F(z)^3\), with Klein's octahedral forms \(V = z(z^4-1)\) and \(F = z^8 + 14z^4 + 1\) |
| constant | \(C = 729/4\) exactly; the earlier sampled value was 0.55% off |
| object | the [Cube–Octahedron Dual](../objects/cube-octahedron-dual.md) |

```python
from polyhedral_functions import fixtures
from polyhedral_functions.recipes import R2, apply

d = apply(R2, fixtures.load("octahedron")).divisor
print(d.summary())  # 6 zeros of order 4, 8 poles of order 3, degree 24
```

On the Platonic solids R2 reproduces Klein's classical invariants. The interesting cases are
the solids beyond them, where recipes that agree on Platonic inputs come apart. That story, and
the evidence for choosing R2 and keeping R4, is in [the exploration](narrative.md).
