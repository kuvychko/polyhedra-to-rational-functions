# 0007: Scripted, owner-approved cut STLs for every piece

Date: 2026-10-03. Status: accepted by the owner.

## Context

Spiky reliefs print best in two halves, each lying on its flat cut face. Downloaders who are not
comfortable sectioning a model in a slicer need the halves provided. The earlier prints were cut
by hand in slicer projects (`*-cut*.3mf`). That made their files hard to trace: the exact printed
meshes were never recorded.

## Decisions

1. **Every printable piece gets cut STLs** at both sizes, alongside the whole STLs. Printables
   listings carry both.
2. **Cuts are scripted** (`cuts.py`, `meshes.export_cuts`), as a plane through the relief's
   centre. Halves are capped, watertight, and posed cut face down on `z = 0`.
3. **The owner approves every plane.**
   - `scripts/p002_cut_proposals.py` proposes the best three distinct planes per piece, ranked by:
     - halves *identical* (a proper symmetry swaps the sides, so one file is printed twice),
       then *mirror*, then *different*;
     - support share;
     - clearance from the nearest feature not in the plane;
     - cut-face area.
   - The owner copies the chosen normal into the catalog (`cut: {normal: [...], approved: true}`).
   - Nothing is cut from an unapproved plane. The checklist orders the work: approve a cut, then
     export the cut STLs, then print.
4. **The new scripted cuts are used for everything, including the four pieces already printed.**
   Their Printables files will be the scripted halves, not the earlier slicer cuts.
5. **Baseline whole STLs are reproducible from this repository.** Regenerating them through
   `meshes.py` gives files byte-identical to figures_repo @ `292bec4` (checked by
   `b2_export_stls.py`, `reproduces_catalog_stl`). The only open provenance question is whether
   the *earlier prints* used those same files.

## Consequences

- Connectors (pins, dowels) are not added. Listings say "glue; add connectors in your slicer if
  you like".
- Mesh triangulation is not exactly symmetric (the latitude–longitude grid), so "identical" halves
  are congruent up to mesh resolution. Printing one file twice is correct.
