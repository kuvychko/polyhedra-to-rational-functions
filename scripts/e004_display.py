"""E004: how much of the visible difference between recipes is the display?

Run:  uv run python scripts/e004_display.py [--publish]

For each fixture, recipe pair and display mapping in ``configs/experiments/E004-display.json``,
this compares the **relief radius fields** ``r(x)`` (`rendering.relief_radius`) of two recipes on
Fibonacci samples. The radii are bounded, so no exclusion caps are needed. It reports their
correlation and RMS difference, and each relief's spread and tip exponent (max order /
sharpness).

The display mappings change only the logistic scale ``k``; the functions are untouched:

- ``fixed``: the same ``k`` for every recipe, as in the E001 atlas;
- ``order-tuned``: ``k = 2 x max |order|``, the baseline's rule, which gives every recipe the same
  tip exponent 1/2;
- ``degree-compressed``: ``k = degree / 6``, so the logistic sees ``log|f| / degree``.

Outputs, in ``out/E004-display/``: ``display.csv``, ``display.png`` (correlations) and
``reliefs-<fixture>.png`` (neutral reliefs, recipe x display).
"""

from __future__ import annotations

import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from polyhedral_functions import fixtures  # noqa: E402
from polyhedral_functions.evaluation import log_modulus_on_sphere  # noqa: E402
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    new_manifest,
    output_entry,
    publish_evidence,
    relative,
    sha256,
    write_json,
)
from polyhedral_functions.normalization import fibonacci_sphere  # noqa: E402
from polyhedral_functions.recipes import PRESETS, apply  # noqa: E402
from polyhedral_functions.rendering import (  # noqa: E402
    DisplaySettings,
    relief_radius,
    render_relief,
    show_image,
)

CONFIG = REPO_ROOT / "configs" / "experiments" / "E004-display.json"


def sharpness(display: dict, divisor) -> float:
    if "value" in display:
        return display["value"]
    if "factor" in display:
        return display["factor"] * int(np.abs(divisor.orders).max())
    return display["per_degree"] * divisor.degree


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    out = REPO_ROOT / "out" / config["id"]
    out.mkdir(parents=True, exist_ok=True)
    manifest = new_manifest(config)
    manifest["config_file"] = {"path": relative(CONFIG), "sha256": sha256(CONFIG)}
    x = fibonacci_sphere(config["samples"])
    depth = config["depth"]

    rows = []
    for fixture_id in config["fixtures"]:
        poly = fixtures.load(fixture_id)
        divisors = {name: apply(PRESETS[name], poly).divisor for name in config["recipes"]}
        logs = {name: log_modulus_on_sphere(d, x) for name, d in divisors.items()}
        for mode, display in config["displays"].items():
            k = {name: sharpness(display, d) for name, d in divisors.items()}
            radius = {name: relief_radius(logs[name], k[name], depth) for name in divisors}
            for a, b in config["pairs"]:
                ra, rb = radius[a], radius[b]
                rows.append(
                    {
                        "fixture": fixture_id,
                        "display": mode,
                        "pair": f"{a}~{b}",
                        "correlation": float(np.corrcoef(ra, rb)[0, 1]),
                        "rms_radius_difference": float(np.sqrt(np.mean((ra - rb) ** 2))),
                        f"sharpness_{a}": k[a],
                        f"sharpness_{b}": k[b],
                        f"tip_exponent_{a}": int(np.abs(divisors[a].orders).max()) / k[a],
                        f"tip_exponent_{b}": int(np.abs(divisors[b].orders).max()) / k[b],
                        f"radius_spread_{a}": float(ra.std()),
                        f"radius_spread_{b}": float(rb.std()),
                    }
                )
        print(
            f"{fixture_id}: "
            + ", ".join(
                f"{r['display']} {r['pair']} {r['correlation']:.3f}"
                for r in rows
                if r["fixture"] == fixture_id
            )
        )

    fields = []
    for row in rows:
        fields += [k for k in row if k not in fields]
    csv_path = out / "display.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in row.items()}
            )

    figures = [correlation_figure(config, rows, out)]
    figures += [relief_grid(config, fixture_id, out) for fixture_id in config["render_fixtures"]]
    manifest["runs"] = rows
    manifest["outputs"] = [output_entry(p) for p in (csv_path, *figures)]
    write_json(out / "manifest.json", manifest)
    print(f"wrote {relative(out)}")
    if args.publish:
        dest = publish_evidence(manifest, [csv_path, *figures], config["id"])
        print(f"published to {relative(dest)}")


def correlation_figure(config, rows, out):
    pairs = [f"{a}~{b}" for a, b in config["pairs"]]
    modes = list(config["displays"])
    fig, axes = plt.subplots(1, len(pairs), figsize=(6.0 * len(pairs), 3.8), sharey=True)
    width = 0.8 / len(modes)
    for ax, pair in zip(axes, pairs, strict=True):
        for m, mode in enumerate(modes):
            vals = [
                next(
                    r["correlation"]
                    for r in rows
                    if r["fixture"] == f and r["display"] == mode and r["pair"] == pair
                )
                for f in config["fixtures"]
            ]
            ax.bar(np.arange(len(vals)) + m * width, vals, width, label=mode)
        ax.set_xticks(np.arange(len(config["fixtures"])) + width * (len(modes) - 1) / 2)
        ax.set_xticklabels(config["fixtures"], rotation=25, ha="right", fontsize=7)
        ax.set_title(f"relief radius correlation, {pair}", fontsize=9)
        ax.set_ylim(0, 1.02)
        ax.grid(True, axis="y", alpha=0.3)
    axes[0].legend(fontsize=7)
    fig.suptitle("E004: the same functions under three display mappings", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    path = out / "display.png"
    fig.savefig(path, dpi=110, facecolor="white")
    plt.close(fig)
    return path


def relief_grid(config, fixture_id, out):
    poly = fixtures.load(fixture_id)
    view = config["views"][fixture_id]
    modes = list(config["displays"])
    fig, axes = plt.subplots(
        len(config["recipes"]), len(modes), figsize=(2.8 * len(modes), 2.8 * len(config["recipes"]))
    )
    for r, name in enumerate(config["recipes"]):
        d = apply(PRESETS[name], poly).divisor
        for c, mode in enumerate(modes):
            k = sharpness(config["displays"][mode], d)
            settings = DisplaySettings(
                relief_resolution=config["display"]["relief_resolution"],
                window=config["display"]["window"],
                depth=config["depth"],
                sharpness=k,
            )
            tile = render_relief(
                d, out / "tiles" / f"{fixture_id}-{name}-{mode}.png", view, settings, "neutral"
            )
            show_image(axes[r, c], tile, f"{name} (deg {d.degree}), {mode}: k = {k:.3g}")
    fig.suptitle(f"{fixture_id}: neutral reliefs, recipe (rows) x display (columns)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path = out / f"reliefs-{fixture_id}.png"
    fig.savefig(path, dpi=100, facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    main()
