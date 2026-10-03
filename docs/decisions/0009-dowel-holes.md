# 0009: Alignment dowel holes in every cut face

Date: 2026-10-03. Status: accepted by the owner.

## Context

Gluing two halves by eye leaves a visible step if they slip. The owner has M5 dowel pins, 20 mm
and 10 mm long. A pin in matching blind holes aligns the halves and strengthens the joint.

## Decision

1. **Every cut STL gets a centred blind hole**, both the plain halves (decision 0007) and the
   hanging-ornament halves (decision 0008). The whole STLs are unchanged.
2. **5.2 mm across**, on the cut normal through the centre. It is bored into the whole solid
   before the split, so the two holes line up by construction. Each half prints cut face down,
   so the hole is vertical and its 5.2 mm ceiling is a short bridge.
3. **Pin by print size.** 130 mm prints take the **20 mm** pin (holes 11 mm deep each side), and
   80 mm prints take the **10 mm** pin (6 mm each side). That is half the pin plus 1 mm of slack
   for glue. If the preferred pin does not fit, the shorter one is used, and the choice is
   recorded per file.
4. **Checks** (`dowels.py`, recorded in `catalog/exports.json`):
   - at least 1.2 mm of floor beyond each hole;
   - at least 1.5 mm of side wall, checked by intersecting a widened cylinder with the solid;
   - the two holes together longer than the pin;
   - the thread hole at least 5 mm clear of the dowel.
5. **Identical halves stay one file.** The dowel is symmetric, so both printed copies of a single
   half file get the hole.

## Reopen if

A test print shows a different hole diameter fits the pins better (printed holes often shrink).
Then change `DIAMETER_MM` and re-export.
