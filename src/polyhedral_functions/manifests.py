"""Run manifests: what was run, on what code, with what settings, producing what.

A manifest records the fields `PROGRAM.md` §11 asks for:

- the experiment's identity and question;
- the configuration snapshot;
- the code commit and dirty-tree state;
- dependency versions;
- geometry hashes;
- outputs with their hashes;
- the metrics.

Changing a default later therefore never reinterprets an old run. Plain JSON, written with LF line
endings.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKED_PACKAGES = (
    "polyhedra-to-rational-functions",
    "complexplorer",
    "numpy",
    "scipy",
    "matplotlib",
    "pyvista",
    "vtk",
)


def git_state(root: Path = REPO_ROOT) -> dict:
    """Commit hash and whether tracked or untracked files differ from it (ignored files aside)."""

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()

    try:
        commit = git("rev-parse", "HEAD")
        changes = [line for line in git("status", "--porcelain").splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None, "changed_paths": []}
    return {
        "commit": commit,
        "dirty": bool(changes),
        "changed_paths": [line[3:] for line in changes][:50],
    }


def environment() -> dict:
    versions = {}
    for name in TRACKED_PACKAGES:
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": versions,
    }


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def relative(path: Path, root: Path = REPO_ROOT) -> str:
    """A repository-relative POSIX path, so manifests never record local absolute paths."""
    return Path(path).resolve().relative_to(root).as_posix()


def output_entry(path: Path) -> dict:
    return {"path": relative(path), "sha256": sha256(path), "bytes": Path(path).stat().st_size}


def new_manifest(config: dict) -> dict:
    """A manifest skeleton for one run of an experiment configuration."""
    return {
        "experiment": {
            k: config.get(k) for k in ("id", "question", "hypothesis", "changed_factor")
        },
        "started": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": config,
        "code": git_state(),
        "environment": environment(),
        "conventions": {
            "chart": "complexplorer stereographic: z = 0 south pole, z = inf north pole",
            "normalization": "chordal (decision 0003): log|f| = sum m log chi; geometric mean 1",
            "phase": "chart phase with C > 0",
            "evaluation": "log-domain, factored (evaluation.py)",
        },
        "runs": [],
        "outputs": [],
    }


def write_json(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False, default=_jsonable)
        fh.write("\n")
    return path


def _jsonable(value):
    try:
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return value.tolist()
    except ImportError:  # pragma: no cover
        pass
    if isinstance(value, Path):
        return value.as_posix()
    raise TypeError(f"not JSON-serializable: {type(value).__name__}")


PUBLISHED_IMAGE_WIDTH = 1400


def publish_evidence(manifest: dict, files: list[Path], experiment_id: str) -> Path:
    """Copy a run's evidence to ``experiments/<id>/`` for committing.

    Images are downscaled to `PUBLISHED_IMAGE_WIDTH` and saved as JPEG, since the lossless
    originals stay in ``out/``. Other files are copied as they are. The manifest is written
    last, with a ``published`` list of what was copied and its hashes.
    """
    from PIL import Image

    dest = REPO_ROOT / "experiments" / experiment_id
    dest.mkdir(parents=True, exist_ok=True)
    published = []
    for src in files:
        src = Path(src)
        if src.suffix.lower() == ".png":
            image = Image.open(src).convert("RGB")
            if image.width > PUBLISHED_IMAGE_WIDTH:
                height = round(image.height * PUBLISHED_IMAGE_WIDTH / image.width)
                image = image.resize((PUBLISHED_IMAGE_WIDTH, height), Image.LANCZOS)
            target = dest / src.with_suffix(".jpg").name
            image.save(target, quality=88, optimize=True)
        else:
            target = dest / src.name
            target.write_bytes(src.read_bytes())
        published.append({**output_entry(target), "source": relative(src)})
    manifest["published"] = published
    write_json(dest / "manifest.json", manifest)
    return dest
