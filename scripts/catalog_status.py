"""Validate the piece catalog and regenerate the Phase 2 checklist.

Run:  uv run python scripts/catalog_status.py           # writes catalog/CHECKLIST.md
      uv run python scripts/catalog_status.py --check   # exit 1 if the checklist is stale

The checklist is derived from ``catalog/pieces.yaml`` and the print screen
(``experiments/P001-print-screen/screen.csv``). Never edit it by hand.
"""

import argparse
import sys

from polyhedral_functions.catalog import CHECKLIST_FILE, checklist, load, screened_ids


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail if CHECKLIST.md is out of date")
    args = ap.parse_args()
    text = checklist(load(), screened_ids())
    if args.check:
        current = CHECKLIST_FILE.read_text(encoding="utf-8") if CHECKLIST_FILE.exists() else ""
        if current != text:
            sys.exit("catalog/CHECKLIST.md is out of date: run scripts/catalog_status.py")
        print("checklist is up to date")
        return
    with CHECKLIST_FILE.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(f"wrote {CHECKLIST_FILE.name}: {text.splitlines()[-1]}")


if __name__ == "__main__":
    main()
