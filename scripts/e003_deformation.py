"""E003: recipes under fixed-combinatorics deformation, and when placement leaves its cell.

Run:  uv run python scripts/e003_deformation.py [--publish]

For each family in ``configs/experiments/E003-deformation.json`` (pyramid apex height, box
shear), at each parameter value, this computes:

- each recipe's **continuity**: the absolute ``log|f|`` RMS residual against the reference
  parameter, and the largest ratio of residual to parameter step between neighbouring values;
- **shape separations**, as per-degree correlations: R1 against R2, R2 polar against R2
  centroid, R4ve foot against R4ve midpoint;
- the **placement criterion** (`diagnostics.placement_report`): faces whose polar direction lies
  outside the face's cone, and edges whose foot lies off the edge.

Outputs go to ``out/E003-deformation/``: ``deformation.csv``, ``deformation.png`` (curves) and
``geometry.png`` (R2 polar against R2 centroid at selected parameters).
"""

from __future__ import annotations

import argparse
import csv
import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from polyhedral_functions import families  # noqa: E402
from polyhedral_functions.diagnostics import field_comparison, placement_report  # noqa: E402
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    new_manifest,
    output_entry,
    publish_evidence,
    relative,
    sha256,
    write_json,
)
from polyhedral_functions.recipes import PRESETS, R2, R4VE, apply  # noqa: E402
from polyhedral_functions.rendering import (  # noqa: E402
    DisplaySettings,
    render_geometry,
    show_image,
)

CONFIG = REPO_ROOT / "configs" / "experiments" / "E003-deformation.json"


def unreduced(recipe, poly):
    result = apply(recipe, poly)
    return result.divisor * result.gcd


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    out = REPO_ROOT / "out" / config["id"]
    out.mkdir(parents=True, exist_ok=True)
    manifest = new_manifest(config)
    manifest["config_file"] = {"path": relative(CONFIG), "sha256": sha256(CONFIG)}
    n, excl = config["comparison_samples"], config["comparison_exclusion"]

    def compare(a, b, per_degree=True):
        return field_comparison(a, b, n=n, exclusion=excl, per_degree=per_degree)

    rows = []
    for fam_name, spec in config["families"].items():
        family = getattr(families, fam_name)
        params = spec["parameters"]
        reference = {
            name: unreduced(PRESETS[name], family(spec["reference"])) for name in config["recipes"]
        }
        previous = {}
        for p in params:
            poly = family(p)
            row = {"family": fam_name, "parameter": p, **placement_report(poly)}
            current = {name: unreduced(PRESETS[name], poly) for name in config["recipes"]}
            for name, d in current.items():
                row[f"{name}_rms_vs_reference"] = compare(d, reference[name], False)[
                    "rms_difference"
                ]
                if name in previous:
                    prev_p, prev_d = previous[name]
                    step = compare(d, prev_d, False)["rms_difference"] / abs(p - prev_p)
                    row[f"{name}_rms_per_step"] = step
            previous = {name: (p, d) for name, d in current.items()}
            row["corr_R1_R2"] = compare(
                apply(PRESETS["R1"], poly).divisor, apply(R2, poly).divisor
            )["correlation"]
            row["corr_R2_polar_centroid"] = compare(
                apply(R2, poly).divisor, apply(R2.placed(face="centroid"), poly).divisor
            )["correlation"]
            row["corr_R4ve_foot_midpoint"] = compare(
                apply(R4VE, poly).divisor, apply(R4VE.placed(edge="midpoint"), poly).divisor
            )["correlation"]
            rows.append(row)
            print(
                f"{fam_name:18} {p:5}: faces polar outside {row['faces_polar_outside']}, "
                f"R1~R2 {row['corr_R1_R2']:.3f}, polar~centroid {row['corr_R2_polar_centroid']:.3f}"
            )

    fields = sorted(
        {k for r in rows for k in r}, key=lambda k: (k not in ("family", "parameter"), k)
    )
    csv_path = out / "deformation.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in row.items()}
            )

    curves = curves_figure(config, rows, out)
    geometry = geometry_figure(config, out)
    manifest["runs"] = rows
    manifest["outputs"] = [output_entry(p) for p in (csv_path, curves, geometry)]
    write_json(out / "manifest.json", manifest)
    print(f"wrote {relative(out)}")
    if args.publish:
        dest = publish_evidence(manifest, [csv_path, curves, geometry], config["id"])
        print(f"published to {relative(dest)}")


def curves_figure(config, rows, out):
    fams = list(config["families"])
    fig, axes = plt.subplots(3, len(fams), figsize=(5.2 * len(fams), 9.5))
    for c, fam in enumerate(fams):
        spec = config["families"][fam]
        rs = [r for r in rows if r["family"] == fam]
        p = np.array([r["parameter"] for r in rs])

        ax = axes[0, c]
        for name in config["recipes"]:
            ax.plot(p, [r[f"{name}_rms_vs_reference"] for r in rs], marker="o", ms=3, label=name)
        ax.axvline(spec["reference"], color="gray", lw=0.8, ls=":")
        ax.set_ylabel("RMS Δ log|f| vs reference", fontsize=8)
        ax.set_title(f"{fam}: continuity (smooth, zero at the reference)", fontsize=9)
        ax.legend(fontsize=7)

        ax = axes[1, c]
        ax.plot(p, [r["corr_R1_R2"] for r in rs], marker="o", ms=3, label="R1 ~ R2")
        ax.plot(
            p,
            [r["corr_R2_polar_centroid"] for r in rs],
            marker="s",
            ms=3,
            label="R2 polar ~ centroid",
        )
        ax.plot(
            p,
            [r["corr_R4ve_foot_midpoint"] for r in rs],
            marker="^",
            ms=3,
            label="R4ve foot ~ midpoint",
        )
        ax.set_ylabel("per-degree correlation", fontsize=8)
        ax.set_ylim(min(0.0, ax.get_ylim()[0]), 1.02)
        ax.set_title("shape separations", fontsize=9)
        ax.legend(fontsize=7)

        ax = axes[2, c]
        ax.plot(
            p,
            [r["faces_polar_min_margin"] for r in rs],
            marker="o",
            ms=3,
            label="min face-cone margin of polar directions",
        )
        ax.plot(
            p,
            [abs(r["edges_foot_worst_t"] - 0.5) for r in rs],
            marker="s",
            ms=3,
            label="max |edge-foot t − 0.5| (off the edge above 0.5)",
        )
        ax.axhline(0, color="k", lw=0.8)
        ax.axhline(0.5, color="k", lw=0.5, ls="--")
        ax.set_xlabel(spec["label"], fontsize=8)
        ax.set_title(
            "placement: is the feature over its own cell? (margin < 0 or |t − 0.5| > 0.5: no)",
            fontsize=9,
        )
        ax.legend(fontsize=7)
        for a in axes[:, c]:
            a.tick_params(labelsize=7)
            a.grid(True, alpha=0.3)
    fig.suptitle("E003: fixed-combinatorics deformation", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    path = out / "deformation.png"
    fig.savefig(path, dpi=110, facecolor="white")
    plt.close(fig)
    return path


def geometry_figure(config, out):
    settings = DisplaySettings(window=config["display"]["window"])
    fams = list(config["families"])
    cols = max(len(config["families"][f]["illustrate"]) for f in fams)
    fig, axes = plt.subplots(2 * len(fams), cols, figsize=(3.0 * cols, 3.0 * 2 * len(fams)))
    for f, fam in enumerate(fams):
        for c, p in enumerate(config["families"][fam]["illustrate"]):
            poly = getattr(families, fam)(p)
            for r, recipe in enumerate((R2, R2.placed(face="centroid"))):
                tile = render_geometry(
                    poly,
                    apply(recipe, poly).divisor,
                    out / "tiles" / f"{fam}-{p:g}-{r}.png",
                    (2.2, 1.0, 0.9),
                    settings,
                )
                show_image(axes[2 * f + r, c], tile, f"{fam} {p:g}: {recipe.name}")
    fig.suptitle(
        "R2 poles (red) at polar directions (rows 1, 3) vs face centroids (rows 2, 4)", fontsize=10
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    path = out / "geometry.png"
    fig.savefig(path, dpi=100, facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    main()
