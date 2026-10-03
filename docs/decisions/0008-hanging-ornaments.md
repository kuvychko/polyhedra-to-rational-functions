# 0008: A hanging-ornament variant of every piece

Date: 2026-10-03. Status: accepted by the owner.

## Context

The objects make natural tree ornaments. A thread hole near a spike tip turns any piece into one,
with no hardware. Drilling such a hole by hand into a finished print is awkward and risks
cracking a spike.

## Decision

1. **A third set of files for every printable piece:** cut halves with a **1.5 mm** thread hole,
   at both sizes, alongside the whole and plain cut STLs (`hangers.py`,
   `meshes.export_ornament`). Printables listings carry all three.
2. **The hole runs along the approved cut plane's normal.** It is vertical in print pose, so it
   needs no bridging or support.
3. **The spike is the most prominent one the cut plane bisects**, so the hole passes through both
   halves and aligns on gluing. When no spike lies in the plane (the irregular pieces), the hole
   goes through the most prominent spike within 35° of it, entirely within one half.
4. **The hole starts 9 mm from the tip** (the owner asked for 8–10 mm). It moves inward in 0.5 mm
   steps until at least 1 mm of wall remains on both sides, and it fails above 16 mm. The final
   distance and wall are recorded per piece and size in `catalog/exports.json`.
5. **Safety checks.** The volume removed must match the cylinder crossing the spike, so a bore
   that cuts into another part of the object fails the export. Booleans and the split use
   `manifold3d`, and every half must be watertight.
6. **Ornament halves are always two files (a and b).** The hole breaks the symmetry that made
   the plain halves identical.

## Reopen if

A printed ornament shows a better diameter, distance or thread path: for example, a hole
perpendicular to the spike within the cut plane, if vertical holes clog with glue.
