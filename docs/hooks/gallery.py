"""Generate the object pages from ``catalog/pieces.yaml`` at build time (decision 0006).

The catalog is the single source for the gallery and for the Phase 2 checklist, so the site can
never disagree with it. Nothing is written into ``docs/``: the pages are added to the build as
generated files. Each object page shows:

- the coordinated views precomputed by ``scripts/a4_site_assets.py``
  (geometry → plane → sphere → relief → printed shape);
- the owner's photographs, when the catalog lists them;
- the function and its divisor;
- the print and listing status;
- links to the recipe and to the experiments that cover it.
"""

from __future__ import annotations

import logging
from collections import Counter
from pathlib import Path

from mkdocs.structure.files import File

from polyhedral_functions import catalog, fixtures

log = logging.getLogger("mkdocs.hooks.gallery")

DOCS = Path(__file__).resolve().parents[1]
ATLAS_SHEETS = DOCS.parent / "experiments" / "E001-atlas" / "sheets"

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
VIEWS = [
    ("geometry", "The solid, with zeros (blue) and poles (red) on the sphere"),
    ("plane", "Phase portrait of f in the plane"),
    ("sphere", "Phase on the Riemann sphere"),
    ("relief", "The printed shape, colored by phase"),
    ("neutral", "The printed shape"),
]


def orders_text(orders) -> str:
    counts = Counter(abs(int(o)) for o in orders)
    return ", ".join(f"{n} of order {m}" for m, n in sorted(counts.items()))


def solid_name(piece) -> str:
    return fixtures.load(piece.polyhedron).name


def recipe_label(piece) -> str:
    return f"{piece.recipe}{' (reciprocal)' if piece.reciprocal else ''}"


def recipe_paragraph(piece) -> str:
    zeros, poles = RECIPE_TEXT[piece.recipe]
    if piece.reciprocal:
        zeros, poles = poles.replace("poles", "zeros"), zeros.replace("zeros", "poles")
    return (
        f"Recipe **{recipe_label(piece)}** on the **{solid_name(piece)}** "
        f"([how the recipes work](../research/recipes.md)): {zeros}; {poles}."
    )


def asset(piece, view: str) -> str | None:
    """The page-relative path of a precomputed view, if it has been generated."""
    if (DOCS / "assets" / "pieces" / piece.id / f"{view}.jpg").exists():
        return f"../assets/pieces/{piece.id}/{view}.jpg"
    return None


def viewer_block(piece) -> list[str]:
    """The interactive geometry view, with the static render inside it as the fallback."""
    data = DOCS / "assets" / "pieces" / piece.id / "geometry.json"
    still = asset(piece, "geometry")
    if not (data.exists() and still):
        return []
    alt = f"The {solid_name(piece)} with the zeros (blue) and poles (red) of its function"
    return [
        "## Zeros and poles",
        "",
        # data-src is relative to the fallback image (see javascripts/geometry-viewer.js).
        '<div class="geometry-viewer" data-src="geometry.json" markdown>',
        '<div class="geometry-viewer__stage" markdown>',
        f"![{alt}]({still})",
        "</div>",
        '<p class="geometry-viewer__legend"><span class="dot dot--zero"></span> zeros (pits) '
        '<span class="dot dot--pole"></span> poles (spikes). Markers grow with order. '
        "Drag to rotate, scroll or pinch to zoom, hover or tap a marker for details.</p>",
        "</div>",
        "",
    ]


def views_block(piece) -> list[str]:
    figures = [
        (asset(piece, view), caption)
        for view, caption in VIEWS
        if asset(piece, view) and not (view == "geometry" and viewer_block(piece))
    ]
    if not figures:
        return []
    lines = ["## Views", "", '<div class="piece-views" markdown>', ""]
    for src, caption in figures:
        lines += [
            "<figure markdown>",
            f"![{caption}]({src})",
            f"<figcaption>{caption}</figcaption>",
            "</figure>",
            "",
        ]
    return lines + ["</div>", ""]


def photos_block(piece) -> list[str]:
    if not piece.photos:
        return []
    lines = ["## Photographs", "", '<div class="piece-photos" markdown>', ""]
    for i, photo in enumerate(piece.photos, start=1):
        src = "../" + Path(photo).relative_to("docs").as_posix()
        lines += [f"![Photograph {i} of the printed {piece.title}]({src})", ""]
    return lines + ["</div>", ""]


FILES = (
    "whole, cut halves, and a [hanging-ornament](../printing.md#hanging-ornaments) version; "
    "80 and 130 mm"
)


def listing(piece) -> str:
    if piece.printables_url:
        return f"[on Printables]({piece.printables_url}): {FILES}"
    return f"coming to Printables: {FILES}"


def lineage(piece) -> list[str]:
    items = [
        "- How the recipes work and how the constant is fixed: "
        "[The recipes](../research/recipes.md)."
    ]
    if (ATLAS_SHEETS / f"{piece.polyhedron}-recipes.jpg").exists():
        sheet = f"../experiments/E001-atlas/sheets/{piece.polyhedron}-recipes.jpg"
        items.append(
            f"- Every recipe on the {solid_name(piece)}, side by side: [E001 atlas sheet]({sheet})."
        )
    if not piece.digital_only:
        items.append(
            "- Printability and the cut plane: "
            "[P001 and P002](../research/experiments.md#for-printing-p001-and-p002)."
        )
    return ["## Where it comes from", "", *items, ""]


def piece_page(piece, screened, exports) -> str:
    d = piece.divisor()
    origin = (
        "One of the original Klein-invariant ornaments (the baseline, R0)."
        if piece.origin == "baseline"
        else "A Phase 1 recipe applied beyond the Platonic solids."
    )
    lines = [f"# {piece.title}", "", origin, "", recipe_paragraph(piece), ""]
    if piece.function:
        lines += [f"Classical form: `f(z) = {piece.function}`.", ""]
    if piece.notes:
        lines += ["!!! note", f"    {piece.notes}", ""]
    lines += viewer_block(piece) + views_block(piece) + photos_block(piece)
    lines += [
        "## The function and the print",
        "",
        "| | |",
        "|---|---|",
        f"| **zeros** | {len(d.zeros)} points: {orders_text(d.zeros.orders)} |",
        f"| **poles** | {len(d.poles)} points: {orders_text(d.poles.orders)} |",
        f"| **degree** | {d.degree} |",
    ]
    if piece.digital_only:
        lines += ["| **print** | digital only |", ""]
    else:
        printed = ", ".join(f"{s} mm" for s in piece.printed_sizes()) or "not yet"
        planned = f"{piece.planned_size_mm} mm" if piece.planned_size_mm else "undecided"
        cut = exports.get(piece.id, {}).get("cuts", {}).get("130", {}).get("halves")
        lines += [
            f"| **printed** | {printed} |",
            f"| **planned size** | {planned}, tip to tip |",
            f"| **cut** | {HALVES_TEXT.get(cut, 'not yet chosen')} |",
            f"| **print files** | {listing(piece)} |",
            "",
        ]
    lines += lineage(piece)
    lines.append(
        f"*Status: {piece.status(screened)}. Generated from the catalog entry `{piece.id}`.*"
    )
    return "\n".join(lines) + "\n"


def card(piece) -> str:
    thumb = asset(piece, "relief")
    image = f"![{piece.title}]({thumb})" if thumb else ""
    meta = f"{recipe_label(piece)} on the {solid_name(piece)}, degree {piece.divisor().degree}"
    return (
        f'<a class="piece-card" href="{piece.id}/" markdown>\n{image}\n'
        f'<span class="piece-title">{piece.title}</span>\n'
        f'<span class="piece-meta">{meta}</span>\n</a>\n'
    )


def index_page(pieces) -> str:
    groups = [
        ("Printed", [p for p in pieces if p.printed and not p.digital_only]),
        ("In the print queue", [p for p in pieces if not p.printed and not p.digital_only]),
        ("Digital only", [p for p in pieces if p.digital_only]),
    ]
    lines = [
        "# The objects",
        "",
        "Each object is the modulus relief of one rational function on the Riemann sphere: "
        "poles are spikes, zeros are pits, and the color is the function's phase. The recipes "
        "that place them are explained under [The question](../research/index.md). Each object "
        "has its own page with its views, its function, how it is printed, and where to get "
        "the files.",
        "",
    ]
    for heading, members in groups:
        if members:
            lines += [f"## {heading}", "", '<div class="piece-cards" markdown>', ""]
            lines += [card(p) for p in members]
            lines += ["</div>", ""]
    return "\n".join(lines)


def on_files(files, config):
    pieces = catalog.load()
    screened, exports = catalog.screened_ids(), catalog.exports()
    files.append(File.generated(config, "objects/index.md", content=index_page(pieces)))
    for piece in pieces:
        content = piece_page(piece, screened, exports)
        files.append(File.generated(config, f"objects/{piece.id}.md", content=content))
    log.info("gallery: generated %d object pages", len(pieces))
    return files
