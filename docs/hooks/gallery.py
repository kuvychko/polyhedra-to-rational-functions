"""Generate the object pages from ``catalog/pieces.yaml`` at build time (decision 0006).

The catalog is the single source for the gallery and for the Phase 2 checklist, so the site can
never disagree with it. Nothing is written into ``docs/``: the pages are added to the build as
generated files. Each page describes the piece's function, its divisor, and its print and listing
status.
"""

from __future__ import annotations

import logging
from collections import Counter

from mkdocs.structure.files import File

from polyhedral_functions import catalog, fixtures

log = logging.getLogger("mkdocs.hooks.gallery")

RECIPE_TEXT = {
    "R2": (
        "zeros at the vertex directions, each of order equal to the vertex's valence",
        "poles at the polar face directions, each of order equal to the face's number of sides",
    ),
    "R4ve": (
        "zeros at the vertex directions, each of order equal to the vertex's valence",
        "poles at the edge points (feet of the perpendiculars from the centre), each of order 2",
    ),
    "R4fe": (
        "zeros at the polar face directions, each of order equal to the face's number of sides",
        "poles at the edge points, each of order 2",
    ),
    "R1": ("zeros at the vertex directions", "poles at the face directions, all of equal order"),
    "flag": ("zeros at vertices and faces", "poles at the edge points, each of order 4"),
}
HALVES_TEXT = {
    "identical": "two identical halves: print the half file twice",
    "mirror": "two mirror-image halves",
    "different": "two different halves (a and b)",
}


def orders_text(orders) -> str:
    counts = Counter(abs(int(o)) for o in orders)
    return ", ".join(f"{n} of order {m}" for m, n in sorted(counts.items()))


def recipe_paragraph(piece) -> str:
    zeros, poles = RECIPE_TEXT[piece.recipe]
    if piece.reciprocal:
        zeros, poles = poles.replace("poles", "zeros"), zeros.replace("zeros", "poles")
    solid = fixtures.load(piece.polyhedron).name
    return (
        f"Recipe **{piece.recipe}**{' (reciprocal)' if piece.reciprocal else ''} on the "
        f"**{solid}**: {zeros}; {poles}."
    )


def piece_page(piece, screened, exports) -> str:
    d = piece.divisor()
    lines = [f"# {piece.title}", ""]
    origin = (
        "One of the original Klein-invariant ornaments (the baseline, R0)."
        if piece.origin == "baseline"
        else "A Phase 1 recipe applied beyond the Platonic solids."
    )
    lines += [origin, "", recipe_paragraph(piece), ""]
    if piece.function:
        lines += [f"Classical form: `f(z) = {piece.function}`.", ""]
    lines += [
        "| | |",
        "|---|---|",
        f"| zeros | {len(d.zeros)} points: {orders_text(d.zeros.orders)} |",
        f"| poles | {len(d.poles)} points: {orders_text(d.poles.orders)} |",
        f"| degree | {d.degree} |",
    ]
    if piece.digital_only:
        lines += ["| print | digital only |", ""]
    else:
        printed = ", ".join(f"{s} mm" for s in piece.printed_sizes()) or "not yet"
        planned = f"{piece.planned_size_mm} mm" if piece.planned_size_mm else "undecided"
        cut = exports.get(piece.id, {}).get("cuts", {}).get("130", {}).get("halves")
        lines += [
            f"| printed | {printed} |",
            f"| planned size | {planned} (tip to tip) |",
            f"| cut | {HALVES_TEXT.get(cut, 'not yet chosen')} |",
            f"| print files | {listing(piece)} |",
            "",
        ]
    if piece.notes:
        lines += [f"!!! note\n    {piece.notes}", ""]
    lines += [
        f"*Status: {piece.status(screened)}. Generated from the catalog entry `{piece.id}`.*",
        "",
    ]
    return "\n".join(lines)


def listing(piece) -> str:
    if piece.printables_url:
        return f"[Printables]({piece.printables_url}): whole and cut STLs, 80 and 130 mm"
    return "coming to Printables (whole and cut STLs, 80 and 130 mm)"


def index_page(pieces, screened) -> str:
    groups = [
        ("Printed", [p for p in pieces if p.printed and not p.digital_only]),
        ("In the print queue", [p for p in pieces if not p.printed and not p.digital_only]),
        ("Digital only", [p for p in pieces if p.digital_only]),
    ]
    lines = [
        "# The objects",
        "",
        "Each object is the modulus relief of one rational function on the Riemann sphere: "
        "poles are spikes, zeros are pits. The recipes that place them are explained under "
        "[The question](../research/index.md). Every object has its own page with its function, "
        "how it is printed, and where to get the files.",
        "",
    ]
    for heading, members in groups:
        if not members:
            continue
        lines += [
            f"## {heading}",
            "",
            "| object | recipe | degree | print files |",
            "|---|---|---|---|",
        ]
        for p in members:
            files = f"[Printables]({p.printables_url})" if p.printables_url else "coming"
            if p.digital_only:
                files = "–"
            lines.append(
                f"| [{p.title}]({p.id}.md) | {p.recipe}{' (reciprocal)' if p.reciprocal else ''} "
                f"on {fixtures.load(p.polyhedron).name} | {p.divisor().degree} | {files} |"
            )
        lines.append("")
    return "\n".join(lines)


def on_files(files, config):
    pieces = catalog.load()
    screened, exports = catalog.screened_ids(), catalog.exports()
    files.append(File.generated(config, "objects/index.md", content=index_page(pieces, screened)))
    for piece in pieces:
        files.append(
            File.generated(
                config, f"objects/{piece.id}.md", content=piece_page(piece, screened, exports)
            )
        )
    log.info("gallery: generated %d object pages", len(pieces))
    return files
