"""Write the geometry corpus to ``data/polyhedra/`` from its constructions.

Run:  uv run python scripts/make_fixtures.py

The stored JSON is what experiments load. ``tests/test_fixtures.py`` checks that it still
matches a fresh construction, so rerun this after changing a construction on purpose.
"""

import json

from polyhedral_functions.fixtures import CONSTRUCTIONS, DATA_DIR, to_record


def dumps(record: dict) -> str:
    """JSON with one vertex and one face per line, so diffs of a fixture stay readable."""
    head = json.dumps({k: v for k, v in record.items() if k not in ("vertices", "faces")}, indent=1)
    body = [
        f' "{key}": [\n' + ",\n".join(f"  {json.dumps(row)}" for row in record[key]) + "\n ]"
        for key in ("vertices", "faces")
    ]
    return head[: -len("\n}")] + ",\n" + ",\n".join(body) + "\n}\n"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for fixture_id, construct in CONSTRUCTIONS.items():
        record = to_record(fixture_id, construct())
        path = DATA_DIR / f"{fixture_id}.json"
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(dumps(record))
        s = record["summary"]
        print(f"{fixture_id:<28} V={s['V']:<3} E={s['E']:<3} F={s['F']:<3} -> {path.name}")


if __name__ == "__main__":
    main()
