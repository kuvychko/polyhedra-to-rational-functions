# 0004: Polar face directions and edge feet as the default placement

Date: 2026-10-01. Status: accepted.

## Context

Every recipe needs a point per face and, for R4, a point per edge. `PROGRAM.md` §7 asks for
polar-dual directions to be compared with projected centroids. Decision 0002 added edge feet
and projected edge midpoints.

## Decision

The defaults are **polar face directions** (`n`, from the plane `n·x = h`) and **edge feet**
(the foot of the perpendicular from the origin). Centroid and midpoint placements remain as
explicit variants (`Recipe.placed`) for controlled comparison.

## Why

They are the only placements that commute with polarity:

- polar face directions are the dual's vertex directions;
- an edge and its dual edge share their foot direction.

So with these defaults, R1 and R2 give exactly the reciprocal function on the polar dual, and
R4ve and R4fe swap. The alternatives break both relations on every fixture where they differ
from the defaults (`notes/2026-10-01-recipes-and-diagnostics.md`). All placements are
rotation-equivariant and preserve symmetry, so those criteria do not decide between them.

## Reopen if

A visual or interpretive comparison (M5/M6) shows centroid or midpoint placement reading
markedly better, enough to outweigh exact duality. Record that as a design preference, not a
mathematical one.
