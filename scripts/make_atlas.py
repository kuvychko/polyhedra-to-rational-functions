"""Build the comparison atlas: standard panels and metrics for every fixture and recipe.

Run:  uv run python scripts/make_atlas.py                      # full atlas -> out/E001-atlas/
      uv run python scripts/make_atlas.py -f cube -f irregular-9
      uv run python scripts/make_atlas.py --publish            # also copy evidence to experiments/

Everything is driven by ``configs/experiments/E001-atlas.json``. For each fixture it writes two
sheets.

**Recipe sheet**, one row per recipe:

- geometry with zero and pole markers;
- plane portrait;
- colored sphere;
- colored relief;
- neutral relief;
- ``log|f| / degree`` map.

**Difference sheet**, per-degree difference maps:

- each recipe against the reference recipe;
- each placement variant against the default placement.

Display settings are fixed across the whole atlas (a fixed-display comparison). The metrics and
the manifest go next to the sheets. With ``--publish``, the manifest, the metrics and downscaled
sheets (JPEG) are copied to ``experiments/<id>/`` for committing. Full-size tiles stay in ``out/``.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from polyhedral_functions import fixtures  # noqa: E402
from polyhedral_functions.diagnostics import (  # noqa: E402
    duality_report,
    field_comparison,
    symmetry_report,
    winding_orders,
)
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    new_manifest,
    output_entry,
    relative,
    sha256,
    write_json,
)
from polyhedral_functions.recipes import PRESETS, apply  # noqa: E402
from polyhedral_functions.rendering import (  # noqa: E402
    DisplaySettings,
    difference_map,
    log_modulus_map,
    plane_portrait,
    render_geometry,
    render_relief,
    show_image,
)

DEFAULT_CONFIG = REPO_ROOT / "configs" / "experiments" / "E001-atlas.json"
PUBLISHED_WIDTH = 1400


def run_fixture(fixture_id: str, config: dict, settings: DisplaySettings, out: Path) -> dict:
    poly = fixtures.load(fixture_id)
    view = config["views"].get(fixture_id, config["views"]["default"])
    group = poly.symmetry_group()
    n, excl = config["comparison_samples"], config["comparison_exclusion"]
    reference = config["reference_recipe"]
    results = {name: apply(PRESETS[name], poly) for name in config["recipes"]}

    rows, tiles = [], {}
    for name, result in results.items():
        d = result.divisor
        windings = winding_orders(d)
        duality = duality_report(PRESETS[name], poly, n=n // 4, exclusion=excl)
        symmetry = symmetry_report(d, group)
        vs_ref = (
            None
            if name == reference
            else field_comparison(d, results[reference].divisor, n=n, exclusion=excl)
        )
        rows.append(
            {
                "fixture": fixture_id,
                **result.record(),
                "winding_ok": all(w["declared"] == w["measured"] for w in windings),
                "duality": duality,
                "symmetry": symmetry,
                "vs_reference": vs_ref,
                "near_pairs": len(d.near_pairs(config["near_pair_radius"])),
            }
        )
        base = out / "tiles" / fixture_id / name
        tiles[name] = {
            "geometry": render_geometry(
                poly, d, base.with_name(f"{name}-geometry.png"), view, settings
            ),
            "sphere": render_relief(
                d, base.with_name(f"{name}-sphere.png"), view, settings, "sphere"
            ),
            "relief": render_relief(d, base.with_name(f"{name}-relief.png"), view, settings),
            "neutral": render_relief(
                d, base.with_name(f"{name}-neutral.png"), view, settings, "neutral"
            ),
        }

    sheets = [
        recipe_sheet(fixture_id, poly, results, tiles, settings, out, config["sheet_dpi"]),
        difference_sheet(fixture_id, poly, results, config, settings, out),
    ]
    return {"rows": rows, "sheets": sheets, "tiles": tiles}


def recipe_sheet(fixture_id, poly, results, tiles, settings, out, dpi) -> Path:
    columns = [
        "geometry",
        "plane portrait",
        "colored sphere",
        "colored relief",
        "neutral relief",
        "log|f| / degree",
    ]
    n = len(results)
    fig, axes = plt.subplots(
        n,
        len(columns),
        figsize=(2.3 * len(columns), 2.3 * n),
        gridspec_kw={"width_ratios": [1, 1, 1, 1, 1, 1.6]},
    )
    for r, (name, result) in enumerate(results.items()):
        d = result.divisor
        show_image(axes[r, 0], tiles[name]["geometry"])
        plane_portrait(d, axes[r, 1], settings)
        show_image(axes[r, 2], tiles[name]["sphere"])
        show_image(axes[r, 3], tiles[name]["relief"])
        show_image(axes[r, 4], tiles[name]["neutral"])
        log_modulus_map(d, axes[r, 5], settings)
        orders = f"zeros ≤{d.zeros.orders.max()}, poles ≤{-d.poles.orders.min()}"
        axes[r, 0].text(
            -0.15,
            0.5,
            f"{name}\ndeg {d.degree}\n{orders}",
            transform=axes[r, 0].transAxes,
            ha="right",
            va="center",
            fontsize=8,
        )
    for c, title in enumerate(columns):
        axes[0, c].set_title(title, fontsize=8)
    summary = poly.summary()
    fig.suptitle(
        f"{fixture_id}  (V={summary['V']}, E={summary['E']}, F={summary['F']})  "
        f"fixed display: sharpness {settings.sharpness}, depth {settings.depth}; "
        "zeros blue/o, poles red/x",
        fontsize=9,
    )
    fig.tight_layout(rect=[0.06, 0, 1, 0.97])
    path = out / "sheets" / f"{fixture_id}-recipes.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
    return path


def difference_sheet(fixture_id, poly, results, config, settings, out) -> Path:
    reference = config["reference_recipe"]
    ref = results[reference].divisor
    panels = [
        (f"{name} − {reference}", results[name].divisor, ref)
        for name in results
        if name != reference
    ]
    for variant in config["placement_variants"]:
        default = apply(PRESETS[variant["recipe"]], poly).divisor
        placed = apply(PRESETS[variant["recipe"]].placed(variant["face"], variant["edge"]), poly)
        panels.append((f"{placed.recipe.name} − {variant['recipe']}", placed.divisor, default))

    fig, axes = plt.subplots(1, len(panels), figsize=(3.0 * len(panels), 2.2))
    for ax, (title, a, b) in zip(np.atleast_1d(axes), panels, strict=True):
        image = difference_map(a, b, ax, settings)
        cmp = field_comparison(
            a, b, n=config["comparison_samples"], exclusion=config["comparison_exclusion"]
        )
        ax.set_title(f"{title}\ncorr {cmp['correlation']:.3f}", fontsize=8)
    fig.colorbar(image, ax=axes, shrink=0.8, label="Δ log|f| / degree")
    fig.suptitle(
        f"{fixture_id}: per-degree differences (markers: first recipe's zeros o, poles x)",
        fontsize=9,
        y=1.12,
    )
    path = out / "sheets" / f"{fixture_id}-differences.png"
    fig.savefig(path, dpi=config["sheet_dpi"], facecolor="white", bbox_inches="tight")
    plt.close(fig)
    return path


def write_metrics_csv(rows: list[dict], path: Path) -> Path:
    fields = [
        "fixture",
        "recipe",
        "degree",
        "unreduced_degree",
        "gcd",
        "n_zeros",
        "n_poles",
        "max_zero_order",
        "max_pole_order",
        "winding_ok",
        "dual_equal",
        "dual_residual",
        "symmetry_preserved",
        "group_order",
        "corr_vs_reference",
        "rms_vs_reference",
        "near_pairs",
    ]
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            ref = row["vs_reference"] or {}
            writer.writerow(
                {
                    "fixture": row["fixture"],
                    "recipe": row["recipe"]["name"],
                    "degree": row["divisor"]["degree"],
                    "unreduced_degree": row["unreduced_degree"],
                    "gcd": row["gcd"],
                    "n_zeros": row["divisor"]["n_zeros"],
                    "n_poles": row["divisor"]["n_poles"],
                    "max_zero_order": max(row["divisor"]["zero_orders"]),
                    "max_pole_order": max(row["divisor"]["pole_orders"]),
                    "winding_ok": row["winding_ok"],
                    "dual_equal": row["duality"]["divisors_equal"],
                    "dual_residual": f"{row['duality']['max_log_modulus_residual']:.1e}",
                    "symmetry_preserved": row["symmetry"]["preserved"],
                    "group_order": row["symmetry"]["group_order"],
                    "corr_vs_reference": f"{ref['correlation']:.3f}" if ref else "",
                    "rms_vs_reference": f"{ref['rms_difference']:.3f}" if ref else "",
                    "near_pairs": row["near_pairs"],
                }
            )
    return path


def publish(manifest: dict, out: Path, config: dict) -> None:
    dest = REPO_ROOT / "experiments" / config["id"]
    (dest / "sheets").mkdir(parents=True, exist_ok=True)
    published = []
    for entry in manifest["outputs"]:
        src = REPO_ROOT / entry["path"]
        if src.parent.name != "sheets":
            continue
        image = Image.open(src).convert("RGB")
        if image.width > PUBLISHED_WIDTH:
            scale = PUBLISHED_WIDTH / image.width
            image = image.resize((PUBLISHED_WIDTH, round(image.height * scale)), Image.LANCZOS)
        # JPEG keeps the committed evidence small; the lossless sheets stay in out/.
        target = dest / "sheets" / src.with_suffix(".jpg").name
        image.save(target, quality=88, optimize=True)
        published.append({**output_entry(target), "downscaled_from": entry["path"]})
    manifest["published"] = published
    (dest / "metrics.csv").write_bytes((out / "metrics.csv").read_bytes())
    write_json(dest / "manifest.json", manifest)
    print(f"published {len(published)} sheets, manifest and metrics to {relative(dest)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("-f", "--fixture", action="append", help="only this fixture (repeatable)")
    ap.add_argument("--publish", action="store_true", help="copy evidence to experiments/<id>/")
    args = ap.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    settings = DisplaySettings(**config["display"])
    out = REPO_ROOT / "out" / config["id"]
    manifest = new_manifest(config)
    manifest["config_file"] = {"path": relative(args.config), "sha256": sha256(args.config)}
    manifest["geometry"] = {
        fid: {
            "path": relative(fixtures.DATA_DIR / f"{fid}.json"),
            "sha256": sha256(fixtures.DATA_DIR / f"{fid}.json"),
        }
        for fid in (args.fixture or config["fixtures"])
    }

    rows = []
    for fixture_id in args.fixture or config["fixtures"]:
        print(f"{fixture_id} ...", flush=True)
        result = run_fixture(fixture_id, config, settings, out)
        rows += result["rows"]
        for path in result["sheets"]:
            manifest["outputs"].append(output_entry(path))
        for recipe_tiles in result["tiles"].values():
            for path in recipe_tiles.values():
                manifest["outputs"].append(output_entry(path))

    manifest["runs"] = rows
    write_metrics_csv(rows, out / "metrics.csv")
    manifest["outputs"].append(output_entry(out / "metrics.csv"))
    write_json(out / "manifest.json", manifest)
    print(f"wrote {relative(out)}: {len(rows)} runs, {len(manifest['outputs'])} outputs")
    if args.publish:
        publish(manifest, out, config)


if __name__ == "__main__":
    main()
