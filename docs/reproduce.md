# Reproduce

Everything on this site is generated from the repository: the functions, the figures, the
checks and the print files. You need [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                        # the pinned environment (complexplorer 3.1.0)
uv run pytest                                  # every derived and numerical claim with a test
uv run python scripts/make_atlas.py            # E001, the comparison atlas
uv run python scripts/e002_transitions.py      # E002; likewise e003_deformation, e004_display
uv run python scripts/p001_print_screen.py     # the printability screen
uv run python scripts/b2_export_stls.py        # whole and cut STLs for every printable piece
uv run --group docs mkdocs serve               # this site
```

Each experiment writes a manifest recording its configuration, its code commit (which must be
clean), package versions, and output hashes. The STL export checks that the baseline pieces'
files come out byte-identical to the originals.
