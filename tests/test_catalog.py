"""The piece catalog: valid entries, divisors matching the baseline, a current checklist."""

import pytest

from polyhedral_functions import catalog
from polyhedral_functions.baseline import ornaments
from polyhedral_functions.chart import to_sphere
from polyhedral_functions.evaluation import log_modulus_on_sphere
from polyhedral_functions.normalization import polynomial_ratio_constant

PIECES = catalog.load()


def test_catalog_validates_and_ids_are_unique():
    assert len({p.id for p in PIECES}) == len(PIECES)


def test_every_piece_has_a_balanced_divisor():
    for piece in PIECES:
        d = piece.divisor()
        assert d.is_balanced and d.degree > 0, piece.id


@pytest.mark.parametrize("piece", [p for p in PIECES if p.origin == "baseline"], ids=lambda p: p.id)
def test_baseline_entries_reproduce_the_baseline_function(piece):
    """The catalog's recipe description of a baseline piece is its actual function."""
    import numpy as np

    d = piece.divisor()
    finite, orders, _ = d.chart_form()
    c = polynomial_ratio_constant(
        np.repeat(finite[orders > 0], orders[orders > 0]),
        np.repeat(finite[orders < 0], -orders[orders < 0]),
    )
    z = np.random.default_rng(3).normal(size=200) + 1j * np.random.default_rng(4).normal(size=200)
    z = z[np.abs(z) < 8]
    with np.errstate(all="ignore"):
        baseline = np.log(np.abs(c * ornaments.BY_SLUG[piece.baseline_slug].raw(z)))
    assert np.allclose(baseline, log_modulus_on_sphere(d, to_sphere(z)), atol=1e-8)


def test_owner_size_choices_are_recorded():
    by_id = {p.id: p for p in PIECES}
    assert by_id["cube-octahedron-dual"].planned_size_mm == 80
    assert by_id["cube-octahedron-dual"].printed_sizes() == [130]
    assert by_id["tetrahedral-dual"].planned_size_mm == 80
    assert by_id["cube-octahedron-dual"].next_action(catalog.screened_ids()) in (
        "screen at 80 and 130 mm (B1)",
        "print at 80 mm",
    )


def test_checklist_is_current():
    """CHECKLIST.md is generated; regenerate it with scripts/catalog_status.py after any change."""
    expected = catalog.checklist(PIECES, catalog.screened_ids())
    assert catalog.CHECKLIST_FILE.read_text(encoding="utf-8") == expected
