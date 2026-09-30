# 0002: Explore edge-incidence recipes (R4) deliberately

Date: 2026-09-30. Status: accepted.

## Context

The baseline audit (`notes/2026-09-30-baseline-audit.md`) found two kinds of existing piece:

- The three "dual" pieces are exactly recipes R1 = R2 on Platonic inputs.
- The octahedral crown, icosahedral crown and icosidodecahedral star put features at edge
  midpoints instead, which none of the v2.1 candidates do.

The audit first proposed keeping them as references only, since `PROGRAM.md` §7 limits new
point sets to those that answer a specific question.

## Decision

Treat the edge construction as a candidate family, **R4**, and compare it alongside R1 and R2.

It is a direct generalization of R2, not an unrelated addition. R2 weights the vertex–face
pair by incidence. R4 weights the vertex–edge and face–edge pairs the same way: order =
valence or number of sides for vertices or faces, and 2 for edges. Every pair totals `2E`. That
reproduces all three baseline pieces **[D]**:

| piece | recipe | orders |
|---|---|---|
| octahedral crown `E/V²` | vertex–edge on the octahedron | 4:2 → 2:1 |
| icosahedral crown `T²/V⁵` | vertex–edge on the icosahedron | 5:2 |
| icosidodecahedral star `H³/T²` | vertex–edge on the dodecahedron = face–edge on the icosahedron | 3:2 |

The baseline pieces are the reciprocal orientation, with poles on the vertex side. As with
R1, both orientations are valid.

## Consequences

- `PROGRAM.md` v2.2 adds R4 to §7, the sequence and the exit criteria.
- The geometry contract (M2) must provide edges with their incidences, and two edge point
  sets: the foot of the perpendicular from the origin (self-dual under polarity) and the
  projected midpoint.
- Duality checks for R4 compare vertex–edge on P with face–edge on P*, not with itself.

## Reopen if

R4 turns out to be dominated by R2 on every criterion in `PROGRAM.md` §5 across the corpus.
