"""E002: recipes across combinatorial transitions.

Run:  uv run python scripts/e002_transitions.py [--publish]

For each family in ``configs/experiments/E002-transitions.json`` (a cube with a small face or
short edge of size ``s``), and each recipe, this compares the recipe's function at ``s`` with
the same recipe on the cube, the family's ``s = 0`` limit. **Unreduced** divisors are compared:
gcd reduction is itself discontinuous across a transition (it can change the degree), and is
reported separately.

Outputs, in ``out/E002-transitions/``:

- ``convergence.csv``: the absolute ``log|f|`` RMS and maximum residual against the cube, away
  from features, and the closest zero-pole distance, per family x recipe x ``s``;
- ``jumps.json``: the exact **jump divisor** per family x recipe. It is the recipe at a tiny
  ``s`` with its collapsing features clustered, minus the cube's recipe, and is empty for a
  continuous recipe;
- ``transitions.png``: geometry at the illustration parameter, and residual against ``s``.
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
from polyhedral_functions.diagnostics import field_comparison  # noqa: E402
from polyhedral_functions.manifests import (  # noqa: E402
    REPO_ROOT,
    new_manifest,
    output_entry,
    publish_evidence,
    relative,
    sha256,
    write_json,
)
from polyhedral_functions.recipes import PRESETS, apply  # noqa: E402
from polyhedral_functions.rendering import (  # noqa: E402
    DisplaySettings,
    render_geometry,
    show_image,
)

CONFIG = REPO_ROOT / "configs" / "experiments" / "E002-transitions.json"


def unreduced(recipe, poly):
    result = apply(recipe, poly)
    return result.divisor * result.gcd, result


def jump_divisor(recipe, family, config) -> list[dict]:
    """Collapsed limit of the family's divisor minus the cube's, as a list of signed points."""
    near_limit, _ = unreduced(recipe, family(config["limit_parameter"]))
    limit, _ = near_limit.coalesced(tol=config["limit_cluster_tol"])
    cube, _ = unreduced(recipe, families.cube())
    jump, _ = (limit - cube).coalesced(tol=config["limit_cluster_tol"])
    return [
        {"direction": [round(float(c), 4) for c in p], "order": int(o)}
        for p, o in zip(jump.points, jump.orders, strict=True)
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    out = REPO_ROOT / "out" / config["id"]
    out.mkdir(parents=True, exist_ok=True)
    manifest = new_manifest(config)
    manifest["config_file"] = {"path": relative(CONFIG), "sha256": sha256(CONFIG)}

    cube = families.cube()
    rows, jumps = [], {}
    for fam_name in config["families"]:
        family = getattr(families, fam_name)
        jumps[fam_name] = {}
        for name in config["recipes"]:
            recipe = PRESETS[name]
            reference, ref_result = unreduced(recipe, cube)
            jumps[fam_name][name] = jump_divisor(recipe, family, config)
            for s in config["parameters"]:
                poly = family(s)
                d, result = unreduced(recipe, poly)
                cmp = field_comparison(
                    d,
                    reference,
                    n=config["comparison_samples"],
                    exclusion=config["comparison_exclusion"],
                    per_degree=False,
                )
                pairs = result.divisor.near_pairs(config["near_pair_radius"])
                rows.append(
                    {
                        "family": fam_name,
                        "recipe": name,
                        "s": s,
                        "unreduced_degree": result.unreduced_degree,
                        "reduced_degree": result.degree,
                        "cube_reduced_degree": ref_result.degree,
                        "rms_residual": cmp["rms_difference"],
                        "max_residual": cmp["max_abs_difference"],
                        "min_zero_pole_distance": min(
                            (p["chordal_distance"] for p in pairs), default=float("nan")
                        ),
                    }
                )
            print(f"{fam_name:24} {name:5} jump: {jumps[fam_name][name] or 'none (continuous)'}")

    csv_path = out / "convergence.csv"
    with csv_path.open("w", encoding="utf-8", newline="\n") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in row.items()}
            )
    jumps_path = write_json(out / "jumps.json", jumps)

    figure_path = figure(config, rows, out)
    manifest["runs"] = rows
    manifest["jumps"] = jumps
    manifest["outputs"] = [output_entry(p) for p in (csv_path, jumps_path, figure_path)]
    write_json(out / "manifest.json", manifest)
    print(f"wrote {relative(out)}")
    if args.publish:
        dest = publish_evidence(manifest, [csv_path, jumps_path, figure_path], config["id"])
        print(f"published to {relative(dest)}")


def figure(config, rows, out):
    settings = DisplaySettings(window=config["display"]["window"])
    fams = config["families"]
    fig, axes = plt.subplots(
        2, len(fams), figsize=(4.2 * len(fams), 7.6), gridspec_kw={"height_ratios": [1, 1.1]}
    )
    illus = PRESETS[config["illustration_recipe"]]
    for c, fam_name in enumerate(fams):
        poly = getattr(families, fam_name)(config["illustration_parameter"])
        tile = render_geometry(
            poly,
            apply(illus, poly).divisor,
            out / "tiles" / f"{fam_name}.png",
            (2.0, 1.4, 1.2),
            settings,
        )
        show_image(
            axes[0, c],
            tile,
            f"{fam_name}, s = {config['illustration_parameter']}"
            f"\n({illus.name} zeros blue, poles red)",
        )
        ax = axes[1, c]
        for name in config["recipes"]:
            pts = [
                (r["s"], r["rms_residual"])
                for r in rows
                if r["family"] == fam_name and r["recipe"] == name
            ]
            s, rms = np.array(pts).T
            ax.loglog(s, np.maximum(rms, 1e-12), marker="o", ms=3, label=name)
        ax.set_xlabel("s (size of the vanishing face / edge)", fontsize=8)
        ax.set_ylabel("RMS |Δ log|f|| vs cube (unreduced)", fontsize=8)
        ax.set_ylim(1e-9, 20)
        ax.tick_params(labelsize=7)
        ax.grid(True, which="major", alpha=0.3)
    axes[1, 0].legend(fontsize=7)
    fig.suptitle(
        "E002: does the recipe's function converge to the cube's as the new feature "
        "vanishes? (flat = jump, falling = continuous)",
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path = out / "transitions.png"
    fig.savefig(path, dpi=110, facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    main()
