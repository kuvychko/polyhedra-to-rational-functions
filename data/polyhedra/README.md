# Geometry fixtures

The geometry corpus (`PROGRAM.md` §9). Each file is written by `scripts/make_fixtures.py` from a
construction in `src/polyhedral_functions/fixtures.py`. That construction is the fixture's
provenance: nothing is transcribed from third-party coordinate data. `tests/test_fixtures.py`
checks that every stored file still matches its construction and passes the geometry contract.

| id | V | E | F | construction | scale |
|---|---|---|---|---|---|
| `tetrahedron` | 4 | 6 | 4 | roots of complexplorer's `tetrahedral_vertex` | circumradius 1 |
| `cube` | 8 | 12 | 6 | `(±1,±1,±1)/√3`, the octahedron's face directions | circumradius 1 |
| `octahedron` | 6 | 12 | 8 | vertices on the axes | circumradius 1 |
| `icosahedron` | 12 | 30 | 20 | vertex at each pole, rings at `z = ±1/√5` | circumradius 1 |
| `dodecahedron` | 20 | 30 | 12 | the icosahedron's face directions | circumradius 1 |
| `rhombicuboctahedron` | 24 | 48 | 26 | permutations of `(±1, ±1, ±(1+√2))` | midradius 1 |
| `deltoidal-icositetrahedron` | 26 | 48 | 24 | polar dual of the rhombicuboctahedron (canonical) | midradius 1 |
| `irregular-9` | 14 | 21 | 9 | nine hand-chosen half-spaces, no symmetry, faces of 3–6 sides | smallest face distance 0.7 |

All are centred at the origin except `irregular-9`, whose origin is just an interior point.
The Platonic solids share the orientation of the baseline Klein forms, so recipe divisors can be
compared with R0 directly.

Each file holds `id`, `name`, `construction`, `description`, a combinatorial `summary`,
`vertices` and `faces`. Faces are listed counterclockwise as seen from outside. Load a fixture
with `polyhedral_functions.fixtures.load(id)`.

The deformation and combinatorial-transition cases are experiments, not fixtures. They are
built in M6 from these fixtures with `Polyhedron.with_vertices` (fixed combinatorics) and
`Polyhedron.from_points` (hull, may change combinatorics).
